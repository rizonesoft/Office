using System.Diagnostics;

namespace Rizonesoft.Office
{
    public static class Utilities
    {
        public static string BooleanToString(bool bBoolean) { return bBoolean.ToString(); }

        public static string GetRelativePath(string name)
        {
            name = "Data\\" + name;
            string path = System.Windows.Forms.Application.StartupPath;
            string s = "\\";
            for(int i = 0; i <= 10; i++)
            {
                if(System.IO.File.Exists(path + s + name))
                    return (path + s + name);
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
            if(bool.TryParse(sBoolean, out bool bResult))
            {
                return bResult;
            } else
            {
                return false;
            }
        }
    }
}