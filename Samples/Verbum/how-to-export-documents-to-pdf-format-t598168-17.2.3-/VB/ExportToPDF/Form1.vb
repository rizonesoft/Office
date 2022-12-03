Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports DevExpress.XtraEditors
Imports DevExpress.XtraPrinting

Namespace ExportToPDF
    Partial Public Class Form1
        Inherits XtraForm

        Public Sub New()
            InitializeComponent()
            richEditControl1.LoadDocument("Grimm.docx")
        End Sub

        Private Sub pdfExportItem_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles pdfExportItem.ItemClick
'            #Region "#ExportToPdf"
            'Set the required export options:
            Dim options As New PdfExportOptions()
            options.DocumentOptions.Author = "Mark Jones"
            options.Compressed = False
            options.ImageQuality = PdfJpegImageQuality.High
            'Export the document to the file:
            richEditControl1.ExportToPdf("Document.pdf", options)
            System.Diagnostics.Process.Start("Document.pdf")
'            #End Region ' #ExportToPdf
        End Sub
    End Class
End Namespace
