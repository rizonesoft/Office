namespace Rizonesoft.Office.ExceptionHandlers;

using EnvironmentEx;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

internal static class ExceptionHandler
{
    public static string EnvironmentToString()
    {
        WinVersion.GetVersion(out var osInfo);

        var sInfo = $"Rizonesoft Office version: {Application.ProductVersion}\r\n";
        sInfo += $"Framework: {Assembly.GetEntryAssembly()?.GetCustomAttribute<TargetFrameworkAttribute>()?.FrameworkName}\r\n";
        sInfo += $"Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss zzz}\r\n";
        sInfo += $"Windows version: {osInfo.Major}.{osInfo.Minor}.{osInfo.BuildNum}";
        return sInfo;
    }

    public static string ExceptionToString(Exception? ex)
    {
        if (ex == null) return "null\n";
        var sReport = string.Empty;
        sReport += $"Exception: {ex.GetType()}\r\n";
        sReport += $"Message: {ex.Message}\r\n";
        sReport += $"Stack:\r\n{ex.StackTrace}\r\n";
        if (ex is ExternalException exception) // e.g. COMException
        {
            sReport += $"ErrorCode: {exception.ErrorCode}\r\n";
        }

        if (ex.InnerException == null) return sReport;
        sReport += "--- InnerException: ---\r\n";
        sReport += ExceptionToString(ex.InnerException);
        return sReport;
    }

}