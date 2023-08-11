using DevExpress.Utils.Svg;
using System.IO;
using System.Reflection;

namespace Rizonesoft.Office.Programs;

/// <summary>
/// A utility class for managing resources for Rizonesoft Office applications.
/// </summary>
public static class ProgramSvgImage
{
    /// <summary>
    /// Gets the SVG image for a given Rizonesoft Office application from embedded resources.
    /// </summary>
    /// <param name="officeProgram">The Rizonesoft Office application.</param>
    /// <returns>A SvgImage representing the SVG image for the given Rizonesoft Office application.</returns>
    public static SvgImage GetSvgImage(OfficeProgram officeProgram)
    {
        var resourceName = $"Rizonesoft.Office.Programs.Resources.{officeProgram}.svg";
        var assembly = Assembly.GetExecutingAssembly();

        using var stream = assembly.GetManifestResourceStream(resourceName);
        return stream == null
            ? throw new FileNotFoundException($"Resource not found: {resourceName}")
            : SvgImage.FromStream(stream);
    }
}