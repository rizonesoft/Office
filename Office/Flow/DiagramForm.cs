

namespace Rizonesoft.Office.Flow
{
    using System.IO;

    public partial class DiagramForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        public string FileName { get; internal set; }

        public DiagramForm()
        {
            InitializeComponent();
        }

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
    }
}