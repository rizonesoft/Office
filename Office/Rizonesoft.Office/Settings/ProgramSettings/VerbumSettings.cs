namespace Rizonesoft.Office.Settings.ProgramSettings
{
    public static class VerbumSettings
    {
        private const bool DefaultAutoSpellCheck = true;
        private const string AutoSpellCheckRegistryKey = "AutoSpellCheck";
        private const string DefaultSpellingLanguage = "en-US";
        private const string SpellingLanguageRegistryKey = "SpellingLanguage";

        private static readonly RegistrySetting<bool> AutoSpellCheckSetting = new(AutoSpellCheckRegistryKey, DefaultAutoSpellCheck, RegistryOperations.SettingScope.Local);
        private static readonly RegistrySetting<string> SpellingLanguageSetting = new(SpellingLanguageRegistryKey, DefaultSpellingLanguage, RegistryOperations.SettingScope.Local);

        public static bool AutoSpellCheck
        {
            get => AutoSpellCheckSetting.Value;
            set => AutoSpellCheckSetting.Value = value;
        }

        public static string SpellingLanguage
        {
            get => SpellingLanguageSetting.Value;
            set => SpellingLanguageSetting.Value = value;
        }
    }
}
