# DuoPlayer

一个适用于 Windows 10 / 11 的多格式视频播放器，支持多窗口、视频旋转、字幕、音轨、倍速和画中画。

## 我只是想使用播放器

### 推荐：下载安装版

[下载 DuoPlayer-Setup-x64.exe](https://github.com/ASDFGHJ0/DuoPlayer/releases/latest/download/DuoPlayer-Setup-x64.exe)

1. 双击安装程序并完成安装。
2. 安装后可从开始菜单启动 DuoPlayer。
3. 右键视频 → `打开方式`，即可选择 DuoPlayer；也可选择“始终使用”。
4. Windows“已安装的应用”中可以正常卸载。

安装版不需要 Python，也不需要单独安装 mpv。

> 当前安装器尚未购买代码签名证书。首次运行时 Windows 可能显示“Windows 已保护你的电脑”，确认下载来源是本仓库后，可点击“更多信息”→“仍要运行”。

### 便携版

如果不想安装，可以下载 [DuoPlayer-Windows-x64.zip](https://github.com/ASDFGHJ0/DuoPlayer/releases/latest/download/DuoPlayer-Windows-x64.zip)。便携版必须完整解压并保留整个文件夹，不能只复制其中的 `DuoPlayer.exe`。

> 请不要下载 GitHub 自动生成的 `Source code (zip)` 或 `Source code (tar.gz)`。它们是开发者源码，不能直接当播放器运行。
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
.\build-installer.bat
```

安装器生成于 `release\DuoPlayer-Setup-x64.exe`，便携目录生成于 `dist\DuoPlayer`。构建脚本默认从 `C:\Program Files\MPV Player` 复制 mpv。

## 项目文件

```text
DuoPlayer/
├─ app.py                # 播放器界面与功能
├─ mpv_backend.py        # mpv 播放核心控制
├─ assets/               # 应用图标
├─ DuoPlayer.spec        # Windows 打包配置
├─ build.bat             # 构建便携目录
├─ build-installer.bat   # 构建安装程序
├─ installer.iss         # 安装和文件关联配置
├─ run.bat               # 从源码启动
├─ requirements.txt      # 运行依赖
└─ requirements-dev.txt  # 打包依赖
```

## 隐私

仓库和发布包不包含测试视频、字幕、播放历史或个人设置。DuoPlayer 不会修改源视频文件。
