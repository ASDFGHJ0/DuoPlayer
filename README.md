# DuoPlayer

一个适用于 Windows 10 / 11 的多格式视频播放器，支持多窗口、视频旋转、字幕、音轨、倍速和画中画。

## 我只是想使用播放器

请下载下面这个文件：

### [下载 DuoPlayer-Windows-x64.zip](https://github.com/ASDFGHJ0/DuoPlayer/releases/latest/download/DuoPlayer-Windows-x64.zip)

下载后按下面操作：

1. 解压 `DuoPlayer-Windows-x64.zip`。
2. 打开解压后的 `DuoPlayer` 文件夹。
3. 双击 `DuoPlayer.exe`。
4. 把视频拖进窗口，或者按 `Ctrl+O` 选择视频。

不需要安装 Python，也不需要单独安装 mpv。

> 请不要下载 GitHub 自动生成的 `Source code (zip)` 或 `Source code (tar.gz)`。它们是给开发者看的源码，不能直接当播放器运行。

## 主要功能

- 支持 MP4、MKV、MOV、AVI、WebM、FLV、WMV、TS、M2TS 等格式
- 支持 H.264、H.265/HEVC、AV1、VP8、VP9、MPEG、ProRes 等编码
- 支持同时打开多个独立播放器窗口
- 播放、暂停、进度跳转、前进/后退 10 秒、音量、静音和倍速
- 顺时针或逆时针旋转 90°
- 音轨选择、字幕轨选择和外挂字幕
- 播放列表、循环播放、截图、全屏和窗口置顶
- 可移动、可缩放的画中画模式
- 记忆播放位置、音量、倍速和窗口状态
- 支持 Windows 高 DPI 缩放

## 常用快捷键

| 快捷键 | 功能 |
| --- | --- |
| `Ctrl+O` | 打开视频 |
| `Space` | 播放 / 暂停 |
| `←` / `→` | 后退 / 前进 10 秒 |
| `M` | 静音 / 恢复声音 |
| `R` | 顺时针旋转 90° |
| `F` | 全屏 |
| `Esc` | 退出全屏 |

播放器按钮也提供中文悬停提示。

## 给开发者

运行源码需要 Windows 10/11、Python 3.10+ 和 mpv：

```powershell
python -m pip install -r requirements.txt
python app.py
```

生成 Windows 独立版：

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
.\build.bat
```

构建结果位于 `dist\DuoPlayer`。构建脚本默认从 `C:\Program Files\MPV Player` 复制 mpv。

## 项目文件

```text
DuoPlayer/
├─ app.py                # 播放器界面与功能
├─ mpv_backend.py        # mpv 播放核心控制
├─ assets/               # 应用图标
├─ DuoPlayer.spec        # Windows 打包配置
├─ build.bat             # 一键打包
├─ run.bat               # 从源码启动
├─ requirements.txt      # 运行依赖
└─ requirements-dev.txt  # 打包依赖
```

## 隐私

仓库和发布包不包含测试视频、字幕、播放历史或个人设置。DuoPlayer 不会修改源视频文件。
