namespace Rizonesoft.Office.Settings;

/// <summary>
/// Class that holds the application-wide settings of Rizonesoft Office.
/// </summary>
public static class CommonSettings
{
    private const string DefaultGeometry = "";
    private const string GeometryRegistryKey = "Geometry";

    /// <summary>
    /// Represents the geometry settings in the registry.
    /// </summary>
    private static readonly RegistrySetting<string> geometry = new(GeometryRegistryKey, DefaultGeometry, RegistryOperations.SettingScope.Local);

    /// <summary>
    /// Gets or sets the geometry value.
    /// </summary>
    public static string Geometry
    {
        get => geometry.Value;
        set => geometry.Value = value;
    }
}