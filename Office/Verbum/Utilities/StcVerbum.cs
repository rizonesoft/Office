namespace Rizonesoft.Office.Verbum.Utilities
{
    using Rizonesoft.Office.Utilities;
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal class StcVerbum
    {
        public const string ProductName = "Verbum";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        public static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        public static readonly string UserAppDirectory = Path.Combine(GlobalFunctions.GetUserAppDataPath(), $"Rizonesoft\\Office\\{ProductName}\\");
        public static readonly string DictionariesPath = Path.Combine(ProductBasePath, "Dictionaries");
        public static readonly string CurrentRegConfigPath = $"Rizonesoft\\{GlobalProperties.ProductName}\\{ProductName}";
        public static readonly string CurrentRegGeneralPath = $"{CurrentRegConfigPath}\\General";
        public static readonly string CurrentRegInterfacePath = $"{CurrentRegConfigPath}\\Interface";
        public static readonly string CurrentRegSpellingPath = $"{CurrentRegConfigPath}\\Spelling";
        public static readonly string CurrentRegMRUPath = $"{CurrentRegConfigPath}\\MRU";
        public static readonly string CurrentSpellingXmlFile = Path.Combine(UserAppDirectory, "Spelling.conf");
        public static readonly string StaticRegInterfacePath = $"{GlobalProperties.CurrentUserReg}\\{CurrentRegConfigPath}\\Interface";
        public static readonly string StaticRegSpellingPath = $"{GlobalProperties.CurrentUserReg}\\{CurrentRegConfigPath}\\Spelling";

        public static bool ReviewPanelVisible { get; set; }
        public static bool AutoSpellCheck { get; set; }
        public static string SpellingLanguage { get; set; } = "en_US";

    }
}
