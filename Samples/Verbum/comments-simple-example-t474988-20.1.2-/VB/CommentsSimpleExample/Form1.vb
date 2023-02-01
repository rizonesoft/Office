Imports System
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit

Namespace CommentsSimpleExample
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            InitSkinGallery()
            InitializeRichEditControl()
            ribbonControl.SelectedPage = homeRibbonPage1

            richEditControl.LoadDocument("Comments.docx", DocumentFormat.OpenXml)
        End Sub

        Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
            InsertComment()
            EditComment()
            EditCommentProperties()
            InsertNestedComment()

            StyleComments(richEditControl.Document)
        End Sub
        Private Sub EditComment()
'            #Region "#EditCommentContent"
            Dim document As Document = richEditControl.Document

            Dim commentCount As Integer = document.Comments.Count
            If commentCount > 0 Then
                'The target comment is the first one
                Dim comment As Comment = document.Comments(0)
                If comment IsNot Nothing Then
                    'Open the comment for modification
                    Dim commentDocument As SubDocument = comment.BeginUpdate()

                    'Add text to the comment range
                    commentDocument.InsertText(commentDocument.CreatePosition(0), "J. Taylor, Enabling Voice - over - IP and RAID with sofa,  in Proceedings of NOSSDAV, Oct. 1994." & ControlChars.CrLf & "R.Tarjan, S.Shenker, J.Gray, A.Einstein, Q.Thomas, and X.Sato, ""Deconstructing operating systems with flanchedripper"", in Proceedings of INFOCOM, Mar. 2000.")

                    'End the comment update
                    comment.EndUpdate(commentDocument)
                End If
            End If
'            #End Region ' #EditCommentContent
        End Sub
        Private Sub InsertComment()
'            #Region "#InsertComment"
            'The target range is the specific phrase in the introduction's first paragraph
            Dim foundRanges() As DocumentRange = richEditControl.Document.FindAll("an extensive problem in hardware and architecture is the construction of the emulation of checksums", SearchOptions.None)
            If foundRanges.Length > 0 Then
                'Create a new comment
                Dim comment As Comment = richEditControl.Document.Comments.Create(foundRanges(0), "Johnson Alphonso D", New Date(2014, 4, 25))
            End If
'            #End Region ' #InsertComment
        End Sub


        Private Sub InsertNestedComment()
'            #Region "#NestedComment"
            Dim document As Document = richEditControl.Document


            If document.Comments.Count > 0 Then
                'Create a new comment nested to the second comment in the collection
                Dim nestedComment As Comment = document.Comments.Create("Brian Zetc", Date.Now, document.Comments(1))

                'Add text to the newly created comment
                Dim nestedCommentDocument As SubDocument = nestedComment.BeginUpdate()
                Dim textRange As DocumentRange = nestedCommentDocument.InsertText(nestedCommentDocument.CreatePosition(0), "Suffix trees are comprehensively reviewed in Wikipedia")
                nestedComment.EndUpdate(nestedCommentDocument)
            End If
'            #End Region ' #NestedComment
        End Sub
        Private Sub EditCommentProperties()
'            #Region "#CommentProperties"
            Dim document As Document = richEditControl.Document
            Dim commentCount As Integer = document.Comments.Count

            If commentCount > 0 Then

                document.BeginUpdate()
                'The target is the second last comment
                Dim comment As Comment = document.Comments(document.Comments.Count - 1)

                'Change the comment's name, author and creation date
                comment.Name = "Reference"
                comment.Date = Date.Now
                comment.Author = "Vicars Annie"
                document.EndUpdate()
            End If
'            #End Region ' #CommentProperties
        End Sub

        Private Sub InitSkinGallery()
        End Sub
        Private Sub InitializeRichEditControl()
        End Sub
        Private Sub StyleComments(ByVal document As Document)
            For i As Integer = 0 To document.Comments.Count - 1
                Dim commentDocument As SubDocument = document.Comments(i).BeginUpdate()
                For j As Integer = 0 To commentDocument.Paragraphs.Count - 1
                    commentDocument.Paragraphs(j).Style = document.ParagraphStyles("Balloon Text")
                Next j
                document.Comments(i).EndUpdate(commentDocument)
            Next i
        End Sub

    End Class
End Namespace