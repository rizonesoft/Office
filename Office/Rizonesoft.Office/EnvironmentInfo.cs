using OSVersionExtension;
using System.Reflection;
using System.Runtime.InteropServices;

namespace Rizonesoft.Office
{
    public class EnvironmentInfo
    {

        public static string EnvironmentToString()
        {

            string sInfo = "Rizonesoft Office version: " + Application.ProductVersion + "\r\n";
            sInfo += "Time: " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss zzz") + "\r\n";
            sInfo += "Windows Build: " + OSVersion.GetOSVersion().Version.Major + "." + OSVersion.GetOSVersion().Version.Minor + "." + OSVersion.GetOSVersion().Version.Build + "\r\n";
            sInfo += "Windows version: " + OSVersion.GetOperatingSystem() + "\r\n";
            sInfo += "Windows type: " + GetOSType() + "\r\n";
            sInfo += "64-Bit OS: " + OSVersion.Is64BitOperatingSystem;

            if (OSVersion.GetOSVersion().Version.Major >= 10)
            {
                sInfo += "\r\n";
                sInfo += "Windows Release ID: " + OSVersion.MajorVersion10Properties().ReleaseId + "\r\n";
                sInfo += "Windows Update Build Revision: " + OSVersion.MajorVersion10Properties().UBR;
            }

            return sInfo;
        }


        private static string GetOSType()
        {
            if (OSVersion.IsWorkstation == true) 
            {
                return "Workstation";
            }

            if (OSVersion.IsServer == true)
            {
                return "Server";
            }

            return "Unknown";

        }



        public static string ExceptionToString(Exception ex)
        {
            if (ex == null)
            {
                return "null\n";
            }

            string sReport = "";
            sReport += "Exception: " + ex.GetType().ToString() + "\r\n";
            sReport += "Message: " + ex.Message + "\r\n";
            sReport += "Stack:\r\n" + ex.StackTrace + "\r\n";
            if (ex is ExternalException)   // e.g. COMException
            {
                sReport += "ErrorCode: " + (ex as ExternalException).ErrorCode.ToString() + "\r\n";
            }
            if (ex.InnerException != null)
            {
                sReport += "--- InnerException: ---\r\n";
                sReport += ExceptionToString(ex.InnerException);
            }
            return sReport;
        }



    }
}