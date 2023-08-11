using DevExpress.Utils.Svg;
using System.IO;
using System.Reflection;

namespace Rizonesoft.Office.Utilities;

/// <summary>
/// Provides functionality to load SVG images from embedded resources.
/// </summary>
public static class ImageResourceLoader
{
    private static readonly Dictionary<string, string> ExtensionIconMap = new(StringComparer.OrdinalIgnoreCase)
    {
        { ".DOC", "exporttodoc" },
        { ".DOCX", "exporttodocx" },
        { ".RTF", "exporttortf" },
        { ".ODT", "exporttoodt" },
        { ".EPUB", "exporttoepub" },
        { ".TXT", "exporttotxt" },
        { ".PDF", "exporttopdf" },
        { ".XLS", "exporttoxls" },
        { ".XLSX", "exporttoxlsx" },
        { ".CSV", "exporttocsv" },
        { ".HTML", "exporttohtml" },
        { ".MHT", "exporttomht" },
        { ".XML", "exporttoxml" },
        { ".XPS", "exporttoxps" }

    };


    /// <summary>
    /// Loads an SVG image from the specified embedded resource, or returns a default image if the resource is not found.
    /// </summary>
    /// <param name="resourceName">The name of the SVG image resource.</param>
    /// <returns>An SvgImage object containing the loaded image or a default image if the resource is not found.</returns>
    public static SvgImage LoadSvgImageFromResource(string resourceName)
    {
        var assembly = Assembly.GetExecutingAssembly();

        using var stream = assembly.GetManifestResourceStream(resourceName);
        return stream is not null ? SvgImage.FromStream(stream) : CreateDefaultSvgImage();
    }

    /// <summary>
    /// Loads a bitmap image from the specified embedded resource, or returns a default image if the resource is not found.
    /// </summary>
    /// <param name="resourceName">The name of the bitmap image resource.</param>
    /// <returns>A Bitmap object containing the loaded image or a default image if the resource is not found.</returns>
    public static Bitmap LoadImageFromResource(string resourceName)
    {
        var assembly = Assembly.GetExecutingAssembly();

        using var stream = assembly.GetManifestResourceStream(resourceName);
        return stream is not null ? new Bitmap(stream) : CreateDefaultImage();
    }

    /// <summary>
    /// Creates a default SVG image.
    /// </summary>
    /// <returns>A default SvgImage.</returns>
    private static SvgImage CreateDefaultSvgImage()
    {
        const string defaultImageSvgContent = @"<?xml version='1.0' encoding='UTF-8'?>
<svg viewBox=""-4 -4 32 32"" xmlns=""http://www.w3.org/2000/svg"" xmlns:xlink=""http://www.w3.org/1999/xlink"">
  <g id=""Layer_1"" transform=""translate(-4, -4)"" style=""enable-background:new 0 0 32 32"">
    <g id=""Forbid"">
      <path d=""M16, 4C9.4, 4 4, 9.4 4, 16C4, 22.6 9.4, 28 16, 28C22.6, 28 28, 22.6 28, 16C28, 9.4 22.6, 4 16, 4zM16, 8C17.5, 8 18.9, 8.4 20.1, 9.1L9.1, 20.1C8.4, 18.9 8, 17.5 8, 16C8, 11.6 11.6, 8 16, 8zM16, 24C14.5, 24 13.2, 23.6 12, 22.9L22.9, 12C23.6, 13.2 24, 14.5 24, 16C24, 20.4 20.4, 24 16, 24z"" fill=""#D11C1C"" class=""Red"" />
    </g>
  </g>
</svg>";

        using var memoryStream = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(defaultImageSvgContent));
        return SvgImage.FromStream(memoryStream);
    }

    /// <summary>
    /// Creates a default Bitmap image.
    /// </summary>
    /// <param name="width">The width of the default image.</param>
    /// <param name="height">The height of the default image.</param>
    /// <returns>A default Bitmap image.</returns>
    private static Bitmap CreateDefaultImage(int width = 32, int height = 32)
    {
        // Create a blank Bitmap image with the specified width and height
        var blankImage = new Bitmap(width, height);

        // Optionally, you can set a background color for the blank image
        using var graphics = Graphics.FromImage(blankImage);
        graphics.Clear(Color.White);

        return blankImage;
    }

    /// <summary>
    /// Maps a file extension to the corresponding icon URI.
    /// </summary>
    /// <param name="fileExtension">The file extension.</param>
    /// <returns>The icon URI.</returns>
    public static string GetImageUriForExtension(string fileExtension)
    {
        // Check if the file extension is in the dictionary
        return ExtensionIconMap.TryGetValue(fileExtension, out var iconName) ? $"export/{iconName}" : "actions/new";
    }

    /// <summary>
    /// Retrieves the name of the icon corresponding to a given file extension.
    /// </summary>
    /// <param name="fileExtension">The file extension for which an icon name is to be retrieved.</param>
    /// <returns>
    /// The name of the icon corresponding to the given file extension. 
    /// If the file extension is not found in the extension-icon map, returns the name of a default icon ("new").
    /// </returns>
    public static string GetIconForExtension(string fileExtension)
    {
        return ExtensionIconMap.TryGetValue(fileExtension, out var icon) ? icon : "new";
    }

}