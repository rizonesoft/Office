using System;
using Microsoft.Win32;
using System.Windows.Forms;


namespace Rizonesoft.Office.Settings
{
    public class Settings
    {
        static RegistryKey BaseKey = Registry.CurrentUser.OpenSubKey("Software", true)!;

        public static string? GetSetting(string RegKey, string ValueName, string Default)
        {

            RegistryKey subKey = BaseKey.OpenSubKey(RegKey)!;

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
                RegistryKey subKey = BaseKey.CreateSubKey(RegKey);
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
                RegistryKey subKey = BaseKey.CreateSubKey(RegKey)!;

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
