namespace Rizonesoft.Office.Utilities
{
    using DevExpress.XtraEditors;
    using System.Diagnostics;
    using System.IO;
    using System.Text.RegularExpressions;

    public static class RizonesoftEx
    {
        // Utility class with extension methods and helper functions
        private const int CurrentBetaVersion = 1;

        public const string CurrentUserReg = "HKEY_CURRENT_USER\\Software";
        public const string ProductName = "Office";
        internal const string LicenseRegPath = $"{CurrentUserReg}\\Rizonesoft\\{ProductName}\\General";
        public static readonly Version ProductVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version!;
        public static readonly string ProductVersionMajor = ProductVersion.Major.ToString();
        internal static readonly string UserAppDirectory = Path.Combine(GetUserAppDataPath(), $"Rizonesoft\\{ProductName}");
        public static Regex UrlRegex = new(@"((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|
                                www\d{0,3}[.]|ftp[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()
                                <>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+
                                |(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'"".,<>?«»“”‘’]))", RegexOptions.IgnoreCase);

        public static bool AutoSpellCheck { get; set; }
        public static string BetaVersionString => IsBetaVersion ? $"Beta {CurrentBetaVersion}" : string.Empty;
        public static bool IsBetaVersion { get; set; }
        public static bool IsLicensed { get; set; }

        // public static bool ReviewPanelVisible { get; set; }
        // public static string SpellingLanguage { get; set; } = "en_US";

        public static string BooleanToString(bool bBoolean)
        {
            return bBoolean.ToString();
        }

        public static void GeometryFromString(string thisWindowGeometry, XtraForm formIn)
        {
            if (string.IsNullOrEmpty(thisWindowGeometry))
            {
                return;
            }
            var numbers = thisWindowGeometry.Split('|');
            var windowString = numbers[4];
            switch (windowString)
            {
                case "Normal":
                {
                    var windowPoint = new Point(int.Parse(numbers[0]),
                        int.Parse(numbers[1]));
                    var windowSize = new Size(int.Parse(numbers[2]),
                        int.Parse(numbers[3]));

                    var locOkay = GeometryIsBizarreLocation(windowPoint, windowSize);
                    var sizeOkay = GeometryIsBizarreSize(windowSize);

                    if (locOkay && sizeOkay)
                    {
                        formIn.Location = windowPoint;
                        formIn.Size = windowSize;
                        formIn.StartPosition = FormStartPosition.Manual;
                        formIn.WindowState = FormWindowState.Normal;
                    }
                    else if (sizeOkay)
                    {
                        formIn.Size = windowSize;
                    }

                    break;
                }
                case "Maximized":
                    formIn.Location = new Point(100, 100);
                    formIn.StartPosition = FormStartPosition.Manual;
                    formIn.WindowState = FormWindowState.Maximized;
                    break;
            }
        }

        public static string GeometryToString(XtraForm mainForm)
        {
            return $"{mainForm.Location.X}|{mainForm.Location.Y}|{mainForm.Size.Width}|{mainForm.Size.Height}|{mainForm.WindowState}";
        }

        public static string GetRelativePath(string name)
        {
            name = $"Data\\{name}";
            var path = Application.StartupPath;
            var s = "\\";
            for (var i = 0; i <= 10; i++)
            {
                if (File.Exists(path + s + name))
                    return path + s + name;
                else
                    s += "..\\";
            }
            return string.Empty;
        }

        public static string GetUserAppDataPath()
        {
            var userCommPath = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            if (!userCommPath.EndsWith("\\")) userCommPath += "\\";
            {
                return userCommPath;
            }
        }

        public static void OpenWebPage(string webAddress)
        {
            var process = new Process();
            process.StartInfo.FileName = webAddress;
            process.StartInfo.Verb = "Open";
            process.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
            process.Start();
        }

        public static void SetBetaVersion()
        {
        }
        public static bool StringToBoolean(string sBoolean)
        {
            return bool.TryParse(sBoolean, out var bResult) && bResult;
        }

        private static bool GeometryIsBizarreLocation(Point loc, Size size)
        {
            bool locOkay;
            if (loc.X < 0 || loc.Y < 0)
            {
                locOkay = false;
            }
            else if (Screen.PrimaryScreen != null && loc.X + size.Width > Screen.PrimaryScreen.WorkingArea.Width)
            {
                locOkay = false;
            }
            else if (Screen.PrimaryScreen != null && loc.Y + size.Height > Screen.PrimaryScreen.WorkingArea.Height)
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
            return Screen.PrimaryScreen != null &&
                   size.Height <= Screen.PrimaryScreen.WorkingArea.Height &&
                   size.Width <= Screen.PrimaryScreen.WorkingArea.Width;
        }
    }
}