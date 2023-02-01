Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports System.IO
Imports DevExpress.XtraRichEdit.Export

Namespace PlainTextExport
    Partial Public Class Form1
        Inherits DevExpress.XtraEditors.XtraForm

        Public Sub New()
            InitializeComponent()
            richEditControl1.LoadDocument("sample.docx", DocumentFormat.OpenXml)
'            #Region "#PlainTextDocumentExporterOptions"
            richEditControl1.Options.Export.PlainText.ExportHiddenText = True
            richEditControl1.Options.Export.PlainText.FieldCodeStartMarker = "[<"
            richEditControl1.Options.Export.PlainText.FieldCodeEndMarker = ">"
            richEditControl1.Options.Export.PlainText.FieldResultEndMarker = "]"
            richEditControl1.Options.Export.PlainText.Encoding = Encoding.GetEncoding("Windows-1252")
'            #End Region ' #PlainTextDocumentExporterOptions
        End Sub

        Private Sub btnExport_Click(ByVal sender As Object, ByVal e As EventArgs) Handles btnExport.Click
            Dim stream As New MemoryStream()
            richEditControl1.SaveDocument(stream, DocumentFormat.PlainText)
            stream.Position = 0
            Dim sr As New StreamReader(stream, richEditControl1.Options.Export.PlainText.Encoding)
            memoEdit1.Text = sr.ReadToEnd()
        End Sub
    End Class
End Namespace