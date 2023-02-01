Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native

Namespace RichEditCheckFonts
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			richEditControl1.LoadDocument("test.rtf")
		End Sub

		Private Sub button1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles button1.Click
			Dim fonts As List(Of String) = GetUsedFonts()

			MessageBox.Show(String.Join(", ", fonts.ToArray()), "Used fonts")
		End Sub

		Private Function GetUsedFonts() As List(Of String)
			Dim fonts As New List(Of String)()

			Dim document As Document = richEditControl1.Document

			document.BeginUpdate()
			Dim length As Integer = richEditControl1.Document.Range.Length

			For i As Integer = 0 To length - 2
				Dim range As DocumentRange = document.CreateRange(i, 1)
				Dim cp As CharacterProperties = document.BeginUpdateCharacters(range)

				If (Not fonts.Contains(cp.FontName)) Then
					fonts.Add(cp.FontName)
				End If

				document.EndUpdateCharacters(cp)
			Next i

			document.EndUpdate()

			Return fonts
		End Function
	End Class
End Namespace