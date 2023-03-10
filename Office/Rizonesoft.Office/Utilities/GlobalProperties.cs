namespace Rizonesoft.Office.Utilities
{
    using System.IO;

    public static class GlobalProperties
    {

        public const string ProductName = "Office";
        public const string CurrentUserReg = "HKEY_CURRENT_USER\\Software";
        public const int CurrentBetaVersion = 1;

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version!;
        public static readonly string ProductVersionMajor = ProductVersion.Major.ToString();
        public static readonly string UserAppDirectory = Path.Combine(GlobalFunctions.GetUserAppDataPath(), "Rizonesoft\\" + ProductName + "\\");
        public static readonly string LicenseRegPath = $"{CurrentUserReg}\\Rizonesoft\\{ProductName}\\General";

        static bool isBetaVersion = false;
        static string spellingLanguage = "en_US";

        public static bool ReviewPanelVisible { get; set; }
        public static bool AutoSpellCheck { get; set; }
        public static bool IsBetaVersion { get => isBetaVersion; set => isBetaVersion = value; }
        public static string SpellingLanguage { get => spellingLanguage; set => spellingLanguage = value; }
        public static string BetaVersionString
        {
            get => IsBetaVersion ? $"Beta {CurrentBetaVersion}" : string.Empty;
            set => throw new NotImplementedException();
        }
    }
}
