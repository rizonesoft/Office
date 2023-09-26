;* Rizonesoft Office - Installer script x64
;*
;* (c) Rizonesoft 2008-2023

; Requirements:
; Inno Setup: https://jrsoftware.org/isinfo.php

; Preprocessor related stuff
// #define public Dependency_Path_NetCoreCheck "dependencies\"
// #include "CodeDependencies.iss"

#define GUID="F0085D50-B268-5FEB-B289-5F999C5C26FD"
#define app_name "Office"
#define app_publisher "Rizonesoft"
#define RLSdir "..\Office\Bin\Release\"
#define app_version GetVersionNumbersString(RLSdir + "Rizonesoft.Office.dll")
#define VRSN=" Alpha 5"
#define app_copyright "Copyright © 2008-" + GetDateTimeString("yyyy", "", "") + " Rizonesoft"
#define quick_launch "{userappdata}\Microsoft\Internet Explorer\Quick Launch"

[Setup]
AppId={#GUID}
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
OutputBaseFilename={#app_name}-{#app_version}{#StringChange(VRSN, " ", "-")}-Install
WizardStyle=modern
Compression=lzma
SolidCompression=yes
InternalCompressLevel=max
EnableDirDoesntExistWarning=no
AllowNoIcons=yes
ShowTasksTreeLines=yes
DisableProgramGroupPage=yes
AllowCancelDuringInstall=yes
UsedUserAreasWarning=no
MinVersion=10.0.17763
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64
CloseApplications=no
SetupMutex={#app_name}_setup_mutex_{#GUID},Global\{#app_name}_setup_mutex_{#GUID}
UpdateUninstallLogAppName=yes
AppendDefaultDirName=no
PrivilegesRequired=admin

[Languages]
Name: en; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\Office\Bin\Release\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#app_publisher}\Scholar"; Filename: "{app}\Scholar.exe"; Comment: "Launch Scholar"
Name: "{commondesktop}\Scholar"; Filename: "{app}\Scholar.exe"; Comment: "Launch Scholar"; Tasks: desktopicons
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

[Code]

function InitializeSetup: Boolean;
var
  UninstallString: string;
  ErrorCode: Integer;
  UserResponse: Integer;
  AppIds: array of string;
  i: Integer;
begin
  // Define the AppIds to look for
  SetArrayLength(AppIds, 2);
  AppIds[0] := 'Office_is1';
  AppIds[1] := '{#GUID}_is1';

  // Loop through each AppId and check for installations
  for i := 0 to GetArrayLength(AppIds) - 1 do
  begin
    if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' + AppIds[i], 'UninstallString', UninstallString) then
    begin
      // Inform the user about the uninstallation
      UserResponse := MsgBox('We have detected a previous version of Rizonesoft Office ' + 
                             '. To ensure optimal performance and a seamless upgrade experience, ' + 
                             'it is recommended to uninstall the older version before proceeding. ' + 
                             'Would you like to continue with the uninstallation?', mbConfirmation, MB_YESNO);
      
      // If the user agrees to proceed
      if UserResponse = IDYES then
      begin
        // Execute the Uninstall string
        if not ShellExec('', UninstallString, '/NORESTART', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode) then
        begin
          MsgBox('Uninstallation failed with error code: ' + IntToStr(ErrorCode), mbError, MB_OK);
        end
        else
        begin
          Log('Execution successful.');
        end;
      end
      else
      begin
        MsgBox('Installation cannot proceed without uninstalling the previous version. We promise not to delete any of your data.', mbError, MB_OK);
        Result := False;  // Stop the installation
        Exit;
      end;
    end;
  end;

  Result := True;  // Continue with the installation
end;
