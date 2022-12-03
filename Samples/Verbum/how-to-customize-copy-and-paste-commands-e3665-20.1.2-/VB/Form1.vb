Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.Services

Namespace RichEditCustomCopyPaste
	Partial Public Class Form1
		Inherits Form

		Public ReadOnly Property UseCustomCopy() As Boolean
			Get
				Return cbCopyHtml.Checked
			End Get
		End Property
		Public ReadOnly Property UseCustomPaste() As Boolean
			Get
				Return cbPastePlainText.Checked
			End Get
		End Property

		Public Sub New()
			InitializeComponent()

			Dim commandFactory As New CustomRichEditCommandFactoryService(richEditControl1, richEditControl1.GetService(Of IRichEditCommandFactoryService)())
			richEditControl1.RemoveService(GetType(IRichEditCommandFactoryService))
			richEditControl1.AddService(GetType(IRichEditCommandFactoryService), commandFactory)
		End Sub
	End Class

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
			If id = RichEditCommandId.CopySelection AndAlso DirectCast(Application.OpenForms(0), Form1).UseCustomCopy Then
				Return New CustomCopySelectionCommand(control)
			End If
			If id = RichEditCommandId.PasteSelection AndAlso DirectCast(Application.OpenForms(0), Form1).UseCustomPaste Then
				Return New CustomPasteSelectionCommand(control)
			End If

			Return service.CreateCommand(id)
		End Function
	End Class
End Namespace