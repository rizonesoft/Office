Imports DevExpress.Spreadsheet
Imports DevExpress.XtraRichEdit.API.Native
Public Class CustomDocumentVisitor
    Inherits DocumentVisitorBase
    Private richTextString As RichTextString
    Private endPosition As Integer
    Public ReadOnly Property RichText As RichTextString
        Get
            Return richTextString
        End Get
    End Property
    Public Sub New(ByVal endPos As Integer)
        richTextString = New RichTextString()
        endPosition = endPos
    End Sub
    Public Overrides Sub Visit(ByVal text As DocumentText)
        MyBase.Visit(text)
        Dim runFont As RichTextRunFont = CreateRichTextRun(text.TextProperties)
        richTextString.AddTextRun(text.Text, runFont)
    End Sub
    Public Overrides Sub Visit(ByVal paragraphEnd As DocumentParagraphEnd)
        MyBase.Visit(paragraphEnd)
        If endPosition - 1 <> paragraphEnd.Position Then
            Dim runFont As RichTextRunFont = CreateRichTextRun(paragraphEnd.TextProperties)
            richTextString.AddTextRun(paragraphEnd.Text, runFont)
        End If
    End Sub
    Private Function CreateRichTextRun(ByVal tp As ReadOnlyTextProperties) As RichTextRunFont
        Dim runFont As New RichTextRunFont(tp.FontName, tp.DoubleFontSize \ 2, tp.ForeColor)
        runFont.Bold = tp.FontBold
        runFont.Italic = tp.FontItalic
        runFont.Strikethrough = tp.StrikeoutType = StrikeoutType.Single
        Select Case tp.Script
            Case DevExpress.Office.CharacterFormattingScript.Subscript
                runFont.Script = ScriptType.Subscript
            Case DevExpress.Office.CharacterFormattingScript.Superscript
                runFont.Script = ScriptType.Superscript
            Case Else
                runFont.Script = ScriptType.None
        End Select
        Select Case tp.UnderlineType
            Case DevExpress.XtraRichEdit.API.Native.UnderlineType.Single
                runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.Single
            Case DevExpress.XtraRichEdit.API.Native.UnderlineType.Double
                runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.Double
            Case Else
                runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.None
        End Select
        Return runFont
    End Function
End Class

