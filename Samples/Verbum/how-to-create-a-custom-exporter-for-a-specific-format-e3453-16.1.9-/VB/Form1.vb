Imports Microsoft.VisualBasic
Imports System
Imports System.IO
Imports System.Windows.Forms

Namespace RichEditBBCExporter
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			BBCodeDocumentExporter.Register(richEditControl1)

			richEditControl1.LoadDocument("test.html")
		End Sub

		Private Sub button1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles button1.Click
			richEditControl1.SaveDocument("test.bbc", BBCodeDocumentFormat.Id)
		End Sub
	End Class
End Namespace