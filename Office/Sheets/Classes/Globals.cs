using DevExpress.XtraEditors;
using System;
using System.Drawing;
using System.Text.RegularExpressions;
using System.Windows.Forms;


namespace Rizonesoft.Office.Sheets.Classes
{
    internal class Globals
    {

        public static string basePath = System.IO.Path.GetDirectoryName(Application.ExecutablePath);
        public static string userAppDataPath = System.IO.Path.Combine(Utilities.GetUserAppDataPath(), "Rizonesoft\\Office\\Sheets\\");
        public static string loggingFilePath = System.IO.Path.Combine(userAppDataPath, "Logging\\Error.log");


    }
}
