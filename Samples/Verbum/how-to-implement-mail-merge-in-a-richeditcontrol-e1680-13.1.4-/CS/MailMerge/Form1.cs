using DevExpress.XtraBars;
using DevExpress.XtraRichEdit;
#region #usings
using DevExpress.XtraRichEdit.API.Native;
#endregion #usings
using DevExpress.XtraTab;
using System.Windows.Forms;

namespace MailMerge
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            ribbonControl1.SelectedPage = mailingsRibbonPage1;
            richEditControl1.LoadDocument("invitation.rtf", DocumentFormat.Rtf);
            #region #setdatasource
            richEditControl1.Options.MailMerge.DataSource = new SampleData();
            richEditControl1.Options.MailMerge.ViewMergedData = true;
            #endregion #setdatasource
        }

        private void mergeToNewDocumentItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            #region #merge
            MailMergeOptions myMergeOptions = richEditControl1.Document.CreateMailMergeOptions();
            myMergeOptions.FirstRecordIndex = 1;
            myMergeOptions.LastRecordIndex = 3;
            myMergeOptions.MergeMode = MergeMode.NewSection;
            richEditControl1.Document.MailMerge(myMergeOptions, richEditControl2.Document);
            #endregion #merge
            xtraTabControl1.SelectedTabPageIndex = 1;
        }

        private void xtraTabControl1_Selected(object sender, TabPageEventArgs e)
        {
            switch (e.PageIndex)
            {
                case 0:
                    this.richEditBarController1.RichEditControl = this.richEditControl1;
                    break;
                case 1:
                    this.richEditBarController1.RichEditControl = this.richEditControl2;
                    break;
            }
        }

        private void mergeToFileItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            MailMergeOptions myMergeOptions = richEditControl1.Document.CreateMailMergeOptions();
            myMergeOptions.DataSource = new SampleData();
            myMergeOptions.FirstRecordIndex = 1;
            myMergeOptions.LastRecordIndex = 3;
            myMergeOptions.MergeMode = MergeMode.NewSection;

            SaveFileDialog fileDialog = new SaveFileDialog();
            fileDialog.Filter = "MS Word 2007 documents (*.docx)|*.docx|All files (*.*)|*.*";
            fileDialog.FilterIndex = 1;
            fileDialog.RestoreDirectory = true;

            DialogResult dialogResult = fileDialog.ShowDialog();
            if (dialogResult == System.Windows.Forms.DialogResult.OK)
            {
                string fName = fileDialog.FileName;
                if (fName != "")
                {
                    richEditControl1.Document.MailMerge(myMergeOptions, fileDialog.FileName, DocumentFormat.OpenXml);
                    System.Diagnostics.Process.Start(fileDialog.FileName);
                }
            }
        }
    }
}