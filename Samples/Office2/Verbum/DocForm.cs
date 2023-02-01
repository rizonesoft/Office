using DevExpress.Utils.Controls;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraSpellChecker;
using Rizonesoft.Office.Verbum.Classes;
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

        bool IncludeTextBoxes
        {
            get { return _includeTextBoxes; }
            set
            {
                if (_includeTextBoxes == value)
                    return;
                _includeTextBoxes = value;
                OnIncludeTextBoxesChanged();
            }
        }

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


            this.headerFooterToolsRibbonPageCategory.Visible = false;
            this.tableToolsRibbonPageCategory.Visible = false;
            this.floatingPictureToolsRibbonPageCategory.Visible = false;
        }

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
          }

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
        private void fileCustomNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
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
        private void coreRichEditControl_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {
        }
        private void coreRichEditControl_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e)
        {   
        }
        void OnPagesInfoChanged()
        {
        }
        private void frmDoc_Load(object sender, EventArgs e)
        {
        }
        private void DocumentSaveOptions_OnChanged(object sender, BaseOptionChangedEventArgs e)
        {
        }
        void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
        }
        private void coreRichEditControl_VisibleChanged(object sender, EventArgs e)
        {
        }
        private void coreRichEditControl_SelectionChanged(object sender, EventArgs e)
        {
        }
        private void barZoomItem_EditValueChanged(object sender, EventArgs e)
        { 
        }
        private void coreRichEditControl_ZoomChanged(object sender, EventArgs e)
        {
        }
        private void coreRichEditControl_ContentChanged(object sender, EventArgs e)
        { 
        }
        private void documentStatsTimer_Tick(object sender, EventArgs e)
        {  
        }
        void OnIncludeTextBoxesChanged()
        {
        }
        void CalculateDocumentStatistics()
        {
        }
        private void docStatBtnItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { 
        }
        private void coreRichEditControl_InvalidFormatException(object sender, RichEditInvalidFormatExceptionEventArgs e)
        {
        }

        
    }
}

