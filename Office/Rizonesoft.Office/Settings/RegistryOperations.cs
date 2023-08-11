using Microsoft.Win32;
using System;
using Rizonesoft.Office.Programs;

namespace Rizonesoft.Office.Settings
{
    /// <summary>
    /// Provides operations for reading, writing and deleting registry keys.
    /// </summary>
    public static class RegistryOperations
    {
        private const string GlobalSubKey = @"SOFTWARE\Rizonesoft\Office\Global";
        private static readonly string LocalSubKey = ProgramConfiguration.RegistryPath;

        /// <summary>
        /// Specifies the scope of the registry operation.
        /// </summary>
        public enum SettingScope
        {
            /// <summary>
            /// Specifies that the registry operation is global in scope.
            /// </summary>
            Global,

            /// <summary>
            /// Specifies that the registry operation is local in scope.
            /// </summary>
            Local
        }

        /// <summary>
        /// Reads a value from the registry.
        /// </summary>
        /// <exception cref="ArgumentException">If the scope is invalid.</exception>
        /// <exception cref="InvalidOperationException">If the key or value could not be found.</exception>
        public static object Read(string key, SettingScope scope)
        {
            string subKey = GetSubKey(scope);
            using RegistryKey rk = Registry.CurrentUser.OpenSubKey(subKey);
            if (rk == null)
                throw new InvalidOperationException($"Cannot find key {subKey}");

            object result = rk.GetValue(key);
            if (result == null)
                throw new InvalidOperationException($"Cannot find value {key}");

            return result;
        }

        /// <summary>
        /// Writes a value to the registry.
        /// </summary>
        /// <exception cref="ArgumentException">If the scope is invalid.</exception>
        /// <exception cref="InvalidOperationException">If the key could not be created or opened.</exception>
        public static void Write(string key, object value, SettingScope scope)
        {
            string subKey = GetSubKey(scope);
            using RegistryKey rk = Registry.CurrentUser.CreateSubKey(subKey);
            if (rk == null)
                throw new InvalidOperationException($"Cannot create or open key {subKey}");

            rk.SetValue(key, value);
        }

        /// <summary>
        /// Deletes a key from the registry.
        /// </summary>
        /// <exception cref="ArgumentException">If the scope is invalid.</exception>
        /// <exception cref="InvalidOperationException">If the key could not be found.</exception>
        public static void DeleteKey(string key, SettingScope scope)
        {
            string subKey = GetSubKey(scope);
            using RegistryKey rk = Registry.CurrentUser.OpenSubKey(subKey);
            if (rk == null)
                throw new InvalidOperationException($"Cannot find key {subKey}");

            rk.DeleteValue(key);
        }

        /// <summary>
        /// Deletes a subkey tree from the registry.
        /// </summary>
        /// <exception cref="ArgumentException">If the scope is invalid.</exception>
        public static void DeleteSubKeyTree(SettingScope scope)
        {
            string subKey = GetSubKey(scope);
            Registry.CurrentUser.DeleteSubKeyTree(subKey);
        }

        /// <summary>
        /// Gets the appropriate subkey based on the scope.
        /// </summary>
        /// <exception cref="ArgumentException">If the scope is invalid.</exception>
        private static string GetSubKey(SettingScope scope) => scope switch
        {
            SettingScope.Global => GlobalSubKey,
            SettingScope.Local => LocalSubKey,
            _ => throw new ArgumentException("Invalid scope", nameof(scope)),
        };
    }
}
