Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.IO
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.Internal
Imports DevExpress.XtraRichEdit.Services

Namespace RichEditControlExtensions
	Public Class CustomRichEditCommandFactoryService
		Implements IRichEditCommandFactoryService
		Private ReadOnly service As IRichEditCommandFactoryService
		Private ReadOnly control As RichEditControl

		Public Sub New(ByVal control As RichEditControl, ByVal service As IRichEditCommandFactoryService)
			DevExpress.Utils.Guard.ArgumentNotNull(control, "control")
			DevExpress.Utils.Guard.ArgumentNotNull(service, "service")
			Me.control = control
			Me.service = service
		End Sub

        Public Function CreateCommand(ByVal id As RichEditCommandId) As RichEditCommand Implements IRichEditCommandFactoryService.CreateCommand
            If id.Equals(RichEditCommandId.FileOpen) Then
                Return New CustomLoadDocumentCommand(control)
            End If

            Return service.CreateCommand(id)
        End Function
	End Class

	Public Class CustomLoadDocumentCommand
		Inherits LoadDocumentCommand
		Public Sub New(ByVal richEdit As IRichEditControl)
			MyBase.New(richEdit)
		End Sub

		Protected Overrides Sub ExecuteCore()

			Dim openFileDialog1 As New OpenFileDialog()
			openFileDialog1.InitialDirectory = ""
			openFileDialog1.Filter = "All files (*.*)|*.*"
			openFileDialog1.Filter &= "|Rich Text Format (*.rtf)|*.rtf"
			openFileDialog1.Filter &= "|Text Files (*.txt)|*.txt"
			openFileDialog1.Filter &= "|HyperText Markup Language Format (*.html)|*.html"
			openFileDialog1.Filter &= "|Word 2007 Document (*.docx)|*.docx"
			openFileDialog1.Filter &= "|OpenDocument Text Document (*.odt)|*.odt"
			openFileDialog1.Filter &= "|Microsoft Word Document (*.doc)|*.doc"

			openFileDialog1.FilterIndex = 1
			openFileDialog1.RestoreDirectory = True

			If openFileDialog1.ShowDialog() = DialogResult.OK Then
				Try
					Control.LoadDocumentEx(openFileDialog1.FileName)
				Catch ex As Exception
					MessageBox.Show("Error: Could not read file from disk. Original error: " & ex.Message)
				End Try
			End If

			'base.ExecuteCore();
		End Sub
	End Class
End Namespace
