using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using DevExpress.Utils;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using DevExpress.XtraTabbedMdi;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Scholar.Classes;
using Rizonesoft.Office.Scholar.Forms;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.UI.Ribbon;
using Rizonesoft.Office.Utilities;
using SautinSoft;
using Syncfusion.Pdf;
using Syncfusion.Pdf.Parsing;

namespace Rizonesoft.Office.Scholar;

/// <summary>
///     Represents the main form of the Scholar application.
/// </summary>
public sealed partial class MainForm : RibbonFormBase
{
    private readonly CopyData copyData;
    private int viewerIndex;
    private static MruList _mruList;
    private readonly SvgImageCollection extensionsSvgImages;
    private Dictionary<string, Action<string>> exportActions;

    [SuppressMessage("ReSharper", "InconsistentNaming")]
    public enum ExportType
    {
        DOCX,
        XLS,
        Image,
        HTML,
        XML,
        TXT
    }

    private DocForm CurrentDocument
    {
        get
        {
            if (ActiveMdiChild == null) return null;
            if (mainMdiManager.ActiveFloatForm != null) return mainMdiManager.ActiveFloatForm as DocForm;

            return ActiveMdiChild as DocForm;
        }
    }

    private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
    {
        if (e.ChannelName != null && !e.ChannelName.Equals("DocChannel")) return;
        if (WindowState == FormWindowState.Minimized) WindowState = FormWindowState.Normal;

        var fileName = (string)e.Data;
        CreateNewViewer(fileName);
        AddFileToMruList(fileName);
        Activate();

        // MessageBox.Show(@"Eureka! We've struck data! Filename: " + fileName);
    }

    /// <summary>
    ///     Initializes a new instance of the MainForm class.
    /// </summary>
    public MainForm(string fileName)
    {
        SplashScreenHelper.ShowSplashScreen(this);

        copyData = new CopyData();
        copyData.AssignHandle(Handle);
        copyData.Channels?.Add("DocChannel");
        copyData.DataReceived += CopyData_DataReceived;

        extensionsSvgImages = new SvgImageCollection();
        InitializeSvgImages();

        InitializeComponent();
        AfterInitializeComponents();

        InitializeRibbon();
        exportDropDown.DefaultDropDownLink = exportPopupMenu.ItemLinks[0];
        SetupEventHandlers();
        PopulateExportActions();
        UpdateUi();

        ControlConfig.SetDefaultMdiManagerConfig(mainMdiManager, this);
        CreateNewViewer(fileName);
    }

    private void SetupEventHandlers()
    {
        AttachExportHandlers(exportDocxItem, exportXlsItem, exportImageItem, exportHtmlItem, exportXmlItem, exportTextItem);
    }

    protected override void OnClosed(EventArgs e)
    {
        base.OnClosed(e);
        SaveSettings();
    }

    private void UpdateUi()
    {
        HomeRibbonPage.Text = Strings.RibbonMain_Home;
        ToolsRibbonPage.Text = Strings.RibbonMain_Tools;
    }

    public static void AddFileToMruList(string fileName)
    {
        if (string.IsNullOrEmpty(fileName)) return;
        try
        {
            _mruList?.AddFile(fileName);
        }
        catch (Exception ioEx)
        {
            Serilogger.LogMessage(LogLevel.Warning, "The file could not be found.", ioEx);
        }
    }

    private void InitializeSvgImages()
    {
        extensionsSvgImages.Add("exporttopdf", "image://svgimages/export/exporttopdf.svg");
        extensionsSvgImages.Add("new", "image://svgimages/actions/new.svg");
    }

    private void CreateNewViewer(string fileName)
    {
        if (!string.IsNullOrEmpty(fileName))
            foreach (var openForm in MdiChildren.Cast<DocForm>())
            {
                if (string.Compare(openForm.FileName, fileName, StringComparison.OrdinalIgnoreCase) != 0) continue;
                openForm.Activate();
                return;
            }
        else
            viewerIndex++;

        DocForm newViewer = new()
        {
            MdiParent = this
        };
        newViewer.OpenFile(fileName, viewerIndex);
        newViewer.Show();
    }

    private void OpenFile(string fileName)
    {
        CreateNewViewer(fileName);
    }

    private void OpenFileFolder()
    {
        var openFileDlg = new OpenFileDialog
        {
            Filter = Strings.OpenFileFolder_Filter,
            FilterIndex = 1,
            Title = Strings.OpenFileFolder_Title,
            CheckFileExists = true,
            CheckPathExists = true,
            Multiselect = false,
            SupportMultiDottedExtensions = true,
            ValidateNames = true,
            RestoreDirectory = true,
            AddExtension = true,
            DefaultExt = "pdf",
            InitialDirectory = CommonSettings.InitialOpenDir
        };
        var dlgResult = openFileDlg.ShowDialog();

        // Show the dialog and get result.
        if (dlgResult != DialogResult.OK) return;
        var fileName = openFileDlg.FileName;

        AddFileToMruList(fileName);
        CommonSettings.InitialOpenDir = Path.GetDirectoryName(fileName) ?? CommonSettings.DefaultInitialDirectory;
        OpenFile(fileName);
    }

    private void InitializeRibbon()
    {
        ribbonMain.ForceInitialize();
        _ = new RibbonGroupOptions(this, ribbonMain, OptionsRibbonGroup)
        {
            IsLanguageDropdownVisible = false
        };
        _ = new RibbonPageSupport(ribbonMain);
    }

    private void MainForm_Shown(object sender, EventArgs e)
    {
        SplashScreenHelper.CloseSplashScreen();
    }

    private void MainForm_Load(object sender, EventArgs e)
    {
        FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
        ribbonMain.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");

        try
        {
            if (ProgramConfiguration.SettingsFilePath != null)
            {
                _mruList = new MruList(mruPopupMenu, 10, new MruRegistryHandler());
                _mruList.Initialize();
                _mruList.FileSelected += MruList_FileSelected;
            }
        }
        catch (Exception ex)
        {
            // Handle or log the exception here.
            Console.WriteLine(ex.Message);
        }
    }

    private void SaveSettings()
    {
        CommonSettings.Geometry = FormGeometry.GeometryToString(this);
        ribbonMain.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
    }

    private void SaveRibbon()
    {
    }

    private void MruList_FileSelected(string fileName)
    {
        OpenFile(fileName);
    }

    private void OpenBarItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        OpenFileFolder();
    }

    private void CompressBarButton_ItemClick(object sender, ItemClickEventArgs e)
    {
        var inputFile = File.ReadAllBytes(CurrentDocument.FileName);

        var ldoc = new PdfLoadedDocument(inputFile);
        var options = new PdfCompressionOptions();

        options.CompressImages = true;
        options.ImageQuality = 8;
        options.OptimizeFont = true;
        options.OptimizePageContents = true;
        options.RemoveMetadata = true;

        ldoc.CompressionOptions = options;

        using (var ms = new MemoryStream())
        {
            ldoc.Save(ms);

            // Show "Save As" dialog to allow the user to choose the save location and file name.
            var saveFileDialog = new SaveFileDialog();
            saveFileDialog.Filter = "PDF files (*.pdf)|*.pdf|All files (*.*)|*.*";
            saveFileDialog.FileName = "compressed_" + Path.GetFileName(CurrentDocument.FileName);

            if (saveFileDialog.ShowDialog() == DialogResult.OK)
            {
                // Save the compressed PDF to the selected file path.
                File.WriteAllBytes(saveFileDialog.FileName, ms.ToArray());
                MessageBox.Show("Compression complete. File saved to: " + saveFileDialog.FileName);
            }
        }
    }

    private void MainMdiManager_PageAdded(object sender, MdiTabPageEventArgs e)
    {
        if (e.Page.MdiChild is DocForm docForm) docForm.FileNameChanged += DocForm_FileNameChanged;
    }

    private void DocForm_FileNameChanged(object sender, EventArgs e)
    {
        if (sender is DocForm childDocForm) UpdateTabImageForBookForm(childDocForm);
    }

    private void UpdateTabImageForBookForm(DocForm childDocForm)
    {
        if (childDocForm == null) return;

        var fileName = childDocForm.FileName;
        var extension = Path.GetExtension(fileName);
        var tabPage = mainMdiManager.Pages[childDocForm];

        if (tabPage == null) return;
        if (!string.IsNullOrWhiteSpace(extension))
        {
            var svgImage = ImageResourceLoader.GetIconForExtension(extension);
            tabPage.ImageOptions.SvgImage = extensionsSvgImages[svgImage];
        }
        else
        {
            tabPage.ImageOptions.SvgImage = extensionsSvgImages["new"];
        }

        tabPage.ImageOptions.SvgImageSize = new Size(24, 24);
    }


    #region EXPORT (CONVERT)

    private void AttachExportHandlers(params BarButtonItem[] items)
    {
        foreach (var item in items) item.ItemClick += ExportBarButton_ItemClick;
    }

    private void ExportOptionsItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        using var dialogForm = new ExportOptionsForm();
        dialogForm.TopMost = true;
        dialogForm.StartPosition = FormStartPosition.CenterParent;
        dialogForm.ShowDialog(this);

        // Determine the format string based on the CustomDialogResult
        var format = dialogForm.CustomDialogResult switch
        {
            ExportOptionsForm.ExportOptionResult.ExportToDocx => "DOCX",
            ExportOptionsForm.ExportOptionResult.ExportToXLS => "XLS",
            ExportOptionsForm.ExportOptionResult.ExportToImage => "Image",
            ExportOptionsForm.ExportOptionResult.ExportToHTML => "HTML",
            ExportOptionsForm.ExportOptionResult.ExportToXML => "XML",
            ExportOptionsForm.ExportOptionResult.ExportToText => "TXT",
            _ => null
        };

        if (format == null) return;
        var outFileName = GetFileName(format);
        if (string.IsNullOrWhiteSpace(outFileName)) return;
        // Convert the format string to the corresponding ExportType enum value
        var exportType = Enum.Parse<ExportType>(format);
        UnifiedExportFunction(outFileName, exportType);
    }

    private void PopulateExportActions()
    {
        exportActions = new Dictionary<string, Action<string>>
        {
            { "DOCX", outFileName => UnifiedExportFunction(outFileName, ExportType.DOCX) },
            { "XLS", outFileName => UnifiedExportFunction(outFileName, ExportType.XLS) },
            { "Image", outFileName => UnifiedExportFunction(outFileName, ExportType.Image) },
            { "HTML", outFileName => UnifiedExportFunction(outFileName, ExportType.HTML) },
            { "XML", outFileName => UnifiedExportFunction(outFileName, ExportType.XML) },
            { "TXT", outFileName => UnifiedExportFunction(outFileName, ExportType.TXT) }
        };
    }

    /// <summary>
    ///     Exports a PDF file to various formats based on the specified export type.
    /// </summary>
    /// <param name="outFileName">The name of the output file.</param>
    /// <param name="exportType">The type of export desired.</param>
    private void UnifiedExportFunction(string outFileName, ExportType exportType)
    {
        try
        {
            var overlayManager = new OverlayManager();
            overlayManager.ShowOverlay(this);

            PdfFocus pdfFocus = new()
            {
                Password = CurrentDocument.PdfPassword
            };

            if (ocrBarCheckItem.Down)
            {
                pdfFocus.OCROptions.Mode = PdfFocus.COCROptions.eOCRMode.AllImages;
                // pdfFocus.OCROptions.Method += OCR.PerformOCRTesseract;
            }

            pdfFocus.OpenPdf(Path.GetFullPath(CurrentDocument.FileName));

            if (ScholarSettings.InsertCopyright) pdfFocus.CopyrightText = ScholarSettings.Copyright;

            pdfFocus.PreserveEmbeddedFonts = ScholarSettings.PreserveFonts switch
            {
                true => PdfFocus.ePropertyState.Enabled,
                false => PdfFocus.ePropertyState.Disabled
            };

            pdfFocus.PreserveImages = ScholarSettings.PreserveImages;
            pdfFocus.PreserveGraphics = ScholarSettings.PreserveGraphics;
            CommonSettings.InitialExportDir =
                Path.GetDirectoryName(outFileName) ?? CommonSettings.DefaultInitialDirectory;

            if (pdfFocus.PageCount > 0)
                switch (exportType)
                {
                    case ExportType.DOCX:
                        ExportToDocx(pdfFocus, outFileName);
                        break;
                    case ExportType.XLS:
                        ExportToXls(pdfFocus, outFileName);
                        break;
                    case ExportType.Image:
                        ExportToImage(pdfFocus, outFileName);
                        break;
                    case ExportType.HTML:
                        ExportToHtml(pdfFocus, outFileName);
                        break;
                    case ExportType.XML:
                        ExportToXml(pdfFocus, outFileName);
                        break;
                    case ExportType.TXT:
                        ExportToText(pdfFocus, outFileName);
                        break;
                    default:
                        throw new ArgumentException("Unsupported export type");
                }

            overlayManager.DisposeOverlay();
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, $"Error exporting PDF to {exportType}", ex);
        }
    }

    private static void ExportToDocx(PdfFocus pdfFocus, string fileName)
    {
        try
        {
            pdfFocus.WordOptions.Format = Path.GetExtension(fileName).Equals(".rtf", StringComparison.OrdinalIgnoreCase)
                ? PdfFocus.CWordOptions.eWordDocument.Rtf
                : PdfFocus.CWordOptions.eWordDocument.Docx;

            pdfFocus.WordOptions.RenderMode = ScholarSettings.PdfRenderMode switch
            {
                0 => // Flowing
                    PdfFocus.CWordOptions.eRenderMode.Flowing,
                1 => // Exact
                    PdfFocus.CWordOptions.eRenderMode.Exact,
                2 => // Continuous
                    PdfFocus.CWordOptions.eRenderMode.Continuous,
                _ => throw new NotSupportedException($"Unsupported render mode: {ScholarSettings.PdfRenderMode}")
            };

            pdfFocus.WordOptions.DetectTables = ScholarSettings.DocxDetectTables;
            pdfFocus.WordOptions.KeepCharScaleAndSpacing = ScholarSettings.DocxKeepCharacterScale;
            pdfFocus.WordOptions.ShowInvisibleText = ScholarSettings.DocxShowInvisibleText;

            var result = pdfFocus.ToWord(fileName);
            if (result == 0)
                FileLauncher.ExecuteProcess(fileName);
            else
                ExportFailedMessage();
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
            throw;
        }
    }

    private static void ExportToXls(PdfFocus pdfFocus, string fileName)
    {
        pdfFocus.ExcelOptions.ConvertNonTabularDataToSpreadsheet = ScholarSettings.XlsConvertNonTabularData;
        pdfFocus.ExcelOptions.PreservePageLayout = ScholarSettings.PreservePageLayout;

        if (pdfFocus.ToExcel(fileName) == 0) FileLauncher.ExecuteProcess(fileName);
    }

    private static void ExportToImage(PdfFocus pdfFocus, string fileName)
    {
        pdfFocus.ImageOptions.Dpi = 300;
        pdfFocus.ImageOptions.ImageFormat = Path.GetExtension(fileName) switch
        {
            // ".jpg" or ".jpeg" => ImageFormat.Jpeg,
            // ".png" => ImageFormat.Png,
            // ".gif" => ImageFormat.Gif,
            // ".bmp" => ImageFormat.Bmp,
            // ".tiff" => ImageFormat.Tiff,
            // ".emf" => ImageFormat.Emf,
            // ".wmf" => ImageFormat.Wmf,
            // _ => throw new NotSupportedException($"Unsupported image format: {Path.GetExtension(fileName)}")
        };

        // if (pdfFocus.ToImage(fileName, 1) == 0) FileLauncher.ExecuteProcess(fileName);
    }

    private static void ExportToHtml(PdfFocus pdfFocus, string fileName)
    {
        pdfFocus.HtmlOptions.Title = ScholarSettings.HtmlTitle;
        pdfFocus.HtmlOptions.IncludeImageInHtml = ScholarSettings.HtmlEmbedImages;

        pdfFocus.HtmlOptions.RenderMode = ScholarSettings.HtmlRenderMode switch
        {
            0 => // Fixed
                PdfFocus.CHtmlOptions.eHtmlRenderMode.Fixed,
            1 => // Flowing
                PdfFocus.CHtmlOptions.eHtmlRenderMode.Flowing,
            _ => throw new NotSupportedException($"Unsupported render mode: {ScholarSettings.PdfRenderMode}")
        };

        if (ScholarSettings.HtmlRenderMode == 0)
            pdfFocus.HtmlOptions.KeepCharScaleAndSpacing = ScholarSettings.HtmlKeepCharScale;

        pdfFocus.EmbeddedImagesFormat = ScholarSettings.HtmlImageFormat switch
        {
            0 => // Auto
                PdfFocus.eImageFormat.Auto,
            1 => // JPG
                PdfFocus.eImageFormat.Jpeg,
            2 => // PNG
                PdfFocus.eImageFormat.Png,
            _ => throw new NotSupportedException($"Unsupported render mode: {ScholarSettings.PdfRenderMode}")
        };

        if (!ScholarSettings.HtmlEmbedImages)
        {
            pdfFocus.HtmlOptions.ImageFolder = Path.GetDirectoryName(fileName);
            pdfFocus.HtmlOptions.ImageSubFolder = $"{Path.GetFileNameWithoutExtension(fileName)}_images";
        }

        if (pdfFocus.ToHtml(fileName) == 0) FileLauncher.ExecuteProcess(fileName);
    }

    private static void ExportToXml(PdfFocus pdfFocus, string fileName)
    {
        pdfFocus.XmlOptions.ConvertNonTabularDataToSpreadsheet = ScholarSettings.XmlConvertNonTabularData;

        if (pdfFocus.ToXml(fileName) == 0) FileLauncher.ExecuteProcess(fileName);
    }

    private static void ExportToText(PdfFocus pdfFocus, string fileName)
    {
        if (pdfFocus.ToText(fileName) == 0) FileLauncher.ExecuteProcess(fileName);
    }

    private void ExportBarButton_ItemClick(object sender, ItemClickEventArgs e)
    {
        if (e.Item.Tag is not string format)
            throw new ArgumentException($"Item tag must be a string, but was {e.Item.Tag?.GetType()}");

        if (exportActions.TryGetValue(format, out var exportAction))
        {
            var outFileName = GetFileName(format);
            if (!string.IsNullOrWhiteSpace(outFileName)) exportAction(outFileName);
        }
        else
        {
            throw new NotSupportedException($"Unsupported export format: {format}");
        }
    }

    private string GetFileName(string format)
    {
        var filter = format switch
        {
            "DOCX" => "Word Document (*.docx)|*.docx",
            "XLS" => "Excel Workbook (*.xls)|*.xls",
            "Image" =>
                "Image (*.jpg; *.jpeg; *.png; *.gif; *.bmp; *.tiff; *.emf; *.wmf)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.emf;*.wmf",
            "HTML" => "HyperText Markup Language Format (*.htm; *.html)|*.htm;*.html",
            "XML" => "Extensible Markup Language (*.XML)|*.xml",
            "TXT" => "Plain Text (*.txt)|*.txt",
            _ => throw new NotSupportedException($"Unsupported export format: {format}")
        };

        var saveFileDlg = new SaveFileDialog
        {
            Filter = filter,
            Title = string.Format(Strings.Export_As, format),
            InitialDirectory = CommonSettings.InitialExportDir,
            FileName = Path.GetFileNameWithoutExtension(CurrentDocument.FileName) ?? string.Empty
        };

        return saveFileDlg.ShowDialog() == DialogResult.OK ? saveFileDlg.FileName : null;
    }

    private static void ExportFailedMessage()
    {
        const string message =
            "It appears our PDF export feature has stumbled, likely due to a mischievous line of code penned by one of our over-caffeinated developers. " +
            "We'll have a word with them, ensuring they swap their coffee for decaf next time. Please restart Scholar and try again.";
        XtraMessageBox.Show(message, "Failed miserable!", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }

    #endregion EXPORT (CONVERT)
}