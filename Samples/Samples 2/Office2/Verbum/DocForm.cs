using DevExpress.Utils.Controls;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraSpellChecker;
using Rizonesoft.Office.Verbum.Classes;
using Rizonesoft.Office.Verbum.Forms;
using Rizonesoft.Office.Verbum.Helpers;
using Rizonesoft.Office.Verbum.Properties;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Windows.Forms;


namespace Rizonesoft.Office.Verbum
{
    public partial class DocForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        private static readonly log4net.ILog bugLog = log4net.LogManager.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        bool _isZoomChanging = false;
        bool _includeTextBoxes = false;
        int pageCount = 1;
        int currentPage = 1;
        private string newFileName;


        

        

        private void processFileName(string fileName, int docIndex)
        {

            if (!String.IsNullOrEmpty(fileName))
            {
                FileInfo fileInf = new FileInfo(fileName);
                this.coreRichEditControl.LoadDocument(fileName);
                this.Text = fileInf.Name + " - " + this.Text;
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + " - " + this.Text;
            }

        }

        private void loadFile()
        {
        }

        

        public string FileName
        {
            get { return newFileName; }
            set { newFileName = value; }
        }






















        public DocForm()
        {
            InitializeComponent();
            LoadConfiguration();

            new RichEditExceptionHandler(coreRichEditControl).Install();
            new SpellCheckerExceptionHandler(coreSpellChecker).Install();

            

            this.headerFooterToolsRibbonPageCategory.Visible = false;
            this.tableToolsRibbonPageCategory.Visible = false;
            this.floatingPictureToolsRibbonPageCategory.Visible = false;
        }


        #region Configuration

        /// <summary>
        /// Load various configurations.
        /// </summary>
        private void LoadConfiguration()
        {
            Configuration.GeometryFromString(Settings.Default.WindowGeometry, this);
            Configuration.autoSpellCheck = Settings.Default.AutoSpellCheck;
        }


        private void SaveConfiguration()
        {
            Settings.Default.WindowGeometry = Configuration.GeometryToString(this);
            Settings.Default.AutoSpellCheck = Configuration.autoSpellCheck;
            Settings.Default.Save();
        }


        private void optionsBarItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                OptionsForm optionsDlg = new OptionsForm();
                // optionsDlg.coreOptionsTab.SelectedTabPageIndex = 1;
                optionsDlg.Show(this);
            }
            catch (Exception ex)
            {
                bugLog.Error(ex.Message.ToString());
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        #endregion


        #region Backstage



        #endregion


        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveConfiguration();

            if (coreRichEditControl.Modified)
            {
                string currentFileName = coreRichEditControl.Options.DocumentSaveOptions.CurrentFileName;
                string message = !string.IsNullOrEmpty(currentFileName) ?
                    string.Format("Do you want to save the changes you made for '{0}'?", currentFileName) : "Do you want to save the changes?";
                DialogResult result = XtraMessageBox.Show(message, "Warning", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Warning);
                if (result == DialogResult.Yes)
                {
                    coreRichEditControl.SaveDocument();
                }

                e.Cancel = result == DialogResult.Cancel;
            }
        }




























        public DocForm(string fileName, int docIndex)
            : this()
        {
            newFileName = fileName;
            processFileName(newFileName, docIndex);
        }


        #region File Page

        private void fileCustomNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewFile();
        }

        private void iOpen_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            

        }

        private void CreateNewFile(string newFileName = "")
        {
            CopyData copyData = new CopyData();
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            copyData.Channels["DocChannel"].Send(newFileName);
        }

        private void fileOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            
        }

        private void OpenFile()
        {

        }


















































































        // private void iPageSetup_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        // {
            //PageSetupDialog settings
            //pageSetupDlg.Document = printDoc;
            //pageSetupDlg.AllowMargins = false;
            //pageSetupDlg.AllowOrientation = false;
            //pageSetupDlg.AllowPaper = false;
            //pageSetupDlg.AllowPrinter = false;
            //pageSetupDlg.Reset();

            // if (pageSetupDlg.ShowDialog() == DialogResult.OK)
            // {

                // printDoc.DefaultPageSettings = pageSetupDlg.PageSettings;

                // coreDoc.Document.Sections[0].Page.PaperKind = printDoc.DefaultPageSettings.PaperSize.Kind;
                //coreDoc.Document.Sections[0].Page.PaperKind = printSystem.PageSettings.PaperKind;
                // coreDoc.Document.Sections[0].Page.Landscape = printDoc.DefaultPageSettings.Landscape;
                // coreDoc.Document.Sections[0].Margins.Left = printDoc.DefaultPageSettings.Margins.Left;

                //printDoc.DefaultPageSettings =
                //setupDlg.PageSettings;
                //printDoc.PrinterSettings =
                //setupDlg.PrinterSettings;
            // }

            //printCoreDocLink.CreateDocument();
            //printSystem.PreviewFormEx.Show();
            //printSystem.PageSetup();



            //coreDoc.ActiveViewType = DevExpress.XtraRichEdit.RichEditViewType.PrintLayout;
            //coreDoc.ActiveView.ZoomFactor = 0.5f;
        // }

        // private void coreDoc_BeforeExport(object sender, DevExpress.XtraRichEdit.BeforeExportEventArgs e)
        // {
            // DocumentExportCapabilities checkDocument = coreDoc.Document.RequiredExportCapabilities;
            // if ((e.DocumentFormat == DocumentFormat.Rtf) && checkDocument.InlinePictures)
            // {
                // if ((bool)Settings.Default["CompactFormat"])
                // {
                    // RtfDocumentExporterOptions options = e.Options as RtfDocumentExporterOptions;
                    // if (options != null) options.Compatibility.DuplicateObjectAsMetafile = false;
                // }
            // }
        // }

        #endregion  File Menu

        private void coreRichEditControl_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerFooterToolsRibbonPageCategory.Visible = true;
            coreRibbonControl.SelectedPage = headerFooterToolsDesignRibbonPage;
        }

        private void coreRichEditControl_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            headerFooterToolsRibbonPageCategory.Visible = false;
            coreRibbonControl.SelectedPage = headerFooterToolsDesignRibbonPage;
        }

        void OnPagesInfoChanged()
        {
            pagesBarItem.Caption = String.Format("Page {0} of {1}", currentPage, pageCount);
        }


        









        private void frmDoc_Load(object sender, EventArgs e)
        {
            coreRichEditControl.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
            coreRichEditControl.Options.DocumentSaveOptions.Changed += DocumentSaveOptions_OnChanged;
            coreRibbonControl.SelectedPage = homeRibbonPage;

            // coreRichEditControl.HyphenationDictionaries.Add(new OpenOfficeHyphenationDictionary(System.Windows.Forms.Application.StartupPath + @"\Dictionaries\af_ZA.dic", new System.Globalization.CultureInfo("af-ZA")));

        }



        private void DocumentSaveOptions_OnChanged(object sender, BaseOptionChangedEventArgs e)
        {

            if (e.Name == "CurrentFileName")
            {
                string sFileName = e.NewValue.ToString();

                bugLog.Info("Options.DocumentSaveOptions.Changed");
                bugLog.Info("Adding [" + sFileName + "] to Most Recent List (MRU).");

            }

        }

        













        void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
            BeginInvoke(new Action(() => {
                pageCount = coreRichEditControl.DocumentLayout.GetPageCount();
            }));

            OnPagesInfoChanged();
        }

        private void coreRichEditControl_VisibleChanged(object sender, EventArgs e)
        {
            currentPage = coreRichEditControl.ActiveView.GetVisiblePageLayoutInfos()[0].PageIndex + 1;
            OnPagesInfoChanged();
        }

        private void coreRichEditControl_SelectionChanged(object sender, EventArgs e)
        {
            RangedLayoutElement element = coreRichEditControl.DocumentLayout.GetElement<RangedLayoutElement>(coreRichEditControl.Document.CaretPosition);
            if (element != null)
            {
                currentPage = coreRichEditControl.DocumentLayout.GetPageIndex(element) + 1;
            }

            OnPagesInfoChanged();

            tableToolsRibbonPageCategory.Visible = coreRichEditControl.IsSelectionInTable();
            floatingPictureToolsRibbonPageCategory.Visible = coreRichEditControl.IsFloatingObjectSelected;

        }

        private void coreRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
            
        }

        private void coreRichEditControl_ContentChanged(object sender, EventArgs e)
        {
            documentStatsTimer.Start();
        }

        private void documentStatsTimer_Tick(object sender, EventArgs e)
        {
            documentStatsTimer.Stop();
            BeginInvoke(new Action(CalculateDocumentStatistics));
        }

        void OnIncludeTextBoxesChanged()
        {
            CalculateDocumentStatistics();
        }

        void CalculateDocumentStatistics()
        {
            DocumentIterator iterator = new DocumentIterator(coreRichEditControl.Document, true);
            StaticsticsVisitor visitor = new StaticsticsVisitor(IncludeTextBoxes);
            while (iterator.MoveNext()) {
                iterator.Current.Accept(visitor);
            }

            docStatBtnItem.Caption = String.Format("{0} words", visitor.WordCount);
        }

        private void docStatBtnItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            using (DocumentStatisticsForm form = new DocumentStatisticsForm(coreRichEditControl.Document, IncludeTextBoxes))
            {
                form.LookAndFeel.ParentLookAndFeel = LookAndFeel;
                form.ShowDialog();
                IncludeTextBoxes = form.IncludeTextboxes;
            }
        }

        private void coreRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
        {
            XtraMessageBox.Show(string.Format("Cannot open the file '{0}' because the file format or file extension is not valid.\n" +
                "Verify that file has not been corrupted and that the file extension matches the format of the file.", coreRichEditControl.Options.DocumentSaveOptions.CurrentFileName),
                "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

        private void barButtonItem2_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {

        }

        private void barStaticItem1_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {

        }

        private void coreRichEditControl_Click(object sender, EventArgs e)
        {

        }

        
    }
}

