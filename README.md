# DuoPlayer

DuoPlayer 是一款面向 Windows 的轻量本地视频播放器。界面使用 PySide6/Qt 构建，播放核心使用 mpv，支持多种常见视频编码和封装格式。

## 功能

- 支持 MP4、MKV、MOV、AVI、WebM、FLV、WMV、TS、M2TS 等格式
- 支持 H.264、H.265/HEVC、AV1、VP8、VP9、MPEG、ProRes 等常见编码
- 播放、暂停、跳转、前进/后退 10 秒、音量和倍速控制
- 内置音轨与字幕轨选择、外挂字幕加载
- 顺时针与逆时针 90° 旋转
- 播放列表、上一项、下一项和循环播放
- 画面截图、全屏、窗口置顶
- 可移动、可缩放的画中画模式
- 记忆播放位置、音量、倍速及窗口状态
- 支持同时启动多个独立播放器进程
- Per-Monitor V2 高 DPI 适配

## 环境要求

- Windows 10 或 Windows 11
- Python 3.10 或更高版本
- [mpv](https://mpv.io/)（默认查找 `C:\Program Files\MPV Player\mpv.exe`）

## 安装

```powershell
python -m pip install -r requirements.txt
```

安装 mpv 后，确认 `mpv.exe` 位于以下任一位置：

```text
C:\Program Files\MPV Player\mpv.exe
%LOCALAPPDATA%\Programs\mpv\mpv.exe
```

## 启动

双击 `run.bat`，或在项目目录执行：

```powershell
python app.py
```

也可以将视频路径作为参数传入：

```powershell
python app.py "D:\Videos\example.mp4"
```

每次再次运行 `run.bat` 都会创建一个独立播放器窗口。

## 常用操作

| 操作 | 功能 |
| --- | --- |
| `Ctrl+O` | 打开视频 |
| `Space` | 播放 / 暂停 |
| `←` / `→` | 后退 / 前进 10 秒 |
| `M` | 静音 / 恢复声音 |
| `R` | 顺时针旋转 90° |
| `F` | 全屏 |
| `Esc` | 退出全屏 |

播放器按钮提供中文悬停提示，更多功能位于右上角“更多”菜单。

## 项目结构

```text
DuoPlayer/
├─ app.py             # Qt 界面与播放器交互
├─ mpv_backend.py     # mpv JSON IPC 与原生窗口嵌入
├─ requirements.txt   # Python 依赖
└─ run.bat            # Windows 无控制台启动脚本
```

## 隐私说明

本仓库不包含本地测试视频、字幕、播放历史或个人设置。播放器不会修改源视频文件。
