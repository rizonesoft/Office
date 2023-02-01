Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native
#Region "#usings"
Imports DevExpress.Services
#End Region ' #usings
Imports DevExpress.XtraRichEdit

Namespace ProgressIndicator
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()
			richEditControl1.LoadDocument("Docs\invitation.docx")
			richEditControl1.Options.MailMerge.DataSource = New SampleData()
		End Sub

		Private Sub btnMailMerge_Click(ByVal sender As Object, ByVal e As EventArgs) Handles btnMailMerge.Click
			Dim myMergeOptions As MailMergeOptions = richEditControl1.Document.CreateMailMergeOptions()
			myMergeOptions.MergeMode = MergeMode.NewSection
			richEditControl1.Document.MailMerge(myMergeOptions, richEditControl2.Document)
			xtraTabControl1.SelectedTabPageIndex = 1
		End Sub

		Private Sub richEditControl1_MailMergeStarted(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.MailMergeStartedEventArgs) Handles richEditControl1.MailMergeStarted
'			#Region "#servicesubst"
			richEditControl1.ReplaceService(Of IProgressIndicationService) _
 (New MyProgressIndicatorService(richEditControl1, Me.progressBarControl1))
'			#End Region ' #servicesubst
		End Sub

		Private Sub richEditControl1_MailMergeFinished(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.MailMergeFinishedEventArgs) Handles richEditControl1.MailMergeFinished
			richEditControl1.RemoveService(GetType(IProgressIndicationService))
		End Sub

		Private Sub richEditControl1_MailMergeRecordStarted(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.MailMergeRecordStartedEventArgs) Handles richEditControl1.MailMergeRecordStarted
			' Imitating slow data fetching
			System.Threading.Thread.Sleep(100)
		End Sub

		Private Sub richEditControl1_MailMergeRecordFinished(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.MailMergeRecordFinishedEventArgs) Handles richEditControl1.MailMergeRecordFinished
			e.RecordDocument.AppendDocumentContent("Docs\bungalow.docx", DocumentFormat.OpenXml)
		End Sub

		Private Sub xtraTabControl1_Selected(ByVal sender As Object, ByVal e As DevExpress.XtraTab.TabPageEventArgs) Handles xtraTabControl1.Selected
			Select Case e.PageIndex
				Case 0
					Me.btnMailMerge.Enabled = True
				Case 1
					Me.btnMailMerge.Enabled = False
			End Select
		End Sub
	End Class
End Namespace