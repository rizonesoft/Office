

namespace Rizonesoft.Office.Verbum
{
    using DevExpress.LookAndFeel;
    using DevExpress.Services;
    using DevExpress.Utils.Controls;
    using DevExpress.XtraBars;
    using DevExpress.XtraBars.Docking;
    using DevExpress.XtraEditors;
    using DevExpress.XtraRichEdit;
    using DevExpress.XtraRichEdit.API.Layout;
    using DevExpress.XtraRichEdit.API.Native;
    using DevExpress.XtraRichEdit.Services;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSpellChecker.Forms;
    using DevExpress.XtraSpellChecker.Native;
    using Rizonesoft.Office.Debugging;
    using Rizonesoft.Office.ROUtilities;
    using Rizonesoft.Office.Verbum.Classes;
    using Rizonesoft.Office.Verbum.Forms;
    using Rizonesoft.Office.Verbum.Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Globalization;
    using System.IO;
    using System.Windows.Forms;
    using static System.Windows.Forms.Design.AxImporter;

    public partial class DocForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        internal bool _includeTextBoxes = false;
        internal bool isZoomChanging;

        #region Properties

        public string FileName { get; internal set; }

        #endregion Properties

        public DocForm()
        {
            InitializeComponent();
            mainRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
            mainRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_Changed;

            new RichEditExceptionHandler(mainRichEditControl).Install();
            new SpellCheckerExceptionHandler(mainSpellChecker).Install();

            CustomCommandListenerService customComExecListenerService = new();
            CustomCommandListenerService service = customComExecListenerService;
            service.RichEditControl = mainRichEditControl;
            service.CommandExecutedEvent += Service_CommandExecutedEvent;
            mainRichEditControl.RemoveService(typeof(ICommandExecutionListenerService));
            mainRichEditControl.AddService(typeof(ICommandExecutionListenerService), service);
            debugComPanel.Visibility = DockVisibility.Hidden;

            var commandFactory = new CustomCommandFactoryService(mainRichEditControl, mainRichEditControl.GetService<IRichEditCommandFactoryService>());
            mainRichEditControl.ReplaceService<IRichEditCommandFactoryService>(commandFactory);
            MainForm.SetSkins();
            

            //
            // coreSpellChecker.Culture = CultureInfo.;

            // InitializeRichEditControl();
            // coreRibbonControl.SelectedPage = homeRibbonPage1;

            // this.headerFooterToolsRibbonPageCategory.Visible = false;
            // this.tableToolsRibbonPageCategory.Visible = false;
            // this.floatingPictureToolsRibbonPageCategory.Visible = false;

        }



        public string DocumentFormTitle
        {
            get
            {
                return this.Text;
            }
        }



        public RichEditControl RichEditControlCore
        {
            get
            {
                return this.mainRichEditControl;
            }
        }

        #region Review



        #endregion

        #region Events

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            float zoomFactor = this.mainRichEditControl.ActiveView.ZoomFactor;

        }

        private void DocForm_Load(object sender, EventArgs e)
        {

            if (DesignMode)
            {
                return;
            }

            // this.mainRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
            this.mainRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_OnChanged;

            LoadSpellingOptions();


            this.mainRichEditControl.Modified = false;
            this.mainRichEditControl.Focus();
        }

        private void DocForm_Activated(object sender, EventArgs e)
        {
            if (MdiParent == null)
            {
                Owner = null;
            }
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            base.OnClosing(e);
            // mainRibbonControl.Toolbar.SaveLayoutToXml(Configuration.saveToolbarToXmlFileName);
            // mainRibbonControl.Toolbar.SaveLayoutToRegistry("");
        }

        private void MainRichEditControl_DocumentClosing(object sender, CancelEventArgs e)
        {

        }

        private void mainRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
        {
            // string currentFileName = mainRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
            // nlogger.Error(string.Format("Cannot open the file '{0}' because the file format or file extension is not valid.", currentFileName));
            // XtraMessageBox.Show(string.Format("Cannot open the file '{0}' because the file format or file extension is not valid.\n" +
            // "Verify that file has not been corrupted and that the file extension matches the format of the file.", currentFileName),
            // "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);

        }


        private void mainRichEditControl_DocumentLoaded(object sender, EventArgs e)
        {
            //string currentFileName = this.mainRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
            //Text = currentFileName;

            //CharacterProperties cp = coreRichEditControl.Document.BeginUpdateCharacters(coreRichEditControl.Document.Range);
            //cp.Language = new DevExpress.XtraRichEdit.Model.LangInfo(coreSpellChecker.Culture, coreSpellChecker.Culture, coreSpellChecker.Culture);
            //coreRichEditControl.Document.EndUpdateCharacters(cp);
        }

        private void DocumentSaveOptions_OnChanged(object sender, BaseOptionChangedEventArgs e)
        {
            if (e.Name == "CurrentFileName")
            {
                string sFileName = e.NewValue.ToString();
                SetDocumentCaption(sFileName);
                //if (mainRichEditControl.Modified)
                //Text = Text[0..^2];
                // Text = mainRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
            }
        }



        private void spellOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsSpelling spellOptions = this.mainSpellChecker.GetSpellCheckerOptions(this.mainRichEditControl);
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

                    mainSpellChecker.SetSpellCheckerOptions(mainRichEditControl, spellOptions);
                    mainSpellChecker.OptionsSpelling.CombineOptions(mainSpellChecker.GetSpellCheckerOptions(this.mainRichEditControl));
                    mainSpellChecker.SaveToRegistry(StcVerbum.StaticRegSpellingPath);
                    StcVerbum.SpellingLanguage = mainSpellChecker.Culture.ToString();
                    ROSettings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", StcVerbum.SpellingLanguage);
                    // barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
                }

            }
        }



        #endregion Events



        

        #region DocForm Events (Overrides)

        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (this.mainRichEditControl.Modified)
            {
                DialogResult result = XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{FileName}\"?",
                                          "Warning",
                                          MessageBoxButtons.YesNoCancel,
                                          MessageBoxIcon.Warning);
                if (result == DialogResult.Yes)
                {
                    mainRichEditControl.SaveDocument();
                }

                e.Cancel = result == DialogResult.Cancel;
            }
        }

        #endregion DocForm Events (Overrides)

        #region Document Processing

        public void OpenFile(string docName, int docIndex)
        {

            if (!string.IsNullOrEmpty(docName))
            {
                FileName = docName;
                switch (Path.GetExtension(docName))
                {
                    case "eml":
                        this.mainRichEditControl.LoadDocument(docName, DocumentFormat.Mht);
                        break;
                    default:
                        this.mainRichEditControl.LoadDocument(docName);
                        break;
                }

                SetDocumentCaption(docName);
                return;
            }
            Text = FileName = $@"Document {docIndex}";
        }

        private void SetDocumentCaption(string fileName)
        {
            if (string.IsNullOrEmpty(fileName)) return;

            string fileCaption = Path.GetFileName(fileName);
            if (fileCaption.Length > 28)
            {
                fileCaption = $"{fileCaption.Remove(29)}...";
            }
            Text = fileCaption;
        }

        void DocumentSaveOptions_Changed(object sender, BaseOptionChangedEventArgs e)
        {

        }

        #endregion Document Processing

        #region Spelling (Dictionaries)

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

        private void LoadSpellingOptions()
        {
            StcVerbum.SpellingLanguage = ROSettings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "SpellingLanguage", mainSpellChecker.Culture.ToString());
            StcVerbum.AutoSpellCheck = ROFunctions.StringToBoolean(ROSettings.Settings.GetSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", "True"));
            mainSpellChecker.RestoreFromRegistry(StcVerbum.StaticRegSpellingPath);

            mainSpellChecker.Culture = new CultureInfo(StcVerbum.SpellingLanguage);
            barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
            autoSpellingItem.Checked = StcVerbum.AutoSpellCheck;
            LoadHyphenationDictionaries(mainRichEditControl.Document);
        }

        private void LoadHyphenationDictionaries(Document document)
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

                    if (!sFileParts[0].Equals("hyph"))
                    {
                        continue;
                    }

                    AddHyphenationDictionary(sFile, new CultureInfo($"{sFileParts[1]}-{sFileParts[2]}"));
                }

                document.Hyphenation = true;
                document.HyphenateCaps = true;

            }
            catch (Exception ex)
            {
                ROLogging.ROLogger.Error(ex, "Whoops!");
                MessageBox.Show(ex.Message, "Whoops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void AddHyphenationDictionary(string hyphPath, CultureInfo hyphCulture)
        {
            OpenOfficeHyphenationDictionary hyphenationDictionary = new(hyphPath, hyphCulture);
            mainRichEditControl.HyphenationDictionaries.Add(hyphenationDictionary);

        }

        #endregion Spelling (Dictionaries)

        #region Document Statistics

        internal int pageCount = 1;
        internal int currentPage = 1;

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

        internal void OnIncludeTextBoxesChanged()
        {
            CalculateDocumentStatistics();
        }

        internal void OnPagesInfoChanged()
        {
            pagesBarItem.Caption = $"Page {currentPage} of {pageCount}";
        }

        internal void CalculateDocumentStatistics()
        {
            DocumentIterator iterator = new(mainRichEditControl.Document, true);
            StaticsticsVisitor visitor = new(IncludeTextBoxes);
            while (iterator.MoveNext())
            {
                iterator.Current.Accept(visitor);
            }

            docStatBtnItem.Caption = $"{visitor.WordCount} Words";
        }

        private void MainRichEditControl_SelectionChanged(object sender, EventArgs e)
        {

            if (mainRichEditControl.DocumentLayout.IsDocumentFormattingCompleted)
            {
                RangedLayoutElement element = mainRichEditControl.DocumentLayout.GetElement<RangedLayoutElement>(mainRichEditControl.Document.CaretPosition);
                if (element != null)
                {
                    currentPage = mainRichEditControl.DocumentLayout.GetPageIndex(element) + 1;
                    OnPagesInfoChanged();
                }

                CustomLayoutVisitor visitor = new(mainRichEditControl.Document);

                for (int i = 0; i < mainRichEditControl.DocumentLayout.GetPageCount(); i++)
                {
                    visitor.Reset();
                    LayoutPage page = mainRichEditControl.DocumentLayout.GetPage(i);
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

        }

        private void MainRichEditControl_VisiblePagesChanged(object sender, EventArgs e)
        {
            currentPage = mainRichEditControl.ActiveView.GetVisiblePageLayoutInfos()[0].PageIndex + 1;
        }

        private void MainRichEditControl_ContentChanged(object sender, EventArgs e)
        {
            documentStatsTimer.Start();
        }

        private void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
            pageCount = mainRichEditControl.DocumentLayout.GetPageCount();
            OnPagesInfoChanged();
        }

        private void DocumentStatsTimer_Tick(object sender, EventArgs e)
        {
            documentStatsTimer.Stop();
            BeginInvoke(new Action(CalculateDocumentStatistics));
        }

        private void DocStatBtnItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            using DocumentStatisticsForm docStatsForm = new(mainRichEditControl.Document, IncludeTextBoxes);
            docStatsForm.LookAndFeel.ParentLookAndFeel = LookAndFeel;
            docStatsForm.ShowDialog();
            IncludeTextBoxes = docStatsForm.IncludeTextboxes;
        }

        #endregion Document Statistics

        #region Zoom

        private void ZoomResetItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            mainRichEditControl.ActiveView.ZoomFactor = 1;
        }

        private void MainRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;
            int zoomValue = (int)Math.Round(mainRichEditControl.ActiveView.ZoomFactor * 100);
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

        private void ZoomBarEditItem_EditValueChanged(object sender, EventArgs e)
        {
            if (isZoomChanging) return;

            int zoomValue = Convert.ToInt32(zoomBarEditItem.EditValue);
            isZoomChanging = true;

            try
            {
                mainRichEditControl.ActiveView.ZoomFactor = zoomValue / 100f;
                zoomBarEditItem.Caption = $"{zoomValue}%";
            }
            finally
            {
                isZoomChanging = false;
            }
        }

        #endregion Zoom

        #region Developer Tools (Debugging)

        private void Service_CommandExecutedEvent(object sender, CommandEventArgs e)
        {
            if (!Debugging.IsDebugging) return;
            if ((sender == null) || (e == null)) return;

            if (!IsShowCommand(e.CommandName.ToString(), new List<string>
            {
                "DevExpress.XtraRichEdit.Commands.InsertTextCommand",
                "DevExpress.XtraRichEdit.Commands.Internal.ExtendSelectionByCharactersCommand"
            }))
            {
                debugComMemoEdit.AppendText($"{e.CommandName}{Environment.NewLine}Description: {e.CommandDescription}{Environment.NewLine}");
            }

        }

        private static bool IsShowCommand(string command, List<string> richEditCommands)
        {

            if (richEditCommands.Contains(command))
            {
                return true;
            }

            return false;
        }

        private void ComBarBtnItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            debugComPanel.Visibility = comBarBtnItem.Down ? DockVisibility.Visible : DockVisibility.Hidden;
            Debugging.IsDebugging = comBarBtnItem.Down;

        }

        #endregion Developer Tools (Debugging)

    }

}