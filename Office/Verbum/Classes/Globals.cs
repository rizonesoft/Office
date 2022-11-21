using DevExpress.XtraEditors;
using System;
using System.Drawing;
using System.Text.RegularExpressions;
using System.Windows.Forms;


namespace Rizonesoft.Office.Verbum.Classes
{
    internal class Globals
    {

        public static bool autoSpellCheck = true;
        public static string spellingLanguage = "en_US";

        public static string basePath = System.IO.Path.GetDirectoryName(Application.ExecutablePath);
        public static string dictionariesPath = System.IO.Path.Combine(basePath, "Dictionaries");
        public static string userAppDataPath = System.IO.Path.Combine(Utilities.GetUserAppDataPath(), "Rizonesoft\\Office\\Verbum\\");
        public static string loggingFilePath = System.IO.Path.Combine(userAppDataPath, "Logging\\Error.log");
        public static string userSpellingOptionsFile = System.IO.Path.Combine(userAppDataPath, "SpellingOptions.xml");
        public static string saveToolbarToXmlFileName = System.IO.Path.Combine(userAppDataPath, "ToolbarSettings.xml");
        public static string saveLayoutToXmlFileName = System.IO.Path.Combine(userAppDataPath, "RibbonSettings.xml");

    }
}
