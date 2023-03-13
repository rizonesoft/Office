namespace Rizonesoft.Office.Utilities
{
    using DevExpress.XtraEditors;
    using System.Diagnostics;
    using System.Globalization;
    using System.IO;
    using System.Text.RegularExpressions;

    public static class RizonesoftEx
    {

        public const string ProductName = "Office";
        public const string CurrentUserReg = "HKEY_CURRENT_USER\\Software";
        public const int CurrentBetaVersion = 1;

        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version!;
        public static readonly string ProductVersionMajor = ProductVersion.Major.ToString();
        public static readonly string UserAppDirectory = Path.Combine(GetUserAppDataPath(), "Rizonesoft\\" + ProductName + "\\");
        public static readonly string LicenseRegPath = $"{CurrentUserReg}\\Rizonesoft\\{ProductName}\\General";

        static bool isBetaVersion = false;
        static bool isLicensed = false;
        static string spellingLanguage = "en_US";

        public static bool ReviewPanelVisible { get; set; }
        public static bool AutoSpellCheck { get; set; }
        public static bool IsBetaVersion { get => isBetaVersion; set => isBetaVersion = value; }
        public static bool IsLicensed { get => isLicensed; set => isLicensed = value; }
        public static string SpellingLanguage { get => spellingLanguage; set => spellingLanguage = value; }
        public static string BetaVersionString
        {
            get => IsBetaVersion ? $"Beta {CurrentBetaVersion}" : string.Empty;
            set => throw new NotImplementedException();
        }

        public static void SetBetaVersion()
        {

        }

        public static Regex urlRegex = new Regex(@"((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|
                                www\d{0,3}[.]|ftp[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()
                                <>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+
                                |(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'"".,<>?«»“”‘’]))", RegexOptions.IgnoreCase);

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

        public static string BooleanToString(bool bBoolean)
        {
            return bBoolean.ToString();
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

        public static string GeometryToString(XtraForm mainForm)
        {
            return $"{mainForm.Location.X}|{mainForm.Location.Y}|{mainForm.Size.Width}|{mainForm.Size.Height}|{mainForm.WindowState}";
        }

        public static string GetRelativePath(string name)
        {
            name = "Data\\" + name;
            string path = Application.StartupPath;
            string s = "\\";
            for (int i = 0; i <= 10; i++)
            {
                if (System.IO.File.Exists(path + s + name))
                    return path + s + name;
                else
                    s += "..\\";
            }
            return string.Empty;
        }

        public static string GetUserAppDataPath()
        {
            string userCommPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            if (!userCommPath.EndsWith("\\")) userCommPath += "\\";
            {
                return userCommPath;
            }
        }

        public static void OpenWebPage(string webAddress)
        {
            Process process = new Process();
            process.StartInfo.FileName = webAddress;
            process.StartInfo.Verb = "Open";
            process.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
            process.Start();
        }

        public static bool StringToBoolean(string sBoolean)
        {
            if (bool.TryParse(sBoolean, out bool bResult))
            {
                return bResult;
            }
            else
            {
                return false;
            }
        }

    }
}
