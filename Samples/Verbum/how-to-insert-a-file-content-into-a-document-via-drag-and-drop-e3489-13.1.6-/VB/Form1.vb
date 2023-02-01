Imports Microsoft.VisualBasic
Imports System.Drawing
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.Office.Utils

Namespace RichEditInsertDroppedFile
	Partial Public Class Form1
		Inherits Form
		Private richEditGraphics As Graphics = Nothing

		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub richEditControl1_DragEnter(ByVal sender As Object, ByVal e As DragEventArgs) Handles richEditControl1.DragEnter
			If (Not e.Data.GetDataPresent(DataFormats.FileDrop)) Then
				Return
			End If

			richEditControl1.Options.Behavior.Drop = DevExpress.XtraRichEdit.DocumentCapability.Disabled
			e.Effect = DragDropEffects.Copy
		End Sub

		Private Sub richEditControl1_DragOver(ByVal sender As Object, ByVal e As DragEventArgs) Handles richEditControl1.DragOver
			If (Not e.Data.GetDataPresent(DataFormats.FileDrop)) Then
				Return
			End If

			Dim docPoint As Point = Units.PixelsToDocuments(richEditControl1.PointToClient(Form.MousePosition), richEditControl1.DpiX, richEditControl1.DpiY)

            Dim pos As DocumentPosition = richEditControl1.GetPositionFromPoint(docPoint)
            If pos IsNot Nothing Then
                Dim rect As Rectangle = Units.DocumentsToPixels(richEditControl1.GetBoundsFromPosition(pos), richEditControl1.DpiX, richEditControl1.DpiY)

                richEditControl1.Document.CaretPosition = pos

                If richEditGraphics Is Nothing Then
                    richEditGraphics = richEditControl1.CreateGraphics()
                End If

                rect.Width = 2
                richEditControl1.Refresh()
                richEditGraphics.FillRectangle(Brushes.Blue, rect)
                richEditControl1.ScrollToCaret()
            End If
        End Sub

		Private Sub richEditControl1_DragDrop(ByVal sender As Object, ByVal e As DragEventArgs) Handles richEditControl1.DragDrop
			If (Not e.Data.GetDataPresent(DataFormats.FileDrop)) Then
				Return
			End If

			Dim path As String = (CType(e.Data.GetData(DataFormats.FileDrop), String()))(0)
			Dim server As New RichEditDocumentServer()

			server.LoadDocument(path)

			richEditControl1.Document.BeginUpdate()
			Dim rangeInsertedContent As DocumentRange = richEditControl1.Document.InsertDocumentContent(richEditControl1.Document.CaretPosition, server.Document.Range)
			Dim rangeNewLine As DocumentRange = richEditControl1.Document.CreateRange(rangeInsertedContent.End.ToInt() - 1, 1)
			richEditControl1.Document.Delete(rangeNewLine)
			richEditControl1.Document.EndUpdate()

			richEditControl1.Options.Behavior.Drop = DevExpress.XtraRichEdit.DocumentCapability.Enabled
		End Sub
	End Class
End Namespace