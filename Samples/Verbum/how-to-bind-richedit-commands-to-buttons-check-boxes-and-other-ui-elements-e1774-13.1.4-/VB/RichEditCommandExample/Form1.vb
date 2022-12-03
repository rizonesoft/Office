Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Text
Imports System.Windows.Forms
#Region "#usings"
Imports DevExpress.Utils.Commands
Imports DevExpress.XtraRichEdit.Commands
#End Region ' #usings

Namespace RichEditCommandExample
	Partial Public Class Form1
		Inherits Form
		Public Sub New()

			InitializeComponent()

'			#Region "#commandbuttonusage"
			btnUndo.Initialize(richEditControl1, RichEditCommandId.Undo)
'			#End Region ' #commandbuttonusage

'			#Region "#commandbuttonadapterusage"
			Dim redoAdapter As New CommandButtonAdapter()
			redoAdapter.Initialize(richEditControl1, RichEditCommandId.Undo)
			redoAdapter.Button = btnRedo
			redoAdapter.CommandId = RichEditCommandId.Redo
			redoAdapter.RichEditControl = richEditControl1
'			#End Region ' #commandbuttonadapterusage

			Dim fontBoldAdapter As New CommandCheckBoxAdapter()
			fontBoldAdapter.CommandId = RichEditCommandId.ToggleFontBold
			fontBoldAdapter.RichEditControl = richEditControl1
			fontBoldAdapter.CheckBox = chkToggleFontBold

		End Sub

		Private Sub btnToggleReadOnly_Click(ByVal sender As Object, ByVal e As EventArgs) Handles btnToggleReadonly.Click
			richEditControl1.ReadOnly = Not richEditControl1.ReadOnly
		End Sub
	End Class
End Namespace