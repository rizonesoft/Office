Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraEditors
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native

Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class InsertFieldDialog
		Inherits XtraForm

		Private richEditControl As RichEditControl

		Public Sub New(ByVal control As RichEditControl)
			InitializeComponent()
			richEditControl = control
		End Sub

		Private Sub InsertFieldDialog_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
			simpleButtonOk.Enabled = InsertFieldRichEditHelper.VariableTypes.Keys.Count > 0
			If listBoxFieldNames.Items.Count = 0 Then
				For i As Integer = 0 To InsertFieldRichEditHelper.VariableTypes.Keys.Count - 1
					listBoxFieldNames.Items.Add(InsertFieldRichEditHelper.VariableTypes.Keys.ToList()(i))
				Next i
				listBoxFieldNames.SelectedIndex = 0
			End If
		End Sub

		Private Sub simpleButtonOk_Click(ByVal sender As Object, ByVal e As EventArgs) Handles simpleButtonOk.Click
			Dim fieldCode As String = InsertFieldRichEditHelper.CurrentVariableType
			Dim parametersDialog As IFieldParametersDialog = TryCast(InsertFieldRichEditHelper.VariableTypes(InsertFieldRichEditHelper.CurrentVariableType), IFieldParametersDialog)
			If parametersDialog IsNot Nothing Then
				Dim parametersString As String = parametersDialog.GenerateFieldParametersString()
				Dim currentDocument As SubDocument = richEditControl.Document.CaretPosition.BeginUpdateDocument()

				If TypeOf parametersDialog Is ucIFFIELD Then
					Dim IFFieldInsertDialog As ucIFFIELD = TryCast(parametersDialog, ucIFFIELD)
					If IFFieldInsertDialog.IsFieldParametersValid() Then

						Dim newField As Field = currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode & " " & parametersString)

						Dim nestedFiueldsList As List(Of String) = IFFieldInsertDialog.GetNestedFieldsList()

						For Each nestedFieldCode As String In nestedFiueldsList
							Dim ranges() As DocumentRange = currentDocument.FindAll(nestedFieldCode, SearchOptions.WholeWord)
							For Each range As DocumentRange In ranges
								currentDocument.Fields.Create(range)
							Next range
						Next nestedFieldCode
					End If
				Else
					If parametersString <> InsertFieldRichEditHelper.EmptyFieldCode Then
						currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode & " " & parametersString)
					Else
						currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode)
					End If
				End If

				currentDocument.Fields.Update()
				richEditControl.Document.CaretPosition.EndUpdateDocument(currentDocument)
			End If
			Close()
		End Sub

		Private Sub listBoxFieldNames_SelectedIndexChanged(ByVal sender As Object, ByVal e As EventArgs) Handles listBoxFieldNames.SelectedIndexChanged
			InsertFieldRichEditHelper.CurrentVariableType = listBoxFieldNames.SelectedItem.ToString()
			layoutControl1.BeginUpdate()
			Dim previousControl As Control = layoutControlItemMainContent.Control
			layoutControlItemMainContent.Control = InsertFieldRichEditHelper.VariableTypes(InsertFieldRichEditHelper.CurrentVariableType)
			previousControl.Parent = Nothing
			layoutControl1.EndUpdate()
		End Sub
	End Class
End Namespace
