using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Toast;
using System.Diagnostics;
using System.IO;
using Rizonesoft.Office.Settings;

// Disable "Missing XML comments for publicly visible types or members." warning.
#pragma warning disable CS1591


namespace Rizonesoft.Office.Programs;

/// <summary>
/// A static class for configuring application settings and visual styles.
/// </summary>
public static class ProgramConfiguration
{
    public const string CompanyName = "Rizonesoft";
    public const string SuiteName = "Office";

    public static string? ProgramName { get; private set; }
    public static string? AppDataPath { get; private set; }
    public static string? RegistryPath { get; private set; }
    public static string? SettingsFilePath { get; private set; }
    public static string? LogFilePath { get; private set; }
    public static string? ExecutablePath { get; private set; }
    public static string? DictionariesPath { get; private set; }
    public static string? CustomDictionariesPath { get; private set; }
    public static (int major, int minor, int build, int revision, string? fullVersion)? Version { get; private set; }

    /// <summary>
    /// Configures the application settings and visual styles.
    /// </summary>
    /// <param name="programName">The name of the program.</param>
    public static void Configure(OfficeProgram programName)
    {
        UnhandledExceptionHandler.Register(true);

        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.SetHighDpiMode(GetOptimalHighDpiMode());

        var sSkin = GlobalSettings.SkinName;
        var sPalette = GlobalSettings.Palette;
        WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        WindowsFormsSettings.TrackWindowsAccentColor = GlobalSettings.TrackWindowsAccentColor ?
            DevExpress.Utils.DefaultBoolean.True :
            DevExpress.Utils.DefaultBoolean.False;
        
        XtraMessageBox.SmartTextWrap = true;

        var languageCode = Task.Run(LanguageManager.GetLanguageCodeAsync).Result;
        LanguageManager.SetCultureInfo(languageCode);
        InitializeSettings(programName.ToString());
        LoadSettings();
        EnsureAppDataPathExists();
    }

    private static void LoadSettings()
    {
        
    }

    private static void InitializeSettings(string programName)
    {
        ProgramName = programName;
        AppDataPath = GetAppDataPath();
        RegistryPath = GetRegistryPath();
        SettingsFilePath = GetSettingsFilePath();
        LogFilePath = GetLogFilePath();
        ExecutablePath = GetExecutablePath(programName);
        DictionariesPath = GetDictionariesPath();
        CustomDictionariesPath = GetCustomDictionariesPath();
        Version = GetVersion();
    }

    private static HighDpiMode GetOptimalHighDpiMode()
    {
        return !SystemInformation.TerminalServerSession && Screen.AllScreens.Length > 1
            ? HighDpiMode.PerMonitorV2
            : HighDpiMode.SystemAware;
    }

    private static void EnsureAppDataPathExists()
    {
        try
        {
            if (AppDataPath != null) Directory.CreateDirectory(AppDataPath);
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while loading program configuration.", ex);
            ToastHelper.CreateErrorToast(Strings.Toast_AppDataPathError_Header, Strings.Toast_AppDataPathError);
        }
    }

    private static string GetAppDataPath()
    {
        var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);

        if (ProgramName == null)
        {
            throw new InvalidOperationException("Program name is not set.");
        }

        var path = Path.Combine(localAppData, CompanyName, SuiteName, ProgramName);
        return path;
    }

    private static string GetRegistryPath()
    {
        if (ProgramName == null)
        {
            throw new InvalidOperationException("Program name is not set.");
        }

        return $@"SOFTWARE\{CompanyName}\{SuiteName}\{ProgramName}";
    }

    private static string GetSettingsFilePath()
    {
        if (AppDataPath == null || ProgramName == null)
        {
            throw new InvalidOperationException("AppDataPath or ProgramName is not set.");
        }

        return Path.Combine(AppDataPath, $"{ProgramName}.settings");
    }

    private static string GetLogFilePath()
    {
        if (AppDataPath == null || ProgramName == null)
        {
            throw new InvalidOperationException("AppDataPath or ProgramName is not set.");
        }

        return Path.Combine(AppDataPath, "Logger", $"{ProgramName}.log");
    }

    private static string GetExecutablePath(string programName)
    {
        var exeName = $"{programName}.exe";
        var exePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, exeName);

        if (!File.Exists(exePath))
        {
            throw new FileNotFoundException("Executable file not found.", exeName);
        }

        return exePath;
    }

    private static string GetDictionariesPath()
    {
        var startupPath = AppDomain.CurrentDomain.BaseDirectory;
        return Path.Combine(startupPath, "Dictionaries");
    }

    private static string GetCustomDictionariesPath()
    {
        if (AppDataPath == null)
        {
            throw new InvalidOperationException("AppDataPath is not set.");
        }

        return Path.Combine(AppDataPath, "Dictionaries");
    }

    public static (int major, int minor, int build, int revision, string? fullVersion) GetVersion()
    {
        if (ExecutablePath == null)
        {
            throw new InvalidOperationException("ExecutablePath is not set.");
        }

        var versionInfo = FileVersionInfo.GetVersionInfo(ExecutablePath);

        return (versionInfo.FileMajorPart, versionInfo.FileMinorPart,
            versionInfo.FileBuildPart, versionInfo.FilePrivatePart, versionInfo.FileVersion);
    }

}