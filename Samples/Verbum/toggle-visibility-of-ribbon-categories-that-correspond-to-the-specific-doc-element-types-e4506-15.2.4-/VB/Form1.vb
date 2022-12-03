Imports Microsoft.VisualBasic
Imports System
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit

Namespace RichEditToggleRibbonCategories
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()
			richEditControl1.LoadDocument("Template.rtf")
		End Sub

		Private Sub richEditControl1_StartHeaderFooterEditing(ByVal sender As Object, ByVal e As HeaderFooterEditingEventArgs) Handles richEditControl1.StartHeaderFooterEditing
			headerFooterToolsRibbonPageCategory1.Visible = True
			ribbonControl1.SelectedPage = headerFooterToolsDesignRibbonPage1
		End Sub

		Private Sub richEditControl1_FinishHeaderFooterEditing(ByVal sender As Object, ByVal e As HeaderFooterEditingEventArgs) Handles richEditControl1.FinishHeaderFooterEditing
			headerFooterToolsRibbonPageCategory1.Visible = False
		End Sub

		Private Sub richEditControl1_SelectionChanged(ByVal sender As Object, ByVal e As EventArgs) Handles richEditControl1.SelectionChanged
			tableToolsRibbonPageCategory1.Visible = richEditControl1.IsSelectionInTable()
			floatingPictureToolsRibbonPageCategory1.Visible = richEditControl1.IsFloatingObjectSelected
		End Sub
	End Class
End Namespace