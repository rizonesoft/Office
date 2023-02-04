namespace Rizonesoft.Office.ROUtilities
{
    using System.IO;

    public static class ROGlobals
    {

        public const string LicenseHomeString = "Unregistered!";
        public const string LicenseBusinessString = "Business";
        public const string ProductName = "Office";
        public const string CurrentUserReg = "HKEY_CURRENT_USER\\Software";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version!;
        public static readonly string ProductVersionMajor = ProductVersion.Major.ToString();
        public static readonly string ProductVersionYear = "20" + ProductVersionMajor;
        public static readonly string UserAppDirectory = Path.Combine(ROFunctions.GetUserAppDataPath(), "Rizonesoft\\" + ProductName + "\\");

        public static bool ReviewPanelVisible { get; set; }
        public static bool AutoSpellCheck { get; set; }
        public static string SpellingLanguage { get; set; } = "en_US";
    }
}
