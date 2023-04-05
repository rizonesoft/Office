﻿namespace Rizonesoft.Office.Verbum
{
    using DevExpress.Utils.Controls;
    using DevExpress.XtraBars;
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrintingLinks;
    using DevExpress.XtraRichEdit;
    using DevExpress.XtraRichEdit.API.Layout;
    using DevExpress.XtraRichEdit.API.Native;
    using DevExpress.XtraRichEdit.Export;
    using DevExpress.XtraRichEdit.Import;
    using DevExpress.XtraRichEdit.Services;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSpellChecker.Forms;
    using DevExpress.XtraSpellChecker.Native;
    using Rizonesoft.Office.Utilities;
    using Classes;
    using Forms;
    using Utilities;
    using System;
    using System.Drawing.Imaging;
    using System.Globalization;
    using System.IO;
    using System.Windows.Forms;
    using System.Drawing.Printing;
    using System.Windows.Controls.Ribbon;

    internal sealed partial class DocForm : RibbonForm
    {
        // ReSharper disable once InconsistentNaming
        private bool _includeTextBoxes;
        private int currentPage = 1;
        private bool isZoomChanging;
        private int pageCount = 1;

        public DocForm()
        {
            InitializeComponent();
            ChildRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;

            new RichEditExceptionHandler(ChildRichEditControl).Install();
            new SpellCheckerExceptionHandler(mainSpellChecker).Install();

            var commandFactory = new CustomCommandFactoryService(ChildRichEditControl, ChildRichEditControl.GetService<IRichEditCommandFactoryService>());
            ChildRichEditControl.ReplaceService<IRichEditCommandFactoryService>(commandFactory);

            // MainForm.SetSkins();

            exportBarButton.DefaultDropDownLink = exportPopupMenu.ItemLinks[0];
            exportPDFPopupMenuItem.ItemClick += ExportBarButton_ItemClick;
            exportEBUPopupMenuItem.ItemClick += ExportBarButton_ItemClick;
            exportImagePopupMenuItem.ItemClick += ExportBarButton_ItemClick;
            exportHTMLPopupMenuItem.ItemClick += ExportBarButton_ItemClick;
            exportMHTPopupMenuItem.ItemClick += ExportBarButton_ItemClick;
        }

        public DocForm(string fileName) : this()
        {
            ChildRichEditControl.LoadDocument(fileName);
            ChildRichEditControl.Modified = false;
            ChildRichEditControl.Focus();
        }

        public string FileName { get; private set; }

        /*
                public RichEditControl RichEditControlCore
                {
                    get
                    {
                        return this.ChildRichEditControl;
                    }
                }
        */

        private bool IncludeTextBoxes
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
                switch (Path.GetExtension(docName))
                {
                    case "eml":
                        ChildRichEditControl.LoadDocument(docName, DocumentFormat.Mht);
                        break;

                    default:
                        ChildRichEditControl.LoadDocument(docName);
                        break;
                }

                FileName = docName;
                return;
            }

            Text = $@"Document {docIndex}";
        }

        private void CalculateDocumentStatistics()
        {
            DocumentIterator iterator = new(ChildRichEditControl.Document, true);
            StaticsticsVisitor visitor = new(IncludeTextBoxes);
            while (iterator.MoveNext())
            {
                iterator.Current?.Accept(visitor);
            }

            docStatBtnItem.Caption = $@"{visitor.WordCount} Words";
        }

        private void OnIncludeTextBoxesChanged()
        {
            CalculateDocumentStatistics();
        }

        private void OnPagesInfoChanged()
        {
            pagesBarItem.Caption = $@"Page {currentPage} of {pageCount}";
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            // ReSharper disable once UnusedVariable
            var zoomFactor = this.ChildRichEditControl.ActiveView.ZoomFactor;
        }
        private void AddHyphenationDictionary(string hyphPath, CultureInfo hyphCulture)
        {
            OpenOfficeHyphenationDictionary hyphenationDictionary = new(hyphPath, hyphCulture);
            ChildRichEditControl.HyphenationDictionaries.Add(hyphenationDictionary);
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

        private void DocForm_Activated(object sender, EventArgs e)
        {
            if (MdiParent == null)
            {
                Owner = null;
            }
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

            ChildRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_OnChanged;
            LoadSpellingOptions();

            ChildRichEditControl.Modified = false;
            ChildRichEditControl.Focus();
        }
        private void DocRibbon_Merge(object sender, RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = true;
            licenseRibbonGroup.Visible = true;
        }

        private void DocRibbon_UnMerge(object sender, RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = false;
            licenseRibbonGroup.Visible = false;
        }

        private void DocStatBtnItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            using DocumentStatisticsForm docStatsForm = new(ChildRichEditControl.Document, IncludeTextBoxes);
            docStatsForm.LookAndFeel.ParentLookAndFeel = LookAndFeel;
            docStatsForm.ShowDialog();
            IncludeTextBoxes = docStatsForm.IncludeTextboxes;
        }

        private void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
            pageCount = ChildRichEditControl.DocumentLayout.GetPageCount();
            OnPagesInfoChanged();
        }

        private void DocumentSaveOptions_OnChanged(object sender, BaseOptionChangedEventArgs e)
        {
            if (e.Name != "CurrentFileName") return;
            SetDocumentCaption(ChildRichEditControl.Options.DocumentSaveOptions.CurrentFileName);
            FileName = ChildRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
        }

        private void DocumentStatsTimer_Tick(object sender, EventArgs e)
        {
            documentStatsTimer.Stop();
            BeginInvoke(CalculateDocumentStatistics);
        }

        private void DoExport(int filterIndex, string title)
        {
            try
            {
                SaveFileDialog saveFileDlg = new()
                {
                    // ReSharper disable once LocalizableElement
                    Filter = "Adobe PDF Files (*.pdf)|*.pdf|" +
                             "Adobe PDF Files, Optimized (*.pdf)|*.pdf|" +
                             "Electronic Publication (*.epub)|*.epub|" +
                             "Image (*.jpg; *.jpeg; *.png; *.gif; *.bmp; *.tiff; *.emf; *.wmf)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.emf;*.wmf|" +
                             "HyperText Markup Language Format (*.htm; *.html)|*.htm;*.html",
                    FilterIndex = filterIndex,
                    Title = title,
                    FileName = Path.GetFileNameWithoutExtension(FileName) ?? string.Empty
                };

                if (saveFileDlg.ShowDialog() != DialogResult.OK) return;
                if (saveFileDlg.FileName == "") return;
                var fileName = saveFileDlg.FileName;
                switch (saveFileDlg.FilterIndex)
                {
                    case 1:
                        ExportPdfWithOptions(fileName);
                        break;

                    case 2:
                        ExportPdfWithOptions(fileName, true);
                        break;

                    case 4:
                        ExportToImage(fileName);
                        break;

                    case 5:
                        ChildRichEditControl.SaveDocument(fileName, DocumentFormat.Html);
                        break;
                }
            }
            catch (Exception ex)
            {
                Logging.Logger.Error(ex.Message);
                XtraMessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ExportBarButton_ItemClick(object sender, ItemClickEventArgs e)
        {
            switch (e.Item.Tag)
            {
                case "PDF":
                    DoExport(1, "Export to PDF");
                    break;

                case "EPUB":
                    // MessageBox.Show(":)");
                    break;

                case "Image":
                    DoExport(4, "Export to HTML");
                    break;

                case "HTML":
                    DoExport(6, "Export to HTML");
                    break;

                case "MHT":
                    // MessageBox.Show(":)");
                    break;
            }
        }

        private void ExportPdfWithOptions(string fileName, bool compressed = false,
            bool convertImages = false, PdfJpegImageQuality pdfJpegImageQuality = PdfJpegImageQuality.High)
        {
            PdfExportOptions pdfOptions = new()
            {
                DocumentOptions =
                {
                    Author = $@"Rizonesoft Office {RizonesoftEx.ProductVersion.Major}"
                },
                Compressed = compressed,
                ConvertImagesToJpeg = convertImages,
                ImageQuality = pdfJpegImageQuality,
                ShowPrintDialogOnOpen = false,
                PdfUACompatibility = PdfUACompatibility.None,
                PdfACompatibility = PdfACompatibility.None
            };

            ChildRichEditControl.ExportToPdf(fileName, pdfOptions);
            ShellExecuteEx.OpenPdfDocument(fileName);
        }

        private void ExportToImage(string fileName)
        {
            var pcl = new PrintableComponentLinkBase(new PrintingSystemBase());
            pcl.Component = ((IRichEditControl)ChildRichEditControl).InnerControl;
            pcl.CreateDocument(false);

            var imgOptions = new ImageExportOptions
            {
                ExportMode = ImageExportMode.DifferentFiles
            };
            imgOptions.Format = Path.GetExtension(fileName) switch
            {
                ".jpg" => ImageFormat.Jpeg,
                ".jpeg" => ImageFormat.Jpeg,
                ".png" => ImageFormat.Png,
                ".gif" => ImageFormat.Gif,
                ".bmp" => ImageFormat.Bmp,
                ".tiff" => ImageFormat.Tiff,
                ".emf" => ImageFormat.Emf,
                ".wmf" => ImageFormat.Wmf,
                _ => imgOptions.Format
            };
            imgOptions.Resolution = 150;
            //imgOptions.PageRange = "1,3-5";

            pcl.ExportToImage(fileName, imgOptions);
        }

        private void LoadHyphenationDictionaries(DevExpress.XtraRichEdit.API.Native.Document document)
        {
            try
            {
                var dicFiles = Directory.GetFiles(StcVerbum.DictionariesPath);

                foreach (var sFile in dicFiles)
                {
                    if (!sFile.EndsWith(".dic", StringComparison.Ordinal))
                    {
                        continue;
                    }

                    var sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);
                    var sFileParts = sFileNoExtension.Split('_');
                    string sCultureString;

                    if (!sFileParts[0].Equals("hyph"))
                    { continue; }

                    switch (sFileParts.GetUpperBound(0))
                    {
                        case 2:
                            sCultureString = $"{sFileParts[1]}-{sFileParts[2]}";
                            break;
                        case 1:
                            sCultureString = sFileParts[1];
                            break;
                        default:
                            return;
                    }

                    AddHyphenationDictionary(sFile, new CultureInfo(sCultureString));
                }

                document.Hyphenation = true;
                document.HyphenateCaps = true;
            }
            catch (Exception ex)
            {
                Logging.Logger.Error(ex, "Whoops!");
                MessageBox.Show(ex.Message, @"Whoops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LoadSpellingOptions()
        {
            StcVerbum.SpellingLanguage = Settings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", mainSpellChecker.Culture.ToString());
            StcVerbum.AutoSpellCheck = RizonesoftEx.StringToBoolean(Settings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", "True") ?? "False");

            if (File.Exists(StcVerbum.CurrentSpellingXmlFile))
            { mainSpellChecker.RestoreFromXML(StcVerbum.CurrentSpellingXmlFile); }

            if (StcVerbum.SpellingLanguage != null)
                mainSpellChecker.Culture = new CultureInfo(StcVerbum.SpellingLanguage);
            barLangBtnItem.Caption = mainSpellChecker.Culture.EnglishName;
            autoSpellingItem.Checked = StcVerbum.AutoSpellCheck;
            LoadHyphenationDictionaries(ChildRichEditControl.Document);
        }

        private void MainRichEditControl_ActiveViewChanged(object sender, EventArgs e)
        {
            switch (ChildRichEditControl.ActiveViewType)
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
                default:
                    throw new ArgumentOutOfRangeException();
            }
        }

        private void MainRichEditControl_BeforeExport(object sender, BeforeExportEventArgs e)
        {
            if (e.DocumentFormat == DocumentFormat.PlainText)
            {
                //Include document fields in the exported plain text:
                if (e.Options is PlainTextDocumentExporterOptions plainTextOptions)
                {
                    plainTextOptions.ExportHiddenText = true;
                    plainTextOptions.FieldCodeEndMarker = ">";
                    plainTextOptions.FieldCodeStartMarker = "[<";
                    plainTextOptions.FieldResultEndMarker = "]";
                }
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

        private void MainRichEditControl_ContentChanged(object sender, EventArgs e)
        {
            documentStatsTimer.Start();
        }

        private void MainRichEditControl_DocumentLoaded(object sender, EventArgs e)
        {
            SetDocumentCaption(ChildRichEditControl.Options.DocumentSaveOptions.CurrentFileName);
        }

        private void MainRichEditControl_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerToolsChildRibbonCategory.Visible = false;
            DocRibbon.SelectedPage = hfToolsDesignChildRibPage;
        }

        private void mainRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
        {
            Logging.Logger.Warn($"Cannot open the file '{FileName}' because the file format or file extension is not valid.");
            XtraMessageBox.Show($"Cannot open the file '{FileName}' because the file format or file extension is not valid.\n" +
                "Verify that file has not been corrupted and that the file extension matches the format of the file.",
                "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        private void MainRichEditControl_SelectionChanged(object sender, EventArgs e)
        {
            if (ChildRichEditControl.DocumentLayout.IsDocumentFormattingCompleted)
            {
                var element = ChildRichEditControl.DocumentLayout.GetElement<RangedLayoutElement>(ChildRichEditControl.Document.CaretPosition);
                if (element != null)
                {
                    currentPage = ChildRichEditControl.DocumentLayout.GetPageIndex(element) + 1;
                    OnPagesInfoChanged();
                }

                CustomLayoutVisitor visitor = new(ChildRichEditControl.Document);

                for (var i = 0; i < ChildRichEditControl.DocumentLayout.GetPageCount(); i++)
                {
                    visitor.Reset();
                    var page = ChildRichEditControl.DocumentLayout.GetPage(i);
                    visitor.Visit(page);

                    if (!visitor.IsFound)
                    {
                        continue;
                    }

                    break;
                }

                if (visitor.IsFound)
                {
                    barCurrLineItem.Caption = $@"line {visitor.RowIndex}";
                    barCurrColumnItem.Caption = $@"Column {visitor.ColIndex}";
                }
            }

            try
            {
                var tableToolsCat = DocRibbon.MergeOwner.PageCategories["Table Tools"];
                var picToolsCat = DocRibbon.MergeOwner.PageCategories["Picture Tools"];
                var headToolsCat = DocRibbon.MergeOwner.PageCategories["Header & Footer Tools"];

                
                if (ChildRichEditControl.IsSelectionInTable())
                {
                    if (tableToolsCat != null) tableToolsCat.Visible = true;
                    DocRibbon.SelectPage(tableDesignChildRibbonPage);
                }


                if (picToolsCat != null)
                {
                    // To-Do: Complete logic
                    // picToolsCat.Visible = ChildRichEditControl.IsFloatingObjectSelected;
                }

                if (headToolsCat != null)
                {
                    // To-Do: Complete logic
                    // headToolsCat.Visible = ChildRichEditControl.IsSelectionInHeaderOrFooter;
                }
            }
            catch (Exception ex)
            {
                Logging.Logger.Error(ex.Message);
            }
        }

        private void MainRichEditControl_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerToolsChildRibbonCategory.Visible = true;
            // DocRibbon.SelectedPage = hfToolsDesignChildRibPage;
            // DocRibbon.MergeOwner.SelectedPage = DocRibbon.MergeOwner.PageCategories["Header & Footer Tools"].GetPageByText("Design");

        }

        private void MainRichEditControl_VisiblePagesChanged(object sender, EventArgs e)
        {
            currentPage = ChildRichEditControl.ActiveView.GetVisiblePageLayoutInfos()[0].PageIndex + 1;
        }

        private void MainRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;
            int zoomValue = (int)Math.Round(ChildRichEditControl.ActiveView.ZoomFactor * 100);
            isZoomChanging = true;

            try
            {
                zoomBarEditItem.EditValue = zoomValue;
                zoomBarEditItem.Caption = $@"{zoomValue}%";
            }
            finally
            {
                isZoomChanging = false;
            }
        }

        private bool SaveQuestion()
        {
            string tempName = FileName;
            if (string.IsNullOrEmpty(tempName))
            {
                tempName = Text;
            }

            if (ChildRichEditControl.Modified)
            {
                switch (XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{tempName}\"?",
                                  "Warning",
                                  MessageBoxButtons.YesNoCancel,
                                  MessageBoxIcon.Warning))
                {
                    case DialogResult.Cancel:
                        return false;

                    case DialogResult.Yes:
                        ChildRichEditControl.SaveDocument();
                        break;
                }
            }
            return true;
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
        private void spellOptionsItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            var spellOptions = this.mainSpellChecker.GetSpellCheckerOptions(this.ChildRichEditControl);
            this.mainSpellChecker.OptionsSpelling.CombineOptions(spellOptions);
            using SpellingOptionsForm spellOptionsForm = new SpellingOptionsForm(this.mainSpellChecker);
            spellOptionsForm.Init();
            if (spellOptionsForm.ShowDialog(this) != DialogResult.OK) return;
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

            mainSpellChecker.SetSpellCheckerOptions(ChildRichEditControl, spellOptions);
            mainSpellChecker.OptionsSpelling.CombineOptions(mainSpellChecker.GetSpellCheckerOptions(this.ChildRichEditControl));
            mainSpellChecker.SaveToXML(StcVerbum.CurrentSpellingXmlFile);
            StcVerbum.SpellingLanguage = mainSpellChecker.Culture.ToString();
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", StcVerbum.SpellingLanguage);
            barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
        }
        private void ViewStatusItem_DownChanged(object sender, ItemClickEventArgs e)
        {
            if (SimpleViewStatusItem.Down)
            {
                ChildRichEditControl.ActiveViewType = RichEditViewType.Simple;
            }

            if (PrintLayoutStatusItem.Down)
            {
                ChildRichEditControl.ActiveViewType = RichEditViewType.PrintLayout;
            }

            if (DraftViewStatusItem.Down)
            {
                ChildRichEditControl.ActiveViewType = RichEditViewType.Draft;
            }
        }
        private void ZoomBarEditItem_EditValueChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;

            var zoomValue = Convert.ToInt32(zoomBarEditItem.EditValue);
            isZoomChanging = true;

            try
            {
                ChildRichEditControl.ActiveView.ZoomFactor = zoomValue / 100f;
                zoomBarEditItem.Caption = $@"{zoomValue}%";
            }
            finally
            {
                isZoomChanging = false;
            }
        }

        private void ZoomResetItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            ChildRichEditControl.ActiveView.ZoomFactor = 1;
        }
    }
}