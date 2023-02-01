Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Layout
Imports DevExpress.XtraRichEdit.API.Native
Imports System.Drawing

Namespace LineNumberingExample
	#Region "#MyPagePainter"
	Public Class MyPagePainter
		Inherits PagePainter

		Private richEditControl As RichEditControl
		Private previousColumnIndex As Integer = -1
		Private lineNumberFont As Font

		Public Sub New(ByVal richEdit As RichEditControl)
			MyBase.New()
			richEditControl = richEdit
		End Sub

		Public Sub New(ByVal richEdit As RichEditControl, ByVal backColor As Color, ByVal style As CharacterStyle)
			MyBase.New()
			richEditControl = richEdit
			NumberingHighlightColor = backColor
			NumberingFontName = style.FontName
			NumberingFontSize = If(style.FontSize, 10F)
			NumberingFontColor = If(style.ForeColor, Color.Black)
		End Sub

		Public Property NumberingFontName() As String
		Public Property NumberingFontSize() As Single
		Public Property NumberingFontColor() As Color
		Public Property NumberingHighlightColor() As Color
		Public Property LineNumberPadding() As Integer

		Public Overrides Sub DrawPage(ByVal page As LayoutPage)
			lineNumberFont = New Font(NumberingFontName, NumberingFontSize, FontStyle.Regular)
			MyBase.DrawPage(page)
			lineNumberFont.Dispose()
		End Sub

		Public Overrides Sub DrawPageArea(ByVal pageArea As LayoutPageArea)
			Dim lineNumberBounds As New Rectangle(New Point(-LineNumberPadding, 0), New Size(LineNumberPadding, pageArea.Bounds.Height))
			Canvas.FillRectangle(New RichEditBrush(NumberingHighlightColor), lineNumberBounds)
			MyBase.DrawPageArea(pageArea)
			previousColumnIndex = -1
		End Sub
		Public Overrides Sub DrawColumn(ByVal column As LayoutColumn)
			Dim pageArea As LayoutPageArea = column.GetParentByType(Of LayoutPageArea)()
			If pageArea IsNot Nothing Then
				Dim leftBoundary As Integer = 0
				If previousColumnIndex >= 0 Then
					leftBoundary = pageArea.Columns(previousColumnIndex).Bounds.Right
				End If
				If column.LineNumbers.Count > 0 Then
					HighlightLineNumberingArea(column, leftBoundary)
				End If
				previousColumnIndex += 1
			End If
			MyBase.DrawColumn(column)
		End Sub

		Public Overrides Sub DrawLineNumberBox(ByVal lineNumberBox As LineNumberBox)
			Canvas.DrawString(lineNumberBox.Text, lineNumberFont, New RichEditBrush(NumberingFontColor), lineNumberBox.Bounds, Me.richEditControl.LayoutUnit)
		End Sub

		Private Sub HighlightLineNumberingArea(ByVal column As LayoutColumn, ByVal leftBoundary As Integer)
				Dim page As LayoutPage = column.GetParentByType(Of LayoutPage)()
			Dim marginBounds As New Rectangle(New Point(leftBoundary, 0), New Size(column.Bounds.X - leftBoundary, page.Bounds.Height))
			Canvas.FillRectangle(New RichEditBrush(NumberingHighlightColor), marginBounds)
		End Sub
	End Class
	#End Region ' #MyPagePainter
End Namespace