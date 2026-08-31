#define MyAppName "DuoPlayer"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "ASDFGHJ0"
#define MyAppExeName "DuoPlayer.exe"

[Setup]
AppId={{D9351823-30DC-4D91-BDF7-5FEF7C747B8B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/ASDFGHJ0/DuoPlayer
AppSupportURL=https://github.com/ASDFGHJ0/DuoPlayer/issues
AppUpdatesURL=https://github.com/ASDFGHJ0/DuoPlayer/releases
DefaultDirName={localappdata}\Programs\DuoPlayer
DefaultGroupName=DuoPlayer
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
OutputDir=release
OutputBaseFilename=DuoPlayer-Setup-x64
SetupIconFile=assets\duoplayer.ico
UninstallDisplayIcon={app}\DuoPlayer.exe
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
ChangesAssociations=yes
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=DuoPlayer Windows 安装程序
VersionInfoProductName={#MyAppName}


[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项："; Flags: unchecked

[Files]
Source: "dist\DuoPlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DuoPlayer"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DuoPlayer"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "DuoPlayer"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\shell\open\command"; ValueType: string; ValueData: """{app}\DuoPlayer.exe"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".mp4"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".mkv"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".mov"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".avi"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".webm"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".flv"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".wmv"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".m4v"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".ts"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\Applications\DuoPlayer.exe\SupportedTypes"; ValueType: string; ValueName: ".m2ts"; ValueData: ""
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "DuoPlayer"; ValueData: "Software\DuoPlayer\Capabilities"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "DuoPlayer"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "多格式视频播放器"
Root: HKCU; Subkey: "Software\Classes\DuoPlayer.Video"; ValueType: string; ValueData: "DuoPlayer 视频"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\DuoPlayer.Video\DefaultIcon"; ValueType: string; ValueData: "{app}\DuoPlayer.exe,0"
Root: HKCU; Subkey: "Software\Classes\DuoPlayer.Video\shell\open\command"; ValueType: string; ValueData: """{app}\DuoPlayer.exe"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\.mp4\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mkv\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mov\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.avi\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.webm\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.flv\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.wmv\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.m4v\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.ts\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.m2ts\OpenWithProgids"; ValueType: string; ValueName: "DuoPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp4"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mkv"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mov"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".avi"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".webm"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".flv"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".wmv"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m4v"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ts"; ValueData: "DuoPlayer.Video"
Root: HKCU; Subkey: "Software\DuoPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m2ts"; ValueData: "DuoPlayer.Video"

[Run]
Filename: "{app}\DuoPlayer.exe"; Description: "启动 DuoPlayer"; Flags: nowait postinstall skipifsilent
