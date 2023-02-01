Imports Microsoft.VisualBasic
Imports System
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.API.Native

Namespace RichEditSelectSpecificLine
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub button1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles button1.Click
			SelectCurrentLine()
		End Sub

		Private Sub SelectCurrentLine()
			Dim startOfLineCommand As New StartOfLineCommand(richEditControl1)
			Dim endOfLineCommand As New EndOfLineCommand(richEditControl1)

			startOfLineCommand.Execute()

			Dim start As Integer = richEditControl1.Document.CaretPosition.ToInt()

			endOfLineCommand.Execute()

			Dim length As Integer = richEditControl1.Document.CaretPosition.ToInt() - start

			Dim range As DocumentRange = richEditControl1.Document.CreateRange(start, length)
			Dim range2 As DocumentRange = richEditControl1.Document.CreateRange(start, length + 1)

			Dim text As String = richEditControl1.Document.GetText(range2)

			If text.EndsWith(Environment.NewLine) Then
				richEditControl1.Document.Selection = range2
			Else
				richEditControl1.Document.Selection = range
			End If
		End Sub
	End Class
End Namespace