using DevExpress.Utils.Svg;
using System.Globalization;

namespace Rizonesoft.Office.Localization;

/// <summary>
/// Represents a language with an associated culture and flag image.
/// </summary>
public class Language
{
    /// <summary>
    /// Gets or sets the CultureInfo associated with this language.
    /// </summary>
    public CultureInfo? CultureInfo { get; }

    /// <summary>
    /// Gets or sets the flag image associated with this language.
    /// </summary>
    public SvgImage? FlagImage { get; }

    /// <summary>
    /// Initializes a new instance of the Language class with the provided culture and flag image.
    /// Throws an ArgumentNullException if either the cultureInfo or flagImage parameter is null.
    /// </summary>
    /// <param name="cultureInfo">The CultureInfo associated with the language (required).</param>
    /// <param name="flagImage">The flag image associated with the language (required).</param>
    public Language(CultureInfo cultureInfo, SvgImage flagImage)
    {
        CultureInfo = cultureInfo ?? throw new ArgumentNullException(nameof(cultureInfo));
        FlagImage = flagImage ?? throw new ArgumentNullException(nameof(flagImage));
    }
}