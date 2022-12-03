Imports Microsoft.VisualBasic
Imports System.Drawing
Imports System.Windows.Forms
Imports DevExpress.Utils
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Utils
Imports DevExpress.Office.Utils

Namespace RichEditWordTooltip
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			SetTestHeaderContent()
		End Sub

		Private Sub richEditControl1_MouseMove(ByVal sender As Object, ByVal e As MouseEventArgs) Handles richEditControl1.MouseMove
			Dim docPoint As Point = Units.PixelsToDocuments(e.Location, richEditControl1.DpiX, richEditControl1.DpiY)
			Dim pos As DocumentPosition = richEditControl1.GetPositionFromPoint(docPoint)

			If pos Is Nothing Then
				Return
			End If

			Dim start As DocumentPosition = pos
			Dim [end] As DocumentPosition = pos

			Dim doc As SubDocument = richEditControl1.Document.CaretPosition.BeginUpdateDocument()

			For i As Integer = 0 To doc.Range.End.ToInt() - 1
				If start.ToInt() - i < 0 Then
					start = doc.Range.Start
					Exit For
				End If

				Dim range As DocumentRange = doc.CreateRange(start.ToInt() - i, i + 1)
				Dim str As String = doc.GetText(range)

				If ContainsPunctuationOrWhiteSpace(str) Then
					start = doc.CreatePosition(range.Start.ToInt() + 1)
					Exit For
				End If
			Next i

			For i As Integer = 0 To doc.Range.End.ToInt() - 1
				If [end].ToInt() + i > doc.Range.End.ToInt() Then
					[end] = doc.Range.End
					Exit For
				End If

				Dim range As DocumentRange = doc.CreateRange([end].ToInt(), i + 1)
				Dim str As String = doc.GetText(range)

				If ContainsPunctuationOrWhiteSpace(str) Then
					[end] = doc.CreatePosition(range.End.ToInt() - 1)
					Exit For
				End If
			Next i

			If [end].ToInt() < start.ToInt() Then
				Return
			End If

			Dim wordRange As DocumentRange = doc.CreateRange(start, [end].ToInt() - start.ToInt())
			Dim word As String = doc.GetText(wordRange)

			richEditControl1.Document.CaretPosition.EndUpdateDocument(doc)

			ShowToolTip(word)
		End Sub

		Protected Function ContainsPunctuationOrWhiteSpace(ByVal str As String) As Boolean
			For i As Integer = 0 To str.Length - 1
				If Char.IsPunctuation(str.Chars(i)) OrElse Char.IsWhiteSpace(str.Chars(i)) Then
					Return True
				End If
			Next i
			Return False
		End Function

		Private Sub ShowToolTip(ByVal word As String)
			Dim info As New ToolTipControlInfo(word, word)
			info.ToolTipPosition = Form.MousePosition
			toolTipController1.ShowHint(info)
		End Sub

		Private Sub SetTestHeaderContent()
			Dim firstSection As Section = richEditControl1.Document.Sections(0)
			Dim doc As SubDocument = firstSection.BeginUpdateHeader(HeaderFooterType.Odd)
			doc.InsertText(doc.Range.Start, "Page header")
			richEditControl1.Document.Sections(0).EndUpdateHeader(doc)
		End Sub
	End Class
End Namespace