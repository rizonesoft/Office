Imports DevExpress.XtraBars
Imports DevExpress.XtraRichEdit
#Region "#usings"
Imports DevExpress.XtraRichEdit.API.Native
#End Region ' #usings
Imports DevExpress.XtraTab
Imports System.Windows.Forms

Namespace MailMerge
    Partial Public Class Form1
        Inherits Form

        Public Sub New()
            InitializeComponent()
            ribbonControl1.SelectedPage = mailingsRibbonPage1
            richEditControl1.LoadDocument("invitation.rtf", DocumentFormat.Rtf)
'            #Region "#setdatasource"
            richEditControl1.Options.MailMerge.DataSource = New SampleData()
            richEditControl1.Options.MailMerge.ViewMergedData = True
'            #End Region ' #setdatasource
        End Sub

        Private Sub mergeToNewDocumentItem_ItemClick(ByVal sender As Object, ByVal e As ItemClickEventArgs) Handles mergeToNewDocumentItem.ItemClick
'            #Region "#merge"
            Dim myMergeOptions As MailMergeOptions = richEditControl1.Document.CreateMailMergeOptions()
            myMergeOptions.FirstRecordIndex = 1
            myMergeOptions.LastRecordIndex = 3
            myMergeOptions.MergeMode = MergeMode.NewSection
            richEditControl1.Document.MailMerge(myMergeOptions, richEditControl2.Document)
'            #End Region ' #merge
            xtraTabControl1.SelectedTabPageIndex = 1
        End Sub

        Private Sub xtraTabControl1_Selected(ByVal sender As Object, ByVal e As TabPageEventArgs) Handles xtraTabControl1.Selected
            Select Case e.PageIndex
                Case 0
                    Me.richEditBarController1.RichEditControl = Me.richEditControl1
                Case 1
                    Me.richEditBarController1.RichEditControl = Me.richEditControl2
            End Select
        End Sub

        Private Sub mergeToFileItem_ItemClick(ByVal sender As Object, ByVal e As ItemClickEventArgs) Handles mergeToFileItem.ItemClick
            Dim myMergeOptions As MailMergeOptions = richEditControl1.Document.CreateMailMergeOptions()
            myMergeOptions.DataSource = New SampleData()
            myMergeOptions.FirstRecordIndex = 1
            myMergeOptions.LastRecordIndex = 3
            myMergeOptions.MergeMode = MergeMode.NewSection

            Dim fileDialog As New SaveFileDialog()
            fileDialog.Filter = "MS Word 2007 documents (*.docx)|*.docx|All files (*.*)|*.*"
            fileDialog.FilterIndex = 1
            fileDialog.RestoreDirectory = True


            Dim dialogResult_Renamed As DialogResult = fileDialog.ShowDialog()
            If dialogResult_Renamed = System.Windows.Forms.DialogResult.OK Then
                Dim fName As String = fileDialog.FileName
                If fName <> "" Then
                    richEditControl1.Document.MailMerge(myMergeOptions, fileDialog.FileName, DocumentFormat.OpenXml)
                    System.Diagnostics.Process.Start(fileDialog.FileName)
                End If
            End If
        End Sub
    End Class
End Namespace