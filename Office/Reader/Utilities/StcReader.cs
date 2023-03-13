namespace Rizonesoft.Office.Reader.Utilities
{
    using Rizonesoft.Office.Utilities;
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal class StcReader
    {
        public const string ProductName = "Reader";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        public static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        public static readonly string DocumentsBasePath = Path.Combine(ProductBasePath, "Documents");
        public static readonly string WelcomePDFPath = Path.Combine(DocumentsBasePath, "Welcome.pdf");
        public static readonly string UserAppDirectory = Path.Combine(RizonesoftEx.GetUserAppDataPath(), $"Rizonesoft\\Office\\{ProductName}\\");
        public static readonly string CurrentRegConfigPath = $"Rizonesoft\\{RizonesoftEx.ProductName}\\{ProductName}";
        public static readonly string CurrentRegGeneralPath = $"{CurrentRegConfigPath}\\General";
        public static readonly string CurrentRegInterfacePath = $"{CurrentRegConfigPath}\\Interface";
        public static readonly string StaticRegInterfacePath = $"{RizonesoftEx.CurrentUserReg}\\{CurrentRegConfigPath}\\Interface";

    }
}
