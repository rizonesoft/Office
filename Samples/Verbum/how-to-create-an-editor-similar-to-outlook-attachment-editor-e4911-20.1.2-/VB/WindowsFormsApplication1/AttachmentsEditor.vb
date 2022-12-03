' Developer Express Code Central Example:
' How to create an editor similar to Outlook Attachment Editor
' 
' This example demonstrates how the RichEditControl component can be used to
' emulate the Outlook Attachment Editor behavior.
' The main idea of the approach
' demonstrated in this sample is to use the DOCVARIABLE field
' (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
' display corresponding RTF content for each inserted file.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E4911


Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit

Namespace WindowsFormsApplication1
	Partial Public Class AttachmentsEditor
		Inherits UserControl
		Public Sub New()
			InitializeComponent()
		End Sub

		'int filesCount = 0;
		Private filesCollection As New Dictionary(Of String, FileFieldInfo)()
		Private Sub simpleButton1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles simpleAddButton.Click
			Dim openFileDialog As New OpenFileDialog()
			openFileDialog.Title = "Select a file"
			openFileDialog.Filter = "All files|*.*"
			If openFileDialog.ShowDialog() = DialogResult.OK Then
				If filesCollection.ContainsKey(openFileDialog.SafeFileName) Then
					MessageBox.Show(String.Format("The file: {0} is already added to collection", openFileDialog.SafeFileName))
					Return
				End If
				richEditControl1.Document.Fields.Create(richEditControl1.Document.Range.End, "DOCVARIABLE " & openFileDialog.SafeFileName)
				filesCollection.Add(openFileDialog.SafeFileName, New FileFieldInfo() With {.DocField = richEditControl1.Document.Fields(richEditControl1.Document.Fields.Count - 1), .FileName = openFileDialog.SafeFileName, .FullFileName = openFileDialog.FileName})
				richEditControl1.Document.Fields.Update()

			End If
		End Sub

		Private Sub AttachmentsEditor_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
			richEditControl1.CreateNewDocument()
			richEditControl1.Document.DefaultCharacterProperties.FontName = "Times New Roman"
			richEditControl1.Document.DefaultCharacterProperties.FontSize = 10
			AddHandler richEditControl1.SelectionChanged, AddressOf richEditControl1_SelectionChanged
			AddHandler richEditControl1.Document.ContentChanged, AddressOf Document_ContentChanged
			AddHandler richEditControl1.Document.CalculateDocumentVariable, AddressOf Document_CalculateDocumentVariable

		End Sub

		Private isLocked As Boolean = False
		Private Sub richEditControl1_SelectionChanged(ByVal sender As Object, ByVal e As EventArgs)
			If isLocked Then
				Return
			End If
			SyncronizeFilesCollection()

			Dim pos As DocumentPosition = richEditControl1.Document.CaretPosition
			For Each item As KeyValuePair(Of String, FileFieldInfo) In filesCollection
				Dim fieldRange As DocumentRange = item.Value.DocField.ResultRange
				If fieldRange.Contains(pos) AndAlso fieldRange.Start.ToInt() <> pos.ToInt() AndAlso fieldRange.End.ToInt() <> pos.ToInt() Then
					isLocked = True
					Dim deltaFromStart As Integer = pos.ToInt() - fieldRange.Start.ToInt()
					Dim deltaFromEnd As Integer = fieldRange.End.ToInt() - pos.ToInt()
					If deltaFromEnd > deltaFromStart Then
						richEditControl1.Document.CaretPosition = item.Value.DocField.Range.End
					Else
						richEditControl1.Document.CaretPosition = item.Value.DocField.Range.Start
					End If
					isLocked = False
					Exit For
				End If
			Next item
		End Sub


		Private Sub Document_CalculateDocumentVariable(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.CalculateDocumentVariableEventArgs)
			If filesCollection.ContainsKey(e.VariableName) Then
				Dim server As IRichEditDocumentServer = richEditControl1.CreateDocumentServer()
				Dim info As FileFieldInfo = filesCollection(e.VariableName)
				server.Document.Images.Insert(server.Document.Range.End, New Bitmap(Icon.ExtractAssociatedIcon(info.FullFileName).ToBitmap(), New Size(16, 16)))
				Dim range As DocumentRange = server.Document.AppendText(info.FileName & "; ")
				Dim hyperlink As Hyperlink = server.Document.Hyperlinks.Create(range.Start, range.Length - 1)
				hyperlink.Target = info.FullFileName
				hyperlink.ToolTip = info.FileName
				hyperlink.NavigateUri = info.FullFileName

				e.Value = server.Document
				e.Handled = True
			End If
		End Sub

		Private Sub Document_ContentChanged(ByVal sender As Object, ByVal e As EventArgs)
			SyncronizeFilesCollection()
		End Sub

		Private Sub SyncronizeFilesCollection()
			Dim removedKeys As New List(Of String)()
			For Each key As String In filesCollection.Keys
				Dim keyExist As Boolean = False
				For Each field As Field In richEditControl1.Document.Fields
					If filesCollection(key).DocField Is field Then
						keyExist = True
						Exit For
					End If
				Next field
				If (Not keyExist) Then
					removedKeys.Add(key)
				End If
			Next key
			For Each removedKey As String In removedKeys
				filesCollection.Remove(removedKey)
			Next removedKey
		End Sub

	End Class

	Public Class FileFieldInfo
		Public Property DocField() As Field
		Public Property FileName() As String
		Public Property FullFileName() As String
	End Class
End Namespace
