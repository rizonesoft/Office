using System.Runtime.InteropServices;

namespace Rizonesoft.Office.Ecosystem;

/// <summary>
/// A static helper class that retrieves version information for the current application and its components.
/// </summary>
public static class RuntimeHelper
{
    /// <summary>
    /// Gets the .NET runtime version of the current application.
    /// </summary>
    /// <value>The .NET runtime version as a string.</value>
    public static string RuntimeVersion => GetRuntimeVersion();

    /// <summary>
    /// Retrieves the .NET runtime version.
    /// </summary>
    /// <returns>The .NET runtime version as a string.</returns>
    private static string GetRuntimeVersion()
    {
        return RuntimeInformation.FrameworkDescription;
    }
}