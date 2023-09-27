namespace Rizonesoft.Office.Settings
{
    /// <summary>
    /// Class that holds the application-wide settings of Rizonesoft Office.
    /// </summary>
    public static class GlobalSettings
    {
        private const string DefaultLanguageCode = "en";
        private const int DefaultLogRollingInterval = 3;
        private const int DefaultLogFileLimit = 10;
        private const string DefaultSkinName = "WXI";
        private const string DefaultPalette = "Clearness";
        private const bool DefaultTrackWindowsAppMode = false;
        private const bool DefaultTrackWindowsAccentColor = false;
        
        private const string SkinNameRegistryKey = "SkinName";
        private const string PaletteRegistryKey = "Palette";

        private static readonly RegistrySetting<string> languageCode = new("LanguageCode", DefaultLanguageCode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<int> logRollingInterval = new("LogRollingInterval", DefaultLogRollingInterval, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<int> logFileLimit = new("LogFileLimit", DefaultLogFileLimit, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<string> skinName = new(SkinNameRegistryKey, DefaultSkinName, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<string> palette = new(PaletteRegistryKey, DefaultPalette, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<bool> trackWindowsAppMode = new("TrackWindowsAppMode", DefaultTrackWindowsAppMode, RegistryOperations.SettingScope.Global);
        private static readonly RegistrySetting<bool> trackWindowsAccentColor = new("TrackWindowsAccentColor", DefaultTrackWindowsAccentColor, RegistryOperations.SettingScope.Global);

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

        /// <summary>
        /// Gets or sets the skin name for the application interface.
        /// </summary>
        public static string SkinName
        {
            get => skinName.Value;
            set => skinName.Value = value;
        }

        public static string Palette
        {
            get => palette.Value;
            set => palette.Value = value;
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

        

    }
}
