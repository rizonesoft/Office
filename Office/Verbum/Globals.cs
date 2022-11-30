namespace Rizonesoft.Office.Verbum
{
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal class Globals
    {
        public const string ProductName = "Verbum";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        public static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        public static readonly string UserAppDirectory = Path.Combine(Utilities.GetUserAppDataPath(), $"Rizonesoft\\Office\\{Globals.ProductName}\\");
        public static readonly string LoggingFilePath = Path.Combine(UserAppDirectory, "Logging\\Error.log");
        public static readonly string DictionariesPath = Path.Combine(ProductBasePath, "Dictionaries");

        public static bool ReviewPanelVisible { get; set; }
        public static bool AutoSpellCheck { get; set; }
        public static string SpellingLanguage { get; set; } = "en_US";

    }
}
