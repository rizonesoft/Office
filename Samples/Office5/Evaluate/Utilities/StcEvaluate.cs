namespace Rizonesoft.Office.Evaluate.Utilities
{
    using Rizonesoft.Office.ROUtilities;
    using System;
    using System.IO;
    using System.Windows.Forms;

    internal class StcEvaluate
    {
        public const string ProductName = "Evaluate";

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
        public static readonly string ProductVersionString = $"20{ProductVersion.Major}";
        public static readonly string ProductBasePath = Path.GetDirectoryName(Application.ExecutablePath);
        public static readonly string UserAppDirectory = Path.Combine(ROFunctions.GetUserAppDataPath(), $"Rizonesoft\\Office\\{ProductName}\\");
        public static readonly string CurrentRegConfigPath = $"Rizonesoft\\{ROGlobals.ProductName}\\{ProductName}";
        public static readonly string CurrentRegGeneralPath = $"{CurrentRegConfigPath}\\General";
        public static readonly string CurrentRegInterfacePath = $"{CurrentRegConfigPath}\\Interface";
        public static readonly string StaticRegInterfacePath = $"{ROGlobals.CurrentUserReg}\\{CurrentRegConfigPath}\\Interface";
    }
}
