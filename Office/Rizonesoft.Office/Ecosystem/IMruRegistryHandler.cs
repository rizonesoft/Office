namespace Rizonesoft.Office.Ecosystem;

/// <summary>
/// Interface for classes that handle the registry operations for the Most Recently Used (MRU) list.
/// </summary>
public interface IMruRegistryHandler
{
    /// <summary>
    /// Loads the file paths from the registry.
    /// </summary>
    /// <returns>An array of file paths.</returns>
    string[] LoadFiles();

    /// <summary>
    /// Saves the file paths to the registry.
    /// </summary>
    /// <param name="filePaths">A list of file paths to save.</param>
    void SaveFiles(IReadOnlyList<string> filePaths);
}