// ReSharper disable InconsistentNaming
namespace Rizonesoft.Office.Settings.ProgramSettings;

/// <summary>
/// Class that holds the application-wide settings of Rizonesoft Office.
/// </summary>
public static class ScholarSettings
{
    // DEFAULT CONSTANTS
    // General export options
    private const bool DefaultPreserveFonts = true;
    private const bool DefaultPreserveImages = true;
    private const bool DefaultPreserveGraphics = true;
    private const bool DefaultInsertCopyright = false;
    private const string DefaultCopyright = "© 2023 Rizonesoft";
    // Export to Docx Options
    private const int DefaultPdfRenderMode = 2; // Default to Continuous
    private const bool DefaultDocxDetectTables = true;
    private const bool DefaultDocxShowInvisibleText = false;
    private const bool DefaultDocxKeepCharacterScale = false;
    // Export to Xls Options
    private const bool DefaultXlsConvertNonTabularData = true;
    private const bool DefaultPreservePageLayout = true;
    private const string DefaultNumDecimalSeparator = ".";
    private const string DefaultNumGroupSeparator = ",";
    // Export to Image Options
    private const bool DefaultImageAutoSize = true;
    private const decimal DefaultImageDpi = 300;
    private const decimal DefaultImageWidth = 800;
    private const decimal DefaultImageHeight = 600;
    private const int DefaultImageColorDepthIndex = 2;  // default to "RGB (24 Bits)"
    private const int DefaultJpegQuality = 8; // Default to 80%
    // Export to Html Options
    private const string DefaultHtmlTitle = "Converted by Rizonesoft Office";  // Set the default title as needed
    private const int DefaultHtmlRenderMode = 0;  // 0 for Fixed, 1 for Flowing
    private const bool DefaultHtmlKeepCharScale = false;
    private const bool DefaultHtmlEmbedImages = true;
    private const int DefaultHtmlImageFormat = 0;  // 0 for JPG, 1 for PNG
    // Export to Xml Options
    private const bool DefaultXmlConvertNonTabularData = true;
    private const int DefaultNavigationPaneWidth = 400;
    
    // REGISTRY KEYS
    // General export options
    private const string InsertCopyrightRegistryKey = "InsertCopyright";
    private const string PreserveFontsRegistryKey = "PreserveFonts";
    private const string PreserveImagesRegistryKey = "PreserveImages";
    private const string PreserveGraphicsRegistryKey = "PreserveGraphics";
    private const string CopyrightRegistryKey = "DefaultCopyright";
    // Export to Docx Options
    private const string PdfRenderModeRegistryKey = "PdfRenderMode";
    private const string DocxDetectTablesRegistryKey = "DocxDetectTables";
    private const string DocxShowInvisibleTextRegistryKey = "DocxShowInvisibleText";
    private const string DocxKeepCharacterScaleRegistryKey = "DocxKeepCharacterScale";
    // Export to Xls Options
    private const string XlsConvertNonTabularDataRegistryKey = "XlsConvertTabularData";
    private const string PreservePageLayoutRegistryKey = "PreservePageLayout";
    private const string NumDecimalSeparatorRegistryKey = "NumDecimalSeparator";
    private const string NumGroupSeparatorRegistryKey = "NumGroupSeparator";
    // Export to Image Options
    private const string ImageAutoSizeRegistryKey = "ImageExportAutoSize";
    private const string ImageDpiRegistryKey = "ImageExportDpi";
    private const string ImageWidthRegistryKey = "ImageExportWidth";
    private const string ImageHeightRegistryKey = "ImageExportHeight";
    private const string ImageColorDepthIndexRegistryKey = "ImageExportColorDepthIndex";
    private const string JpegQualityRegistryKey = "ImageExportJpegQuality";
    // Export to Html Options
    private const string HtmlTitleRegistryKey = "HtmlTitle";
    private const string HtmlRenderModeRegistryKey = "HtmlRenderMode";
    private const string HtmlKeepCharScaleRegistryKey = "HtmlKeepCharScale";
    private const string HtmlEmbedImagesRegistryKey = "HtmlEmbedImages";
    private const string HtmlImageFormatRegistryKey = "HtmlImageFormat";
    // Export to Xml Options
    private const string XmlConvertNonTabularDataRegistryKey = "XmlConvertTabularData";
    // UI Options
    private const string NavigationPaneWidthRegistryKey = "NavigationPaneWidth";

    // REGISTRY SETTINGS
    // General export options
    private static readonly RegistrySetting<bool> insertCopyright = new(InsertCopyrightRegistryKey, DefaultInsertCopyright, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> preserveFonts = new(PreserveFontsRegistryKey, DefaultPreserveFonts, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> preserveImages = new(PreserveImagesRegistryKey, DefaultPreserveImages, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> preserveGraphics = new(PreserveGraphicsRegistryKey, DefaultPreserveGraphics, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> copyRight = new(CopyrightRegistryKey, DefaultCopyright, RegistryOperations.SettingScope.Local);
    // Export to Docx Options
    private static readonly RegistrySetting<int> pdfRenderMode = new(PdfRenderModeRegistryKey, DefaultPdfRenderMode, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> docxDetectTables = new(DocxDetectTablesRegistryKey, DefaultDocxDetectTables, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> docxShowInvisibleText = new(DocxShowInvisibleTextRegistryKey, DefaultDocxShowInvisibleText, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> docxKeepCharacterScale = new(DocxKeepCharacterScaleRegistryKey, DefaultDocxKeepCharacterScale, RegistryOperations.SettingScope.Local);
    // Export to Xls Options
    private static readonly RegistrySetting<bool> xlsConvertNonTabularData = new(XlsConvertNonTabularDataRegistryKey, DefaultXlsConvertNonTabularData, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> preservePageLayout = new(PreservePageLayoutRegistryKey, DefaultPreservePageLayout, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> numDecimalSeparator = new(NumDecimalSeparatorRegistryKey, DefaultNumDecimalSeparator, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<string> numGroupSeparator = new(NumGroupSeparatorRegistryKey, DefaultNumGroupSeparator, RegistryOperations.SettingScope.Local);
    // Export to Image Options
    private static readonly RegistrySetting<bool> imageAutoSize = new(ImageAutoSizeRegistryKey, DefaultImageAutoSize, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<decimal> imageDpi = new(ImageDpiRegistryKey, DefaultImageDpi, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<decimal> imageWidth = new(ImageWidthRegistryKey, DefaultImageWidth, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<decimal> imageHeight = new(ImageHeightRegistryKey, DefaultImageHeight, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<int> imageColorDepthIndex = new(ImageColorDepthIndexRegistryKey, DefaultImageColorDepthIndex, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<int> jpegQuality = new(JpegQualityRegistryKey, DefaultJpegQuality, RegistryOperations.SettingScope.Local);
    // Export to Html Options
    private static readonly RegistrySetting<string> htmlTitle = new(HtmlTitleRegistryKey, DefaultHtmlTitle, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<int> htmlRenderMode = new(HtmlRenderModeRegistryKey, DefaultHtmlRenderMode, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> htmlKeepCharScale = new(HtmlKeepCharScaleRegistryKey, DefaultHtmlKeepCharScale, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<bool> htmlEmbedImages = new(HtmlEmbedImagesRegistryKey, DefaultHtmlEmbedImages, RegistryOperations.SettingScope.Local);
    private static readonly RegistrySetting<int> htmlImageFormat = new(HtmlImageFormatRegistryKey, DefaultHtmlImageFormat, RegistryOperations.SettingScope.Local);
    // Export to Xml Options
    private static readonly RegistrySetting<bool> xmlConvertNonTabularData = new(XmlConvertNonTabularDataRegistryKey, DefaultXmlConvertNonTabularData, RegistryOperations.SettingScope.Local);
    // UI Options
    private static readonly RegistrySetting<int> navigationPaneWidth = new(NavigationPaneWidthRegistryKey, DefaultNavigationPaneWidth, RegistryOperations.SettingScope.Local);


    // PROPERTIES

    // General export options

    /// <summary>
    /// Gets or sets a value indicating whether to insert a copyright notice.
    /// </summary>
    public static bool InsertCopyright
    {
        get => insertCopyright.Value;
        set => insertCopyright.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to preserve fonts during export.
    /// </summary>
    public static bool PreserveFonts
    {
        get => preserveFonts.Value;
        set => preserveFonts.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to preserve images during export.
    /// </summary>
    public static bool PreserveImages
    {
        get => preserveImages.Value;
        set => preserveImages.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to preserve graphics during export.
    /// </summary>
    public static bool PreserveGraphics
    {
        get => preserveGraphics.Value;
        set => preserveGraphics.Value = value;
    }

    /// <summary>
    /// Gets or sets the default copyright text.
    /// </summary>
    public static string Copyright
    {
        get => copyRight.Value;
        set => copyRight.Value = value;
    }

    // Export to Docx Options

    /// <summary>
    /// Gets or sets the PDF rendering mode.
    /// </summary>
    public static int PdfRenderMode
    {
        get => pdfRenderMode.Value;
        set => pdfRenderMode.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to detect tables when exporting to DOCX.
    /// </summary>
    public static bool DocxDetectTables
    {
        get => docxDetectTables.Value;
        set => docxDetectTables.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to show invisible text when exporting to DOCX.
    /// </summary>
    public static bool DocxShowInvisibleText
    {
        get => docxShowInvisibleText.Value;
        set => docxShowInvisibleText.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to keep character scale when exporting to DOCX.
    /// </summary>
    public static bool DocxKeepCharacterScale
    {
        get => docxKeepCharacterScale.Value;
        set => docxKeepCharacterScale.Value = value;
    }

    // Export to Xls Options

    /// <summary>
    /// Gets or sets a value indicating whether to convert non-tabular data when exporting to XLS.
    /// </summary>
    public static bool XlsConvertNonTabularData
    {
        get => xlsConvertNonTabularData.Value;
        set => xlsConvertNonTabularData.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to preserve page layout when exporting.
    /// </summary>
    public static bool PreservePageLayout
    {
        get => preservePageLayout.Value;
        set => preservePageLayout.Value = value;
    }

    /// <summary>
    /// Gets or sets the decimal separator for numbers.
    /// </summary>
    public static string NumDecimalSeparator
    {
        get => numDecimalSeparator.Value;
        set => numDecimalSeparator.Value = value;
    }

    /// <summary>
    /// Gets or sets the group separator for numbers.
    /// </summary>
    public static string NumGroupSeparator
    {
        get => numGroupSeparator.Value;
        set => numGroupSeparator.Value = value;
    }

    // Export to Image Options

    /// <summary>
    /// Gets or sets a value indicating whether to auto-size images during export.
    /// </summary>
    public static bool ImageAutoSize
    {
        get => imageAutoSize.Value;
        set => imageAutoSize.Value = value;
    }

    /// <summary>
    /// Gets or sets the DPI setting for exported images.
    /// </summary>
    public static decimal ImageDpi
    {
        get => imageDpi.Value;
        set => imageDpi.Value = value;
    }

    /// <summary>
    /// Gets or sets the default width for exported images.
    /// </summary>
    public static decimal ImageWidth
    {
        get => imageWidth.Value;
        set => imageWidth.Value = value;
    }

    /// <summary>
    /// Gets or sets the default height for exported images.
    /// </summary>
    public static decimal ImageHeight
    {
        get => imageHeight.Value;
        set => imageHeight.Value = value;
    }

    /// <summary>
    /// Gets or sets the color depth setting for exported images based on the index value.
    /// </summary>
    public static int ImageColorDepthIndex
    {
        get => imageColorDepthIndex.Value;
        set => imageColorDepthIndex.Value = value;
    }

    /// <summary>
    /// Gets or sets the JPEG quality setting for exported images.
    /// </summary>
    public static int JpegQuality
    {
        get => jpegQuality.Value;
        set => jpegQuality.Value = value;
    }

    // Export to Html Options

    /// <summary>
    /// Gets or sets the default title for exported HTML files.
    /// </summary>
    public static string HtmlTitle
    {
        get => htmlTitle.Value;
        set => htmlTitle.Value = value;
    }

    /// <summary>
    /// Gets or sets the rendering mode for exported HTML files.
    /// </summary>
    public static int HtmlRenderMode
    {
        get => htmlRenderMode.Value;
        set => htmlRenderMode.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to keep character scale when exporting to HTML.
    /// </summary>
    public static bool HtmlKeepCharScale
    {
        get => htmlKeepCharScale.Value;
        set => htmlKeepCharScale.Value = value;
    }

    /// <summary>
    /// Gets or sets a value indicating whether to embed images when exporting to HTML.
    /// </summary>
    public static bool HtmlEmbedImages
    {
        get => htmlEmbedImages.Value;
        set => htmlEmbedImages.Value = value;
    }

    /// <summary>
    /// Gets or sets the image format for exported HTML files.
    /// </summary>
    public static int HtmlImageFormat
    {
        get => htmlImageFormat.Value;
        set => htmlImageFormat.Value = value;
    }

    // Export to Xml Options

    /// <summary>
    /// Gets or sets a value indicating whether to convert non-tabular data during XML export.
    /// </summary>
    public static bool XmlConvertNonTabularData
    {
        get => xmlConvertNonTabularData.Value;
        set => xmlConvertNonTabularData.Value = value;
    }

    // UI Options

    /// <summary>
    /// Gets or sets the width of the navigation pane.
    /// </summary>
    public static int NavigationPaneWidth
    {
        get => navigationPaneWidth.Value;
        set => navigationPaneWidth.Value = value;
    }


}
