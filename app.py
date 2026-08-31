from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        pass

from PySide6.QtCore import QEasingCurve, QPoint, QRect, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QGraphicsBlurEffect, QGraphicsDropShadowEffect, QHBoxLayout,
    QLabel, QPushButton, QSizeGrip, QSizePolicy, QSlider, QVBoxLayout, QWidget
)

from mpv_backend import MpvController


BG = "#080A0D"
SURFACE = "#0B0E12"
PANEL = "rgba(15,20,28,225)"
HOVER = "rgba(255,255,255,15)"
TEXT = "#F4F7FB"
SECONDARY = "#8E98A8"
WEAK = "#5F6877"
CYAN = "#69E2FF"
BLUE = "#4D8DFF"
VIOLET = "#8B7CFF"
VIDEO_TYPES = "Videos (*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv *.ts *.m2ts *.mpeg *.mpg *.m4v *.3gp *.ogv);;All files (*.*)"

def fmt_time(ms: int) -> str:
    seconds = max(0, int(ms / 1000))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"

OVERLAY_KEY = "#010203"


def enable_color_key(widget):
    """Make a native Qt overlay background transparent above mpv on Windows."""
    if sys.platform != "win32":
        return
    widget.setAttribute(Qt.WA_NativeWindow)
    hwnd = int(widget.winId())
    user32 = ctypes.windll.user32
    get_style = user32.GetWindowLongPtrW
    set_style = user32.SetWindowLongPtrW
    get_style.argtypes = [ctypes.c_void_p, ctypes.c_int]
    get_style.restype = ctypes.c_ssize_t
    set_style.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t]
    set_style.restype = ctypes.c_ssize_t
    ex_style = get_style(ctypes.c_void_p(hwnd), -20)
    set_style(ctypes.c_void_p(hwnd), -20, ex_style | 0x00080000)
    user32.SetLayeredWindowAttributes(ctypes.c_void_p(hwnd), 0x00030201, 255, 0x00000001)
    if isinstance(widget, IconButton):
        widget.keyed_overlay = True
        widget.update()


ICONS = {
    "play": '<polygon points="9 7 22 15 9 23 9 7"/>',
    "pause": '<line x1="11" y1="8" x2="11" y2="22"/><line x1="19" y1="8" x2="19" y2="22"/>',
    "rewind": '<path d="M3 12a12 12 0 1 0 4-7"/><polyline points="3 4 3 12 11 12"/><path d="M10 13v5M14 13v5"/>',
    "forward": '<path d="M27 12a12 12 0 1 1-4-7"/><polyline points="27 4 27 12 19 12"/><path d="M16 13v5M20 13v5"/>',
    "volume": '<polygon points="5 12 10 12 16 7 16 23 10 18 5 18 5 12"/><path d="M21 11a6 6 0 0 1 0 8"/>',
    "muted": '<polygon points="5 12 10 12 16 7 16 23 10 18 5 18 5 12"/><line x1="21" y1="12" x2="27" y2="18"/><line x1="27" y1="12" x2="21" y2="18"/>',
    "captions": '<rect x="4" y="7" width="22" height="16" rx="3"/><path d="M13 13a3 3 0 1 0 0 4M23 13a3 3 0 1 0 0 4"/>',
    "rotate": '<path d="M25 10a11 11 0 1 0 1 9"/><polyline points="25 3 25 10 18 10"/>',
    "fullscreen": '<polyline points="12 4 4 4 4 12"/><polyline points="18 4 26 4 26 12"/><polyline points="4 18 4 26 12 26"/><polyline points="26 18 26 26 18 26"/>',
    "more": '<circle cx="7" cy="15" r="1.5" fill="currentColor" stroke="none"/><circle cx="15" cy="15" r="1.5" fill="currentColor" stroke="none"/><circle cx="23" cy="15" r="1.5" fill="currentColor" stroke="none"/>',
    "folder": '<path d="M3 8a3 3 0 0 1 3-3h6l3 3h9a3 3 0 0 1 3 3v11a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V8z"/>',
    "camera": '<path d="M5 10h4l2-3h8l2 3h4a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V12a2 2 0 0 1 2-2z"/><circle cx="15" cy="17" r="5"/>',
    "window": '<rect x="4" y="5" width="22" height="20" rx="3"/><line x1="4" y1="11" x2="26" y2="11"/>',
    "pin": '<path d="M11 4h8l-1 7 4 4H8l4-4-1-7z"/><line x1="15" y1="15" x2="15" y2="27"/>',
    "prev": '<line x1="9" y1="7" x2="9" y2="23"/><polygon points="23 7 11 15 23 23 23 7"/>',
    "next": '<line x1="21" y1="7" x2="21" y2="23"/><polygon points="7 7 19 15 7 23 7 7"/>',
    "list": '<line x1="10" y1="8" x2="26" y2="8"/><line x1="10" y1="15" x2="26" y2="15"/><line x1="10" y1="22" x2="26" y2="22"/><circle cx="5" cy="8" r="1"/><circle cx="5" cy="15" r="1"/><circle cx="5" cy="22" r="1"/>',
    "music": '<path d="M11 22V8l13-3v14"/><circle cx="7" cy="22" r="4"/><circle cx="20" cy="19" r="4"/>',
    "loop": '<path d="M24 11l3 3-3 3"/><path d="M6 14a6 6 0 0 1 6-6h13"/><path d="M6 19l-3-3 3-3"/><path d="M24 16a6 6 0 0 1-6 6H5"/>',
    "pip": '<rect x="3" y="5" width="24" height="20" rx="3"/><rect x="15" y="14" width="9" height="7" rx="1"/>',
    "minimize": '<line x1="7" y1="19" x2="23" y2="19"/>',
    "maximize": '<rect x="7" y="7" width="16" height="16" rx="2"/>',
    "close": '<line x1="8" y1="8" x2="22" y2="22"/><line x1="22" y1="8" x2="8" y2="22"/>',
}


def svg_bytes(name: str, color=TEXT, width=30, stroke=1.8) -> bytes:
    body = ICONS[name].replace("currentColor", color)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{width}" viewBox="0 0 30 30"
      fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'''.encode()


class SvgIcon(QWidget):
    def __init__(self, name, color=TEXT, size=22, parent=None):
        super().__init__(parent)
        self.name, self.color, self.icon_size = name, color, size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        QSvgRenderer(svg_bytes(self.name, self.color, self.icon_size)).render(p, self.rect())


class IconButton(QPushButton):
    def __init__(self, icon, tooltip="", size=40, icon_size=20, parent=None, accent=False):
        super().__init__(parent)
        self.icon_name, self.icon_size, self.accent = icon, icon_size, accent
        self.keyed_overlay = False; self.keyed_circle = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setStyleSheet(f'''
            QPushButton {{ background: transparent; border: none; border-radius: {size//2}px; }}
            QPushButton:hover {{ background: rgba(255,255,255,0.065); }}
            QPushButton:pressed {{ background: rgba(255,255,255,0.10); }}
        ''')
        if accent:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(28); shadow.setColor(QColor(105, 226, 255, 70)); shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)

    def set_icon(self, name):
        self.icon_name = name
        self.update()

    def paintEvent(self, event):
        if not self.keyed_overlay:
            super().paintEvent(event)
        p = QPainter(self)
        if self.keyed_overlay:
            p.setCompositionMode(QPainter.CompositionMode_Source)
            p.fillRect(self.rect(), QColor(1,2,3))
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setRenderHint(QPainter.Antialiasing)
            if self.keyed_circle:
                p.setPen(Qt.NoPen); p.setBrush(QColor(8,12,18))
                p.drawEllipse(self.rect().adjusted(1,1,-1,-1))
            elif self.underMouse():
                p.setPen(Qt.NoPen); p.setBrush(QColor(27,32,40))
                p.drawEllipse(self.rect().adjusted(1,1,-1,-1))
        p.setRenderHint(QPainter.Antialiasing)
        if self.accent:
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0, QColor(105, 226, 255, 45)); grad.setColorAt(1, QColor(139, 124, 255, 35))
            p.setPen(QPen(QColor(105, 226, 255, 85), 1))
            p.setBrush(grad)
            p.drawEllipse(self.rect().adjusted(2, 2, -2, -2))
        margin = (self.width() - self.icon_size) // 2
        QSvgRenderer(svg_bytes(self.icon_name, TEXT, self.icon_size, 1.8)).render(p, QRect(margin, margin, self.icon_size, self.icon_size))


class PillButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setMinimumWidth(56)
        self.setStyleSheet('''
            QPushButton { color: #DCE3EC; background: rgba(255,255,255,0.035); border: none;
                          border-radius: 11px; padding: 0 13px; font: 500 12px "Segoe UI Variable"; }
            QPushButton:hover { background: rgba(255,255,255,0.075); color: #FFFFFF; }
            QPushButton:pressed { background: rgba(255,255,255,0.10); }
        ''')


class Timeline(QWidget):
    seeked = Signal(float)
    preview = Signal(float, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.hovered = False
        self.dragging = False
        self.setFixedHeight(20)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def set_progress(self, value):
        if not self.dragging:
            self.progress = max(0.0, min(1.0, value)); self.update()

    def _fraction(self, x):
        return max(0.0, min(1.0, (x - 7) / max(1, self.width() - 14)))

    def paintEvent(self, _event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        h = 6 if self.hovered or self.dragging else 3
        y = (self.height() - h) / 2
        track = QRect(7, int(y), self.width() - 14, h)
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 28)); p.drawRoundedRect(track, h/2, h/2)
        played = QRect(track.x(), track.y(), int(track.width() * self.progress), track.height())
        grad = QLinearGradient(played.left(), 0, max(played.right(), played.left()+1), 0)
        grad.setColorAt(0, QColor(CYAN)); grad.setColorAt(.55, QColor(BLUE)); grad.setColorAt(1, QColor(VIOLET))
        p.setBrush(grad); p.drawRoundedRect(played, h/2, h/2)
        x = track.x() + track.width() * self.progress
        if self.hovered or self.dragging:
            p.setBrush(QColor(105, 226, 255, 45)); p.drawEllipse(QPoint(int(x), self.height()//2), 9, 9)
            p.setBrush(QColor(TEXT)); p.drawEllipse(QPoint(int(x), self.height()//2), 5, 5)

    def enterEvent(self, event): self.hovered = True; self.update(); super().enterEvent(event)
    def leaveEvent(self, event): self.hovered = False; self.preview.emit(-1, 0); self.update(); super().leaveEvent(event)
    def mouseMoveEvent(self, event): self.preview.emit(self._fraction(event.position().x()), int(event.position().x())); super().mouseMoveEvent(event)
    def mousePressEvent(self, event): self.dragging = True; self.progress = self._fraction(event.position().x()); self.update()
    def mouseReleaseEvent(self, event):
        self.progress = self._fraction(event.position().x()); self.dragging = False; self.seeked.emit(self.progress); self.update()


class FloatingPanel(QFrame):
    def __init__(self, parent=None, radius=16):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_OpaquePaintEvent); self.setAutoFillBackground(True)
        self.setStyleSheet(f"QFrame {{ background:#111720; border:1px solid #27303C; border-radius:{radius}px; }}")


class SpeedPanel(FloatingPanel):
    selected = Signal(float)
    def __init__(self, parent=None):
        super().__init__(parent, 15)
        lay = QVBoxLayout(self); lay.setContentsMargins(7,7,7,7); lay.setSpacing(2)
        for value in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
            b = QPushButton(f"{value:g}×")
            b.setFixedSize(108, 38); b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet('''QPushButton { text-align:left; padding-left:15px; color:#CBD3DE; background:transparent;
                border:none; border-radius:10px; font:500 12px "Segoe UI Variable"; }
                QPushButton:hover { background:rgba(255,255,255,0.07); color:white; }''')
            b.clicked.connect(lambda _=False, v=value: (self.selected.emit(v), self.close()))
            lay.addWidget(b)


class MenuRow(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.icon_name, self.label = icon, text; self.selected=text.startswith("当前 · ")
        self.setFixedSize(282, 46); self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet('''QPushButton { background:transparent; border:none; border-radius:10px; }
            QPushButton:hover { background:rgba(255,255,255,0.065); }''')
    def paintEvent(self, event):
        super().paintEvent(event); p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        if self.selected:
            p.setPen(Qt.NoPen); p.setBrush(QColor(105,226,255,22)); p.drawRoundedRect(self.rect().adjusted(2,2,-2,-2),9,9)
        color=CYAN if self.selected else SECONDARY
        QSvgRenderer(svg_bytes(self.icon_name,color,19)).render(p,QRect(15,13,19,19))
        p.setPen(QColor(CYAN if self.selected else TEXT)); p.setFont(QFont("Segoe UI Variable",11,QFont.Medium)); p.drawText(QRect(48,0,222,46),Qt.AlignVCenter,self.label)


class MorePanel(FloatingPanel):
    def __init__(self, actions, parent=None):
        super().__init__(parent, 16)
        lay=QVBoxLayout(self); lay.setContentsMargins(7,7,7,7); lay.setSpacing(2)
        for icon, text, callback in actions:
            row=MenuRow(icon,text); row.clicked.connect(lambda _=False, cb=callback: (cb(), self.close())); lay.addWidget(row)


class PipBar(QFrame):
    def __init__(self, window, parent=None):
        super().__init__(parent); self.window_ref=window; self.drag_offset=None
        self.setCursor(Qt.SizeAllCursor)
    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton and sys.platform=="win32":
            ctypes.windll.user32.ReleaseCapture()
            ctypes.windll.user32.SendMessageW(ctypes.c_void_p(int(self.window_ref.winId())),0x00A1,2,0)
            e.accept(); return
        super().mousePressEvent(e)


class NativeResizeGrip(QWidget):
    def __init__(self,window,parent=None):
        super().__init__(parent); self.window_ref=window; self.setCursor(Qt.SizeFDiagCursor); self.setToolTip("拖动调整画中画大小")
    def paintEvent(self,_event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setPen(QPen(QColor(142,152,168),1.5))
        p.drawLine(self.width()-10,self.height()-3,self.width()-3,self.height()-10); p.drawLine(self.width()-6,self.height()-3,self.width()-3,self.height()-6)
    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton and sys.platform=="win32":
            ctypes.windll.user32.ReleaseCapture()
            ctypes.windll.user32.SendMessageW(ctypes.c_void_p(int(self.window_ref.winId())),0x00A1,17,0)
            e.accept(); return
        super().mousePressEvent(e)

class TitleBar(QFrame):
    def __init__(self, window):
        super().__init__(window); self.window=window; self.drag_pos=None; self.setFixedHeight(48)
        self.setStyleSheet("background: transparent;")
        lay=QHBoxLayout(self); lay.setContentsMargins(14,0,8,0); lay.setSpacing(8)
        logo=SvgIcon("play", CYAN, 18)
        title=QLabel("DuoPlayer"); title.setStyleSheet(f"color:{TEXT}; font: 500 12px 'Segoe UI Variable';")
        lay.addWidget(logo); lay.addWidget(title); lay.addStretch()
        for icon, tip, callback in (("minimize","最小化",window.showMinimized),("maximize","最大化 / 还原",window.toggle_maximize),("close","关闭",window.close)):
            b=IconButton(icon,tip,size=34,icon_size=16); b.clicked.connect(callback)
            if icon=="close": b.setStyleSheet(b.styleSheet()+"QPushButton:hover{background:#C94A54;}")
            lay.addWidget(b)
    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton: self.drag_pos=e.globalPosition().toPoint()-self.window.frameGeometry().topLeft()
    def mouseMoveEvent(self,e):
        if self.drag_pos and e.buttons()&Qt.LeftButton and not self.window.isMaximized(): self.window.move(e.globalPosition().toPoint()-self.drag_pos)
    def mouseReleaseEvent(self,e): self.drag_pos=None
    def mouseDoubleClickEvent(self,e): self.window.toggle_maximize()



class BottomGradient(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NativeWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
    def paintEvent(self, _event):
        p = QPainter(self)
        grad = QLinearGradient(0, self.height(), 0, 0)
        grad.setColorAt(0.0, QColor(3, 6, 10, 235))
        grad.setColorAt(0.28, QColor(3, 6, 10, 150))
        grad.setColorAt(0.62, QColor(3, 6, 10, 48))
        grad.setColorAt(1.0, QColor(3, 6, 10, 0))
        p.fillRect(self.rect(), grad)


class PreviewCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(204, 144)
        self.setStyleSheet("background:rgba(8,12,18,235);border:none;border-radius:12px;")
        lay = QVBoxLayout(self); lay.setContentsMargins(6,6,6,6); lay.setSpacing(5)
        self.image = QLabel(); self.image.setFixedSize(192,108); self.image.setAlignment(Qt.AlignCenter)
        self.image.setStyleSheet("background:#0A0E14;border:none;border-radius:8px;")
        self.time = QLabel("00:00"); self.time.setAlignment(Qt.AlignCenter)
        self.time.setStyleSheet("color:rgba(255,255,255,0.72);font:11px 'Cascadia Mono';background:transparent;")
        lay.addWidget(self.image); lay.addWidget(self.time)


class VideoArea(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent); self.setObjectName("videoArea"); self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("#videoArea{background:#070A0E;border:none;border-radius:20px;}")
        self.ambient = QLabel(self); self.ambient.setScaledContents(True); self.ambient.setStyleSheet("background:#070A0E;")
        blur = QGraphicsBlurEffect(self.ambient); blur.setBlurRadius(64); self.ambient.setGraphicsEffect(blur)
        self.ambient_source = QPixmap()
        self.clip_timer=QTimer(self); self.clip_timer.setSingleShot(True); self.clip_timer.timeout.connect(self._clip)
        self.host=QWidget(self); self.host.setAttribute(Qt.WA_NativeWindow); self.host.setStyleSheet("background:#05070A;")
        self.video_aspect = 16 / 9
        self.empty=QWidget(self); empty_lay=QVBoxLayout(self.empty); empty_lay.setAlignment(Qt.AlignCenter); empty_lay.setSpacing(10)
        icon=SvgIcon("play",SECONDARY,56); empty_lay.addWidget(icon,0,Qt.AlignCenter)
        title=QLabel("将视频拖放到这里"); title.setStyleSheet(f"color:{TEXT};font:500 17px 'Segoe UI Variable';")
        sub=QLabel("也可以打开本地文件"); sub.setStyleSheet(f"color:{WEAK};font:12px 'Segoe UI Variable';")
        empty_lay.addWidget(title,0,Qt.AlignCenter); empty_lay.addWidget(sub,0,Qt.AlignCenter)
    def set_video_aspect(self, width, height, rotation=0):
        if not width or not height: return
        if rotation % 180: width, height = height, width
        aspect = width / height
        if abs(aspect - self.video_aspect) > .002:
            self.video_aspect = aspect; self._layout_layers()
    def _layout_layers(self):
        r=self.rect(); self.ambient.setGeometry(r); self.empty.setGeometry(r)
        if r.width()/max(1,r.height()) > self.video_aspect:
            h=r.height(); w=int(h*self.video_aspect)
        else:
            w=r.width(); h=int(w/self.video_aspect)
        x=(r.width()-w)//2; y=(r.height()-h)//2
        self.host.setGeometry(x,y,w,h); self.clip_timer.start(90)
    def resizeEvent(self,e):
        if not getattr(self.window(),"interactive_resizing",False):self._layout_layers()
        super().resizeEvent(e)
    def _clip(self):
        if sys.platform=="win32" and self.host.winId():
            try:
                gdi=ctypes.windll.gdi32; user=ctypes.windll.user32
                class NativeRect(ctypes.Structure):
                    _fields_=[("left",ctypes.c_long),("top",ctypes.c_long),("right",ctypes.c_long),("bottom",ctypes.c_long)]
                rect=NativeRect(); user.GetClientRect(int(self.host.winId()),ctypes.byref(rect))
                width=max(1,rect.right-rect.left); height=max(1,rect.bottom-rect.top)
                radius=max(1,round(22*self.devicePixelRatioF()))
                region=gdi.CreateRoundRectRgn(0,0,width+1,height+1,radius,radius)
                user.SetWindowRgn(int(self.host.winId()),region,True)
            except Exception: pass
    def capture_ambient(self):
        if not self.host.isVisible() or self.host.width()<2: return
        screen=self.window().screen()
        # mpv is a native child HWND; capture its real on-screen pixels.
        top_left=self.host.mapToGlobal(QPoint(0,0)); dpr=screen.devicePixelRatio()
        frame=screen.grabWindow(0,int(top_left.x()*dpr),int(top_left.y()*dpr),
                                max(1,int(self.host.width()*dpr)),max(1,int(self.host.height()*dpr)))
        if frame.isNull(): return
        frame=frame.scaled(360,220,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation)
        painter=QPainter(frame); painter.fillRect(frame.rect(),QColor(5,8,12,178)); painter.end()
        self.ambient_source=frame
        self.ambient.setPixmap(frame.scaled(self.size(),Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation))
        self.ambient.show()
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dropEvent(self,e):
        files=[u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        if files: self.window().add_files(files,True)


class PlayerWindow(QWidget):
    def __init__(self, files=None):
        super().__init__(); self.setWindowFlags(Qt.FramelessWindowHint|Qt.Window)
        self.settings=QSettings("DuoPlayer","DuoPlayer")
        try: self.positions=json.loads(self.settings.value("positions","{}"))
        except (TypeError,ValueError): self.positions={}
        self.saved_volume=max(0,min(100,int(self.settings.value("volume",80))))
        self.saved_speed=float(self.settings.value("speed",1.0))
        self.setAttribute(Qt.WA_OpaquePaintEvent); self.setAutoFillBackground(False); self.resize(1180,760); self.setMinimumSize(800,520)
        self.player=MpvController(self._state_changed); self.path=None; self.playlist=[]; self.index=-1
        self.duration=0; self.state="idle"; self.rotation=0; self.controls_visible=True; self.fullscreen=False; self.topmost=False; self.pending_resume=None
        self.hide_timer=QTimer(self); self.hide_timer.setSingleShot(True); self.hide_timer.timeout.connect(self.hide_controls)
        self.poll=QTimer(self); self.poll.timeout.connect(self.tick); self.poll.start(120)
        self.ambient_timer=QTimer(self); self.ambient_timer.timeout.connect(self.update_ambient); self.ambient_timer.start(1400)
        self.looping=False; self.pip_mode=False; self.last_render_size=None; self.interactive_resizing=False
        self.render_resize_timer=QTimer(self); self.render_resize_timer.setSingleShot(True); self.render_resize_timer.timeout.connect(self.sync_render_size)
        self.region_resize_timer=QTimer(self); self.region_resize_timer.setSingleShot(True); self.region_resize_timer.timeout.connect(self.apply_overlay_regions)
        self.setMouseTracking(True); self.installEventFilter(self)
        self.last_cursor_pos=QCursor.pos(); self.pointer_timer=QTimer(self); self.pointer_timer.timeout.connect(self.watch_pointer); self.pointer_timer.start(100)
        self.build_ui()
        self.resize_preview=QLabel(self); self.resize_preview.setScaledContents(True); self.resize_preview.setStyleSheet("background:#080A0D;border:none;"); self.resize_preview.hide()
        geometry=self.settings.value("windowGeometry")
        if geometry:self.restoreGeometry(geometry)
        if self.settings.value("maximized",False,type=bool):QTimer.singleShot(0,self.showMaximized)
        self.save_timer=QTimer(self); self.save_timer.timeout.connect(self.save_state); self.save_timer.start(5000)
        if files: QTimer.singleShot(300,lambda:self.add_files(files,True))

    def build_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(1,1,1,1); root.setSpacing(0)
        self.body=QFrame(); self.body.setObjectName("body"); self.body.setStyleSheet("#body{background:#070A0E;border:none;border-radius:18px;}")
        body_lay=QVBoxLayout(self.body); body_lay.setContentsMargins(0,0,0,0); body_lay.setSpacing(0)
        self.titlebar=TitleBar(self); body_lay.addWidget(self.titlebar)
        # One expanding cinema surface directly below the title bar.
        self.video=VideoArea(); body_lay.addWidget(self.video,1); root.addWidget(self.body)

        self.gradient=BottomGradient(self.video)
        self.chip=QLabel("SPATIAL   •   READY",self.video); self.chip.setFixedHeight(31)
        self.chip.setStyleSheet("color:rgba(235,240,247,170);background:rgba(5,8,12,145);border:none;border-radius:9px;padding:0 10px;font:500 10px 'Segoe UI Variable';letter-spacing:1px;"); self.chip.hide()
        self.more=IconButton("more","更多",36,18,self.video)
        self.more.setStyleSheet("QPushButton{background:#080C12;border:none;border-radius:18px;}QPushButton:hover{background:#1B2028;}")
        self.more.clicked.connect(self.show_more)

        self.dock=QFrame(self.video); self.dock.setAttribute(Qt.WA_NativeWindow)
        self.dock.setObjectName("dock")
        self.dock.setStyleSheet("#dock{background:#080C12;border:none;border-radius:22px;}")
        dock_lay=QVBoxLayout(self.dock); dock_lay.setContentsMargins(0,0,0,0); dock_lay.setSpacing(8)
        self.timeline=Timeline(); self.timeline.seeked.connect(self.seek_fraction); self.timeline.preview.connect(self.preview_time); dock_lay.addWidget(self.timeline)
        row=QHBoxLayout(); row.setSpacing(3)
        self.play=IconButton("play","播放 / 暂停",44,21); self.play.clicked.connect(self.toggle_play); row.addWidget(self.play)
        self.back=IconButton("rewind","后退 10 秒",40,19); self.back.clicked.connect(lambda:self.seek_relative(-10000)); row.addWidget(self.back)
        self.forward=IconButton("forward","前进 10 秒",40,19); self.forward.clicked.connect(lambda:self.seek_relative(10000)); row.addWidget(self.forward)
        self.volume_btn=IconButton("volume","静音 / 恢复声音",38,18); self.volume_btn.clicked.connect(self.toggle_mute); row.addWidget(self.volume_btn)
        self.volume=QSlider(Qt.Horizontal); self.volume.setRange(0,100); self.volume.setValue(self.saved_volume); self.volume.setFixedWidth(82)
        self.volume.setStyleSheet("QSlider::groove:horizontal{height:2px;background:rgba(255,255,255,0.13);border-radius:1px;}QSlider::sub-page:horizontal{background:rgba(255,255,255,0.58);border-radius:1px;}QSlider::handle:horizontal{width:8px;margin:-3px 0;background:rgba(255,255,255,0.80);border-radius:4px;}")
        self.volume.valueChanged.connect(self.set_volume); row.addWidget(self.volume)
        self.time=QLabel("00:00  /  00:00"); self.time.setStyleSheet("color:rgba(255,255,255,0.58);font:12px 'Cascadia Mono';margin-left:10px;"); row.addWidget(self.time)
        row.addStretch()
        self.speed=PillButton(f"{self.saved_speed:g}×"); self.speed.setToolTip("播放速度"); self.speed.clicked.connect(self.show_speed); row.addWidget(self.speed)
        self.cc=IconButton("captions","音轨和字幕",40,19); self.cc.clicked.connect(self.show_track_menu); row.addWidget(self.cc)
        self.rotate_btn=IconButton("rotate","顺时针旋转 90°",40,19); self.rotate_btn.clicked.connect(lambda:self.rotate(90)); row.addWidget(self.rotate_btn)
        self.loop_btn=IconButton("loop","循环播放",40,19); self.loop_btn.clicked.connect(self.toggle_loop); row.addWidget(self.loop_btn)
        self.pip_btn=IconButton("pip","画中画",40,19); self.pip_btn.clicked.connect(self.toggle_pip); row.addWidget(self.pip_btn)
        self.full=IconButton("fullscreen","全屏",40,19); self.full.clicked.connect(self.toggle_fullscreen); row.addWidget(self.full)
        dock_lay.addLayout(row)

        self.center_play=IconButton("play","继续播放",66,25,self.video)
        self.center_play.setStyleSheet("QPushButton{background:#080C12;border:none;border-radius:33px;}QPushButton:hover{background:#1B2028;}")
        self.center_play.clicked.connect(self.toggle_play); self.center_play.hide()
        self.preview_card=PreviewCard(self.video); self.preview_card.hide()
        self.pip_bar=PipBar(self,self.video); self.pip_bar.setAttribute(Qt.WA_NativeWindow)
        self.pip_bar.setStyleSheet("QFrame{background:#080C12;border:none;border-radius:20px;}")
        pip_lay=QHBoxLayout(self.pip_bar); pip_lay.setContentsMargins(7,4,7,4); pip_lay.setSpacing(4)
        self.pip_play=IconButton("play","播放 / 暂停",40,19); self.pip_play.clicked.connect(self.toggle_play); pip_lay.addWidget(self.pip_play)
        self.pip_exit=IconButton("pip","退出画中画",40,19); self.pip_exit.clicked.connect(self.toggle_pip); pip_lay.addWidget(self.pip_exit)
        self.pip_close=IconButton("close","关闭",40,17); self.pip_close.clicked.connect(self.close); pip_lay.addWidget(self.pip_close)
        self.pip_grip=NativeResizeGrip(self,self.pip_bar); self.pip_grip.setFixedSize(18,18); pip_lay.addWidget(self.pip_grip,0,Qt.AlignBottom)
        self.pip_bar.hide()
        self.dock.setAttribute(Qt.WA_NativeWindow); self.more.setAttribute(Qt.WA_NativeWindow); self.center_play.setAttribute(Qt.WA_NativeWindow)
        QTimer.singleShot(100,self.position_overlays)

    def apply_overlay_regions(self):
        if sys.platform!="win32":return
        user=ctypes.windll.user32; gdi=ctypes.windll.gdi32
        class NativeRect(ctypes.Structure):
            _fields_=[("left",ctypes.c_long),("top",ctypes.c_long),("right",ctypes.c_long),("bottom",ctypes.c_long)]
        items=((self.pip_bar,20,False),) if self.pip_mode else ((self.dock,22,False),(self.more,18,True),(self.center_play,33,True))
        for widget,radius,ellipse in items:
            hwnd=int(widget.winId()); rect=NativeRect()
            if not user.GetClientRect(ctypes.c_void_p(hwnd),ctypes.byref(rect)):continue
            width=max(1,rect.right-rect.left); height=max(1,rect.bottom-rect.top)
            if ellipse:region=gdi.CreateEllipticRgn(0,0,width+1,height+1)
            else:
                rr=max(2,round(radius*self.devicePixelRatioF()))
                region=gdi.CreateRoundRectRgn(0,0,width+1,height+1,rr,rr)
            user.SetWindowRgn(ctypes.c_void_p(hwnd),region,True)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(),QColor(BG))
        if not self.interactive_resizing:
            g=QRadialGradient(self.width()*.5,20,self.width()*.7)
            g.setColorAt(0,QColor(44,72,105,28)); g.setColorAt(1,QColor(8,10,13,0)); p.fillRect(self.rect(),g)
        super().paintEvent(event)

    def showEvent(self,e):
        super().showEvent(e)
        for delay in (0,100,300,700):QTimer.singleShot(delay,self.position_overlays)
    def nativeEvent(self,event_type,message):
        if sys.platform=="win32":
            msg=wintypes.MSG.from_address(int(message))
            if msg.message==0x0084 and self.pip_mode:
                lp=int(msg.lParam); sx=ctypes.c_short(lp&0xFFFF).value; sy=ctypes.c_short((lp>>16)&0xFFFF).value
                rect=wintypes.RECT(); ctypes.windll.user32.GetWindowRect(ctypes.c_void_p(int(self.winId())),ctypes.byref(rect))
                edge=max(4,round(4*self.devicePixelRatioF())); drag=max(edge+2,round(14*self.devicePixelRatioF()))
                left=sx<rect.left+edge; right=sx>=rect.right-edge; top=sy<rect.top+edge; bottom=sy>=rect.bottom-edge
                if top and left:return True,13
                if top and right:return True,14
                if bottom and left:return True,16
                if bottom and right:return True,17
                if left:return True,10
                if right:return True,11
                if top:return True,12
                if bottom:return True,15
                if sy<rect.top+drag:return True,2
            if msg.message==0x0231:
                self.interactive_resizing=True; self.ambient_timer.stop(); self.render_resize_timer.stop(); self.region_resize_timer.stop()
                if self.layout():self.layout().setEnabled(False)
                if not self.video.ambient_source.isNull():self.resize_preview.setPixmap(self.video.ambient_source)
                self.resize_preview.setGeometry(self.rect()); self.resize_preview.show(); self.resize_preview.raise_(); self.video.host.hide()
            elif msg.message==0x0232:
                self.interactive_resizing=False
                if self.layout():self.layout().setEnabled(True)
                QTimer.singleShot(0,self.finish_interactive_resize)
        return super().nativeEvent(event_type,message)
    def finish_interactive_resize(self):
        root=self.layout()
        if root:
            root.invalidate(); root.setGeometry(self.rect()); root.activate()
        body_layout=self.body.layout()
        if body_layout:
            body_layout.invalidate(); body_layout.setGeometry(self.body.rect()); body_layout.activate()
        self.video._layout_layers(); self.position_overlays(); self.last_render_size=None; self.sync_render_size()
        self.video._clip(); self.apply_overlay_regions(); self.video.host.show(); self.resize_preview.hide()
        if not self.ambient_timer.isActive():self.ambient_timer.start(1400)
    def resizeEvent(self,e):
        if self.interactive_resizing and hasattr(self,"resize_preview"):self.resize_preview.setGeometry(self.rect()); self.resize_preview.raise_()
        else:self.position_overlays()
        super().resizeEvent(e)
    def position_overlays(self):
        if not hasattr(self,"video"): return
        w,h=self.video.width(),self.video.height(); self.chip.adjustSize(); self.chip.move(24,20); self.more.move(w-56,18)
        self.gradient.setGeometry(0,max(0,h-270),w,min(270,h))
        self.dock.setGeometry(32,max(0,h-116),w-64,88)
        self.center_play.move((w-self.center_play.width())//2,(h-self.center_play.height())//2)
        self.pip_bar.setGeometry(max(8,(w-220)//2),max(8,h-62),220,48)
        self.region_resize_timer.start(90)
        self.video.ambient.lower(); self.video.host.raise_(); self.gradient.raise_(); self.video.empty.raise_()
        self.more.raise_(); self.dock.raise_(); self.center_play.raise_(); self.preview_card.raise_(); self.pip_bar.raise_()
        self.player.set_hwnd(int(self.video.host.winId()))
        if not self.render_resize_timer.isActive():self.render_resize_timer.start(32)

    def eventFilter(self,obj,event):
        if event.type() in (event.Type.MouseMove,event.Type.Enter): self.show_controls(); self.hide_timer.start(2600)
        return super().eventFilter(obj,event)
    def mouseMoveEvent(self,e): self.show_controls(); self.hide_timer.start(2600); super().mouseMoveEvent(e)

    def watch_pointer(self):
        pos=QCursor.pos()
        if pos != self.last_cursor_pos:
            self.last_cursor_pos=pos
            local=self.mapFromGlobal(pos)
            if self.rect().contains(local): self.show_controls(); self.hide_timer.start(2600)
    def _state_changed(self,_event,state): self.state=state
    def open_files(self):
        files,_=QFileDialog.getOpenFileNames(self,"打开视频","",VIDEO_TYPES)
        if files:self.add_files(files,True)
    def add_files(self,files,play_first=False):
        valid=[os.path.abspath(f) for f in files if os.path.isfile(f)]
        for f in valid:
            if f not in self.playlist:self.playlist.append(f)
        if valid and play_first:self.load(valid[0])
    def load(self,path):
        self.save_progress()
        self.path=os.path.abspath(path); self.index=self.playlist.index(self.path) if self.path in self.playlist else 0
        self.pending_resume=max(0,int(self.positions.get(self.path,0)))
        self.rotation=0; self.player.set_hwnd(int(self.video.host.winId())); self.player.set_rotation(0); self.player.load(self.path)
        self.player.audio_set_volume(self.saved_volume); self.player.set_rate(self.saved_speed)
        self.video.empty.hide(); self.chip.setText("SPATIAL  ·  LOADING"); self.setWindowTitle(Path(path).name)
        for delay in (0,120,350,800,1500):QTimer.singleShot(delay,self.position_overlays)
    def toggle_play(self):
        if not self.path:self.open_files();return
        if self.player.is_playing():self.player.pause()
        else:
            if self.state=="ended":self.player.set_time(0)
            self.player.play()
    def seek_relative(self,delta): self.player.set_time(max(0,min(self.duration-100,self.player.get_time()+delta))) if self.path else None
    def seek_fraction(self,f): self.player.set_time(int(self.duration*f)) if self.duration else None
    def preview_time(self,f,x):
        if f<0 or not self.duration:self.preview_card.hide();return
        self.preview_card.time.setText(fmt_time(int(self.duration*f)))
        if not self.video.ambient_source.isNull():
            self.preview_card.image.setPixmap(self.video.ambient_source.scaled(192,108,Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation))
        px=max(8,min(self.video.width()-212,32+x-102)); self.preview_card.move(px,self.video.height()-272); self.preview_card.show(); self.preview_card.raise_()
    def toggle_mute(self):
        muted=not bool(self.player.audio_get_mute());self.player.audio_set_mute(muted);self.volume_btn.set_icon("muted" if muted else "volume")
    def open_subtitle(self):
        if not self.path:return
        path,_=QFileDialog.getOpenFileName(self,"加载字幕","","字幕文件 (*.srt *.ass *.ssa *.vtt)")
        if path:self.player.video_set_subtitle_file(path)
    def _show_actions(self,actions,anchor=None,above=False):
        panel=MorePanel(actions,self); panel.adjustSize(); anchor=anchor or self.more
        y=-panel.sizeHint().height()-10 if above else anchor.height()+8
        pos=anchor.mapToGlobal(QPoint(anchor.width()-panel.sizeHint().width(),y))
        screen=self.screen().availableGeometry(); pos.setX(max(screen.left()+8,min(pos.x(),screen.right()-panel.width()-8)))
        pos.setY(max(screen.top()+8,min(pos.y(),screen.bottom()-panel.height()-8)))
        panel.move(pos); panel.show(); panel.raise_(); panel.activateWindow(); self._choice_panel=panel
    def show_playlist(self):
        actions=[("folder","添加视频",self.open_files)]
        for idx,path in enumerate(self.playlist[:14]):
            mark="正在播放 · " if idx==self.index else ""
            label=mark+Path(path).name
            if len(label)>28: label=label[:25]+"…"
            actions.append(("play",label,lambda p=path:self.load(p)))
        if len(self.playlist)>14: actions.append(("list",f"还有 {len(self.playlist)-14} 项",lambda:None))
        self._show_actions(actions,self.more)
    def _track_label(self,track,prefix):
        title=track.get("title") or track.get("lang") or f"轨道 {track.get('id','?')}"
        selected="当前 · " if track.get("selected") else ""
        return f"{selected}{prefix} · {title}"
    def show_track_menu(self):
        if not self.path:return
        actions=[]
        audio=self.player.get_tracks("audio")
        subtitles=self.player.get_tracks("sub")
        actions.append(("music","关闭音轨",lambda:self.player.select_audio_track(None)))
        for track in audio[:8]:
            actions.append(("music",self._track_label(track,"音轨"),lambda i=track.get("id"):self.player.select_audio_track(i)))
        actions.append(("captions","关闭字幕",lambda:self.player.select_subtitle_track(None)))
        for track in subtitles[:8]:
            actions.append(("captions",self._track_label(track,"字幕"),lambda i=track.get("id"):self.player.select_subtitle_track(i)))
        actions.append(("folder","加载外挂字幕",self.open_subtitle))
        self._show_actions(actions,self.cc,above=True)
    def rotate(self,delta):
        if not self.path: return
        self.rotation=(self.rotation+delta)%360
        self.player.set_rotation(self.rotation)
        width,height=self.player.video_get_size()
        self.video.set_video_aspect(width,height,self.rotation)
        self.last_render_size=None
        QTimer.singleShot(80,self.sync_render_size)
    def sync_render_size(self):
        render_size=(self.video.host.width(),self.video.host.height())
        if render_size != self.last_render_size:
            if self.player.resize(*render_size)>0:self.last_render_size=render_size
    def show_speed(self):
        panel=SpeedPanel(self);panel.selected.connect(self.set_speed);panel.adjustSize();pos=self.speed.mapToGlobal(QPoint(0,-panel.sizeHint().height()-8));panel.move(pos);panel.show();self._speed_panel=panel
    def set_speed(self,value):
        self.saved_speed=float(value); self.speed.setText(f"{value:g}×"); self.player.set_rate(value)
        self.settings.setValue("speed",self.saved_speed)
    def set_volume(self,value):
        self.saved_volume=int(value); self.player.audio_set_volume(value); self.settings.setValue("volume",self.saved_volume)
    def toggle_loop(self):
        self.looping=not self.looping; self.player.command("set_property","loop-file","inf" if self.looping else "no"); self.loop_btn.setStyleSheet("QPushButton{background:rgba(255,255,255,0.08);border:none;border-radius:20px;}" if self.looping else "QPushButton{background:transparent;border:none;border-radius:20px;}QPushButton:hover{background:rgba(255,255,255,0.065);}")
    def _set_native_topmost(self,enabled):
        if sys.platform=="win32":
            user=ctypes.windll.user32; insert_after=ctypes.c_void_p(-1 if enabled else -2)
            user.SetWindowPos(ctypes.c_void_p(int(self.winId())),insert_after,0,0,0,0,0x0001|0x0002|0x0010|0x0040)
        else:self.setWindowFlag(Qt.WindowStaysOnTopHint,enabled);self.show()
    def toggle_pip(self):
        if not self.pip_mode:
            self.pip_restore_geometry=self.saveGeometry(); self.pip_restore_topmost=self.topmost
            self.pip_mode=True; self.topmost=True
            self.setMinimumSize(320,200); self.layout().setContentsMargins(4,14,4,4); self.titlebar.hide(); self.dock.hide(); self.chip.hide(); self.more.hide(); self.gradient.hide(); self.center_play.hide()
            self.showNormal(); self.resize(480,300); self._set_native_topmost(True)
            area=self.screen().availableGeometry(); self.move(area.right()-self.width()-24,area.bottom()-self.height()-24)
            self.pip_bar.show(); self.pip_bar.raise_(); self.controls_visible=False
        else:
            self.pip_mode=False; self.pip_bar.hide(); self.topmost=self.pip_restore_topmost
            self.setMinimumSize(800,520); self.layout().setContentsMargins(1,1,1,1); self._set_native_topmost(self.topmost)
            self.restoreGeometry(self.pip_restore_geometry); self.titlebar.show(); self.controls_visible=False; self.show_controls()
        for delay in (0,100,300,700):QTimer.singleShot(delay,self.position_overlays)
    def update_ambient(self):
        if self.path and self.player.is_playing() and not self.pip_mode: self.video.capture_ambient()
    def show_more(self):
        actions=[("folder","打开视频",self.open_files),("list",f"播放列表  ·  {len(self.playlist)}",self.show_playlist),("music","音轨和字幕",self.show_track_menu),("window","新建播放器窗口",self.new_process),("rotate","顺时针旋转 90°",lambda:self.rotate(90)),("rotate","逆时针旋转 90°",lambda:self.rotate(-90)),("camera","截取当前画面",self.snapshot),("pin","窗口置顶",self.toggle_topmost),("prev","上一个视频",self.previous),("next","下一个视频",self.next)]
        panel=MorePanel(actions,self);panel.adjustSize();panel.move(self.more.mapToGlobal(QPoint(self.more.width()-panel.sizeHint().width(),self.more.height()+8)));panel.show();self._more_panel=panel
    def snapshot(self):
        if not self.path:return
        path,_=QFileDialog.getSaveFileName(self,"截取当前画面",f"{Path(self.path).stem}.png","PNG (*.png)")
        if path:self.player.video_take_snapshot(0,path,0,0)
    def previous(self):
        if self.playlist:self.load(self.playlist[(self.index-1)%len(self.playlist)])
    def next(self):
        if self.playlist:self.load(self.playlist[(self.index+1)%len(self.playlist)])
    def new_process(self):
        flags=getattr(subprocess,"DETACHED_PROCESS",0)|getattr(subprocess,"CREATE_NEW_PROCESS_GROUP",0)
        subprocess.Popen([sys.executable,str(Path(__file__).resolve())],cwd=str(Path(__file__).parent),close_fds=True,creationflags=flags)
    def toggle_topmost(self):
        self.topmost=not self.topmost; self._set_native_topmost(self.topmost)
    def toggle_maximize(self): self.showNormal() if self.isMaximized() else self.showMaximized()
    def toggle_fullscreen(self): self.fullscreen=not self.fullscreen;self.showFullScreen() if self.fullscreen else self.showNormal();self.titlebar.setVisible(not self.fullscreen);QTimer.singleShot(150,self.position_overlays)
    def hide_controls(self):
        if self.pip_mode:
            self.pip_bar.show(); self.dock.hide(); self.chip.hide(); self.more.hide(); self.gradient.hide(); self.center_play.hide(); return
        if self.player.is_playing():self.dock.hide();self.chip.hide();self.more.hide();self.gradient.hide();self.preview_card.hide();self.controls_visible=False;self.setCursor(Qt.BlankCursor)
    def show_controls(self):
        if self.pip_mode:
            self.dock.hide(); self.chip.hide(); self.more.hide(); self.gradient.hide(); self.center_play.hide(); self.pip_bar.show(); self.pip_bar.raise_(); self.setCursor(Qt.ArrowCursor); return
        if not self.controls_visible:self.gradient.show();self.dock.show();self.more.show();self.controls_visible=True;self.setCursor(Qt.ArrowCursor);self.position_overlays()
    def tick(self):
        if not self.path:return
        current,length=self.player.get_time(),self.player.get_length();self.duration=max(0,length)
        if self.pending_resume is not None and length>0:
            resume=min(self.pending_resume,max(0,length-3000)); self.pending_resume=None
            if resume>=5000:self.player.set_time(resume)
        if length>0:self.timeline.set_progress(current/length);self.time.setText(f"{fmt_time(current)}  /  {fmt_time(length)}")
        icon="pause" if self.player.is_playing() else "play"; self.play.set_icon(icon); self.pip_play.set_icon(icon)
        size=self.player.video_get_size(); self.video.set_video_aspect(size[0],size[1],self.rotation); self.sync_render_size(); quality="4K" if size[0]>=3800 else "FHD" if size[0]>=1900 else "HD" if size[0] else "READY"
        self.chip.setText(f"SPATIAL  ·  {quality}")
        if self.state=="paused" and not self.pip_mode: self.show_controls(); self.center_play.show(); self.center_play.raise_()
        elif self.player.is_playing() or self.pip_mode: self.center_play.hide()
        if self.state=="ended" and len(self.playlist)>1:self.next()
    def keyPressEvent(self,e):
        keys={Qt.Key_Space:self.toggle_play,Qt.Key_Left:lambda:self.seek_relative(-10000),Qt.Key_Right:lambda:self.seek_relative(10000),Qt.Key_F:self.toggle_fullscreen,Qt.Key_R:lambda:self.rotate(90),Qt.Key_M:self.toggle_mute,Qt.Key_Escape:lambda:self.toggle_fullscreen() if self.fullscreen else None}
        if e.modifiers()&Qt.ControlModifier and e.key()==Qt.Key_O:self.open_files()
        elif e.key() in keys:keys[e.key()]()
        else:super().keyPressEvent(e)
    def save_progress(self):
        if not self.path:return
        current=self.player.get_time(); length=self.player.get_length()
        if current>=5000 and (length<=0 or current<length-5000):self.positions[self.path]=current
        elif length>0 and current>=length-5000:self.positions.pop(self.path,None)
    def save_state(self):
        self.save_progress()
        self.settings.setValue("positions",json.dumps(self.positions,ensure_ascii=False))
        self.settings.setValue("windowGeometry",self.saveGeometry())
        self.settings.setValue("maximized",self.isMaximized())
        self.settings.setValue("volume",self.saved_volume)
        self.settings.setValue("speed",self.saved_speed)
        self.settings.sync()
    def closeEvent(self,e):
        self.save_state(); self.player.release(); e.accept()


def main():
    app=QApplication(sys.argv);app.setApplicationName("DuoPlayer");app.setFont(QFont("Segoe UI Variable",10))
    files=[arg for arg in sys.argv[1:] if os.path.isfile(arg)];window=PlayerWindow(files);window.show();sys.exit(app.exec())

if __name__=="__main__":main()
