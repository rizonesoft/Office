Imports System
Imports System.Drawing.Printing
Imports System.Windows.Forms
Imports DevExpress.Pdf
Imports DevExpress.XtraPdfViewer

Namespace PdfPrinterSettingsDemo
    Partial Public Class Form1
        Inherits Form

        Public Sub New()
            InitializeComponent()
        End Sub

        Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
            ' Create a PDF Viewer instance and load a PDF into it.
            Dim pdfViewer As PdfViewer = Me.pdfViewer1
            pdfViewer.LoadDocument("..\..\Demo.pdf")

            ' If required, declare and specify the system printer settings.
            Dim printerSettings As New PrinterSettings()
            printerSettings.PrinterName = "Microsoft XPS Document Writer"
            printerSettings.PrintToFile = True
            printerSettings.PrintFileName = "..\..\Demo.xps"

            ' Declare the PDF printer settings.
            ' If required, pass the system settings to the PDF printer settings constructor.
            Dim pdfPrinterSettings As New PdfPrinterSettings(printerSettings)

            ' Specify the PDF printer settings.
            pdfPrinterSettings.PageOrientation = PdfPrintPageOrientation.Auto
            pdfPrinterSettings.PageNumbers = New Integer() { 1, 3, 4, 5 }
            pdfPrinterSettings.ScaleMode = PdfPrintScaleMode.CustomScale
            pdfPrinterSettings.Scale = 90

            ' Print the document using the specified printer settings.
            pdfViewer.Print(pdfPrinterSettings)
        End Sub
    End Class
End Namespace
