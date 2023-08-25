using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.Programs;
using System.Runtime.InteropServices;
using System.Text;

namespace Rizonesoft.Office.ErrorHandling;

/// <summary>
/// ExceptionHandler provides utility methods for obtaining environment information and formatting exception details.
/// </summary>
internal static class ExceptionHandler
{
    /// <summary>
    /// Converts an Exception object to a formatted string, including its inner exceptions.
    /// </summary>
    /// <param name="ex">The exception to convert.</param>
    /// <returns>A formatted string with the exception details or null if the exception object is null.</returns>
    public static string? ExceptionToString(Exception? ex)
    {
        if (ex == null)
        {
            return null;
        }

        var timestamp = DateTime.UtcNow;
        // var windowsVersion = WinVersion.GetWindowsVersionString();
        var appDomain = AppDomain.CurrentDomain.FriendlyName;
        var appVersion = ProgramConfiguration.Version?.fullVersion ?? "Unknown";

        var sReport = new StringBuilder();
        sReport.AppendLine($"Timestamp: {timestamp}");
        // sReport.AppendLine($"Windows Version: {windowsVersion}");
        sReport.AppendLine($"Domain: {appDomain}");
        sReport.AppendLine($"Program Version: {appVersion}");
        sReport.AppendLine($"Exception: {ex.GetType()}");
        sReport.AppendLine($"Message: {ex.Message}");
        sReport.AppendLine("Stack:");
        sReport.AppendLine(ex.StackTrace);

        if (ex is ExternalException exception) // e.g. COMException
        {
            sReport.AppendLine($"ErrorCode: {exception.ErrorCode}");
        }

        if (ex.InnerException == null) return sReport.ToString();
        sReport.AppendLine("--- InnerException: ---");
        sReport.AppendLine(ex.InnerException.ToString());

        return sReport.ToString();
    }
}