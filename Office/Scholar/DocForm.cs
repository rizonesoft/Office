using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.UI;
using System;

namespace Rizonesoft.Office.Scholar
{
    public partial class DocForm : RibbonForm
    {
        public event EventHandler FileNameChanged;
        private string _fileName;

        public string FileName
        {
            get => _fileName;
            private set
            {
                if (_fileName == value) return;
                _fileName = value;
                OnFileNameChanged();
            }
        }

        protected virtual void OnFileNameChanged()
        {
            FileNameChanged?.Invoke(this, EventArgs.Empty);
        }

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