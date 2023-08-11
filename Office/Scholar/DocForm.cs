using System.IO;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors.ButtonPanel;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.UI;

namespace Rizonesoft.Office.Scholar
{
    public partial class DocForm : RibbonForm
    {
        public string FileName { get; internal set; }

        public DocForm()
        {

            InitializeComponent();
            ChildPDFViewer.NavigationPaneWidth = ScholarSettings.NavigationPaneWidth;
            UpdateUI();
        }

        private void UpdateUI()
        {
            HomeRibbonPage.Text = Dialogs.RibbonMain_Home;
        }

        public void OpenFile(string fileName, int docIndex)
        {

            if (!string.IsNullOrEmpty(fileName))
            {
                FileName = fileName;
                ChildPDFViewer.LoadDocument(fileName);
                ChildDocHelper.SetDocumentCaption(fileName, this);
                return;
            }
            else
            {
                Text = FileName = $@"Document {docIndex}";
            }
        }

        private void RotateLeftBarButton_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            ChildPDFViewer.RotationAngle = (ChildPDFViewer.RotationAngle - 90) % 360;
        }

        private void RotateRightBarButton_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            ChildPDFViewer.RotationAngle = (ChildPDFViewer.RotationAngle + 90) % 360;
        }
    }
}