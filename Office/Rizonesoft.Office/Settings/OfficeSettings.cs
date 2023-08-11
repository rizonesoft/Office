using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using System.Collections.Concurrent;
using System.IO;
using System.Text.Json;

namespace Rizonesoft.Office.Settings;

/// <summary>
/// Provides methods to load and save settings for Rizonesoft Office applications.
/// </summary>
public static class OfficeSettings
{
    // Maintains a cache of loaded settings to improve performance
    private static readonly ConcurrentDictionary<string, ISettingsData> SettingsCache = new();

    /// <summary>
    /// Specifies the scope of the settings.
    /// </summary>
    public enum SettingScope
    {
        /// <summary>
        /// Program scope for settings that are specific to the individual program.
        /// </summary>
        Program,

        /// <summary>
        /// Global scope for settings that are shared across multiple programs.
        /// </summary>
        Global
    }

    /// <summary>
    /// Asynchronously loads settings based on the specified scope.
    /// </summary>
    /// <typeparam name="T">The type of the settings data.</typeparam>
    /// <param name="scope">The scope of the settings.</param>
    /// <param name="cancellationToken">The token to monitor for cancellation requests.</param>
    /// <returns>A task that represents the asynchronous operation, containing the loaded settings data.</returns>
    public static async Task<T> LoadSettingsAsync<T>(SettingScope scope, CancellationToken cancellationToken = default) where T : ISettingsData, new()
    {
        var settingsFilePath = GetSettingsFilePath(scope);

        if (SettingsCache.TryGetValue(settingsFilePath, out var cachedSettings))
        {
            return (T)cachedSettings;
        }

        var settings = new T();
        try
        {
            if (File.Exists(settingsFilePath))
            {
                var jsonString = await File.ReadAllTextAsync(settingsFilePath, cancellationToken).ConfigureAwait(false);
                settings = JsonSerializer.Deserialize<T>(jsonString) ?? settings;
            }
            else
            {
                throw new FileNotFoundException();
            }
        }
        catch (Exception)
        {
            settings.SetDefaultValues();
        }

        SettingsCache[settingsFilePath] = settings;
        return settings;
    }

    /// <summary>
    /// Asynchronously saves the settings data based on the specified scope.
    /// </summary>
    /// <typeparam name="T">The type of the settings data.</typeparam>
    /// <param name="settings">The settings data to save.</param>
    /// <param name="scope">The scope of the settings.</param>
    /// <param name="cancellationToken">The token to monitor for cancellation requests.</param>
    /// <returns>A task that represents the asynchronous operation.</returns>
    public static async Task SaveSettingsAsync<T>(T settings, SettingScope scope, CancellationToken cancellationToken = default) where T : ISettingsData
    {
        var settingsFilePath = GetSettingsFilePath(scope);
        try
        {
            var jsonString = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(settingsFilePath, jsonString, cancellationToken).ConfigureAwait(false);

            SettingsCache[settingsFilePath] = settings;
        }
        catch (IOException)
        {
            // Handle error and display message or retry operation
            Console.WriteLine(@"Oops! There was a problem saving the settings. Want to give it another shot?");
        }
        catch (JsonException)
        {
            // Handle error and display message or use fallback method
            Console.WriteLine(@"Bummer! Couldn't convert the settings to JSON. Maybe try with simpler settings?");
        }
    }

    /// <summary>
    /// Gets the settings file path based on the scope.
    /// </summary>
    /// <param name="scope">The scope of the settings.</param>
    /// <returns>The settings file path as a string.</returns>
    private static string GetSettingsFilePath(SettingScope scope)
    {
        var settingsFilePath = scope == SettingScope.Program
            ? ProgramConfiguration.SettingsFilePath
            : GlobalConfiguration.SettingsFilePath;

        return settingsFilePath ?? throw new InvalidOperationException(
            "Well, you've got a problem. Your settings file path is not set. Might want to look into that.");
    }
}