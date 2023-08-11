namespace Rizonesoft.Office.Settings;

/// <summary>
/// Provides helper methods for managing global settings in the Rizonesoft Office application suite.
/// </summary>
public static class GlobalSettingsHelper
{
    private static int? _logRollingIntervalCache;
    private static int? _logFileLimitCache;
    private const OfficeSettings.SettingScope Scope = OfficeSettings.SettingScope.Global;

    public static async Task SetLicenseCodeAsync(string? licenseCode, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await UpdateAndSaveSettingsAsync(settings => settings.LicenseCode = licenseCode, cancellationToken).ConfigureAwait(false);
    }

    public static async Task<string?> GetLicenseCodeAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        return settings.LicenseCode;
    }

    /// <summary>
    /// Sets the dark mode setting.
    /// </summary>
    /// <param name="isDarkMode">Whether dark mode should be enabled.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetDarkModeAsync(bool isDarkMode, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await UpdateAndSaveSettingsAsync(settings => settings.IsDarkMode = isDarkMode, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>
    /// Gets the dark mode setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains whether dark mode is enabled.</returns>
    public static async Task<bool> GetDarkModeAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        return settings.IsDarkMode;
    }

    /// <summary>
    /// Sets the language code setting.
    /// </summary>
    /// <param name="languageCode">The language code to set.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetLanguageCodeAsync(string? languageCode, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await UpdateAndSaveSettingsAsync(settings => settings.LanguageCode = languageCode, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>
    /// Gets the language code setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains the language code.</returns>
    public static async Task<string?> GetLanguageCodeAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        return settings.LanguageCode;
    }

    /// <summary>
    /// Sets the log rolling interval setting.
    /// </summary>
    /// <param name="logRollingInterval">The log rolling interval to set.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SetLogRollingIntervalAsync(int logRollingInterval, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await UpdateAndSaveSettingsAsync(settings => settings.LogRollingInterval = logRollingInterval, cancellationToken).ConfigureAwait(false);
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
    public static async Task<int> GetLogRollingIntervalAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (_logRollingIntervalCache.HasValue)
        {
            return _logRollingIntervalCache.Value;
        }

        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        _logRollingIntervalCache = settings.LogRollingInterval;
        return _logRollingIntervalCache.Value;
    }

    /// <summary>
    /// Gets the log file limit setting.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The task result contains the log file limit.</returns>
    public static async Task<int> GetLogFileLimitAsync(CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (_logFileLimitCache.HasValue)
        {
            return _logFileLimitCache.Value;
        }

        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        _logFileLimitCache = settings.LogFileLimit;
        return _logFileLimitCache.Value;
    }

    /// <summary>
    /// Updates the settings with the provided action and saves them.
    /// </summary>
    /// <param name="updateAction">The action to update the settings.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    private static async Task UpdateAndSaveSettingsAsync(Action<GlobalSettingsData> updateAction, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var settings = await OfficeSettings.LoadSettingsAsync<GlobalSettingsData>(Scope, cancellationToken).ConfigureAwait(false);
        updateAction(settings);
        await OfficeSettings.SaveSettingsAsync(settings, Scope, cancellationToken).ConfigureAwait(false);
    }
}