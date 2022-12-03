using Microsoft.Win32;
using System.Windows.Forms;
using Microsoft.VisualBasic.Devices;

public static class FileAssociationHelper {
    public static readonly string DefaultRegistryKeyValueName = string.Empty;

    public static void AssociateFileExtension(string fileExtension) {
        string actualFileExtension = (fileExtension[0] == '.' ? fileExtension : '.' + fileExtension);
        string friendlyName = actualFileExtension.TrimStart(new char[] { '.' }) + "file";

        Computer computer = new Computer();

        RegistryKey rkFileExtension = computer.Registry.ClassesRoot.CreateSubKey(actualFileExtension);
        rkFileExtension.SetValue(DefaultRegistryKeyValueName, friendlyName, RegistryValueKind.String);

        RegistryKey rkShellOpenCommand = computer.Registry.ClassesRoot.CreateSubKey(friendlyName + @"\shell\open\command");
        rkShellOpenCommand.SetValue(DefaultRegistryKeyValueName, Application.ExecutablePath + @" ""%l"" ", RegistryValueKind.String);

        RegistryKey rkDefaultIcon = computer.Registry.ClassesRoot.CreateSubKey(friendlyName + @"\DefaultIcon");
        rkDefaultIcon.SetValue(DefaultRegistryKeyValueName, Application.StartupPath + @"\App.ico", RegistryValueKind.String);
    }
}