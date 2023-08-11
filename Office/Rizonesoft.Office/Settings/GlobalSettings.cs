namespace Rizonesoft.Office.Settings
{
    /// <summary>
    /// Class that holds the application-wide settings of Rizonesoft Office.
    /// </summary>
    public static class GlobalSettings
    {
        private const string DefaultLicenseCode = "Unlicensed";
        private const bool DefaultTrackWindowsAppMode = true;
        private const bool DefaultTrackWindowsAccentColor = false;
        private const bool DefaultIsDarkMode = false;
        private const string DefaultLanguageCode = "en";
        private const int DefaultLogRollingInterval = 3;
        private const int DefaultLogFileLimit = 10;

        private static readonly RegistrySetting<string> licenseCode = new("LicenseCode", DefaultLicenseCode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<bool> trackWindowsAppMode = new("TrackWindowsAppMode", DefaultTrackWindowsAppMode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<bool> trackWindowsAccentColor = new("TrackWindowsAccentColor", DefaultTrackWindowsAccentColor, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<bool> isDarkMode = new("IsDarkMode", DefaultIsDarkMode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<string> languageCode = new("LanguageCode", DefaultLanguageCode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<int> logRollingInterval = new("LogRollingInterval", DefaultLogRollingInterval, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<int> logFileLimit = new("LogFileLimit", DefaultLogFileLimit, RegistryOperations.SettingScope.Global);

        /// <summary>
        /// Gets or sets the License Code.
        /// </summary>
        public static string LicenseCode
        {
            get => licenseCode.Value;
            set => licenseCode.Value = value;
        }

        public static bool TrackWindowsAppMode
        {
            get => trackWindowsAppMode.Value;
            set => trackWindowsAppMode.Value = value;
        }

        public static bool TrackWindowsAccentColor
        {
            get => trackWindowsAccentColor.Value;
            set => trackWindowsAccentColor.Value = value;
        }

        /// <summary>
        /// Gets or sets a value indicating whether dark mode is enabled.
        /// </summary>
        public static bool IsDarkMode
        {
            get => isDarkMode.Value;
            set => isDarkMode.Value = value;
        }

        /// <summary>
        /// Gets or sets the Language Code.
        /// </summary>
        public static string LanguageCode
        {
            get => languageCode.Value;
            set => languageCode.Value = value;
        }

        /// <summary>
        /// Gets or sets the Log Rolling Interval.
        /// </summary>
        public static int LogRollingInterval
        {
            get => logRollingInterval.Value;
            set => logRollingInterval.Value = value;
        }

        /// <summary>
        /// Gets or sets the Log File Limit.
        /// </summary>
        public static int LogFileLimit
        {
            get => logFileLimit.Value;
            set => logFileLimit.Value = value;
        }
    }
}
