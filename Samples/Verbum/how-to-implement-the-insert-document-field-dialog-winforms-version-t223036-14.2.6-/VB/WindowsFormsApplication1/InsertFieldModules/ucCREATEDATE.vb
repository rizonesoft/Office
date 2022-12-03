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
	Partial Public Class ucCREATEDATE
		Inherits UserControl
		Implements IFieldParametersDialog
		Public Sub New()
			InitializeComponent()
			InitializeListBoxItemsDateFormats()
		End Sub

		Private Sub InitializeListBoxItemsDateFormats()
			AddHandler listBoxControlFormats.SelectedValueChanged, AddressOf listBoxControlFormats_SelectedValueChanged
			Dim dateTimeFormats() As String = { "dd.MM.yyyy", "dddd, d. MMMM yyyy", "d. MMMM yyyy", "dd.MM.yy", "yyyy-MM-dd", "yy-MM-dd", "dd/MM/yyyy", "dd. MMM. yyyy", "dd/MM/yy", "MMMM yy", "MMM-yy", "dd.MM.yyyy HH:mm", "dd.MM.yyyy HH:mm:ss", "h:mm am/pm", "h:mm:ss am/pm", "HH:mm", "HH:mm:ss" }

			Dim listSource As New List(Of FieldAttributeItem)()
			For i As Integer = 0 To dateTimeFormats.Length - 1
				listSource.Add(New FieldAttributeItem() With {.DisplayName = DateTime.Now.ToString(dateTimeFormats(i).Replace("am/pm", "tt")), .AttributeValue = dateTimeFormats(i)})
			Next i

			listBoxControlFormats.DataSource = listSource
			listBoxControlFormats.DisplayMember = "DisplayName"
			listBoxControlFormats.ValueMember = "AttributeValue"
		End Sub

		Private Sub listBoxControlFormats_SelectedValueChanged(ByVal sender As Object, ByVal e As EventArgs)
			textEditCurrentFormat.Text = If(listBoxControlFormats.SelectedValue Is Nothing, "", listBoxControlFormats.SelectedValue.ToString())
		End Sub

		#Region "IFieldParametersDialog Members"

		Public Function GenerateFieldParametersString() As String Implements IFieldParametersDialog.GenerateFieldParametersString
			Dim resultString As String = ""
			If textEditCurrentFormat.Text.Trim() <> "" Then
				resultString = "\@ """ & textEditCurrentFormat.Text.Trim() & """"
			End If
			Return resultString
		End Function

		#End Region
	End Class
End Namespace
