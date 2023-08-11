;* Rizonesoft Office - Installer script x64
;*
;* (c) Rizonesoft 2008-2023

; Requirements:
; Inno Setup: https://jrsoftware.org/isinfo.php

; Preprocessor related stuff
#define public Dependency_Path_NetCoreCheck "dependencies\"
#include "CodeDependencies.iss"

#define GUID="F0085D50-A268-4FEA-A287-4F949C5C26FD"

// if you compile a "beta, rc or rc2" version, then comment/un-comment the appropriate setting:
;#define VRSN=" beta"
;#define VRSN=" rc"
;#define VRSN=" rc2"
// but, if not a "beta, rc or rc2" version, then comment above settings and un-comment below setting :)
#define VRSN=" Alpha 2"
#IfnDef VRSN
  #error Please set any of the above: #define VRSN(...)
#EndIf

#if VER < EncodeVer(6,2,2)
  #error Update your Inno Setup version (6.2.2 or newer)
#endif

#define Arch="x64"
#IfnDef Arch
  #error Please set any of the above: #define Arch=(...)
#EndIf

#define RLSdir "..\Office\Bin\"+Arch+"\Release\"

#ifnexist RLSdir + "Rizonesoft.Office.dll"
  #pragma error "Compile Rizonesoft Office "+Arch+" first"
#endif

#define app_name "Office"
#define app_publisher "Rizonesoft"

#if VER < 0x06020000
  #define app_version GetFileVersion(RLSdir + "Rizonesoft.Office.dll")
#Else
  #define app_version GetVersionNumbersString(RLSdir + "Rizonesoft.Office.dll")
#EndIf
#define app_copyright "Copyright © 2008-" + GetDateTimeString("yyyy", "", "") + " Rizonesoft"
#define quick_launch "{userappdata}\Microsoft\Internet Explorer\Quick Launch"

[Setup]
AppId={#app_name}
AppName={#app_publisher} {#app_name}{#VRSN}
AppVersion={#app_version}{#VRSN}
AppVerName={#app_name} {#app_version}
AppPublisher={#app_publisher}
AppPublisherURL=https://rizonesoft.com/
AppSupportURL=https://www.rizonesoft.com/contact-us/
AppUpdatesURL=https://www.rizonesoft.com/downloads/rizonesoft-office/
AppContact=https://www.rizonesoft.com/contact-us/
AppCopyright={#app_copyright}
VersionInfoVersion={#app_version}
UninstallDisplayIcon={app}\Zone.exe
UninstallDisplayName={#app_name} {#app_version}{#VRSN}
DefaultDirName={commonpf}\{#app_publisher}\Office
LicenseFile="License.txt"
OutputDir=.\Packages
OutputBaseFilename={#app_name}-{#app_version}{#StringChange(VRSN, " ", "-")}-{#Arch}-Install
WizardStyle=modern
Compression=lzma2/normal
InternalCompressLevel=normal
SolidCompression=no
EnableDirDoesntExistWarning=no
AllowNoIcons=yes
ShowTasksTreeLines=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
DisableWelcomePage=no
AllowCancelDuringInstall=yes
UsedUserAreasWarning=no
MinVersion=0,6.1.7601
#If Arch == "x86"
ArchitecturesAllowed=x86 x64 arm64
ArchitecturesInstallIn64BitMode=
#EndIf
#If Arch == "x64"
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64
#EndIf
CloseApplications=true
SetupMutex={#app_name}_setup_mutex_{#GUID},Global\{#app_name}_setup_mutex_{#GUID}
UpdateUninstallLogAppName=yes
AppendDefaultDirName=no
PrivilegesRequired=admin

[Languages]
Name: en; MessagesFile: "compiler:Default.isl"
Name: fr; MessagesFile: "compiler:Languages\French.isl"
Name: it; MessagesFile: "compiler:Languages\Italian.isl"
Name: de; MessagesFile: "compiler:Languages\German.isl"
Name: es; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
// Source: "..\Office\Bin\x64\Release\*"; DestDir: "{app}\"; Check: Dependency_IsX64; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\Office\Bin\x64\Release\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#app_publisher}\{#app_name}"; Filename: "{app}\Scholar.exe"; Comment: "Launch Scholar"
Name: "{commondesktop}\{#app_name}"; Filename: "{app}\Scholar.exe"; Comment: "Launch Scholar"; Tasks: desktopicons
Name: "{group}\{#app_publisher}\Verbum"; Filename: "{app}\Verbum.exe"; Comment: "Launch Verbum"
Name: "{commondesktop}\Verbum"; Filename: "{app}\Verbum.exe"; Comment: "Launch Verbum"; Tasks: desktopicons
Name: "{group}\{#app_publisher}\Evaluate"; Filename: "{app}\Evaluate.exe"; Comment: "Launch Evaluate"
Name: "{commondesktop}\Evaluate"; Filename: "{app}\Evaluate.exe"; Comment: "Launch Evaluate"; Tasks: desktopicons
Name: "{group}\{#app_publisher}\Imagine"; Filename: "{app}\Imagine.exe"; Comment: "Launch Imagine"
Name: "{commondesktop}\Imagine"; Filename: "{app}\Imagine.exe"; Comment: "Launch Imagine"; Tasks: desktopicons


[Registry]
; Set the default program for .PDF files
Root: HKCR; Subkey: ".pdf"; ValueType: string; ValueName: ""; ValueData: "Rizonesoft.PDF"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "Rizonesoft.PDF"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekeyifempty
Root: HKCR; Subkey: "Rizonesoft.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Rizonesoft.Office.Shell.dll,1"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "Rizonesoft.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Scholar.exe"" ""%1"""
; Add to the Open With list for .pdf files
Root: HKCR; Subkey: ".pdf\OpenWithProgids"; ValueType: string; ValueName: "Scholar.Application"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "Applications\Scholar.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Scholar.exe"" ""%1"""
Root: HKCR; Subkey: "Applications\Scholar.exe\SupportedTypes"; ValueType: string; ValueName: ".pdf"; ValueData: ""; Flags: uninsdeletevalue

; Optional: Add a 'print' command if Scholar.exe supports printing directly from the command line
; Root: HKCR; Subkey: "Rizonesoft.PDF\shell\print\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Scholar.exe"" /print ""%1"""

[Tasks]
Name: "desktopicons"; Description: "Create Desktop Shortcuts"; GroupDescription: "Desktop Shortcuts"

[Code]