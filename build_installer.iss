[Setup]
AppName=AI Data Entry Employee
AppVersion=1.0
DefaultDirName={pf}\AI Data Entry Employee
DefaultGroupName=AI Data Entry Employee
OutputBaseFilename=AI_Data_Entry_Installer
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
Uninstallable=yes
WizardStyle=modern

[Files]
Source: "dist\AI_Data_Entry.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AI Data Entry Employee"; Filename: "{app}\AI_Data_Entry.exe"
Name: "{commondesktop}\AI Data Entry Employee"; Filename: "{app}\AI_Data_Entry.exe"
