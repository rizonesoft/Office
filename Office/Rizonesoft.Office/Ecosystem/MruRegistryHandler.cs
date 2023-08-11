using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Rizonesoft.Office.Programs;

namespace Rizonesoft.Office.Ecosystem
{
    public class MruRegistryHandler : IMruRegistryHandler
    {
        private readonly string? RegistryKeyPath = $"{ProgramConfiguration.RegistryPath}\\MRU";

        public string[] LoadFiles()
        {
            using RegistryKey key = Registry.CurrentUser.OpenSubKey(RegistryKeyPath);

            if (key != null)
            {
                // get the names of the keys
                string[] keyNames = key.GetValueNames();

                // read the value of each key
                string[] filePaths = new string[keyNames.Length];
                for (int i = 0; i < keyNames.Length; i++)
                {
                    filePaths[i] = key.GetValue(keyNames[i]) as string;
                }

                return filePaths;
            }

            return Array.Empty<string>();
        }

        public void SaveFiles(IReadOnlyList<string> filePaths)
        {
            using RegistryKey key = Registry.CurrentUser.CreateSubKey(RegistryKeyPath);

            // Clear old entries
            foreach (string valueName in key.GetValueNames())
            {
                key.DeleteValue(valueName);
            }

            // Set new entries
            for (int i = 0; i < filePaths.Count; i++)
            {
                key.SetValue($"File{i}", filePaths[i]);
            }
        }
    }
}
