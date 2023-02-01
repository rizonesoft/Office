using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using DevExpress.XtraPrinting;

namespace ExportToPDF
{
    public partial class Form1 : XtraForm
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("Grimm.docx");
        }

        private void pdfExportItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            #region #ExportToPdf
			//Set the required export options:
            PdfExportOptions options = new PdfExportOptions();
            options.DocumentOptions.Author = "Mark Jones";
            options.Compressed = false;
            options.ImageQuality = PdfJpegImageQuality.High;
            //Export the document to the file:
            richEditControl1.ExportToPdf("Document.pdf", options);
            System.Diagnostics.Process.Start("Document.pdf");
			#endregion #ExportToPdf
        }
    }
}
