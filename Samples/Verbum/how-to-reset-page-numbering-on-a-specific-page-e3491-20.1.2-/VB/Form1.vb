Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native

Namespace RichEditResetPageNumbering
    Partial Public Class Form1
        Inherits Form

        Public Sub New()
            InitializeComponent()

            ' Fill first section with text
            For i As Integer = 0 To 4
                richEditControl1.Document.AppendText(StringSample.SampleText)
            Next i

            ' Add page numbering to the document
            Dim firstSection As Section = richEditControl1.Document.Sections(0)
            Dim doc As SubDocument = firstSection.BeginUpdateHeader()
            doc.InsertText(doc.CreatePosition(doc.Range.End.ToInt()), "Page ")
            doc.Fields.Create(doc.CreatePosition(doc.Range.End.ToInt()), "PAGE")
            doc.Fields.Update()
            firstSection.EndUpdateHeader(doc)

            ' Add a new section and configure its page numbering
            richEditControl1.Document.AppendSection()
            richEditControl1.Document.Sections(richEditControl1.Document.Sections.Count - 1).PageNumbering.FirstPageNumber = 1
            richEditControl1.Document.AppendText(StringSample.SampleText)
        End Sub
    End Class
End Namespace