using System.IO;
using System.Reflection;
using System.Xml.Linq;

namespace Rizonesoft.Office;

/// <summary>
/// Manages the retrieval of environment settings from an embedded XML resource.
/// </summary>
public static class EnvironmentManager
{
    private static readonly XDocument EmbeddedConfig;

    /// <summary>
    /// Initializes the <see cref="EnvironmentManager"/> class by loading embedded configuration data.
    /// </summary>
    static EnvironmentManager()
    {
        var xmlContent = GetEmbeddedResource("Rizonesoft.Office.Environment.xml") ?? GetDefaultConfig();
        EmbeddedConfig = XDocument.Parse(xmlContent);
    }

    /// <summary>
    /// Gets the value of a given configuration key.
    /// </summary>
    /// <param name="key">The configuration key.</param>
    /// <returns>The configuration value associated with the given key, or null if not found.</returns>
    public static string? Get(string key)
    {
        var settingsElement = EmbeddedConfig.Root?.Element("settings");

        return settingsElement?.Elements("add")
            .FirstOrDefault(e => e.Attribute("key")?.Value == key)
            ?.Attribute("value")
            ?.Value;
    }

    /// <summary>
    /// Retrieves a boolean configuration value.
    /// </summary>
    /// <param name="key">The configuration key.</param>
    /// <returns>True if the configuration value is 'true', false otherwise.</returns>
    public static bool GetBoolean(string key)
    {
        return bool.TryParse(Get(key), out var result) && result;
    }

    /// <summary>
    /// Gets the embedded XML resource content.
    /// </summary>
    /// <param name="resourceName">The name of the embedded resource.</param>
    /// <returns>Content of the embedded XML resource, or null if not found.</returns>
    private static string? GetEmbeddedResource(string resourceName)
    {
        var assembly = Assembly.GetExecutingAssembly();
        using var resourceStream = assembly.GetManifestResourceStream(resourceName);
        if (resourceStream == null)
        {
            return null;
        }

        using StreamReader reader = new(resourceStream);
        return reader.ReadToEnd();
    }

    /// <summary>
    /// Provides a default XML configuration structure.
    /// </summary>
    /// <returns>Default XML configuration string.</returns>
    private static string GetDefaultConfig()
    {
        return @"
<configuration>
    <settings>
        <add key=""BETA_STRING"" value=""Beta"" />
        <add key=""SYNCFUSION_VER"" value=""1.0.0.0"" />
        <add key=""SYNCFUSION_API"" value=""DEMO"" />
    </settings>
</configuration>".Trim();
    }
}