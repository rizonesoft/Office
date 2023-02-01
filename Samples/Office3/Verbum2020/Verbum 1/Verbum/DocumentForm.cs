using System;
using System.IO;
using DevExpress.XtraBars;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using System.Windows.Forms;
using DevExpress.XtraEditors.Controls;
using DevExpress.XtraSpellChecker;
using Rizonesoft.Verbum.Properties;
using DevExpress.XtraEditors;

namespace Rizonesoft.Verbum
{
    public partial class DocumentForm : DevExpress.XtraEditors.XtraForm
    {
        private static int wordCount = 0;

        string fileName;
        public string FileName
        { get { return this.fileName; } }

        public DocumentForm()
        {
            InitializeComponent();

            EmlDocumentExporter.Register(mainDoc);
            EmlDocumentImporter.Register(mainDoc);

            new RichEditUnhandledExceptionsHandler(this.mainDoc).Install();
            new SpellCheckerUnhandledExceptionHandler(this.coreSpellChecker).Install();

            this.coreHelp.HelpNamespace = Application.StartupPath + "\\Documentation\\Verbum.chm";
        }

        private void DocumentForm_Load(object sender, EventArgs e)
        {
            if (DesignMode) { return; }


            this.autoSpellingItem.Checked = Configuration.autoSpellCheck;
            autoSpellingSwitch();
            
            this.headerFooterBar.Visible = false;
            this.tableBar.Visible = false;

            this.mainDoc.Focus();
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            float zoomFactor = this.mainDoc.ActiveView.ZoomFactor;
            UpdateZoomTrackbarCore(zoomFactor);
            UpdateZoomCaption(zoomFactor);
            SubscribeZoomChangedEvent();
            SubscribeZoomTrackbarEvents();
        }

        private void DocumentForm_Activated(object sender, EventArgs e)
        {
            if (MdiParent == null)
            {
                Owner = null;
            }
        }


        #region Zoom-Zoom

        void SubscribeZoomTrackbarEvents()
        {
            this.zoomTrackBar.Edit.EditValueChanging += new ChangingEventHandler(OnZoomTrackBarEditValueChanging);
        }
        void UnsubscribeZoomTrackbarEvents()
        {
            this.zoomTrackBar.Edit.EditValueChanging -= new ChangingEventHandler(OnZoomTrackBarEditValueChanging);
        }
        void SubscribeZoomChangedEvent()
        {
            this.mainDoc.ZoomChanged += new EventHandler(OnZoomChanged);
        }
        void UnsubcribeZoomChangedEvent()
        {
            this.mainDoc.ZoomChanged -= new EventHandler(OnZoomChanged);
        }

        void OnZoomTrackBarEditValueChanging(object sender, ChangingEventArgs e)
        {
            OnZoomTrackBarEditValueChangedCore((int)e.NewValue);
        }
        void OnZoomTrackBarEditValueChangedCore(int value)
        {
            UnsubcribeZoomChangedEvent();
            this.mainDoc.ActiveView.ZoomFactor = (int)value / 100.0f;
            SubscribeZoomChangedEvent();
        }
        void OnZoomChanged(object sender, EventArgs e)
        {
            float zoomFactor = this.mainDoc.ActiveView.ZoomFactor;
            UnsubscribeZoomTrackbarEvents();
            UpdateZoomTrackbarCore(zoomFactor);
            SubscribeZoomTrackbarEvents();
        }
        void UpdateZoomTrackbarCore(float zoomFactor)
        {
            zoomTrackBar.EditValue = (int)Math.Round(zoomFactor * 100);
        }
        void UpdateZoomCaption(float zoomFactor)
        {
            this.zoomStatusItem.Caption = String.Format("{0}%", (int)Math.Round(zoomFactor * 100));
        }

        private void mainDoc_ZoomChanged(object sender, EventArgs e)
        {
            UpdateZoomCaption(this.mainDoc.ActiveView.ZoomFactor);
        }

        #endregion


        #region Spelling

        private void autoSpellingSwitch()
        {
            Configuration.autoSpellCheck = this.autoSpellingItem.Checked;

            if (this.autoSpellingItem.Checked)
            {
                this.coreSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
            }
            else
            {
                this.coreSpellChecker.SpellCheckMode = SpellCheckMode.OnDemand;
            }
        }

        #endregion


        #region File menu

        private void closeItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            this.Close();
        }

        private void pageSetupItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            ShowPageSetupFormCommand pageSetupCommand = new ShowPageSetupFormCommand(this.mainDoc);
            pageSetupCommand.Execute();
        }

        #endregion


        #region Edit menu

        private void deleteItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            DeleteCommand docDeleteCommand = new DeleteCommand(this.mainDoc);
            docDeleteCommand.Execute();
        }

        private void selectAll_ItemClick(object sender, ItemClickEventArgs e)
        {
            SelectAllCommand docSelectCommand = new SelectAllCommand(this.mainDoc);
            docSelectCommand.Execute();
        }

        #endregion


        #region View menu

        private void showSkinsFormItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            try
            {
                OptionsForm OptionsDlg = new OptionsForm();
                OptionsDlg.coreOptionsTab.SelectedTabPageIndex = 1;
                OptionsDlg.Show(this);
            }
            catch (Exception ex)
            {
                Cataloguing.WriteBugToFile("ERROR ~ " + ex.Message.ToString());
                MessageBox.Show(ex.Message.ToString(), "Oops", MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        #endregion


        #region Help menu

        private void supportContentsItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            Help.ShowHelp(this, coreHelp.HelpNamespace);
        }

        private void supportIndexItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            Help.ShowHelpIndex(this, coreHelp.HelpNamespace);
        }

        private void supportSearchItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            Help.ShowHelp(this, coreHelp.HelpNamespace, HelpNavigator.Find, "");
        }

        private void healthItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            HealthForm HealthFrm = new HealthForm();
            HealthFrm.Show();
        }

        private void onTheWebItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            Assistants.OpenWebPage("http://www.rizonesoft.com");
        }

        #endregion


        #region Document Handling

        public void OpenFile(string docName, int docIndex)
        {
            if (!string.IsNullOrEmpty(docName))
            {
                this.fileName = docName;
                switch (Path.GetExtension(docName))
                {
                    case "eml": mainDoc.LoadDocument(docName, DocumentFormat.Mht); break;
                    default: mainDoc.LoadDocument(docName); break;
                }

                SetDocumentCaption(docName);
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + "";
            }
        }

        private void mainDoc_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            this.headerFooterBar.Visible = this.mainDoc.IsSelectionInHeaderOrFooter;
        }

        private void mainDoc_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
            this.headerFooterBar.Visible = this.mainDoc.IsSelectionInHeaderOrFooter;
        }

        private void mainDoc_DocumentProtectionChanged(object sender, EventArgs e)
        {
            this.deleteItem.Enabled = !this.mainDoc.Document.IsDocumentProtected;
        }

        private void mainDoc_ReadOnlyChanged(object sender, EventArgs e)
        {
            
        }

        private void mainDoc_DragDrop(object sender, DragEventArgs e)
        {
            String[] fileExtensions = { "docx", "doc" };
            fileName = String.Empty;

            if (e.Data.GetDataPresent(DataFormats.FileDrop, false) == true)
            {
                string[] fileData = (string[])e.Data.GetData(DataFormats.FileDrop);

                if (fileData != null)
                {
                    if ((fileData.Length == 1) && (fileData.GetValue(0) is String))
                    {
                        fileName = ((string[])fileData)[0];
                        string extFile = Path.GetExtension(fileName).ToLower();
                        foreach (string ext in fileExtensions)
                        { if (ext != "")
                            { if (extFile.Contains(ext))
                                { SetDocumentCaption(fileName); } } }
                    }
                }

            }
            
        }

        private void SetDocumentCaption(string fileName)
        {
            string fileCaption = Path.GetFileName(fileName);
            if (fileCaption.Length > 28) { fileCaption = fileCaption.Remove(29) + "..."; }
            this.Text = fileCaption;
        }

        #endregion


        #region Document

        private void mainDoc_SelectionChanged(object sender, EventArgs e)
        {
            this.positionStatus.Caption = String.Format("Position: {0}", mainDoc.Document.CaretPosition.ToInt());
            this.pageCountStatusItem.Caption = String.Format("Page: {0} of {1}",
                (((PrintLayoutView)mainDoc.ActiveView).CurrentPageIndex + 1).ToString(),
                ((PrintLayoutView)mainDoc.ActiveView).PageCount.ToString());

            if (!docBarManager.Bars.Manager.IsCustomizing)
            {
                tableBar.Visible = mainDoc.IsSelectionInTable();
                this.cellAlignmentItem.Enabled = this.mainDoc.IsSelectionInTable();
                this.objectBar.Visible = this.mainDoc.IsFloatingObjectSelected;
            }



            //if (this.mainDoc.Document.Selection.Length > 1)
            //{ this.deleteItem.Enabled = true; }
            //else
            //{ this.deleteItem.Enabled = false; }
        }



        #endregion


        private void fileOpenItem_ItemClick(object sender, ItemClickEventArgs e)
        {

        }

        private void coreSpellChecker_BeforeCheck(object sender, DevExpress.XtraSpellChecker.BeforeCheckEventArgs e)
        {
            EnsureDictionaryLoading(coreSpellChecker.Culture.ToString());
        }

        private void EnsureDictionaryLoading(string culture)
        {
            if (Assistants.availableDictionaries.ContainsKey(culture))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary
                  dictionary = Assistants.availableDictionaries[culture] as DevExpress.XtraSpellChecker.HunspellDictionary;
                if (!dictionary.Loaded)
                {
                    this.coreSpellChecker.Dictionaries.Add(dictionary);
                    dictionary.Load();
                }
            }
        }

        private void autoSpellingItem_CheckedChanged(object sender, ItemClickEventArgs e)
        {
            autoSpellingSwitch();
        }

        private void coreSpellChecker_AfterLoadDictionaries(object sender, EventArgs e)
        {
            
        }

        private void DocumentForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (this.mainDoc.Modified)
            {
                DialogResult dresSave = XtraMessageBox.Show("Do you wish to save your changes to " + this.Text,
                  "Rizonesoft Verbum", MessageBoxButtons.YesNoCancel, MessageBoxIcon.None);
                if (dresSave == DialogResult.Yes)
                { this.mainDoc.SaveDocument(); }
                else if (dresSave == DialogResult.Cancel)
                { e.Cancel = true; }
            }
        }

        private void mainDoc_DocumentClosing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            //if (this.mainDoc.Modified)
            //{
            //    DialogResult dresSave = XtraMessageBox.Show("Do you wish to save your changes to " + this.Text.Replace(" - Verbum", ""),
            //      "Verbum", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
            //    if (dresSave == DialogResult.Yes)
            //    { this.mainDoc.SaveDocument(); }
            //    else if (dresSave == DialogResult.Cancel)
            //    { e.Cancel = true; }
            //}
        }


        private void mainDoc_TextChanged(object sender, EventArgs e)
        {
            this.wordCountStatusItem.Enabled = false;
            if (!this.countersWorker.IsBusy)
            this.countersWorker.RunWorkerAsync();
        }

        private void countersWorker_DoWork(object sender, System.ComponentModel.DoWorkEventArgs e)
        {
            wordCount = Counters.CountWords(mainDoc.Text);
        }

        private void countersWorker_RunWorkerCompleted(object sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            this.wordCountStatusItem.Caption = String.Format("Words: {0}", wordCount.ToString());
            this.wordCountStatusItem.Enabled = true;
        }


























    }
}