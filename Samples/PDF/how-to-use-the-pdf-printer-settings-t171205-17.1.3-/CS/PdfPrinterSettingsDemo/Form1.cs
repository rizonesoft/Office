
using System;
using System.Drawing.Printing;
using System.Windows.Forms;
using DevExpress.Pdf;
using DevExpress.XtraPdfViewer;

namespace PdfPrinterSettingsDemo {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e) {
            // Create a PDF Viewer instance and load a PDF into it.
            PdfViewer pdfViewer = this.pdfViewer1;
            pdfViewer.LoadDocument(@"..\..\Demo.pdf");

            // If required, declare and specify the system printer settings.
            PrinterSettings printerSettings = new PrinterSettings();
            printerSettings.PrinterName = "Microsoft XPS Document Writer";
            printerSettings.PrintToFile = true;
            printerSettings.PrintFileName = @"..\..\Demo.xps";

            // Declare the PDF printer settings.
            // If required, pass the system settings to the PDF printer settings constructor.
            PdfPrinterSettings pdfPrinterSettings = new PdfPrinterSettings(printerSettings);

            // Specify the PDF printer settings.
            pdfPrinterSettings.PageOrientation = PdfPrintPageOrientation.Auto;
            pdfPrinterSettings.PageNumbers = new int[] { 1, 3, 4, 5 };
            pdfPrinterSettings.ScaleMode = PdfPrintScaleMode.CustomScale;
            pdfPrinterSettings.Scale = 90;

            // Print the document using the specified printer settings.
            pdfViewer.Print(pdfPrinterSettings);
        }
    }
}
