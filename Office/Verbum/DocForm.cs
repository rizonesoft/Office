using System.IO;

namespace Rizonesoft.Office.Verbum
{
    public partial class DocForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        internal bool _isZoomChanging = false;
        internal bool _includeTextBoxes = false;
        internal string fileName;

        public string FileName
        {
            get
            {
                return this.fileName;
            }
        }

        public DocForm()
        {
            InitializeComponent();
        }

        #region Document Handling

        public void OpenFile(string docName, int docIndex)
        {
            if (!string.IsNullOrEmpty(docName))
            {
                this.fileName = docName;
                switch (Path.GetExtension(docName))
                {
                    case "eml":
                        // coreRichEditControl.LoadDocument(docName, DocumentFormat.Mht);
                        break;
                    default:
                        // coreRichEditControl.LoadDocument(docName);
                        break;
                }

                // SetDocumentCaption(docName);
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + "";
            }
        }

        #endregion Document Handling


    }

}