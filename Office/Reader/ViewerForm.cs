

namespace Rizonesoft.Office.Reader
{
    using DevExpress.XtraBars;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Data;
    using System.Drawing;
    using System.IO;
    using System.Linq;
    using System.Text;
    using System.Threading.Tasks;
    using System.Windows.Forms;

    public partial class ViewerForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        #region Properties

        public string FileName { get; internal set; }

        #endregion Properties

        public ViewerForm()
        {
            InitializeComponent();
        }

        #region Viewer Processing

        public void OpenFile(string pdfName, int docIndex)
        {

            if (!string.IsNullOrEmpty(pdfName))
            {
                FileName = pdfName;
                mainPDFViewer.LoadDocument(pdfName);
                SetDocumentCaption(pdfName);
                return;
            }
            else
            {
                Text = FileName = $@"Document {docIndex}";
            }

            
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

        #endregion Viewer Processing

    }
}