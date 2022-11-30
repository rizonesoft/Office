using System;
using Microsoft.Win32;
using System.Windows.Forms;


namespace Rizonesoft.Office.Configure
{
    public class Settings
    {
        const string STR_RegSoftware = "Software";

        public static string? GetSetting(string RegKey, string ValueName, string Default)
        {

            RegistryKey baseKey = Registry.CurrentUser.OpenSubKey(STR_RegSoftware)!;
            RegistryKey subKey = baseKey.OpenSubKey(RegKey)!;

            if (subKey == null)
            {
                return Default;
            }
            else
            {
                try
                {
                    return (string?)subKey.GetValue(ValueName, Default);
                }
                catch (Exception ex)
                {
                    ShowErrorMessage(ex, "Reading registry " + ValueName);
                    return "";
                }
            }
        }

        public static bool SaveSetting(string RegKey, string ValueName, string Value)
        {
            try
            {
                RegistryKey baseKey = Registry.CurrentUser.OpenSubKey(STR_RegSoftware, true)!;
                RegistryKey subKey = baseKey.CreateSubKey(RegKey);
                subKey.SetValue(ValueName, Value);

                return true;
            }
            catch (Exception e)
            {
                ShowErrorMessage(e, "Writing registry " + ValueName);
                return false;
            }
        }



        public static bool DeleteSetting(string RegKey, string ValueName)
        {
            try
            {
                RegistryKey baseKey = Registry.CurrentUser.OpenSubKey("Software", true)!;
                RegistryKey subKey = baseKey.CreateSubKey(RegKey)!;

                if (subKey == null)
                {
                    return true;
                }

                else
                {
                    if (subKey.GetValue(ValueName) != null)
                    {
                        subKey.DeleteValue(ValueName);
                    }
                }

                return true;
            }
            catch (Exception e)
            {
                ShowErrorMessage(e, "Deleting Value " + ValueName);
                return false;
            }
        }

        private static void ShowErrorMessage(Exception e, string Title)
        {
            MessageBox.Show(e.Message, Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

    }
}
