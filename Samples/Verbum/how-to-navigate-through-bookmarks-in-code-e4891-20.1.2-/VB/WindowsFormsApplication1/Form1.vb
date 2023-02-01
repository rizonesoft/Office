Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit

Namespace WindowsFormsApplication1
	Partial Public Class Form1
		Inherits RibbonForm

		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles Me.Load
			richEditControl1.LoadDocument("testDocument.rtf", DocumentFormat.Rtf)
			UpdateButtonsVisibility(0)
		End Sub

		Private Function GetCurrentBookMarkIndex(ByVal currentDoc As DevExpress.XtraRichEdit.API.Native.Document) As Integer
			For i As Integer = 0 To currentDoc.Bookmarks.Count - 1
				If currentDoc.Bookmarks(i).Range.Contains(currentDoc.CaretPosition) OrElse currentDoc.Bookmarks(i).Range.End.ToInt() = currentDoc.CaretPosition.ToInt() Then
					Return i
				End If
			Next i
			Return -1
		End Function

		Private Sub barButtonItemPrev_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles barButtonItemPrev.ItemClick
			Dim currentBookMarkIndex As Integer = GetCurrentBookMarkIndex(richEditControl1.Document)
			If currentBookMarkIndex > 0 Then
				richEditControl1.Document.Bookmarks.Select(richEditControl1.Document.Bookmarks(currentBookMarkIndex - 1))
			End If
			UpdateButtonsVisibility(currentBookMarkIndex - 1)
		End Sub

		Private Sub barButtonItemNext_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles barButtonItemNext.ItemClick
			Dim currentBookMarkIndex As Integer = GetCurrentBookMarkIndex(richEditControl1.Document)
			If currentBookMarkIndex <> -1 AndAlso currentBookMarkIndex < richEditControl1.Document.Bookmarks.Count - 1 Then
				richEditControl1.Document.Bookmarks.Select(richEditControl1.Document.Bookmarks(currentBookMarkIndex + 1))
			End If
			UpdateButtonsVisibility(currentBookMarkIndex + 1)
		End Sub

		Private Sub UpdateButtonsVisibility(ByVal newBookMarkIndex As Integer)
			barButtonItemNext.Enabled = newBookMarkIndex < (richEditControl1.Document.Bookmarks.Count - 1)
			barButtonItemPrev.Enabled = newBookMarkIndex > 0
		End Sub
	End Class
End Namespace
