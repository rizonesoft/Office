using DevExpress.LookAndFeel;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
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

namespace Rizonesoft.Office.Evaluate
{
    public partial class BookForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        internal string fileName;

        public BookForm()
        {
            InitializeComponent();
        }


        #region Properties

        public string FileName
        {
            get
            {
                return this.fileName;
            }
        }

        #endregion Properties


        #region Workbook Processing

        public void OpenFile(string bookName, int bookIndex)
        {
            if (!string.IsNullOrEmpty(bookName))
            {
                fileName = bookName;
                SetDocumentCaption(bookName);
                mainSpreadsheetControl.LoadDocument(bookName);
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

        #endregion Workbook Processing




    }
}