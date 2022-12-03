Imports System
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.Commands.Internal
Imports DevExpress.XtraRichEdit.Export
Imports DevExpress.XtraRichEdit.Export.Html
Imports DevExpress.XtraRichEdit.Utils
Imports DevExpress.Office.Commands.Internal
Imports DevExpress.Office.Utils

Namespace RichEditCustomCopyPaste
	Public Class CustomCopySelectionCommand
		Inherits CopySelectionCommand

		Public Sub New(ByVal control As IRichEditControl)
			MyBase.New(control)
		End Sub
		Protected Overrides Sub ExecuteCore()
			Dim richEditControl As RichEditControl = DirectCast(Control, RichEditControl)
			AddHandler richEditControl.BeforeExport, AddressOf OnBeforeExport
			Dim htmlForClipboard As String = String.Empty

			richEditControl.Options.Export.Html.ExportRootTag = ExportRootTag.Html

			Try
				Dim html As String = Control.Document.GetHtmlText(Control.Document.Selection, New CustomUriProvider(), richEditControl.Options.Export.Html)
				htmlForClipboard = CF_HTMLHelper.GetHtmlClipboardFormat(html)
			Finally
				RemoveHandler richEditControl.BeforeExport, AddressOf OnBeforeExport
			End Try

			Dim data As New DataObject()
			data.SetData(OfficeDataFormats.Rtf, richEditControl.Document.GetRtfText(richEditControl.Document.Selection))
			data.SetData(OfficeDataFormats.UnicodeText, richEditControl.Document.GetText(richEditControl.Document.Selection))
			data.SetData(OfficeDataFormats.Html, htmlForClipboard)
			Clipboard.Clear()
			Clipboard.SetDataObject(data, False)
		End Sub

		Private Sub OnBeforeExport(ByVal sender As Object, ByVal e As BeforeExportEventArgs)
			Dim exporterOptions As HtmlDocumentExporterOptions = TryCast(e.Options, HtmlDocumentExporterOptions)

			If exporterOptions IsNot Nothing Then
				exporterOptions.CssPropertiesExportType = CssPropertiesExportType.Inline
				exporterOptions.ExportRootTag = ExportRootTag.Body
				exporterOptions.EmbedImages = False ' To delegate handling into a CustomUriProvider
			End If
		End Sub
	End Class
	Public Class CustomPasteSelectionCommand
		Inherits PasteSelectionCommand

		Public Sub New(ByVal control As IRichEditControl)
			MyBase.New(control)

		End Sub

		Protected Overrides Function CreateInsertObjectCommand() As RichEditCommand
			Return New CustomPasteSelectionCoreCommand(MyBase.Control, New ClipboardPasteSource())
		End Function
	End Class

	Public Class CustomPasteSelectionCoreCommand
		Inherits PasteSelectionCoreCommand

		Public Sub New(ByVal control As IRichEditControl, ByVal pasteSource As PasteSource)
			MyBase.New(control, pasteSource)

		End Sub

		Public Overrides Sub ForceExecute(ByVal state As DevExpress.Utils.Commands.ICommandUIState)
			Control.Document.InsertText(Control.Document.CaretPosition, Clipboard.GetText())
		End Sub
	End Class
End Namespace