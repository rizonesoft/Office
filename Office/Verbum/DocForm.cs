using System;
using System.Collections.Generic;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.Utils;
using DevExpress.Utils.Controls;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraPrinting;
using DevExpress.XtraPrintingLinks;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Services;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSpellChecker.Forms;
using DevExpress.XtraSpellChecker.Native;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.Utilities;
using Rizonesoft.Office.Verbum.Classes;
using Rizonesoft.Office.Verbum.Forms;
using Rizonesoft.Office.Verbum.Language;
using Document = DevExpress.XtraRichEdit.API.Native.Document;

namespace Rizonesoft.Office.Verbum;

/// <summary>
///     Represents a Document form
/// </summary>
public partial class DocForm : RibbonForm
{
    private bool _includeTextBoxes;
    private int currentPage = 1;
    private bool isZoomChanging;
    private int _pageCount = 1;


    /// <summary>
    ///     Gets the filename of the document
    /// </summary>
    public string FileName { get; private set; }

    private readonly SvgImageCollection _extensionsSvgImages;
    private const string HyphenationFilePrefix = "hyph";
    private const string SpellingOptionsXml = "Spelling.conf";
    private const string TableToolsRibbonCatName = "TableToolsRibbonCat";

    private Dictionary<string, Action<string>> exportActions;

    private bool IncludeTextBoxes
    {
        get => _includeTextBoxes;
        // ReSharper disable once UnusedMember.Local
        set
        {
            if (_includeTextBoxes == value) return;

            _includeTextBoxes = value;
            OnIncludeTextBoxesChanged();
        }
    }

    /// <summary>
    ///     Initializes a new instance of the DocForm class.
    /// </summary>
    /// <param name="fileName">The name of the file.</param>
    public DocForm(string fileName)
    {
        FileName = fileName;
        _extensionsSvgImages = new SvgImageCollection();
        InitializeSvgImages();

        var extension = Path.GetExtension(fileName);
        if (!string.IsNullOrWhiteSpace(extension))
        {
            var svgImage = ImageResourceLoader.GetIconForExtension(extension);
            IconOptions.SvgImage = _extensionsSvgImages[svgImage];
        }
        else
        {
            IconOptions.SvgImage = _extensionsSvgImages["new"];
        }

        InitializeComponent();
        UpdateUi();

        new RichEditExceptionHandler(childRichEditControl).Install();
        new SpellCheckerExceptionHandler(CoreSpellChecker).Install();
        var commandFactory = new CustomCommandService(childRichEditControl,
            childRichEditControl.GetService<IRichEditCommandFactoryService>());
        childRichEditControl.ReplaceService<IRichEditCommandFactoryService>(commandFactory);
        ExportBarButton.DefaultDropDownLink = ExportPopupMenu.ItemLinks[0];
        SetupEventHandlers();
        PopulateExportActions();
    }

    private void SetupEventHandlers()
    {
        childRichEditControl.DocumentLayout.DocumentFormatted += OnDocumentLayoutDocumentFormatted;
        childRichEditControl.Options.DocumentSaveOptions.Changed += OnDocumentSaveOptionsChanged;
        childRichEditControl.ContentChanged += OnChildRichEditControlContentChanged;
        childRichEditControl.DocumentLoaded += OnChildRichEditControlDocumentLoaded;

        AttachExportHandlers(ExportPDFPopupItem, ExportEPUBPopupItem, ExportImagePopupItem, ExportHTMLPopupItem, ExportMHTPopupItem);
    }

    private void AttachExportHandlers(params BarButtonItem[] items)
    {
        foreach (var item in items)
        {
            item.ItemClick += ExportBarButton_ItemClick;
        }
    }

    private void PopulateExportActions()
    {
        this.exportActions = new Dictionary<string, Action<string>>
        {
            { "PDF", ExportToPdf },
            { "EPUB", fileName => ExportToOtherFormats(fileName, DocumentFormat.ePub) },
            { "Image", ExportToImage },
            { "HTML", fileName => ExportToOtherFormats(fileName, DocumentFormat.Html) },
            { "MHT", fileName => ExportToOtherFormats(fileName, DocumentFormat.Mht) },
        };
    }

    private void DocForm_Load(object sender, EventArgs e)
    {
        if (DesignMode) return;

        try
        {
            _ = LoadSpellingOptions();
            if (childRichEditControl == null) return;
            SetViewType(childRichEditControl.ActiveViewType);
            childRichEditControl.Focus();
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "Could not load document.", ex);
        }

    }

    /// <summary>
    /// Asynchronously loads spelling options for the document.
    /// </summary>
    private async Task LoadSpellingOptions()
    {
        try
        {
            if (ProgramConfiguration.AppDataPath != null)
            {
                var filePath = Path.Combine(ProgramConfiguration.AppDataPath, SpellingOptionsXml);
                if (File.Exists(filePath))
                {
                    await Task.Run(() =>
                        CoreSpellChecker.RestoreFromXML(filePath));
                }
            }

            CoreSpellChecker.Culture = new CultureInfo(VerbumSettings.SpellingLanguage);
            LanguageStatusBtn.Caption = CoreSpellChecker.Culture.EnglishName;
            AutoSpellingCheckItem.Checked = VerbumSettings.AutoSpellCheck;

            await Task.Run(() => LoadHyphenationDictionaries(childRichEditControl.Document)).ConfigureAwait(false);

        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while loading spelling options!", ex);
        }

        childRichEditControl.Modified = false;
    }

    private void LoadHyphenationDictionaries(Document document)
    {
        try
        {
            if (ProgramConfiguration.DictionariesPath != null)
            {
                var dicFiles = Directory.GetFiles(ProgramConfiguration.DictionariesPath);

                foreach (var sFile in dicFiles)
                {
                    if (Path.GetExtension(sFile) != ".dic") continue;

                    var cultureInfo = GetHyphenationDictionaryCultureInfo(sFile);

                    if (cultureInfo != null)
                    {
                        Invoke((Action)(() => AddHyphenationDictionary(sFile, cultureInfo)));
                    }
                }
            }

            Invoke((Action)(() =>
            {
                document.Hyphenation = true;
                document.HyphenateCaps = true;
            }));
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "Could not load hyphenation dictionaries.", ex);
        }
    }


    private static CultureInfo GetHyphenationDictionaryCultureInfo(string fileName)
    {
        var sFileNoExtension = Path.GetFileNameWithoutExtension(fileName);
        var sFileParts = sFileNoExtension.Split('_');

        if (!sFileParts[0].Equals(HyphenationFilePrefix)) return null;

        string sCultureString;

        switch (sFileParts.GetUpperBound(0))
        {
            case 2:
                sCultureString = $"{sFileParts[1]}-{sFileParts[2]}";
                break;
            case 1:
                sCultureString = sFileParts[1];
                break;
            default:
                return null;
        }

        return new CultureInfo(sCultureString);
    }

    private void AddHyphenationDictionary(string hyphPath, CultureInfo hyphCulture)
    {
        OpenOfficeHyphenationDictionary hyphenationDictionary = new(hyphPath, hyphCulture);
        childRichEditControl.HyphenationDictionaries.Add(hyphenationDictionary);
    }

    private void InitializeSvgImages()
    {
        _extensionsSvgImages.Add("exporttodoc", "image://svgimages/export/exporttodoc.svg");
        _extensionsSvgImages.Add("exporttodocx", "image://svgimages/export/exporttodocx.svg");
        _extensionsSvgImages.Add("exporttortf", "image://svgimages/export/exporttortf.svg");
        _extensionsSvgImages.Add("exporttoodt", "image://svgimages/export/exporttoodt.svg");
        _extensionsSvgImages.Add("exporttotxt", "image://svgimages/export/exporttotxt.svg");
        _extensionsSvgImages.Add("exporttohtml", "image://svgimages/export/exporttohtml.svg");
        _extensionsSvgImages.Add("exporttomht", "image://svgimages/export/exporttomht.svg");
        _extensionsSvgImages.Add("exporttodocx", "image://svgimages/export/exporttoxml.svg");
        _extensionsSvgImages.Add("exporttodoc", "image://svgimages/export/exporttoepub.svg");
        _extensionsSvgImages.Add("new", "image://svgimages/actions/new.svg");
    }

    #region Export

    /// <summary>
    ///     Handles the click event of the ExportBarButton.
    /// </summary>
    /// <param name="sender">The sender of the event.</param>
    /// <param name="e">The click event arguments.</param>
    private void ExportBarButton_ItemClick(object sender, ItemClickEventArgs e)
    {
        if (e.Item.Tag is not string format)
            throw new ArgumentException($"Item tag must be a string, but was {e.Item.Tag?.GetType()}");

        if (exportActions.TryGetValue(format, out var exportAction))
        {
            var fileName = GetFileName(format);
            if (!string.IsNullOrWhiteSpace(fileName)) exportAction(fileName);
        }
        else
        {
            throw new NotSupportedException($"Unsupported export format: {format}");
        }
    }

    /// <summary>
    ///     Shows a SaveFileDialog and returns the selected file name.
    /// </summary>
    /// <param name="format">The format of the exported file.</param>
    /// <returns>The file name selected by the user, or null if the user cancelled the dialog.</returns>
    private string GetFileName(string format)
    {
        var filter = format switch
        {
            "PDF" => "Adobe PDF Files (*.pdf)|*.pdf",
            "EPUB" => "Electronic Publication (*.epub)|*.epub",
            "Image" =>
                "Image (*.jpg; *.jpeg; *.png; *.gif; *.bmp; *.tiff; *.emf; *.wmf)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.emf;*.wmf",
            "HTML" => "HyperText Markup Language Format (*.htm; *.html)|*.htm;*.html",
            "MHT" => "Single File Web Page (*.mht)|*.mht",
            _ => throw new NotSupportedException($"Unsupported export format: {format}")
        };

        var saveFileDlg = new SaveFileDialog
        {
            Filter = filter,
            Title = string.Format(Strings.ExportTo_Title, format),
            FileName = Path.GetFileNameWithoutExtension(FileName) ?? string.Empty
        };

        return saveFileDlg.ShowDialog() == DialogResult.OK ? saveFileDlg.FileName : null;
    }

    /// <summary>
    ///     Exports the current document as a PDF file.
    /// </summary>
    /// <param name="fileName">The name of the exported file.</param>
    private void ExportToPdf(string fileName)
    {
        PdfExportOptions pdfOptions = new()
        {
            DocumentOptions =
            {
                Author = ProgramConfiguration.CompanyName
            },
            Compressed = true,
            ConvertImagesToJpeg = true,
            ImageQuality = PdfJpegImageQuality.High,
            ShowPrintDialogOnOpen = false,
            PdfUACompatibility = PdfUACompatibility.None,
            PdfACompatibility = PdfACompatibility.None
        };

        childRichEditControl.ExportToPdf(fileName, pdfOptions);
        FileLauncher.OpenPdfInDefaultViewer(fileName);
    }

    /// <summary>
    ///     Exports the current document to a specified format.
    /// </summary>
    /// <param name="fileName">The name of the exported file.</param>
    /// <param name="format">The format of the exported file.</param>
    private void ExportToOtherFormats(string fileName, DocumentFormat format)
    {
        try
        {
            childRichEditControl.SaveDocument(fileName, format);
        }
        catch (Exception ex)
        {
            // Handle the exception
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while exporting document!", ex);
            XtraMessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    /// <summary>
    /// Exports the current document as an image file.
    /// </summary>
    /// <param name="fileName">The name of the exported file.</param>
    private void ExportToImage(string fileName)
    {
        var pcl = new PrintableComponentLinkBase(new PrintingSystemBase())
        {
            Component = ((IRichEditControl)childRichEditControl).InnerControl,
        };
        pcl.CreateDocument(false);

        var imgOptions = new ImageExportOptions
        {
            ExportMode = ImageExportMode.DifferentFiles,
            Format = Path.GetExtension(fileName) switch
            {
                ".jpg" or ".jpeg" => ImageFormat.Jpeg,
                ".png" => ImageFormat.Png,
                ".gif" => ImageFormat.Gif,
                ".bmp" => ImageFormat.Bmp,
                ".tiff" => ImageFormat.Tiff,
                ".emf" => ImageFormat.Emf,
                ".wmf" => ImageFormat.Wmf,
                _ => throw new NotSupportedException($"Unsupported image format: {Path.GetExtension(fileName)}")
            },
            Resolution = 150,
        };
        pcl.ExportToImage(fileName, imgOptions);
    }

    #endregion Export

    private void OnDocumentSaveOptionsChanged(object sender, BaseOptionChangedEventArgs e)
    {
        if (e.Name != nameof(DocumentSaveOptions.CurrentFileName)) return;
        ChildDocHelper.SetDocumentCaption(childRichEditControl.Options.DocumentSaveOptions.CurrentFileName, this);
        FileName = childRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
    }

    private void OnChildRichEditControlContentChanged(object sender, EventArgs e)
    {
        DocumentStatsTimer.Start();
    }

    private void OnChildRichEditControlDocumentLoaded(object sender, EventArgs e)
    {
        ChildDocHelper.SetDocumentCaption(childRichEditControl.Options.DocumentSaveOptions.CurrentFileName, this);
    }

    private void OnDocumentLayoutDocumentFormatted(object sender, EventArgs e)
    {
        _pageCount = childRichEditControl.DocumentLayout.GetPageCount();
        OnPagesInfoChanged();
    }

    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        _ = childRichEditControl.ActiveView.ZoomFactor;
    }

    /// <summary>
    ///     Open a file
    /// </summary>
    /// <param name="fileName">The name of the file to open.</param>
    /// <param name="docIndex">The document index.</param>
    public void OpenFile(string fileName, int docIndex)
    {
        if (!string.IsNullOrWhiteSpace(fileName))
        {
            FileName = fileName;
            switch (Path.GetExtension(fileName))
            {
                case "eml":
                    childRichEditControl.LoadDocument(fileName, DocumentFormat.Mht);
                    break;

                default:
                    childRichEditControl.LoadDocument(fileName);
                    break;
            }

            ChildDocHelper.SetDocumentCaption(fileName, this);
            return;
        }

        Text = FileName = $"Document {docIndex}";
        childRichEditControl.Options.DocumentSaveOptions.DefaultFileName = $"Untitled {docIndex}";
    }

    /// <summary>
    ///     Save the file
    /// </summary>
    public void SaveFile()
    {
        childRichEditControl.SaveDocument();
    }

    private void UpdateUi()
    {
        FileRibbonPage.Text = Dialogs.RibbonPage_File;
        CommonRibbonGroup.Text = Dialogs.RibbonGroup_Common;
        ExportToRibbonGroup.Text = Dialogs.RibbonGroup_Export_To;
        InfoRibbonGroup.Text = Dialogs.RibbonGroup_Info;
        OptionsRibbonGroup.Text = Dialogs.RibbonGroup_Options;
        AutoSpellingCheckItem.Caption = Dialogs.AutoSpellingButton_Caption;
    }

    private void OnIncludeTextBoxesChanged()
    {
        CalculateDocumentStatistics();
    }

    private void CalculateDocumentStatistics()
    {
        DocumentIterator iterator = new(childRichEditControl.Document, true);
        StaticsticsVisitor visitor = new(IncludeTextBoxes);
        while (iterator.MoveNext()) iterator.Current?.Accept(visitor);

        DocStatsStatusBtnItem.Caption = $@"{visitor.WordCount} Words";
    }

    private void DocForm_Shown(object sender, EventArgs e)
    {

    }

    /// <summary>
    /// Handles the SelectionChanged event of the ChildRichEditControl object.
    /// </summary>
    private void ChildRichEditControl_SelectionChanged(object sender, EventArgs e)
    {
        if (!childRichEditControl.DocumentLayout.IsDocumentFormattingCompleted) return;

        var element = childRichEditControl.DocumentLayout.GetElement<RangedLayoutElement>(childRichEditControl.Document.CaretPosition);
        if (element is not null)
        {
            currentPage = childRichEditControl.DocumentLayout.GetPageIndex(element) + 1;
            OnPagesInfoChanged();
        }

        CustomLayoutVisitor visitor = new(childRichEditControl.Document);

        for (var i = 0; i < childRichEditControl.DocumentLayout.GetPageCount(); i++)
        {
            visitor.Reset();
            var page = childRichEditControl.DocumentLayout.GetPage(i);
            visitor.Visit(page);

            if (visitor.IsFound) break;
        }

        if (!visitor.IsFound) return;

        CurrLineStatusItem.Caption = $@"line {visitor.RowIndex}";
        ColumnStatusItem.Caption = $@"Column {visitor.ColIndex}";

        if (!childRichEditControl.IsSelectionInTable()) return;

        var tableToolsCat = ChildRibbon.MergeOwner.PageCategories.GetCategoryByName(TableToolsRibbonCatName);
        if (tableToolsCat is not null) tableToolsCat.Visible = true;
        // ChildRibbon.SelectPage(TableDesignChildRibbonPage);
    }

    private void OnPagesInfoChanged()
    {
        PagesStatusStatic.Caption = $@"Page {currentPage} of {_pageCount}";
    }

    private void DocumentStatsTimer_Tick(object sender, EventArgs e)
    {
        DocumentStatsTimer.Stop();
        BeginInvoke(CalculateDocumentStatistics);
    }

    private void ChildRichEditControl_VisiblePagesChanged(object sender, EventArgs e)
    {
        currentPage = childRichEditControl.ActiveView.GetVisiblePageLayoutInfos()[0].PageIndex + 1;
    }

    private void AutoSpellingCheckItem_CheckedChanged(object sender, ItemClickEventArgs e)
    {
        VerbumSettings.AutoSpellCheck = AutoSpellingCheckItem.Checked;
        AutoSpellingSwitch();
    }

    private void AutoSpellingSwitch()
    {
        if (AutoSpellingCheckItem.Checked)
        {
            VerbumSettings.AutoSpellCheck = true;
            CoreSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
            return;
        }

        VerbumSettings.AutoSpellCheck = false;
        CoreSpellChecker.SpellCheckMode = SpellCheckMode.OnDemand;
    }

    private void ZoomResetStatusItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        childRichEditControl.ActiveView.ZoomFactor = 1;
    }


    private void SpellOptionsItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        try
        {
            var spellOptions = CoreSpellChecker.GetSpellCheckerOptions(childRichEditControl);
            CoreSpellChecker.OptionsSpelling.CombineOptions(spellOptions);

            using var spellOptionsForm = new SpellingOptionsForm(CoreSpellChecker);
            spellOptionsForm.Init();

            if (spellOptionsForm.ShowDialog(this) != DialogResult.OK)
                return;

            // Local function to convert bool to DefaultBoolean
            static DefaultBoolean Convert(bool value) => BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(value);

            spellOptions.BeginUpdate();
            try
            {
                spellOptions.IgnoreUpperCaseWords = Convert(spellOptionsForm.IgnoreUpperCase);
                spellOptions.IgnoreEmails = Convert(spellOptionsForm.IgnoreEmails);
                spellOptions.IgnoreWordsWithNumbers = Convert(spellOptionsForm.IgnoreWordsWithDigits);
                spellOptions.IgnoreUri = Convert(spellOptionsForm.IgnoreUri);
                spellOptions.IgnoreMixedCaseWords = Convert(spellOptionsForm.IgnoreMixedCaseWords);
                spellOptions.IgnoreRepeatedWords = Convert(spellOptionsForm.IgnoreRepeatedWords);
            }
            finally
            {
                spellOptions.EndUpdate();
            }

            CoreSpellChecker.SetSpellCheckerOptions(childRichEditControl, spellOptions);
            CoreSpellChecker.OptionsSpelling.CombineOptions(CoreSpellChecker.GetSpellCheckerOptions(childRichEditControl));
            if (ProgramConfiguration.AppDataPath != null)
                CoreSpellChecker.SaveToXML(Path.Combine(ProgramConfiguration.AppDataPath, SpellingOptionsXml));

            VerbumSettings.SpellingLanguage = CoreSpellChecker.Culture.ToString();
            LanguageStatusBtn.Caption = CoreSpellChecker.Culture.EnglishName;
        }
        catch (Exception ex)
        {
            // Log or handle the exception as needed.
            Console.WriteLine(ex.Message);
        }
    }

    /// <summary>
    /// Checks if the document has been modified and, if so, asks the user if they want to save changes.
    /// </summary>
    /// <returns>
    /// Returns true if the document has not been modified, or if the user does not want to save changes, or if the document has been successfully saved.
    /// Returns false if the user cancels the save dialog.
    /// </returns>
    private bool TrySaveDocument()
    {
        // If the document hasn't been modified, there's nothing to save.
        if (!childRichEditControl.Modified)
        {
            return true;
        }

        // If no filename has been set, use the form's text as the filename.
        string fileName = string.IsNullOrEmpty(FileName) ? Text : FileName;

        try
        {
            switch (XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{fileName}\"?",
                        "Warning",
                        MessageBoxButtons.YesNoCancel,
                        MessageBoxIcon.Warning))
            {
                case DialogResult.Cancel:
                    // The user doesn't want to save changes and has cancelled the operation.
                    return false;

                case DialogResult.Yes:
                    // The user wants to save changes. Try to save the document.
                    childRichEditControl.SaveDocument();
                    // After successfully saving, mark the document as unmodified.
                    childRichEditControl.Modified = false;
                    break;
            }
        }
        catch (Exception ex)
        {
            // Log or handle the exception as needed.
            Console.WriteLine(ex.Message);
            // If an error occurs while saving, return false.
            return false;
        }

        // If the document hasn't been modified, or if the user didn't want to save changes, or if the document has been saved, return true.
        return true;
    }



    /// <summary>
    /// Handles the EditValueChanged event of the ZoomStatusItem control.
    /// </summary>
    /// <param name="sender">The source of the event.</param>
    /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
    private void ZoomStatusItem_EditValueChanged(object sender, EventArgs e)
    {
        if (isZoomChanging) return;

        try
        {
            var zoomValue = Convert.ToInt32(ZoomStatusItem?.EditValue);
            if (zoomValue is < 10 or > 400)
            {
                return;
            }

            isZoomChanging = true;

            if (childRichEditControl?.ActiveView != null)
            {
                childRichEditControl.ActiveView.ZoomFactor = zoomValue / 100f;
            }

            if (ZoomStatusItem != null)
            {
                ZoomStatusItem.Caption = $@"{zoomValue}%";
            }
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Warning, "The Zoom Track-bar could not be updated!", ex);
        }
        finally
        {
            isZoomChanging = false;
        }
    }

    private void ChildRichEditControl_ZoomChanged(object sender, EventArgs e)
    {
        if (isZoomChanging) return;
        var zoomValue = (int)Math.Round(childRichEditControl.ActiveView.ZoomFactor * 100);
        isZoomChanging = true;

        try
        {
            ZoomStatusItem.EditValue = zoomValue;
            ZoomStatusItem.Caption = $@"{zoomValue}%";
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
        }
        finally
        {
            isZoomChanging = false;
        }
    }

    private void SetViewType(RichEditViewType viewType)
    {
        childRichEditControl.ActiveViewType = viewType;
        SimpleViewStatusItem.Down = viewType == RichEditViewType.Simple;
        PrintLayoutStatusItem.Down = viewType == RichEditViewType.PrintLayout;
        DraftViewStatusItem.Down = viewType == RichEditViewType.Draft;
    }

    private void SimpleViewStatusItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        try
        {
            if (childRichEditControl == null) return;
            if (e.Item is BarButtonItem { Down: true } clickedItem)
            {
                SetViewType(clickedItem switch
                {
                    _ when clickedItem == SimpleViewStatusItem => RichEditViewType.Simple,
                    _ when clickedItem == PrintLayoutStatusItem => RichEditViewType.PrintLayout,
                    _ when clickedItem == DraftViewStatusItem => RichEditViewType.Draft,
                    _ => childRichEditControl.ActiveViewType
                });
            }
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "Could not set View Type", ex);
        }
    }

    private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
    {
        e.Cancel = !TrySaveDocument();
    }

    private void ChildRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
    {
        Serilogger.LogMessage(LogLevel.Warning, $"Cannot open the file '{FileName}' because the file format or file extension is not valid.", e.Exception);
        XtraMessageBox.Show(string.Format(Strings.InvalidFormatException_Message, FileName),
            Strings.InvalidFormatException_Caption, MessageBoxButtons.OK, MessageBoxIcon.Warning);
    }

    private void DocStatsStatusBtnItem_ItemClick(object sender, ItemClickEventArgs e)
    {
        using DocumentStatisticsForm docStatsForm = new(childRichEditControl.Document, IncludeTextBoxes);
        docStatsForm.LookAndFeel.ParentLookAndFeel = LookAndFeel;
        docStatsForm.ShowDialog();
        IncludeTextBoxes = docStatsForm.IncludeTextboxes;
    }
}