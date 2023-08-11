using DevExpress.XtraEditors;
using Rizonesoft.Office.Evaluate.Classes;
using Rizonesoft.Office.Evaluate.Language;
using Rizonesoft.Office.UI;
using System;
using System.Windows.Forms;

namespace Rizonesoft.Office.Evaluate
{
    public partial class BookForm : DevExpress.XtraBars.Ribbon.RibbonForm
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

        public BookForm(string fileName)
        {
            FileName = fileName;
            InitializeComponent();
            UpdateUi();

            new SpreadsheetExceptionHandler(ChildSpreadsheetControl).Install();
            SetupEventHandlers();
        }

        private void UpdateUi()
        {
            FileRibbonPage.Text = Dialogs.RibbonPage_File;
            CommonRibbonGroup.Text = Dialogs.RibbonGroup_Common;
        }

        /// <summary>
        ///     Open a Spreadsheet document.
        /// </summary>
        /// <param name="fileName">The name of the file to open.</param>
        /// <param name="bookIndex">The document index.</param>
        public void OpenFile(string fileName, int bookIndex)
        {
            if (!string.IsNullOrWhiteSpace(fileName))
            {
                ChildSpreadsheetControl.LoadDocument(fileName);
                ChildDocHelper.SetDocumentCaption(fileName, this);
                return;
            }

            Text = FileName = $"Document {bookIndex}";
            ChildSpreadsheetControl.Options.Save.DefaultFileName = $"Untitled {bookIndex}";
        }

        private void SetupEventHandlers()
        {

        }

        private void BookForm_Load(object sender, EventArgs e)
        {
            // if (DesignMode) return;
        }

        private void ChildSpreadsheetControl_DocumentSaved(object sender, EventArgs e)
        {
            var savedFileName = ChildSpreadsheetControl.Options.Save.CurrentFileName;

            ChildDocHelper.SetDocumentCaption(savedFileName, this);
            FileName = savedFileName;
            MainForm.AddFileToMruList(savedFileName);
        }

        private bool TrySaveDocument()
        {
            // If the document hasn't been modified, there's nothing to save.
            if (!ChildSpreadsheetControl.Modified)
            {
                return true;
            }

            // If no filename has been set, use the form's text as the filename.
            var fileName = string.IsNullOrEmpty(FileName) ? Text : FileName;

            try
            {
                switch (XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{fileName}\"?",
                            "Warning",
                            MessageBoxButtons.YesNoCancel,
                            MessageBoxIcon.Warning))
                {
                    case DialogResult.Cancel:
                        // The user doesn't want to save changes and has cancelled the operation.
                        return false;

                    case DialogResult.Yes:
                        // The user wants to save changes. Try to save the document.
                        ChildSpreadsheetControl.SaveDocument();
                        // After successfully saving, mark the document as unmodified.
                        ChildSpreadsheetControl.Modified = false;
                        break;
                }
            }
            catch (Exception ex)
            {
                // Log or handle the exception as needed.
                Console.WriteLine(ex.Message);
                // If an error occurs while saving, return false.
                return false;
            }

            // If the document hasn't been modified, or if the user didn't want to save changes, or if the document has been saved, return true.
            return true;
        }

        private void BookForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            e.Cancel = !TrySaveDocument();
        }
    }


}