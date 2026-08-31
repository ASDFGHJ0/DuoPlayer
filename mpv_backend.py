from __future__ import annotations

import ctypes
import json
import os
import subprocess
import threading
import time
import uuid
from pathlib import Path


def find_mpv() -> str:
    candidates = [
        Path(r"C:\Program Files\MPV Player\mpv.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "mpv" / "mpv.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return "mpv.exe"


class MpvController:
    """Small mpv JSON-IPC adapter with the VLC-like methods used by the UI."""

    def __init__(self, state_callback=None):
        self.executable = find_mpv()
        self.state_callback = state_callback
        self.process = None
        self.pipe = None
        self.command_pipe = None
        self.pipe_path = rf"\\.\pipe\duoplayer-{uuid.uuid4().hex}"
        self.writer_lock = threading.Lock()
        self.pending = []
        self.properties = {
            "time-pos": 0.0, "duration": 0.0, "pause": True,
            "eof-reached": False, "paused-for-cache": False,
            "video-params": {}, "track-list": [], "aid": "no", "sid": "no",
            "speed": 1.0, "mute": False, "volume": 80,
        }
        self.hwnd = None
        self.path = None
        self.rotation = 0
        self.closed = False

    def set_hwnd(self, hwnd: int) -> None:
        self.hwnd = int(hwnd)
        if not self.process:
            self._start()

    def resize(self, width: int, height: int) -> int:
        """Fill the native host using its physical client pixels (DPI-safe)."""
        if os.name != "nt" or not self.process or self.process.poll() is not None:
            return 0
        user32 = ctypes.windll.user32
        class Rect(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        client = Rect()
        if user32.GetClientRect(ctypes.c_void_p(self.hwnd), ctypes.byref(client)):
            width = max(1, client.right - client.left)
            height = max(1, client.bottom - client.top)
        else:
            width, height = max(1, int(width)), max(1, int(height))
        count = 0
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def visit(child, _lparam):
            nonlocal count
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(child, ctypes.byref(pid))
            if pid.value == self.process.pid:
                user32.ShowWindow(child, 5)
                user32.SetWindowPos(child, ctypes.c_void_p(0), 0, 0, width, height, 0x0010 | 0x0040)
                count += 1
            return True

        callback = callback_type(visit)
        user32.EnumChildWindows(ctypes.c_void_p(self.hwnd), callback, 0)
        return count

    def _start(self) -> None:
        args = [
            self.executable, f"--wid={self.hwnd}", "--idle=yes", "--force-window=immediate",
            "--keep-open=yes", "--no-config", "--input-default-bindings=no",
            f"--input-ipc-server={self.pipe_path}", "--terminal=no", "--msg-level=all=no",
            "--hwdec=auto", "--cache=yes", "--cache-secs=8", "--demuxer-readahead-secs=8",
            "--video-sync=display-resample", "--audio-pitch-correction=yes",
            "--keepaspect=yes", "--video-align-x=0", "--video-align-y=0", "--panscan=0",
        ]
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self.process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, creationflags=flags)
        threading.Thread(target=self._connect, daemon=True).start()

    def _connect(self) -> None:
        deadline = time.monotonic() + 8
        binary = getattr(os, "O_BINARY", 0)
        while not self.closed and time.monotonic() < deadline:
            try:
                self.pipe = os.open(self.pipe_path, os.O_RDWR | binary)
                break
            except OSError:
                time.sleep(0.05)
        if self.pipe is None:
            self._notify("error")
            return
        for idx, name in enumerate(("time-pos", "duration", "pause", "eof-reached",
                                    "paused-for-cache", "video-params", "track-list", "aid", "sid",
                                    "speed", "mute", "volume"), 1):
            payload = {"command": ["observe_property", idx, name]}
            os.write(self.pipe, (json.dumps(payload) + "\n").encode("utf-8"))
        while not self.closed and time.monotonic() < deadline:
            try:
                self.command_pipe = os.open(self.pipe_path, os.O_RDWR | binary)
                break
            except OSError:
                time.sleep(0.05)
        if self.command_pipe is None:
            self._notify("error")
            return
        queued, self.pending = self.pending, []
        for command in queued:
            self._write(command)
        buffer = b""
        try:
            while not self.closed:
                chunk = os.read(self.pipe, 65536)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line:
                        try:
                            self._handle(json.loads(line.decode("utf-8", errors="replace")))
                        except ValueError:
                            pass
        except OSError:
            if not self.closed:
                self._notify("error")

    def _handle(self, payload: dict) -> None:
        event = payload.get("event")
        if event == "property-change":
            name = payload.get("name")
            if name:
                self.properties[name] = payload.get("data")
            if name == "paused-for-cache" and payload.get("data"):
                self._notify("buffering")
            elif name == "eof-reached" and payload.get("data"):
                self._notify("ended")
            elif name == "pause":
                self._notify("paused" if payload.get("data") else "playing")
        elif event == "file-loaded":
            self._notify("playing")
        elif event == "end-file":
            if payload.get("reason") == "error":
                self._notify("error")
            elif payload.get("reason") == "eof":
                self._notify("ended")

    def _notify(self, state: str) -> None:
        if self.state_callback:
            try:
                self.state_callback(None, state)
            except Exception:
                pass

    def _write(self, payload: dict) -> None:
        if self.command_pipe is None:
            self.pending.append(payload)
            return
        try:
            raw = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
            with self.writer_lock:
                os.write(self.command_pipe, raw)
        except OSError:
            self._notify("error")

    def command(self, *parts) -> None:
        self._write({"command": list(parts)})

    def load(self, path: str) -> None:
        self.path = path
        self.properties.update({"time-pos": 0.0, "duration": 0.0, "eof-reached": False, "pause": False})
        self.command("loadfile", path, "replace")
        self.command("set_property", "video-rotate", self.rotation)

    def play(self): self.command("set_property", "pause", False)
    def pause(self): self.command("set_property", "pause", True)
    def set_pause(self, value): self.pause() if value else self.play()
    def stop(self): self.command("stop")
    def is_playing(self): return int(not bool(self.properties.get("pause", True)) and not bool(self.properties.get("eof-reached")))
    def get_time(self): return int(float(self.properties.get("time-pos") or 0) * 1000)
    def set_time(self, ms): self.command("set_property", "time-pos", max(0, ms) / 1000)
    def get_length(self): return int(float(self.properties.get("duration") or 0) * 1000)
    def set_rate(self, rate): self.properties["speed"] = rate; self.command("set_property", "speed", rate)
    def audio_set_volume(self, volume): self.properties["volume"] = volume; self.command("set_property", "volume", volume)
    def audio_set_mute(self, mute): self.properties["mute"] = bool(mute); self.command("set_property", "mute", bool(mute))
    def audio_get_mute(self): return int(bool(self.properties.get("mute")))
    def video_set_scale(self, _scale): self.command("set_property", "video-unscaled", False)

    def set_rotation(self, degrees: int) -> None:
        self.rotation = degrees % 360
        self.command("set_property", "video-rotate", self.rotation)

    def video_get_size(self, _track=0):
        data = self.properties.get("video-params") or {}
        w, h = int(data.get("dw", data.get("w", 0)) or 0), int(data.get("dh", data.get("h", 0)) or 0)
        return (w, h)

    def get_tracks(self, track_type: str):
        tracks = self.properties.get("track-list") or []
        return [track for track in tracks if track.get("type") == track_type]

    def select_audio_track(self, track_id):
        self.command("set_property", "aid", track_id if track_id is not None else "no")

    def select_subtitle_track(self, track_id):
        self.command("set_property", "sid", track_id if track_id is not None else "no")

    def video_set_subtitle_file(self, path): self.command("sub-add", path, "select"); return True
    def video_take_snapshot(self, _num, path, _w, _h): self.command("screenshot-to-file", path, "video"); return 0

    def release(self) -> None:
        try:
            self.command("quit")
        except Exception:
            pass
        self.closed = True
        try:
            if self.pipe is not None:
                os.close(self.pipe)
                self.pipe = None
            if self.command_pipe is not None:
                os.close(self.command_pipe)
                self.command_pipe = None
        except OSError:
            pass
        if self.process and self.process.poll() is None:
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.terminate()
