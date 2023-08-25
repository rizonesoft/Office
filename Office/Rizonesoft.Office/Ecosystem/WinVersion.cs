using Microsoft.Win32;

namespace Rizonesoft.Office.Ecosystem;

/// <summary>
/// Provides methods to get Windows version information.
/// </summary>
internal static class WinVersion
{
    /// <summary>
    /// Retrieves the version information for the current operating system as a formatted string.
    /// </summary>
    /// <returns>A string representing the version information in the format "Windows [Caption] (Build [BuildNumber])".</returns>
    // public static string GetWindowsVersionString()
    // {
        // var windowsCaption = GetWindowsCaption();
        // var windowsBuildNumber = GetWindowsBuildNumber();

        // return $"{windowsCaption} (Build {windowsBuildNumber})";
    // }

    /// <summary>
    /// Retrieves the Windows caption for the current operating system.
    /// </summary>
    /// <returns>A string representing the Windows caption.</returns>
    // private static string GetWindowsCaption()
    // {
        // var caption = GetWindowsInfoFromWMI("Caption");
        // return !string.IsNullOrEmpty(caption) ? caption : GetWindowsInfoFromRegistry("ProductName");
    // }

    /// <summary>
    /// Retrieves the Windows build number for the current operating system.
    /// </summary>
    /// <returns>A string representing the Windows build number.</returns>
    // private static string GetWindowsBuildNumber()
    // {
        // var buildNumber = GetWindowsInfoFromWMI("BuildNumber");
        // return !string.IsNullOrEmpty(buildNumber) ? buildNumber : GetWindowsInfoFromRegistry("CurrentBuildNumber");
    // }

    // private static string GetWindowsInfoFromWMI(string propertyName)
    // {
        // try
        // {
            // using var searcher = new ManagementObjectSearcher($"SELECT {propertyName} FROM Win32_OperatingSystem");
            // var os = searcher.Get().Cast<ManagementObject>().FirstOrDefault();
            // return os?[propertyName].ToString()?.Replace("Microsoft ", "") ?? "";
        // }
        // catch
        // {
            // return "";
        // }
    // }

    private static string GetWindowsInfoFromRegistry(string valueName)
    {
        using var key = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion");
        return key?.GetValue(valueName)?.ToString() ?? "";
    }
}