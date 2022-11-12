using System.Diagnostics;

namespace Rizonesoft.Office
{
    public static class Utilities
    {
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

        public static string BooleanToString(bool bBoolean)
        {
            return bBoolean.ToString();
        }
    }
}