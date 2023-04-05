namespace Rizonesoft.Office.Reader.Utilities
{
    using Rizonesoft.Office.Utilities;
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal abstract class StcReader
    {
        public const string ProductName = "Reader";
        private const string CURRENT_REG_CONFIG_PATH = $"Rizonesoft\\{RizonesoftEx.ProductName}\\{ProductName}";
        public const string CurrentRegGeneralPath = $"{CURRENT_REG_CONFIG_PATH}\\General";
        public const string CurrentRegInterfacePath = $"{CURRENT_REG_CONFIG_PATH}\\Interface";
        public const string StaticRegInterfacePath = $"{RizonesoftEx.CurrentUserReg}\\{CURRENT_REG_CONFIG_PATH}\\Interface";
        public const string CurrentRegMruPath = $"{CURRENT_REG_CONFIG_PATH}\\MRU";

        private static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        private static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        private static readonly string DocumentsBasePath = Path.Combine(ProductBasePath, "Documents");
        public static readonly string WelcomePdfPath = Path.Combine(DocumentsBasePath, "Demo.pdf");
        public static readonly string UserAppDirectory = Path.Combine(RizonesoftEx.GetUserAppDataPath(), $"Rizonesoft\\Office\\{ProductName}\\");
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        
    }
}
