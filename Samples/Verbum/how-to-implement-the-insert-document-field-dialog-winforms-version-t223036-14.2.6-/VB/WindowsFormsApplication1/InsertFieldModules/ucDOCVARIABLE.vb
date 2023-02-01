Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Drawing
Imports System.Data
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms

Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class ucDOCVARIABLE
		Inherits UserControl
		Implements IFieldParametersDialog
		Public Sub New()
			InitializeComponent()
		End Sub

		#Region "IFieldParametersDialog Members"

		Public Function GenerateFieldParametersString() As String Implements IFieldParametersDialog.GenerateFieldParametersString
			Dim resultString As String = ""
			If textEditVariableName.Text.Trim() = "" Then
				Return InsertFieldRichEditHelper.EmptyFieldCode
			End If

			resultString &= textEditVariableName.Text.Trim()
			If textEditArgument1.Text.Trim() <> "" Then
				resultString &= " " & textEditArgument1.Text.Trim()
			End If
			If textEditArgument2.Text.Trim() <> "" Then
				resultString &= " " & textEditArgument2.Text.Trim()
			End If
			If textEditArgument3.Text.Trim() <> "" Then
				resultString &= " " & textEditArgument3.Text.Trim()
			End If
			If textEditArgument4.Text.Trim() <> "" Then
				resultString &= " " & textEditArgument4.Text.Trim()
			End If
			Return resultString
		End Function

		#End Region
	End Class
End Namespace
