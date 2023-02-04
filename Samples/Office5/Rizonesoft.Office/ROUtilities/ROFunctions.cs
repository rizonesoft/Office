﻿using System.Reflection;

namespace Rizonesoft.Office.ROUtilities
{
    using System;
    using DevExpress.XtraEditors;
    using System.Diagnostics;
    using System.Text.RegularExpressions;

    public static class ROFunctions
    {




        // public static string userAppDataPath = System.IO.Path.Combine(GetUserAppDataPath(), "Rizonesoft\\Office\\");
        // public static string loggingFilePath = System.IO.Path.Combine(userAppDataPath, "Logging\\Error.log");

        public static Regex urlRegex = new Regex(@"((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|
                                www\d{0,3}[.]|ftp[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()
                                <>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+
                                |(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'"".,<>?«»“”‘’]))", RegexOptions.IgnoreCase);

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

        public static string BooleanToString(bool bBoolean)
        {
            return bBoolean.ToString();
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