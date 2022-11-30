using DevExpress.LookAndFeel;
using DevExpress.Utils.Controls;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSpellChecker.Forms;
using DevExpress.XtraSpellChecker.Native;
using Rizonesoft.Office.Verbum.Classes;
using Rizonesoft.Office.Verbum.Forms;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Windows.Forms;

namespace Rizonesoft.Office.Verbum
{
    public partial class DocForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        private static NLog.Logger nlogger = NLog.LogManager.GetCurrentClassLogger();
        private static int wordCount = 0;
        internal bool _includeTextBoxes = false;
        internal bool _isZoomChanging = false;
        internal string fileName;

        public DocForm()
        {
            InitializeComponent();
            this.mainRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;



            UserLookAndFeel.Default.StyleChanged += Default_StyleChanged;
            new RichEditExceptionHandler(mainRichEditControl).Install();
            new SpellCheckerExceptionHandler(mainSpellChecker).Install();

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

        public string FileName
        {
            get
            {
                return this.fileName;
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

            loadSpellingOptions();
            // autoSpellingSwitch();

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

        private void Default_StyleChanged(object sender, EventArgs e)
        {
            Configure.Settings.SaveSetting("Rizonesoft\\Office\\Skins", "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Configure.Settings.SaveSetting("Rizonesoft\\Office\\Skins", "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
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

        private void autoSpellingItem_CheckedChanged(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Globals.AutoSpellCheck = this.autoSpellingItem.Checked;
            autoSpellingSwitch();
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

                    this.mainSpellChecker.SetSpellCheckerOptions(this.mainRichEditControl, spellOptions);
                    this.mainSpellChecker.OptionsSpelling.CombineOptions(this.mainSpellChecker.GetSpellCheckerOptions(this.mainRichEditControl));
                    this.mainSpellChecker.SaveToRegistry("Software\\Rizonesoft\\Verbum");
                    Globals.SpellingLanguage = this.mainSpellChecker.Culture.ToString();
                    Configure.Settings.SaveSetting("Rizonesoft\\Verbum\\Spelling", "SpellingLanguage", Globals.SpellingLanguage);
                    // barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
                }

            }
        }

        private void zoomResetItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            mainRichEditControl.ActiveView.ZoomFactor = 1;
        }

        #endregion Events


        #region Spelling

        private void loadSpellingOptions()
        {

            Globals.SpellingLanguage = Configure.Settings.GetSetting("Rizonesoft\\Verbum\\Spelling", "SpellingLanguage", this.mainSpellChecker.Culture.ToString());
            this.mainSpellChecker.RestoreFromRegistry("Software\\Rizonesoft\\Verbum");

            this.mainSpellChecker.Culture = new CultureInfo(Globals.SpellingLanguage);
            barLangBtnItem.Caption = this.mainSpellChecker.Culture.EnglishName;
            this.autoSpellingItem.Checked = Globals.AutoSpellCheck;
            LoadHyphenationDictionaries(mainRichEditControl.Document);
        }

        private void LoadHyphenationDictionaries(Document document)
        {
            try
            {
                string[] dicFiles = Directory.GetFiles(Globals.DictionariesPath);

                foreach (string sFile in dicFiles)
                {
                    if (sFile.EndsWith(".dic"))
                    {
                        string sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);
                        string[] sFileParts = sFileNoExtension.Split('_');

                        if (sFileParts[0].Equals("hyph"))
                        {
                            AddHyphenationDictionary(sFile,
                            new CultureInfo(String.Format("{0}-{1}", sFileParts[1], sFileParts[2])));
                        }

                    }
                }

                document.Hyphenation = true;
                document.HyphenateCaps = true;

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message,
                    "Bummer!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }
        }

        private void AddHyphenationDictionary(string hyphPath, CultureInfo hyphCulture)
        {
            OpenOfficeHyphenationDictionary hyphenationDictionary = new OpenOfficeHyphenationDictionary(hyphPath, hyphCulture);
            this.mainRichEditControl.HyphenationDictionaries.Add(hyphenationDictionary);

        }

        private void autoSpellingSwitch()
        {
            if (this.autoSpellingItem.Checked)
            {
                Globals.AutoSpellCheck = true;
                this.mainSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
            }
            else
            {
                Globals.AutoSpellCheck = false;
                this.mainSpellChecker.SpellCheckMode = SpellCheckMode.OnDemand;
            }
        }

        #endregion Spelling


        #region Document Handling

        //private void processFileName(string fileName, int docIndex)
        //{
        //DocForm docForm = this;
        //if (!String.IsNullOrEmpty(fileName))
        //{
        //FileInfo fileInf = new FileInfo(fileName);
        //docForm.mainRichEditControl.LoadDocument(fileName);
        //docForm.Text = fileInf.Name + " - " + docForm.Text;
        //}
        //else
        //{
        //docForm.Text = @"Document " + docIndex.ToString() + " - Rizonesoft Verbum";
        //}
        //}

        public void OpenFile(string docName, int docIndex)
        {
            if (!string.IsNullOrEmpty(docName))
            {
                this.fileName = docName;
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
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + string.Empty;
            }
        }

        private void SetDocumentCaption(string fileName)
        {
            string fileCaption = Path.GetFileName(fileName);
            if (fileCaption.Length > 28)
            {
                fileCaption = fileCaption.Remove(29) + "...";
            }
            this.Text = fileCaption;
        }

        #endregion Document Handling


        #region Zoom

        private void zoomBarEditItem_EditValueChanged(object sender, EventArgs e)
        {
            DocForm docForm = this;
            if (docForm._isZoomChanging)
            { return; }

            int value = Convert.ToInt32(docForm.zoomBarEditItem.EditValue);
            docForm._isZoomChanging = true;
            try
            {
                docForm.mainRichEditControl.ActiveView.ZoomFactor = value / 100f;
                docForm.zoomBarEditItem.Caption = String.Format("{0}%", value);
            }
            finally
            {
                docForm._isZoomChanging = false;
            }
        }

        private void mainRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
            DocForm docForm = this;
            if (docForm._isZoomChanging)
                return;
            int value = (int)Math.Round(docForm.mainRichEditControl.ActiveView.ZoomFactor * 100);
            docForm._isZoomChanging = true;
            try
            {
                docForm.zoomBarEditItem.EditValue = value;
                docForm.zoomBarEditItem.Caption = String.Format("{0}%", value);
            }
            finally
            {
                docForm._isZoomChanging = false;
            }
        }

        #endregion Zoom



        #region Document Processing
        #endregion Document Processing

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






        private void mainRichEditControl_ModifiedChanged(object sender, EventArgs e)
        {
           // if (mainRichEditControl.Modified)
           // {
               // Text += " *";
           // }

        }

        private void mainRichEditControl_AfterExport(object sender, EventArgs e)
        {

        }

        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (this.mainRichEditControl.Modified)
            {
                string message = $"Do you want to save the changes you made for '{Text}'?";
                DialogResult result = XtraMessageBox.Show(message, "Warning", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Warning);
                if (result == DialogResult.Yes)
                {
                    mainRichEditControl.SaveDocument();
                }

                e.Cancel = result == DialogResult.Cancel;
            }
        }
    }

}