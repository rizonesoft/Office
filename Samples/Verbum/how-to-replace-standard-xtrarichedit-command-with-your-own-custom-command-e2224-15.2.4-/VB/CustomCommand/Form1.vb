Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.Services
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.Utils
Imports DevExpress.Utils.Commands

Namespace CustomCommand
    Partial Public Class Form1
        Inherits Form

        Public Sub New()
            InitializeComponent()
            MyFactoryHelper.SetMyNewCommandFactory(Me.richEditControl1)
            richEditControl1.CreateNewDocument()
            richEditControl1.Document.AppendSingleLineText("Type at least 7 paragraphs to be able to save the document.")
        End Sub
    End Class

    #Region "#iricheditcommandfactoryservice"
    Public NotInheritable Class MyFactoryHelper

        Private Sub New()
        End Sub

        Public Shared Sub SetMyNewCommandFactory(ByVal control As RichEditControl)
            Dim myCommandFactory = New CustomRichEditCommandFactoryService(control, control.GetService(Of IRichEditCommandFactoryService)())
            control.ReplaceService(Of IRichEditCommandFactoryService)(myCommandFactory)
        End Sub
    End Class

    Public Class CustomRichEditCommandFactoryService
        Implements IRichEditCommandFactoryService

        Private ReadOnly service As IRichEditCommandFactoryService
        Private ReadOnly control As RichEditControl

        Public Sub New(ByVal control As RichEditControl, ByVal service As IRichEditCommandFactoryService)
            Me.control = control
            Me.service = service
        End Sub
        Public Function CreateCommand(ByVal id As RichEditCommandId) As RichEditCommand Implements IRichEditCommandFactoryService.CreateCommand
            If id = RichEditCommandId.FileSave Then
                Return New CustomSaveDocumentCommand(control)
            End If
            Return service.CreateCommand(id)
        End Function
    End Class

    Public Class CustomSaveDocumentCommand
        Inherits SaveDocumentCommand

        Public Sub New(ByVal control As IRichEditControl)
            MyBase.New(control)
        End Sub
        Protected Overrides Sub UpdateUIStateCore(ByVal state As ICommandUIState)
            MyBase.UpdateUIStateCore(state)
            ' Disable the command if the document has less than 5 paragraphs.
            state.Enabled = Control.Document.Paragraphs.Count > 5
        End Sub

        Protected Overrides Sub ExecuteCore()
            ' Cancel execution if the document contains less than 7 paragraphs.
            If Control.Document.Paragraphs.Count > 7 Then
                MyBase.ExecuteCore()
            Else
                MessageBox.Show("You should type at least 7 paragraphs to be able to save the document.", "Please be creative", MessageBoxButtons.OK, MessageBoxIcon.Information)
            End If
        End Sub
    End Class
    #End Region ' #iricheditcommandfactoryservice
End Namespace