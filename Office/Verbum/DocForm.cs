namespace Rizonesoft.Office.Verbum
{
    using DevExpress.Utils.Controls;
    using DevExpress.XtraBars;
    using DevExpress.XtraEditors;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraRichEdit;
    using DevExpress.XtraRichEdit.API.Layout;
    using DevExpress.XtraRichEdit.API.Native;
    using DevExpress.XtraRichEdit.Services;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSpellChecker.Forms;
    using DevExpress.XtraSpellChecker.Native;
    using DevExpress.XtraRichEdit.Import;
    using DevExpress.XtraRichEdit.Export;
    using Rizonesoft.Office.Utilities;
    using Rizonesoft.Office.Verbum.Classes;
    using Rizonesoft.Office.Verbum.Forms;
    using Rizonesoft.Office.Verbum.Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Globalization;
    using System.IO;
    using System.Windows.Forms;
    using DevExpress.ClipboardSource.SpreadsheetML;
    using System.Drawing;
    using System.Drawing.Imaging;
    using DevExpress.XtraEditors.Design;
    using DevExpress.XtraPrintingLinks;
    using static System.Windows.Forms.Design.AxImporter;
    using DevExpress.Diagram.Core.Native.Generation;
    using DevExpress.XtraRichEdit.UI;
    using DevExpress.XtraBars.Ribbon;

    public partial class DocForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        internal bool _includeTextBoxes = false;
        internal int currentPage = 1;
        internal bool isZoomChanging;

        internal int pageCount = 1;


        public DocForm()
        {

            InitializeComponent();
            MainRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
            MainRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_Changed;

            new RichEditExceptionHandler(MainRichEditControl).Install();
            new SpellCheckerExceptionHandler(mainSpellChecker).Install();

            CustomCommandFactoryService commandFactory = new CustomCommandFactoryService(MainRichEditControl, MainRichEditControl.GetService<IRichEditCommandFactoryService>());
            MainRichEditControl.ReplaceService<IRichEditCommandFactoryService>(commandFactory);

            MainForm.SetSkins();

            exportBarButton.DefaultDropDownLink = exportPopupMenu.ItemLinks[0];
            exportPDFPopupMenuItem.ItemClick += new ItemClickEventHandler(ExportBarButton_ItemClick);
            exportEBUPopupMenuItem.ItemClick += new ItemClickEventHandler(ExportBarButton_ItemClick);
            exportImagePopupMenuItem.ItemClick += new ItemClickEventHandler(ExportBarButton_ItemClick);
            exportHTMLPopupMenuItem.ItemClick += new ItemClickEventHandler(ExportBarButton_ItemClick);
            exportMHTPopupMenuItem.ItemClick += new ItemClickEventHandler(ExportBarButton_ItemClick);

            //
            // coreSpellChecker.Culture = CultureInfo.;

            // InitializeRichEditControl();
            // coreRibbonControl.SelectedPage = homeRibbonPage1;

            // this.headerFooterToolsRibbonPageCategory.Visible = false;
            // this.tableToolsRibbonPageCategory.Visible = false;
            // this.floatingPictureToolsRibbonPageCategory.Visible = false;

        }

        public DocForm(string fileName) : this()
        {
            // FileName = fileName;
            MainRichEditControl.LoadDocument(fileName);
            // FileName = MainRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
            MainRichEditControl.Modified = false;
            MainRichEditControl.Focus();

        }

        private void AddHyphenationDictionary(string hyphPath, CultureInfo hyphCulture)
        {
            OpenOfficeHyphenationDictionary hyphenationDictionary = new(hyphPath, hyphCulture);
            MainRichEditControl.HyphenationDictionaries.Add(hyphenationDictionary);

        }

        private void AutoSpellingItem_CheckedChanged(object sender, ItemClickEventArgs e)
        {
            StcVerbum.AutoSpellCheck = autoSpellingItem.Checked;
            AutoSpellingSwitch();
        }

        private void AutoSpellingSwitch()
        {
            if (autoSpellingItem.Checked)
            {
                StcVerbum.AutoSpellCheck = true;
                mainSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
                return;
            }

            StcVerbum.AutoSpellCheck = false;
            mainSpellChecker.SpellCheckMode = SpellCheckMode.OnDemand;
        }


        private void barOptionsItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            try
            {
                OptionsForm optionsDlg = new();
                optionsDlg.Show(this);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void DocForm_Activated(object sender, EventArgs e)
        {
            if (MdiParent == null)
            {
                Owner = null;
            }

        }

        bool SaveQuestion()
        {
            string tempName = FileName;
            if (string.IsNullOrEmpty(tempName))
            {
                tempName = Text;
            }

            if (MainRichEditControl.Modified)
            {
                switch (XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{tempName}\"?",
                                  "Warning",
                                  MessageBoxButtons.YesNoCancel,
                                  MessageBoxIcon.Warning))
                {
                    case DialogResult.Cancel:
                        return false;
                    case DialogResult.Yes:
                        MainRichEditControl.SaveDocument();
                        break;
                }
            }
            return true;
        }

        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            e.Cancel = !SaveQuestion();
        }

        private void DocForm_Load(object sender, EventArgs e)
        {

            if (DesignMode)
            {
                return;
            }

            // this.mainRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
            this.MainRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_OnChanged;
            LoadSpellingOptions();

            this.MainRichEditControl.Modified = false;
            this.MainRichEditControl.Focus();

        }

        private void DocStatBtnItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            using DocumentStatisticsForm docStatsForm = new(MainRichEditControl.Document, IncludeTextBoxes);
            docStatsForm.LookAndFeel.ParentLookAndFeel = LookAndFeel;
            docStatsForm.ShowDialog();
            IncludeTextBoxes = docStatsForm.IncludeTextboxes;
        }

        private void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
            pageCount = MainRichEditControl.DocumentLayout.GetPageCount();
            OnPagesInfoChanged();
        }

        void DocumentSaveOptions_Changed(object sender, BaseOptionChangedEventArgs e)
        {

        }

        private void DocumentSaveOptions_OnChanged(object sender, BaseOptionChangedEventArgs e)
        {
            if (e.Name == "CurrentFileName")
            {
                SetDocumentCaption(MainRichEditControl.Options.DocumentSaveOptions.CurrentFileName);
                FileName = MainRichEditControl.Options.DocumentSaveOptions.CurrentFileName;

            }
        }

        private void DocumentStatsTimer_Tick(object sender, EventArgs e)
        {
            documentStatsTimer.Stop();
            BeginInvoke(new Action(CalculateDocumentStatistics));
        }

        private void ExportBarButton_ItemClick(object sender, ItemClickEventArgs e)
        {

            switch (e.Item.Tag)
            {
                case "PDF":
                    DoExport(1, "Export to PDF");
                    break;
                case "EPUB":
                    MessageBox.Show(":)");
                    break;
                case "Image":
                    DoExport(4, "Export to HTML");
                    break;
                case "HTML":
                    DoExport(6, "Export to HTML");
                    break;
                case "MHT":
                    MessageBox.Show(":)");
                    break;
            }

        }

        private void DoExport(int filterIndex, string title)
        {
            try
            {
                SaveFileDialog saveFileDlg = new()
                {
                    Filter = "Adobe PDF Files (*.pdf)|*.pdf|" +
                             "Adobe PDF Files, Optimized (*.pdf)|*.pdf|" +
                             "Electronic Publication (*.epub)|*.epub|" +
                             "Image (*.jpg; *.jpeg; *.png; *.gif; *.bmp; *.tiff; *.emf; *.wmf)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.emf;*.wmf|" +
                             "HyperText Markup Language Format (*.htm; *.html)|*.htm;*.html",
                    FilterIndex = filterIndex,
                    Title = title,
                    FileName = Path.GetFileNameWithoutExtension(FileName)
                };

                if (saveFileDlg.ShowDialog() == DialogResult.OK)
                {
                    if (saveFileDlg.FileName != "")
                    {
                        string fileName = saveFileDlg.FileName;
                        switch (saveFileDlg.FilterIndex)
                        {
                            case 1:
                                ExportPDFWithOptions(fileName);
                                break;
                            case 2:
                                ExportPDFWithOptions(fileName, true);
                                break;
                            case 4:
                                ExportToImage(fileName);
                                break;
                            case 5:
                                MainRichEditControl.SaveDocument(fileName, DocumentFormat.Html);
                                break;

                            default:
                                break;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Logging.ROLogger.Error(ex.Message);
                XtraMessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ExportPDFWithOptions(string fileName, bool compressed = false,
            bool converImages = false, PdfJpegImageQuality pdfJpegImageQuality = PdfJpegImageQuality.High)
        {
            PdfExportOptions pdfOptions = new();
            pdfOptions.DocumentOptions.Author = $"Rizonesoft Office {GlobalProperties.ProductVersion.Major}";
            pdfOptions.Compressed = compressed;
            pdfOptions.ConvertImagesToJpeg = converImages;
            pdfOptions.ImageQuality = pdfJpegImageQuality;
            pdfOptions.ShowPrintDialogOnOpen = false;
            pdfOptions.PdfUACompatibility = PdfUACompatibility.None;
            pdfOptions.PdfACompatibility = PdfACompatibility.None;

            MainRichEditControl.ExportToPdf(fileName, pdfOptions);
            ShellExecuteEx.OpenPDFDocument(fileName);
        }

        private void ExportToImage(string fileName, bool transparent = false)
        {
            PrintableComponentLinkBase pcl = new PrintableComponentLinkBase(new PrintingSystemBase());
            pcl.Component = ((IRichEditControl)MainRichEditControl).InnerControl;
            pcl.CreateDocument(false);

            ImageExportOptions imgOptions = new ImageExportOptions();
            imgOptions.ExportMode = ImageExportMode.DifferentFiles;
            switch (Path.GetExtension(fileName))
            {
                case ".jpg":
                    imgOptions.Format = ImageFormat.Jpeg;
                    break;
                case ".jpeg":
                    imgOptions.Format = ImageFormat.Jpeg;
                    break;
                case ".png":
                    imgOptions.Format = ImageFormat.Png;
                    break;
                case ".gif":
                    imgOptions.Format = ImageFormat.Gif;
                    break;
                case ".bmp":
                    imgOptions.Format = ImageFormat.Bmp;
                    break;
                case ".tiff":
                    imgOptions.Format = ImageFormat.Tiff;
                    break;
                case ".emf":
                    imgOptions.Format = ImageFormat.Emf;
                    break;
                case ".wmf":
                    imgOptions.Format = ImageFormat.Wmf;
                    break;
                default:
                    break;
            }
            imgOptions.Resolution = 150;
            //imgOptions.PageRange = "1,3-5";

            pcl.ExportToImage(fileName, imgOptions);


        }

        private void LoadHyphenationDictionaries(DevExpress.XtraRichEdit.API.Native.Document document)
        {
            try
            {
                string[] dicFiles = Directory.GetFiles(StcVerbum.DictionariesPath);

                foreach (string sFile in dicFiles)
                {
                    if (!sFile.EndsWith(".dic"))
                    {
                        continue;
                    }

                    string sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);
                    string[] sFileParts = sFileNoExtension.Split('_');
                    string sCultureString;

                    if (!sFileParts[0].Equals("hyph"))
                    { continue; }

                    if (sFileParts.GetUpperBound(0) == 2)
                    { sCultureString = $"{sFileParts[1]}-{sFileParts[2]}"; }
                    else if (sFileParts.GetUpperBound(0) == 1)
                    { sCultureString = sFileParts[1]; }
                    else
                    { return; }

                    AddHyphenationDictionary(sFile, new CultureInfo(sCultureString));
                }

                document.Hyphenation = true;
                document.HyphenateCaps = true;

            }
            catch (Exception ex)
            {
                Logging.ROLogger.Error(ex, "Whoops!");
                MessageBox.Show(ex.Message, "Whoops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LoadSpellingOptions()
        {
            StcVerbum.SpellingLanguage = Settings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", mainSpellChecker.Culture.ToString());
            StcVerbum.AutoSpellCheck = GlobalFunctions.StringToBoolean(Settings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", "True"));

            if (File.Exists(StcVerbum.CurrentSpellingXmlFile))
            { mainSpellChecker.RestoreFromXML(StcVerbum.CurrentSpellingXmlFile); }

            mainSpellChecker.Culture = new CultureInfo(StcVerbum.SpellingLanguage);
            barLangBtnItem.Caption = mainSpellChecker.Culture.EnglishName;
            autoSpellingItem.Checked = StcVerbum.AutoSpellCheck;
            LoadHyphenationDictionaries(MainRichEditControl.Document);
        }

        private void MainRibbonControl_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = true;
            licenseRibbonGroup.Visible = true;
        }

        private void MainRibbonControl_UnMerge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = false;
            licenseRibbonGroup.Visible = false;
        }

        private void MainRichEditControl_ActiveViewChanged(object sender, EventArgs e)
        {
            switch (MainRichEditControl.ActiveViewType)
            {
                case RichEditViewType.Draft:
                    DraftViewStatusItem.Down = true;
                    PrintLayoutStatusItem.Down = false;
                    SimpleViewStatusItem.Down = false;
                    break;
                case RichEditViewType.PrintLayout:
                    PrintLayoutStatusItem.Down = true;
                    DraftViewStatusItem.Down = false;
                    SimpleViewStatusItem.Down = false;
                    break;
                case RichEditViewType.Simple:
                    SimpleViewStatusItem.Down = true;
                    DraftViewStatusItem.Down = false;
                    PrintLayoutStatusItem.Down = false;
                    break;
            }

        }

        private void MainRichEditControl_ContentChanged(object sender, EventArgs e)
        {
            documentStatsTimer.Start();
        }

        private void mainRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
        {
            Logging.ROLogger.Warn($"Cannot open the file '{FileName}' because the file format or file extension is not valid.");
            XtraMessageBox.Show($"Cannot open the file '{FileName}' because the file format or file extension is not valid.\n" +
                $"Verify that file has not been corrupted and that the file extension matches the format of the file.",
                "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);

        }

        private void MainRichEditControl_SelectionChanged(object sender, EventArgs e)
        {

            if (MainRichEditControl.DocumentLayout.IsDocumentFormattingCompleted)
            {
                RangedLayoutElement element = MainRichEditControl.DocumentLayout.GetElement<RangedLayoutElement>(MainRichEditControl.Document.CaretPosition);
                if (element != null)
                {
                    currentPage = MainRichEditControl.DocumentLayout.GetPageIndex(element) + 1;
                    OnPagesInfoChanged();
                }

                CustomLayoutVisitor visitor = new(MainRichEditControl.Document);

                for (int i = 0; i < MainRichEditControl.DocumentLayout.GetPageCount(); i++)
                {
                    visitor.Reset();
                    LayoutPage page = MainRichEditControl.DocumentLayout.GetPage(i);
                    visitor.Visit(page);

                    if (!visitor.IsFound)
                    {
                        continue;
                    }

                    break;
                }

                if (visitor.IsFound)
                {
                    barCurrLineItem.Caption = $"line {visitor.RowIndex}";
                    barCurrColumnItem.Caption = $"Column {visitor.ColIndex}";
                }
            }

            try
            {
                RibbonPageCategory tableToolsCat = ChildRibbonControl.MergeOwner.PageCategories["Table Tools"];
                RibbonPageCategory picToolsCat = ChildRibbonControl.MergeOwner.PageCategories["Picture Tools"];
                RibbonPageCategory headToolsCat = ChildRibbonControl.MergeOwner.PageCategories["Header & Footer Tools"];

                if (tableToolsCat != null)
                {
                    tableToolsCat.Visible = MainRichEditControl.IsSelectionInTable();
                    ChildRibbonControl.SelectPage(tableDesignChildRibbonPage);
                }

                if (picToolsCat != null)
                {
                    // To-Do: Complete logic
                    picToolsCat.Visible = MainRichEditControl.IsFloatingObjectSelected;

                }


                if (headToolsCat != null)
                {
                    // To-Do: Complete logic
                    headToolsCat.Visible = MainRichEditControl.IsSelectionInHeaderOrFooter;
                }

            }
            catch (Exception ex)
            {
                Logging.ROLogger.Error(ex.Message);
            }

        }

        private void MainRichEditControl_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerToolsChildRibbonCategory.Visible = true;
            ChildRibbonControl.SelectedPage = hfToolsDesignChildRibPage;
        }

        private void MainRichEditControl_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerToolsChildRibbonCategory.Visible = false;
            ChildRibbonControl.SelectedPage = hfToolsDesignChildRibPage;
        }

        private void MainRichEditControl_VisiblePagesChanged(object sender, EventArgs e)
        {
            currentPage = MainRichEditControl.ActiveView.GetVisiblePageLayoutInfos()[0].PageIndex + 1;
        }

        private void MainRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;
            int zoomValue = (int)Math.Round(MainRichEditControl.ActiveView.ZoomFactor * 100);
            isZoomChanging = true;

            try
            {
                zoomBarEditItem.EditValue = zoomValue;
                zoomBarEditItem.Caption = $"{zoomValue}%";
            }
            finally
            {
                isZoomChanging = false;
            }
        }

        private void SetDocumentCaption(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                string fileCaption = Path.GetFileName(fileName);
                if (fileCaption.Length > 28)
                {
                    fileCaption = $"{fileCaption.Remove(29)}...";
                }
                Text = fileCaption;
            }

        }



        private void spellOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsSpelling spellOptions = this.mainSpellChecker.GetSpellCheckerOptions(this.MainRichEditControl);
            this.mainSpellChecker.OptionsSpelling.CombineOptions(spellOptions);
            using (SpellingOptionsForm spellOptionsForm = new SpellingOptionsForm(this.mainSpellChecker))
            {
                spellOptionsForm.Init();
                if (spellOptionsForm.ShowDialog(this) == DialogResult.OK)
                {
                    spellOptions.BeginUpdate();
                    try
                    {
                        spellOptions.IgnoreUpperCaseWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreUpperCase);
                        spellOptions.IgnoreEmails = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreEmails);
                        spellOptions.IgnoreWordsWithNumbers = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreWordsWithDigits);
                        spellOptions.IgnoreUri = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreUri);
                        spellOptions.IgnoreMixedCaseWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreMixedCaseWords);
                        spellOptions.IgnoreRepeatedWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreRepeatedWords);

                    }
                    finally
                    {
                        spellOptions.EndUpdate();

                    }

                    mainSpellChecker.SetSpellCheckerOptions(MainRichEditControl, spellOptions);
                    mainSpellChecker.OptionsSpelling.CombineOptions(mainSpellChecker.GetSpellCheckerOptions(this.MainRichEditControl));
                    mainSpellChecker.SaveToXML(StcVerbum.CurrentSpellingXmlFile);
                    StcVerbum.SpellingLanguage = mainSpellChecker.Culture.ToString();
                    Settings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", StcVerbum.SpellingLanguage);
                    barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
                }

            }
        }

        private void ViewStatusItem_DownChanged(object sender, ItemClickEventArgs e)
        {

            if (SimpleViewStatusItem.Down)
            {
                MainRichEditControl.ActiveViewType = RichEditViewType.Simple;
            }

            if (PrintLayoutStatusItem.Down)
            {
                MainRichEditControl.ActiveViewType = RichEditViewType.PrintLayout;
            }

            if (DraftViewStatusItem.Down)
            {
                MainRichEditControl.ActiveViewType = RichEditViewType.Draft;
            }
        }

        private void ZoomBarEditItem_EditValueChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;

            int zoomValue = Convert.ToInt32(zoomBarEditItem.EditValue);
            isZoomChanging = true;

            try
            {
                MainRichEditControl.ActiveView.ZoomFactor = zoomValue / 100f;
                zoomBarEditItem.Caption = $"{zoomValue}%";
            }
            finally
            {
                isZoomChanging = false;
            }
        }

        private void ZoomResetItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            MainRichEditControl.ActiveView.ZoomFactor = 1;
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            base.OnClosing(e);
            // mainRibbonControl.Toolbar.SaveLayoutToXml(Configuration.saveToolbarToXmlFileName);
            // mainRibbonControl.Toolbar.SaveLayoutToRegistry("");
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            float zoomFactor = this.MainRichEditControl.ActiveView.ZoomFactor;

        }

        internal void CalculateDocumentStatistics()
        {
            DocumentIterator iterator = new(MainRichEditControl.Document, true);
            StaticsticsVisitor visitor = new(IncludeTextBoxes);
            while (iterator.MoveNext())
            {
                iterator.Current.Accept(visitor);
            }

            docStatBtnItem.Caption = $"{visitor.WordCount} Words";
        }

        internal void OnIncludeTextBoxesChanged()
        {
            CalculateDocumentStatistics();
        }

        internal void OnPagesInfoChanged()
        {
            pagesBarItem.Caption = $"Page {currentPage} of {pageCount}";
        }

        internal bool IncludeTextBoxes
        {
            get => _includeTextBoxes;
            set
            {
                if (_includeTextBoxes == value)
                {
                    return;
                }

                _includeTextBoxes = value;
                OnIncludeTextBoxesChanged();
            }
        }


        public void OpenFile(string docName, int docIndex)
        {

            if (!string.IsNullOrEmpty(docName))
            {
                // FileName = docName;
                switch (Path.GetExtension(docName))
                {
                    case "eml":
                        this.MainRichEditControl.LoadDocument(docName, DocumentFormat.Mht);
                        break;
                    default:
                        this.MainRichEditControl.LoadDocument(docName);
                        break;
                }

                //SetDocumentCaption(docName);
                return;
            }

            Text = $@"Document {docIndex}";

        }

        private void MainRichEditControl_DocumentLoaded(object sender, EventArgs e)
        {
            SetDocumentCaption(MainRichEditControl.Options.DocumentSaveOptions.CurrentFileName);
        }

        private void MainRichEditControl_DockChanged(object sender, EventArgs e)
        {


        }

        private void MainRichEditControl_BeforeImport(object sender, BeforeImportEventArgs e)
        {
            if (e.DocumentFormat == DocumentFormat.PlainText)
            {
                //Detect plain text encoding automatically:    
                ((PlainTextDocumentImporterOptions)e.Options).AutoDetectEncoding = true;
            }

            if (e.DocumentFormat == DocumentFormat.Doc)
            {
                //Disable loading comments added to removed ranges in DOC documents
                //((DocDocumentImporterOptions)e.Options).KeepCommentsForRemovedRanges = false;
            }

            if (e.DocumentFormat == DocumentFormat.Html)
            {
                //Load images synchronously with HTML documents
                //((HtmlDocumentImporterOptions)e.Options).AsyncImageLoading = false;
            }
        }

        private void MainRichEditControl_BeforeExport(object sender, BeforeExportEventArgs e)
        {

            if (e.DocumentFormat == DocumentFormat.PlainText)
            {
                //Include document fields in the exported plain text:
                PlainTextDocumentExporterOptions plainTextOptions = e.Options as PlainTextDocumentExporterOptions;
                plainTextOptions.ExportHiddenText = true;
                plainTextOptions.FieldCodeEndMarker = ">";
                plainTextOptions.FieldCodeStartMarker = "[<";
                plainTextOptions.FieldResultEndMarker = "]";
            }

            if (e.DocumentFormat == DocumentFormat.OpenXml)
            {
                //Specify what DOCX document properties to export:
                //OpenXmlDocumentExporterOptions docxOptions = e.Options as OpenXmlDocumentExporterOptions;
                //docxOptions.ExportedDocumentProperties = DocumentPropertyNames.Title | DocumentPropertyNames.LastModifiedBy | DocumentPropertyNames.Modified;
            }

            if (e.DocumentFormat == DocumentFormat.Html)
            {
                //Specify HTML export options:
                //HtmlDocumentExporterOptions htmlOptions = e.Options as HtmlDocumentExporterOptions;
                //htmlOptions.EmbedImages = true;
                //htmlOptions.CssPropertiesExportType = CssPropertiesExportType.Style;
                //htmlOptions.UseFontSubstitution = false;
            }
        }



        public string FileName { get; internal set; }

        public RichEditControl RichEditControlCore
        {
            get
            {
                return this.MainRichEditControl;
            }
        }

    }

}