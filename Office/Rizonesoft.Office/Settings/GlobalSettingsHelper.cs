namespace Rizonesoft.Office.Settings;

/// <summary>
/// Provides helper methods for managing global settings in the Rizonesoft Office application suite.
/// </summary>
public static class GlobalSettingsHelper
{
    private static int? _logRollingIntervalCache;
    private static int? _logFileLimitCache;
    private const OfficeSettings.SettingScope Scope = OfficeSettings.SettingScope.Global;

    /// <summary>
    /// Sets the dark mode setting.
    /// </summary>
    /// <param name="isDarkMode">Whether dark mode should be enabled.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetDarkModeAsync(bool isDarkMode)
    {
        await UpdateAndSaveSettingsAsync(settings => settings.IsDarkMode = isDarkMode).ConfigureAwait(false);
    }

    /// <summary>
    /// Gets the dark mode setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains whether dark mode is enabled.</returns>
    public static async Task<bool> GetDarkModeAsync()
    {
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope).ConfigureAwait(false);
        return settings.IsDarkMode;
    }

    /// <summary>
    /// Sets the language code setting.
    /// </summary>
    /// <param name="languageCode">The language code to set.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetLanguageCodeAsync(string? languageCode)
    {
        await UpdateAndSaveSettingsAsync(settings => settings.LanguageCode = languageCode).ConfigureAwait(false);
    }

    /// <summary>
    /// Gets the language code setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains the language code.</returns>
    public static async Task<string?> GetLanguageCodeAsync()
    {
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope).ConfigureAwait(false);
        return settings.LanguageCode;
    }

    /// <summary>
    /// Sets the log rolling interval setting.
    /// </summary>
    /// <param name="logRollingInterval">The log rolling interval to set.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetLogRollingIntervalAsync(int logRollingInterval)
    {
        await UpdateAndSaveSettingsAsync(settings => settings.LogRollingInterval = logRollingInterval).ConfigureAwait(false);
    }

    /// <summary>
    /// Sets the log rolling interval in memory.
    /// </summary>
    /// <param name="logRollingInterval">The log rolling interval to set.</param>
    public static void SetLogRollingIntervalCache(int logRollingInterval)
    {
        _logRollingIntervalCache = logRollingInterval;
    }

    /// <summary>
    /// Sets the log file limit in memory.
    /// </summary>
    /// <param name="logFileLimit">The log file limit to set.</param>
    public static void SetLogFileLimitCache(int logFileLimit)
    {
        _logFileLimitCache = logFileLimit;
    }

    /// <summary>
    /// Gets the log rolling interval setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains the log rolling interval.</returns>
    public static async Task<int> GetLogRollingIntervalAsync()
    {
        if (_logRollingIntervalCache.HasValue)
        {
            return _logRollingIntervalCache.Value;
        }

        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope).ConfigureAwait(false);
        _logRollingIntervalCache = settings.LogRollingInterval;
        return _logRollingIntervalCache.Value;
    }

    /// <summary>
    /// Gets the log file limit setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains the log file limit.</returns>
    public static async Task<int> GetLogFileLimitAsync()
    {
        if (_logFileLimitCache.HasValue)
        {
            return _logFileLimitCache.Value;
        }

        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope).ConfigureAwait(false);
        _logFileLimitCache = settings.LogFileLimit;
        return _logFileLimitCache.Value;
    }

    /// <summary>
    /// Updates the settings with the provided action and saves them.
    /// </summary>
    /// <param name="updateAction">The action to update the settings.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    private static async Task UpdateAndSaveSettingsAsync(Action<GlobalSettingsData> updateAction)
    {
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope).ConfigureAwait(false);
        updateAction(settings);
        await OfficeSettings.SaveSettingsAsync(settings, Scope).ConfigureAwait(false);
    }
}