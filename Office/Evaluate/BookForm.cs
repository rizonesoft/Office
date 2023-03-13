namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.LookAndFeel;
    using DevExpress.XtraBars;
    using DevExpress.XtraEditors;
    using Rizonesoft.Office.Evaluate.Utilities;
    using Rizonesoft.Office.LicensingEx;
    using Rizonesoft.Office.Utilities;
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
    using System.Globalization;
    using DevExpress.XtraSpreadsheet;
    using WinRT;
    using DevExpress.Spreadsheet;

    public partial class BookForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        public string FileName { get; internal set; }

        public BookForm()
        {
            InitializeComponent();
            // ChildSpreadsheetControl.Options.Culture = DefaultCulture;
            ChildSpreadsheetControl.Options.View.Charts.Antialiasing = DocumentCapability.Enabled;
            ChildSpreadsheetControl.Options.View.Charts.TextAntialiasing = DocumentCapability.Enabled;

            MainForm.SetSkins();
        }

        public BookForm(string fileName) : this()
        {
            ChildSpreadsheetControl.LoadDocument(fileName);
            ChildSpreadsheetControl.Modified = false;
            ChildSpreadsheetControl.Focus();

        }

        private void BookForm_Load(object sender, EventArgs e)
        {
            if (DesignMode)
            {
                return;
            }

            ChildSpreadsheetControl.Modified = false;
            ChildSpreadsheetControl.Focus();
            CheckLicense();
        }

        private void BookForm_Activated(object sender, EventArgs e)
        {
            if (MdiParent == null)
            {
                Owner = null;
            }
        }

        public void OpenFile(string bookName, int bookIndex)
        {
            if (!string.IsNullOrEmpty(bookName))
            {
                //fileName = bookName;
                SetDocumentCaption(bookName);
                ChildSpreadsheetControl.LoadDocument(bookName);
            }
            else
            {
                Text = @"Book " + bookIndex.ToString() + string.Empty;
            }
        }

        private void SetDocumentCaption(string fileName)
        {
            string fileCaption = Path.GetFileName(fileName);
            if (fileCaption.Length > 28)
            {
                fileCaption = fileCaption.Remove(29) + "...";
            }
            Text = fileCaption;
        }

        private void CheckLicense()
        {

            if (RizonesoftEx.IsLicensed)
            {
                CalcEditStatusItem.Visibility = BarItemVisibility.Always;
                InsertNumStatusButton.Visibility = BarItemVisibility.Always;
            }
            else
            {
                CalcEditStatusItem.Visibility = BarItemVisibility.Never;
                InsertNumStatusButton.Visibility = BarItemVisibility.Never;
            }

        }

        private void BookForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            e.Cancel = !SaveQuestion();
        }

        bool SaveQuestion()
        {
            string tempName = FileName;
            if (string.IsNullOrEmpty(tempName))
            {
                tempName = Text;
            }

            if (ChildSpreadsheetControl.Modified)
            {
                switch (XtraMessageBox.Show($"Do you want to save changes to:{Environment.NewLine}\"{tempName}\"?",
                                  "Warning",
                                  MessageBoxButtons.YesNoCancel,
                                  MessageBoxIcon.Warning))
                {
                    case DialogResult.Cancel:
                        return false;
                    case DialogResult.Yes:
                        ChildSpreadsheetControl.SaveDocument();
                        break;
                }
            }
            return true;
        }

        private void BookRibbon_UnMerge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = false;
            licenseRibbonGroup.Visible = false;
        }

        private void BookRibbon_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            optionsRibbonGroup.Visible = true;
            licenseRibbonGroup.Visible = true;
        }

        private void ChildSpreadsheetControl_InvalidFormatException(object sender, SpreadsheetInvalidFormatExceptionEventArgs e)
        {
            XtraMessageBox.Show(string.Format("Cannot open the file '{0}' because the file format or file extension is not valid.\n" +
                    "Verify that file has not been corrupted and that the file extension matches the format of the file.", e.SourceUri),
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

        private void ChildSpreadsheetControl_TextChanged(object sender, EventArgs e)
        {

        }
    }

}