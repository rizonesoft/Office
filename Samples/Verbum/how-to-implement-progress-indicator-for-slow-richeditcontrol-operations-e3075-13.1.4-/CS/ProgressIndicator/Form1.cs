using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;
#region #usings
using DevExpress.Services;
#endregion #usings
using DevExpress.XtraRichEdit;

namespace ProgressIndicator
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("Docs\\invitation.docx");
            richEditControl1.Options.MailMerge.DataSource = new SampleData();
        }

        private void btnMailMerge_Click(object sender, EventArgs e)
        {
            MailMergeOptions myMergeOptions = richEditControl1.Document.CreateMailMergeOptions();
            myMergeOptions.MergeMode = MergeMode.NewSection;
            richEditControl1.Document.MailMerge(myMergeOptions, richEditControl2.Document);
            xtraTabControl1.SelectedTabPageIndex = 1;
        }

        private void richEditControl1_MailMergeStarted(object sender, DevExpress.XtraRichEdit.MailMergeStartedEventArgs e)
        {
            #region #servicesubst
            richEditControl1.ReplaceService<IProgressIndicationService>
                (new MyProgressIndicatorService(richEditControl1, this.progressBarControl1));
            #endregion #servicesubst
        }

        private void richEditControl1_MailMergeFinished(object sender, DevExpress.XtraRichEdit.MailMergeFinishedEventArgs e)
        {
            richEditControl1.RemoveService(typeof(IProgressIndicationService));
        }

        private void richEditControl1_MailMergeRecordStarted(object sender, DevExpress.XtraRichEdit.MailMergeRecordStartedEventArgs e)
        {
            // Imitating slow data fetching
            System.Threading.Thread.Sleep(100);
        }

        private void richEditControl1_MailMergeRecordFinished(object sender, DevExpress.XtraRichEdit.MailMergeRecordFinishedEventArgs e)
        {
           e.RecordDocument.AppendDocumentContent("Docs\\bungalow.docx", DocumentFormat.OpenXml);
        }

        private void xtraTabControl1_Selected(object sender, DevExpress.XtraTab.TabPageEventArgs e)
        {
            switch (e.PageIndex) {
                case 0:
                    this.btnMailMerge.Enabled = true;
                    break;
                case 1:
                    this.btnMailMerge.Enabled = false;
                    break;
            }
        }
    }
}