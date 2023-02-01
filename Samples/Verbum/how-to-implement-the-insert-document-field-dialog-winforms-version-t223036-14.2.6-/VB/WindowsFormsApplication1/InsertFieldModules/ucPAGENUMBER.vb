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
	Partial Public Class ucPAGENUMBER
		Inherits UserControl
		Implements IFieldParametersDialog
		Public Sub New(ByVal currentFieldName As String)
			InitializeComponent()
			If currentFieldName = "PAGE" Then
				InitializeListBoxItemsPage()
				labelControl1.Text = "At present the PAGE (NUMPAGES) field attributes are not supported." & Constants.vbCrLf
				labelControl1.Text &= "<href=https://www.devexpress.com/Support/Center/Question/Details/T221870>https://www.devexpress.com/Support/Center/Question/Details/T221870</href>"
				AddHandler labelControl1.HyperlinkClick, AddressOf labelControl1_HyperlinkClick
			Else
				InitializeListBoxItemsNumPages()
				layoutControlItem2.Visibility = DevExpress.XtraLayout.Utils.LayoutVisibility.Never
			End If

		End Sub

		Private Sub labelControl1_HyperlinkClick(ByVal sender As Object, ByVal e As DevExpress.Utils.HyperlinkClickEventArgs)
			System.Diagnostics.Process.Start(e.Link)
		End Sub

		Private Sub InitializeListBoxItemsPage()
			Dim listSource As New List(Of FieldAttributeItem)()
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "1, 2, 3, ...", .AttributeValue = "\* Arabic"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "- 1 -, - 2- , - 3- , ...", .AttributeValue = "\* ArabicDash"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "a, b, c, ...", .AttributeValue = "\* alphabetic"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "A, B, C, ...", .AttributeValue = "\* ALPHABETIC"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "i, ii, iii, ...", .AttributeValue = "\* roman"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "I, II, III, ...", .AttributeValue = "\* ROMAN"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "Use Default Numbering", .AttributeValue = "EMPTY"})

			listBoxControlAttributes.DataSource = listSource
			listBoxControlAttributes.DisplayMember = "DisplayName"
			listBoxControlAttributes.ValueMember = "AttributeValue"
		End Sub

		Private Sub InitializeListBoxItemsNumPages()
			Dim listSource As New List(Of FieldAttributeItem)()
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "(none)", .AttributeValue = "EMPTY"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "1, 2, 3, ...", .AttributeValue = "\* Arabic"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "a, b, c, ...", .AttributeValue = "\* alphabetic"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "A, B, C, ...", .AttributeValue = "\* ALPHABETIC"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "i, ii, iii, ...", .AttributeValue = "\* roman"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "I, II, III, ...", .AttributeValue = "\* ROMAN"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "1st, 2nd, 3rd, ...", .AttributeValue = "\* Ordinal"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "One, Two, Three, ...", .AttributeValue = "\* CardText"})
			listSource.Add(New FieldAttributeItem() With {.DisplayName = "First, Second, Third, ...", .AttributeValue = "\* OrdText"})

			listBoxControlAttributes.DataSource = listSource
			listBoxControlAttributes.DisplayMember = "DisplayName"
			listBoxControlAttributes.ValueMember = "AttributeValue"
		End Sub


		#Region "IFieldParametersDialog Members"

		Public Function GenerateFieldParametersString() As String Implements IFieldParametersDialog.GenerateFieldParametersString
			Dim resultString As String = ""
			If listBoxControlAttributes.SelectedValue IsNot Nothing AndAlso listBoxControlAttributes.SelectedValue.ToString() <> "EMPTY" Then
				resultString = listBoxControlAttributes.SelectedValue.ToString()
			End If
			Return resultString
		End Function

		#End Region
	End Class
End Namespace
