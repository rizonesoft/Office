Imports System
Imports DevExpress.Spreadsheet
Imports DevExpress.XtraRichEdit.API.Native

Public Class RichTextEditForm
    Private cell As Cell
    Public Sub New(ByVal cell As Cell)
        InitializeComponent()
        Me.cell = cell
        InitRichEditControl()
    End Sub
    Private Sub InitRichEditControl()
        RichEditControl1.BeginUpdate()
        If cell.HasRichText Then
            Dim richText As RichTextString = cell.GetRichText()
            Dim document As Document = RichEditControl1.Document
            For Each run As RichTextRun In richText.Runs
                Dim range As DocumentRange = document.InsertText(document.Range.End, run.Text)
                Dim cp As CharacterProperties = document.BeginUpdateCharacters(range)
                cp.Bold = run.Font.Bold
                cp.ForeColor = run.Font.Color
                cp.Italic = run.Font.Italic
                cp.FontName = run.Font.Name
                cp.FontSize = CSng(run.Font.Size)
                cp.Strikeout = If(run.Font.Strikethrough, StrikeoutType.Single, StrikeoutType.None)
                Select Case run.Font.Script
                    Case ScriptType.Subscript
                        cp.Subscript = True
                    Case ScriptType.Superscript
                        cp.Superscript = True
                    Case Else
                        cp.Subscript = False
                        cp.Superscript = False
                End Select
                Select Case run.Font.UnderlineType
                    Case DevExpress.Spreadsheet.UnderlineType.Single
                        cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.Single
                    Case DevExpress.Spreadsheet.UnderlineType.Double
                        cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.Double
                    Case Else
                        cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.None
                End Select
                document.EndUpdateCharacters(cp)
            Next run
        Else
            RichEditControl1.Text = cell.DisplayText
        End If
        RichEditControl1.EndUpdate()
    End Sub
    Private Sub OKButton_Click(sender As Object, e As EventArgs) Handles OKButton.Click
        Dim visitor As New CustomDocumentVisitor(RichEditControl1.Document.Range.End.ToInt())
        Dim iterator As New DocumentIterator(RichEditControl1.Document, True)
        Do While iterator.MoveNext()
            iterator.Current.Accept(visitor)
        Loop
        Dim richText As RichTextString = visitor.RichText
        cell.SetRichText(richText)
        If RichEditControl1.Document.Paragraphs.Count > 1 Then
            cell.Alignment.WrapText = True
        End If
    End Sub
End Class