; Inno Setup script for Simple Audio Player
; Build with: ISCC simple_audio_player.iss

#define MyAppName "Simple Audio Player"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Kamal Yaser"
#define MyAppURL "https://github.com/kamalyaser31/simple-player"
#define MyAppExeName "SimpleAudioPlayer.exe"
#define MyAppDistDir "dist\SimpleAudioPlayer"
#define MyProgId "SimpleAudioPlayer.media"
#define MyContextLabel "Play with Simple Audio Player"

[Setup]
AppId={{D1288C88-8739-4BE1-A302-2E83822C6A8D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=none
OutputDir=dist
OutputBaseFilename=SimpleAudioPlayerSetup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyAppDistDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Updater.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\.sap_installed"

[Registry]
; ProgID and context command
Root: HKCU; Subkey: "Software\Classes\{#MyProgId}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppName} media file"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyProgId}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyProgId}\shell\play_with_simple_audio_player"; ValueType: string; ValueName: ""; ValueData: "{#MyContextLabel}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\{#MyProgId}\shell\play_with_simple_audio_player\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; Applications registration (Open With and shell verb)
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\play_with_simple_audio_player"; ValueType: string; ValueName: ""; ValueData: "{#MyContextLabel}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\play_with_simple_audio_player\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; Default Programs capabilities
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Play audio and media files with {#MyAppName}."; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Simple Audio Player"; ValueData: "Software\SimpleAudioPlayer\Capabilities"; Flags: uninsdeletevalue

; Supported file types for Open With (audio + video)
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".aac"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".aiff"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".alac"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".avi"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".flac"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".flv"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".m2ts"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".m4a"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".m4v"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mkv"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mov"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mp3"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mp4"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mpeg"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mpg"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ogg"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".opus"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ts"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".wav"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".webm"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".wma"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".wmv"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".3gp"; ValueData: ""; Flags: uninsdeletevalue

; Extension associations (same model as app-side registration)
Root: HKCU; Subkey: "Software\Classes\.aac"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.aiff"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.alac"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.avi"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.flac"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.flv"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.m2ts"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.m4a"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.m4v"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mkv"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mov"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mp3"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mp4"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mpeg"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.mpg"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.ogg"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.opus"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.ts"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.wav"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.webm"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.wma"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.wmv"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"
Root: HKCU; Subkey: "Software\Classes\.3gp"; ValueType: string; ValueName: ""; ValueData: "{#MyProgId}"

; OpenWithProgids entries
Root: HKCU; Subkey: "Software\Classes\.aac\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.aiff\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.alac\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.avi\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.flac\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.flv\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.m2ts\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.m4a\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.m4v\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mkv\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mov\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mp3\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mp4\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mpeg\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.mpg\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.ogg\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.opus\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.ts\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.wav\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.webm\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.wma\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.wmv\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\.3gp\OpenWithProgids"; ValueType: none; ValueName: "{#MyProgId}"; Flags: uninsdeletevalue

; Capabilities file associations
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".aac"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".aiff"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".alac"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".avi"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".flac"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".flv"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m2ts"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m4a"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m4v"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mkv"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mov"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp3"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp4"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mpeg"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mpg"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ogg"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".opus"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ts"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".wav"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".webm"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".wma"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".wmv"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\SimpleAudioPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".3gp"; ValueData: "{#MyProgId}"; Flags: uninsdeletevalue

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SaveStringToFile(ExpandConstant('{app}\.sap_installed'), '', False);
end;
