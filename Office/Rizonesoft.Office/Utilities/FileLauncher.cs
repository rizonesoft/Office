using Rizonesoft.Office.ErrorHandling;
using System.Diagnostics;
using System.IO;

namespace Rizonesoft.Office.Utilities;

/// <summary>
/// A utility class to open files and URLs with their default programs.
/// </summary>
public static class FileLauncher
{
    /// <summary>
    /// Opens a URL in the default web browser.
    /// </summary>
    /// <param name="url">The URL to open.</param>
    /// <exception cref="ArgumentException">Thrown when the URL is null, empty, or only contains whitespace.</exception>
    public static void OpenLinkInBrowser(string url)
    {
        if (string.IsNullOrWhiteSpace(url))
        {
            throw new ArgumentException(@"URL cannot be null or empty.", nameof(url));
        }

        ExecuteProcess(url);
    }

    /// <summary>
    /// Executes an executable with arguments.
    /// </summary>
    /// <param name="executablePath">The path to the executable file.</param>
    /// <param name="arguments">The command-line arguments to pass to the executable.</param>
    /// <exception cref="ArgumentException">Thrown when the executable path is null, empty, or only contains whitespace.</exception>
    public static void RunExecutable(string executablePath, string arguments = "")
    {
        if (string.IsNullOrWhiteSpace(executablePath))
        {
            throw new ArgumentException(@"Executable path cannot be null or empty.", nameof(executablePath));
        }

        ExecuteProcess(executablePath, arguments);
    }

    /// <summary>
    /// Opens a PDF in the Scholar application.
    /// </summary>
    /// <param name="pdfPath">The path to the PDF file.</param>
    /// <exception cref="ArgumentException">Thrown when the PDF path is null, empty, or only contains whitespace.</exception>
    /// <exception cref="FileNotFoundException">Thrown when the Scholar executable or the PDF file is not found.</exception>
    public static void OpenPdfInScholar(string pdfPath)
    {
        if (string.IsNullOrWhiteSpace(pdfPath))
        {
            throw new ArgumentException(@"PDF path cannot be null or empty.", nameof(pdfPath));
        }

        if (!Path.GetExtension(pdfPath).Equals(".pdf", StringComparison.OrdinalIgnoreCase))
        {
            throw new ArgumentException(@"Invalid file type. Please provide a PDF file.", nameof(pdfPath));
        }

        var baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
        var scholarPath = Path.Combine(baseDirectory, "Scholar.exe");

        if (!File.Exists(scholarPath))
        {
            throw new FileNotFoundException($"Scholar application not found in the base directory: {baseDirectory}", nameof(scholarPath));
        }

        if (!File.Exists(pdfPath))
        {
            throw new FileNotFoundException($"PDF file not found: {pdfPath}", nameof(pdfPath));
        }

        ExecuteProcess(scholarPath, $"\"{pdfPath}\"");
    }


    /// <summary>
    /// Opens a PDF in the default PDF viewer.
    /// </summary>
    /// <param name="pdfPath">The path to the PDF file.</param>
    /// <exception cref="ArgumentException">Thrown when the PDF path is null, empty, or only contains whitespace, or when the file is not a PDF file.</exception>
    public static void OpenPdfInDefaultViewer(string pdfPath)
    {
        if (string.IsNullOrWhiteSpace(pdfPath))
        {
            throw new ArgumentException(@"PDF path cannot be null or empty.", nameof(pdfPath));
        }

        if (!Path.GetExtension(pdfPath).Equals(".pdf", StringComparison.OrdinalIgnoreCase))
        {
            throw new ArgumentException(@"Invalid file type. Please provide a PDF file.", nameof(pdfPath));
        }

        ExecuteProcess(pdfPath);
    }

    /// <summary>
    /// Executes a process with the specified path and arguments.
    /// </summary>
    /// <param name="path">The path to the executable or file.</param>
    /// <param name="arguments">The arguments to pass to the executable, if any.</param>
    public static void ExecuteProcess(string path, string arguments = "")
    {
        try
        {
            Process.Start(new ProcessStartInfo(path, arguments) { UseShellExecute = true });
        }
        catch (Exception ex) when (ex is FileNotFoundException)
        {
            Serilogger.LogMessage(LogLevel.Error, $"File not found: {ex.Message}", ex);
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, $"Error executing process: {ex.Message}", ex);
        }
    }
}