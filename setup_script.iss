; Script generated for PyInstaller PDF Reader

#define MyAppName "Local PDF Reader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "pdf_reader.exe"

[Setup]
; Unique app identifier (Generate a new GUID or keep custom)
AppId={{A9E8B67C-1234-4567-89AB-CDEF01234567}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Where the generated setup.exe will be saved
OutputDir=.
OutputBaseFilename=PDFReaderSetup_v1.0.0
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Path to your PyInstaller output executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; OPTIONAL: If using PyInstaller directory mode (--onedir instead of --onefile), include all subfolders:
; Source: "dist\pdf_reader\*"; DestDir: "{app}"; Flags:ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Desktop shortcut (if selected during installation)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to launch app after installation completes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent