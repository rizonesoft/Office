Imports Microsoft.VisualBasic
Imports System
Imports System.IO
Imports System.Text
Imports System.Windows.Forms
Imports System.Drawing.Imaging
Imports DevExpress.Utils
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Export
Imports DevExpress.XtraRichEdit.Utils
Imports DevExpress.Office.Utils
Imports DevExpress.Office.Services
Imports Outlook = Microsoft.Office.Interop.Outlook

Namespace RichEditOpenInOutlook
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			richEdit.LoadDocument("Hello.docx")
		End Sub

		Private Sub btnSend_Click(ByVal sender As Object, ByVal e As EventArgs) Handles btnSend.Click
			If (edtTo.Text.Trim() = "") OrElse (edtSubject.Text.Trim() = "") Then
				MessageBox.Show("Fill in required fields")
				Return
			End If
			Try
				Dim application As New Outlook.Application()
				Dim mailItem As Outlook.MailItem = CType(application.CreateItem(Outlook.OlItemType.olMailItem), Outlook.MailItem)

				mailItem.To = edtTo.Text
				mailItem.Subject = edtSubject.Text

				Dim exporter As New RichEditMailMessageExporter(richEdit, mailItem)
				exporter.Export()

				mailItem.Display(False)
			Catch exc As Exception
				MessageBox.Show(exc.Message)
			End Try
		End Sub

		Public Class RichEditMailMessageExporter
			Implements IUriProvider
			Private ReadOnly control As RichEditControl
			Private ReadOnly mailItem As Outlook.MailItem
			Private imageId As Integer
			Private tempFiles As String = Path.Combine(Directory.GetCurrentDirectory(), "TempFiles")

			Public Sub New(ByVal control As RichEditControl, ByVal mailItem As Outlook.MailItem)
				Guard.ArgumentNotNull(control, "control")
				Guard.ArgumentNotNull(mailItem, "mailItem")

				Me.control = control
				Me.mailItem = mailItem
			End Sub

			Public Overridable Sub Export()
				If (Not Directory.Exists(tempFiles)) Then
					Directory.CreateDirectory(tempFiles)
				End If

				AddHandler control.BeforeExport, AddressOf OnBeforeExport
				Dim htmlBody As String = control.Document.GetHtmlText(control.Document.Range, Me)
				RemoveHandler control.BeforeExport, AddressOf OnBeforeExport

				mailItem.BodyFormat = Outlook.OlBodyFormat.olFormatHTML
				mailItem.HTMLBody = htmlBody
			End Sub

			Private Sub OnBeforeExport(ByVal sender As Object, ByVal e As BeforeExportEventArgs)
				Dim options As HtmlDocumentExporterOptions = TryCast(e.Options, HtmlDocumentExporterOptions)
				If options IsNot Nothing Then
					options.Encoding = Encoding.UTF8
				End If
			End Sub

			#Region "IUriProvider Members"
			Public Function CreateCssUri(ByVal rootUri As String, ByVal styleText As String, ByVal relativeUri As String) As String Implements IUriProvider.CreateCssUri
				Return String.Empty
			End Function

			Public Function CreateImageUri(ByVal rootUri As String, ByVal image As OfficeImage, ByVal relativeUri As String) As String Implements IUriProvider.CreateImageUri
				Dim imageName As String = String.Format("image{0}.png", imageId)
				imageId += 1

				Dim imagePath As String = Path.Combine(tempFiles, imageName)

				image.NativeImage.Save(imagePath, ImageFormat.Png)

				mailItem.Attachments.Add(imagePath, Outlook.OlAttachmentType.olByValue, 0, Type.Missing)

				Return "cid:" & imageName
			End Function
			#End Region
		End Class
	End Class
End Namespace