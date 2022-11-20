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


        public static Regex urlRegex = new Regex(@"((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|
                                www\d{0,3}[.]|ftp[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()
                                <>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+
                                |(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'"".,<>?«»“”‘’]))", RegexOptions.IgnoreCase);

        public static string basePath = System.IO.Path.GetDirectoryName(Application.ExecutablePath);
        public static string licensePath = System.IO.Path.Combine(basePath, "License.lic");
        public static string dictionariesPath = System.IO.Path.Combine(basePath, "Dictionaries");
        public static string userAppDataPath = System.IO.Path.Combine(GetUserAppDataPath(), "Rizonesoft\\Office\\Verbum\\");
        public static string loggingFilePath = System.IO.Path.Combine(userAppDataPath, "Logging\\Error.log");
        public static string userSpellingOptionsFile = System.IO.Path.Combine(userAppDataPath, "SpellingOptions.xml");
        public static string saveToolbarToXmlFileName = System.IO.Path.Combine(userAppDataPath, "ToolbarSettings.xml");
        public static string saveLayoutToXmlFileName = System.IO.Path.Combine(userAppDataPath, "RibbonSettings.xml");

        public static string GetUserAppDataPath()
        {
            string userCommPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            if (!userCommPath.EndsWith("\\")) userCommPath += "\\";
            {
                return userCommPath;
            }
        }



        public static void GeometryFromString(string thisWindowGeometry, XtraForm formIn)
        {
            if (string.IsNullOrEmpty(thisWindowGeometry) == true)
            {
                return;
            }
            string[] numbers = thisWindowGeometry.Split('|');
            string windowString = numbers[4];
            if (windowString == "Normal")
            {
                Point windowPoint = new Point(int.Parse(numbers[0]),
                    int.Parse(numbers[1]));
                Size windowSize = new Size(int.Parse(numbers[2]),
                    int.Parse(numbers[3]));

                bool locOkay = GeometryIsBizarreLocation(windowPoint, windowSize);
                bool sizeOkay = GeometryIsBizarreSize(windowSize);

                if (locOkay == true && sizeOkay == true)
                {
                    formIn.Location = windowPoint;
                    formIn.Size = windowSize;
                    formIn.StartPosition = FormStartPosition.Manual;
                    formIn.WindowState = FormWindowState.Normal;
                }
                else if (sizeOkay == true)
                {
                    formIn.Size = windowSize;
                }
            }
            else if (windowString == "Maximized")
            {
                formIn.Location = new Point(100, 100);
                formIn.StartPosition = FormStartPosition.Manual;
                formIn.WindowState = FormWindowState.Maximized;
            }
        }

        private static bool GeometryIsBizarreLocation(Point loc, Size size)
        {
            bool locOkay;
            if (loc.X < 0 || loc.Y < 0)
            {
                locOkay = false;
            }
            else if (loc.X + size.Width > Screen.PrimaryScreen.WorkingArea.Width)
            {
                locOkay = false;
            }
            else if (loc.Y + size.Height > Screen.PrimaryScreen.WorkingArea.Height)
            {
                locOkay = false;
            }
            else
            {
                locOkay = true;
            }
            return locOkay;
        }

        private static bool GeometryIsBizarreSize(Size size)
        {
            return size.Height <= Screen.PrimaryScreen.WorkingArea.Height &&
                size.Width <= Screen.PrimaryScreen.WorkingArea.Width;
        }

        public static string GeometryToString(XtraForm mainForm)
        {
            return mainForm.Location.X.ToString() + "|" +
                mainForm.Location.Y.ToString() + "|" +
                mainForm.Size.Width.ToString() + "|" +
                mainForm.Size.Height.ToString() + "|" +
                mainForm.WindowState.ToString();
        }


    }
}
