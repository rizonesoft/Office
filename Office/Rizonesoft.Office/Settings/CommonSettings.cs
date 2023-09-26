using DevExpress.Utils;
using DevExpress.XtraEditors;
using System.IO;
using Rizonesoft.Office.ErrorHandling;

namespace Rizonesoft.Office.Settings;

/// <summary>
/// Class that holds the application-wide settings of Rizonesoft Office.
/// </summary>
public static class CommonSettings
{
    private const string DefaultGeometry = "";
    /// <summary>
    /// The default directory used for settings if no other valid directory is provided.
    /// Defaults to the user's Documents directory.
    /// </summary>
    public static readonly string DefaultInitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);

    private const string GeometryRegistryKey = "Geometry";
    private const string InitialOpenDirRegistryKey = "InitialOpenDir";
    private const string InitialSaveDirectoryRegistryKey = "InitialSaveDirectory";
    private const string InitialExportDirRegistryKey = "InitialExportDir";
    private const string InitialImportDirRegistryKey = "InitialImportDir";

    private static readonly RegistrySetting<string> geometry = new(GeometryRegistryKey, DefaultGeometry, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> initialOpenDir = new(InitialOpenDirRegistryKey, DefaultInitialDirectory, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> initialSaveDir = new(InitialSaveDirectoryRegistryKey, DefaultInitialDirectory, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> initialExportDir = new(InitialExportDirRegistryKey, DefaultInitialDirectory, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> initialImportDir = new(InitialImportDirRegistryKey, DefaultInitialDirectory, RegistryOperations.SettingScope.Local);

    public static string Geometry
    {
        get => geometry.Value;
        set => geometry.Value = value;
    }

    public static string InitialOpenDir
    {
        get => GetDirectory(initialOpenDir.Value);
        set => SetDirectory(initialOpenDir, value);
    }

    public static string InitialSaveDirectory
    {
        get => GetDirectory(initialSaveDir.Value);
        set => SetDirectory(initialSaveDir, value);
    }

    public static string InitialExportDir
    {
        get => GetDirectory(initialExportDir.Value);
        set => SetDirectory(initialExportDir, value);
    }

    public static string InitialImportDir
    {
        get => GetDirectory(initialImportDir.Value);
        set => SetDirectory(initialImportDir, value);
    }

    private static string GetDirectory(string directoryValue)
    {
        return Directory.Exists(directoryValue) ? directoryValue : DefaultInitialDirectory;
    }

    private static void SetDirectory(RegistrySetting<string> registrySetting, string directoryValue)
    {
        if (Directory.Exists(directoryValue))
        {
            registrySetting.Value = directoryValue;
        }
        else
        {
            // Log a warning that the provided directory doesn't exist and default to the DefaultDirectory
            Serilogger.LogMessage(LogLevel.Warning, $"Directory '{directoryValue}' does not exist. Defaulting to '{DefaultInitialDirectory}'.");
            registrySetting.Value = DefaultInitialDirectory;
        }
    }
}
