; Inno Setup Script for Visitor Counting System
[Setup]
AppName=Visitor Counter
AppVersion=1.0
DefaultDirName={pf}\VisitorCounter
DefaultGroupName=Visitor Counter
OutputDir=.
OutputBaseFilename=VisitorCounterSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\visitor_counter.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "staff_images\*"; DestDir: "{app}\staff_images"; Flags: recursesubdirs createallsubdirs
Source: "visitor_log.csv"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "staff_attendance.csv"; DestDir: "{app}"; Flags: onlyifdoesntexist
[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional tasks"

[Icons]
Name: "{group}\Visitor Counter"; Filename: "{app}\visitor_counter.exe"
Name: "{commondesktop}\Visitor Counter"; Filename: "{app}\visitor_counter.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\visitor_counter.exe"; Description: "Launch Visitor Counter"; Flags: nowait postinstall skipifsilent
