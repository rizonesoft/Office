

namespace Rizonesoft.Office.Flow
{
    using System.IO;

    public partial class DiagramForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        #region Properties

        public string FileName { get; internal set; }

        #endregion Properties

        public DiagramForm()
        {
            InitializeComponent();
        }

        #region Viewer Processing

        public void OpenFile(string diagramName, int docIndex)
        {

            if (!string.IsNullOrEmpty(diagramName))
            {
                FileName = diagramName;
                mainDiagramControl.LoadDocument(diagramName);
                SetDocumentCaption(diagramName);
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