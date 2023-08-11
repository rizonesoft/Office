using System.Diagnostics;
using System.IO;
using System.Reflection;

namespace Rizonesoft.Office.Framework;

/// <summary>
/// A static class for configuring global application settings.
/// </summary>
public static class GlobalConfiguration
{

    /// <summary>
    /// The name of the company.
    /// </summary>
    public const string CompanyName = "Rizonesoft";

    private const string SuiteName = "Office";
    private const string LoggerDirectoryName = "Serilogger";
    private const string SettingsFileExtension = ".settings";

    /// <summary>
    /// Gets the path to the global application data directory.
    /// </summary>
    public static string AppDataPath => GetGlobalAppDataPath();

    /// <summary>
    /// Gets the path to the global application registry.
    /// </summary>
    public static string RegistryPath => GetGlobalRegistryPath();

    /// <summary>
    /// Gets the path to the global application settings file.
    /// </summary>
    public static string SettingsFilePath => GetGlobalSettingsFilePath();

    /// <summary>
    /// Gets the global path to the application's log file.
    /// </summary>
    public static string LogFilePath => GetGlobalLogFilePath();

    /// <summary>
    /// Gets the global path to the application's log directory.
    /// </summary>
    public static string LogDirPath => GetGlobalLogDirPath();

    private static string GetGlobalAppDataPath() =>
        Directory.CreateDirectory(
            Path.Join(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                CompanyName, SuiteName)).FullName;

    private static string GetGlobalRegistryPath() => $@"SOFTWARE\{CompanyName}\{SuiteName}";

    private static string GetGlobalSettingsFilePath() =>
        Path.Join(AppDataPath, $"{SuiteName}{SettingsFileExtension}");

    private static string GetGlobalLogFilePath() => Path.Join(AppDataPath, LoggerDirectoryName, $"{SuiteName}.log");

    private static string GetGlobalLogDirPath() => Path.Join(AppDataPath, LoggerDirectoryName);

    private static Assembly OfficeAssembly => Assembly.GetExecutingAssembly();

    private static FileVersionInfo OfficeFileVersionInfo =>
        FileVersionInfo.GetVersionInfo(OfficeAssembly.Location);

    /// <summary>
    /// Gets the name of the product.
    /// </summary>
    public static string? ProductName => OfficeFileVersionInfo.ProductName;

    /// <summary>
    /// Gets the version of the product.
    /// </summary>
    public static string? ProductVersion => OfficeFileVersionInfo.FileVersion;
}