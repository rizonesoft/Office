using Rizonesoft.Office.EnvironmentEx;
using System;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

namespace Rizonesoft.Office.ExceptionHandlers
{
    public static class ExceptionHandler
    {
        public static string EnvironmentToString()
        {
            WinVersion.GetVersion(out var osInfo);

            string sInfo = $"Rizonesoft Office version: {Application.ProductVersion}\r\n";
            sInfo += $"Framework: {Assembly.GetEntryAssembly()?.GetCustomAttribute<TargetFrameworkAttribute>()?.FrameworkName}\r\n";
            sInfo += $"Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss zzz}\r\n";
            sInfo += $"Windows version: {osInfo.Major}.{osInfo.Minor}.{osInfo.BuildNum}";
            return sInfo;
        }

        public static string ExceptionToString(Exception ex)
        {
            if (ex == null)
            {
                return "null\n";
            }

            string sReport = string.Empty;
            sReport += $"Exception: {ex.GetType()}\r\n";
            sReport += $"Message: {ex.Message}\r\n";
            sReport += $"Stack:\r\n{ex.StackTrace}\r\n";
            if (ex is ExternalException)   // e.g. COMException
            {
                sReport += $"ErrorCode: {(ex as ExternalException).ErrorCode}\r\n";
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
