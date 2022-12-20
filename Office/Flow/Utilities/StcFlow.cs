namespace Rizonesoft.Office.Flow.Utilities
{
    using Rizonesoft.Office.Utilities;
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal class StcFlow
    {
        public const string ProductName = "Flow";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        public static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        public static readonly string UserAppDirectory = Path.Combine(GlobalFunctions.GetUserAppDataPath(), $"Rizonesoft\\Office\\{ProductName}\\");
        public static readonly string CurrentRegConfigPath = $"Rizonesoft\\{GlobalProperties.ProductName}\\{ProductName}";
        public static readonly string CurrentRegGeneralPath = $"{CurrentRegConfigPath}\\General";
        public static readonly string CurrentRegInterfacePath = $"{CurrentRegConfigPath}\\Interface";
        public static readonly string StaticRegInterfacePath = $"{GlobalProperties.CurrentUserReg}\\{CurrentRegConfigPath}\\Interface";

    }
}
