namespace Rizonesoft.Office.Evaluate
{
    using System;
    using System.Windows.Forms;


    internal class Globals
    {
        public static readonly string Company = "Rizonetech";
        public static readonly string LicenseHomeString = "Home";
        public static readonly string icenseBusinessString = "Business";
        public static readonly string ProductName = "Evaluate";
        public static readonly string ProductYear = "2023";

        public static string LoggingBasePath
        {
            get => System.IO.Path.Combine(UserAppDirectory, "Logging\\Error.log");
            set => throw new NotImplementedException();
        }
        public static string ProductBasePath
        {
            get => System.IO.Path.GetDirectoryName(Application.ExecutablePath);
            set => throw new NotImplementedException();
        }

        public static Version ProductVersion
        {
            get => System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            set => throw new NotImplementedException();
        }
        public static string UserAppDirectory
        {
            get => System.IO.Path.Combine(Utilities.GetUserAppDataPath(), "Rizonesoft\\Office\\" + Globals.ProductName + "\\");
            set => throw new NotImplementedException();
        }
    }
}
