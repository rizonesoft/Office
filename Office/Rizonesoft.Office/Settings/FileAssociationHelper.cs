using Microsoft.Win32;
using System.Windows.Forms;
using Microsoft.VisualBasic.Devices;

namespace Rizonesoft.Office.Settings
{
    public static class FileAssociationHelper
    {
        public static readonly string DefaultValueName = string.Empty;

        public static void AssociateFileExtension(string fileExtension, string friendlyName, string appIcon)
        {
            string actualFileExtension = (fileExtension[0] == '.' ? fileExtension : '.' + fileExtension);

            Computer computer = new Computer();

            RegistryKey rkFileExtension = computer.Registry.ClassesRoot.CreateSubKey(actualFileExtension);
            rkFileExtension.SetValue(DefaultValueName, friendlyName, RegistryValueKind.String);

            RegistryKey rkShellOpenCommand = computer.Registry.ClassesRoot.CreateSubKey(friendlyName + @"\shell\open\command");
            rkShellOpenCommand.SetValue(DefaultValueName, Application.ExecutablePath + @" ""%l"" ", RegistryValueKind.String);

            RegistryKey rkDefaultIcon = computer.Registry.ClassesRoot.CreateSubKey(friendlyName + @"\DefaultIcon");
            rkDefaultIcon.SetValue(DefaultValueName, $"{Application.StartupPath}\\{appIcon}", RegistryValueKind.String);
        }
    }
}
