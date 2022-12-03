Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Text
Imports System.Windows.Forms
#Region "#usings"
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Import
#End Region ' #usings

Namespace BeforeImport
	Partial Public Class Form1
		Inherits Form
		Private imgPath As String
		Private cur_Encoding As Encoding

		Public Sub New()
			InitializeComponent()
			labelControl1.Text = "Use radio buttons to switch folder containing images"
			labelControl2.Text = "Select correct encoding and press the button to load Cyrillic text"
			LoadSampleHTML()
			InitEncodings()
		End Sub

		Private Sub InitEncodings()
			cmbEncodings.Properties.Items.BeginUpdate()
			cmbEncodings.Properties.Items.Add("koi8-r")
			cmbEncodings.Properties.Items.Add("koi8-u")
			cmbEncodings.Properties.Items.Add("windows-1251")
			cmbEncodings.Properties.Items.Add("cp866")
			cmbEncodings.Properties.Items.EndUpdate()


		End Sub

		Private Sub LoadSampleHTML()
			imgPath = rgImgPath.EditValue.ToString()
			richEditControl1.LoadDocument("sample.htm", DocumentFormat.Html)
		End Sub

		Private Sub LoadSampleText()
			If cmbEncodings.SelectedItem Is Nothing Then
				cur_Encoding = Encoding.Unicode
			Else
				cur_Encoding = Encoding.GetEncoding(cmbEncodings.SelectedItem.ToString())
			End If
			richEditControl2.LoadDocument("TerribleRevengeKOI8R.txt", DocumentFormat.PlainText)
		End Sub

		#Region "#beforeimport"
		Private Sub richEditControl1_BeforeImport(ByVal sender As Object, ByVal e As BeforeImportEventArgs) Handles richEditControl1.BeforeImport
			If e.DocumentFormat = DocumentFormat.Html Then
				e.Options.SourceUri = "file:///" & Application.StartupPath & imgPath
			End If
		End Sub
		Private Sub richEditControl2_BeforeImport(ByVal sender As Object, ByVal e As BeforeImportEventArgs) Handles richEditControl2.BeforeImport
			If e.DocumentFormat = DocumentFormat.PlainText Then
				CType(e.Options, PlainTextDocumentImporterOptions).Encoding = cur_Encoding
			End If
		End Sub
		#End Region ' #beforeimport
		Private Sub rgImgPath_SelectedIndexChanged(ByVal sender As Object, ByVal e As EventArgs) Handles rgImgPath.SelectedIndexChanged
			LoadSampleHTML()
		End Sub

		Private Sub btnLoadRTF_Click(ByVal sender As Object, ByVal e As EventArgs) Handles btnLoadRTF.Click
			LoadSampleText()
		End Sub

	End Class
End Namespace