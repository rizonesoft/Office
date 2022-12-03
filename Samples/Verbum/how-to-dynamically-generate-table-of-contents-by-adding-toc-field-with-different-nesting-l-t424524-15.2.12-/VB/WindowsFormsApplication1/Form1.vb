Imports Microsoft.VisualBasic
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
Imports DevExpress.XtraRichEdit.API.Native

Namespace WindowsFormsApplication1
	Partial Public Class Form1
		Inherits RibbonForm
		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
			richEditControl1.CreateNewDocument()
		End Sub

		Private Sub simpleButton1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles simpleButton1.Click
			If textEdit1.Text.Trim() = "" OrElse memoEdit1.Text.Trim() = "" Then
				Return
			End If

			Dim isTocInserted As Boolean = False
			For i As Integer = 0 To richEditControl1.Document.Fields.Count - 1
				Dim currentField As Field = richEditControl1.Document.Fields(i)
				Dim fieldCode As String = richEditControl1.Document.GetText(currentField.CodeRange)
				If fieldCode.Contains("TOC") Then
					isTocInserted = True
					Exit For
				End If
			Next i

			If isTocInserted Then
				TOCContentHelper.AppendNewDocumentFragment(textEdit1.Text.Trim(), memoEdit1.Text.Trim(), richEditControl1.Document, Convert.ToInt32(spinEdit1.EditValue), True)
			Else
				TOCContentHelper.InsertTOC("\h", richEditControl1.Document)
				TOCContentHelper.AppendNewDocumentFragment(textEdit1.Text.Trim(), memoEdit1.Text.Trim(), richEditControl1.Document, Convert.ToInt32(spinEdit1.EditValue), False)
				TOCContentHelper.InsertPageNumber(richEditControl1.Document)
			End If
			richEditControl1.Document.Fields.Update()
			TOCContentHelper.UpdateTOCFieldFormatting(richEditControl1.Document)
		End Sub
	End Class
End Namespace
