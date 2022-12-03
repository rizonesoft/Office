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
	Partial Public Class ucIFFIELD
		Inherits UserControl
		Implements IFieldParametersDialog
		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub comboBoxEdit1_SelectedIndexChanged(ByVal sender As Object, ByVal e As EventArgs) Handles comboBoxEditOperation.SelectedIndexChanged
			GenerateLayoutControlGroupsCaptions()
		End Sub

		Protected Overrides Sub OnLoad(ByVal e As EventArgs)
			MyBase.OnLoad(e)
			GenerateLayoutControlGroupsCaptions()
		End Sub

		Private Sub GenerateLayoutControlGroupsCaptions()
			Dim leftTemplate As String = "A value isnerted when the LEFT expression"
			Dim rightTemplate As String = "the RIGHT expression"

			Dim trueText As String = ""
			Dim falseText As String = ""

			Select Case comboBoxEditOperation.Text
				Case "="
					trueText = "EQUALS"
					falseText = "DOESN'T EQUAL"
				Case "<>"
					trueText = "DOESN'T EQUAL"
					falseText = "EQUALS"
				Case ">"
					trueText = "IS GREATER THAN"
					falseText = "IS NOT GREATER THAN"
				Case "<"
					trueText = "IS LESS THAN"
					falseText = "IS NOT LESS THAN"
				Case ">="
					trueText = "IS GREATER THAN OR EQUALS"
					falseText = "IS LESS THAN"
				Case "<="
					trueText = "IS LESS THAN OR EQUALS"
					falseText = "IS GREATER THAN"
				Case Else
			End Select

			layoutControlGroup4.Text = leftTemplate & " " & trueText & " " & rightTemplate
			layoutControlGroup5.Text = leftTemplate & " " & falseText & " " & rightTemplate

		End Sub

		#Region "IFieldParametersDialog Members"

		Public Function GenerateFieldParametersString() As String Implements IFieldParametersDialog.GenerateFieldParametersString
			Dim resultString As String = ""
			resultString &= textEditLeftExpression.Text.Trim()
			resultString &= " " & comboBoxEditOperation.Text & " "
			resultString &= textEditRIGHTExpression.Text.Trim()
			resultString &= " " & textEditResultTRUE.Text.Trim() & " "
			resultString &= textEditResultFALSE.Text.Trim()
			Return resultString
		End Function
		#End Region

		Public Function IsFieldParametersValid() As Boolean
			If textEditLeftExpression.Text.Trim() = "" Then
				Return False
			End If
			If textEditRIGHTExpression.Text.Trim() = "" Then
				Return False
			End If
			If textEditResultFALSE.Text.Trim() = "" Then
				Return False
			End If
			If textEditResultTRUE.Text.Trim() = "" Then
				Return False
			End If
			Return True
		End Function

		Public Function GetNestedFieldsList() As List(Of String)
			Dim nestedFieldsList As New List(Of String)()
			If checkEditInsertLeftAsField.Checked Then
				nestedFieldsList.Add(textEditLeftExpression.Text.Trim())
			End If
			If checkEditInsertRightAsField.Checked Then
				nestedFieldsList.Add(textEditRIGHTExpression.Text.Trim())
			End If
			If checkEditInsertResultFALSEAsField.Checked Then
				nestedFieldsList.Add(textEditResultFALSE.Text.Trim())
			End If
			If checkEditInsertResultTRUEAsField.Checked Then
				nestedFieldsList.Add(textEditResultTRUE.Text.Trim())
			End If
			Return nestedFieldsList
		End Function
	End Class
End Namespace
