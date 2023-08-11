namespace Rizonesoft.Office.Settings;

/// <summary>
/// Represents the data model for storing Rizonesoft Office global settings.
/// </summary>
public class GlobalSettingsData : ISettingsData
{
    /// <summary>
    /// Initializes a new instance of the <see cref="GlobalSettingsData"/> class.
    /// </summary>
    public GlobalSettingsData()
    {
        SetDefaultValues();
    }

    /// <summary>
    /// Gets or sets the license code for the application.
    /// </summary>
    public string? LicenseCode { get; set; }

    /// <summary>
    /// Gets or sets a value indicating whether the dark mode is enabled.
    /// </summary>
    public bool IsDarkMode { get; set; }

    /// <summary>
    /// Gets or sets the language code for the application.
    /// </summary>
    public string? LanguageCode { get; set; }

    /// <summary>
    /// Gets or sets the rolling interval for log files.
    /// </summary>
    public int LogRollingInterval { get; set; }

    /// <summary>
    /// Gets or sets the limit for the number of log files.
    /// </summary>
    public int LogFileLimit { get; set; }

    // Add other common settings properties here

    /// <summary>
    /// Sets the default values for the settings class.
    /// </summary>
    public void SetDefaultValues()
    {
        LicenseCode = "Unlicensed";
        IsDarkMode = false;
        LanguageCode = "en";
        LogRollingInterval = 3;
        LogFileLimit = 10;
    }

}