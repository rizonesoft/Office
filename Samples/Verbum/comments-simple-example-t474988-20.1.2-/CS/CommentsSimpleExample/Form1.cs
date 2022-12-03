using System;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit;

namespace CommentsSimpleExample
{
    public partial class Form1 : RibbonForm
    {

        public Form1()
        {
            InitializeComponent();
            InitSkinGallery();
            InitializeRichEditControl();
            ribbonControl.SelectedPage = homeRibbonPage1;

            richEditControl.LoadDocument("Comments.docx", DocumentFormat.OpenXml);            
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            InsertComment();
            EditComment();
            EditCommentProperties();
            InsertNestedComment();

            StyleComments(richEditControl.Document);
        }
        private void EditComment()
        {
            #region #EditCommentContent
            Document document = richEditControl.Document;

            int commentCount = document.Comments.Count;
            if (commentCount > 0)
            {
                //The target comment is the first one
                Comment comment = document.Comments[0];
                if (comment != null)
                {
                    //Open the comment for modification
                    SubDocument commentDocument = comment.BeginUpdate();

                    //Add text to the comment range
                    commentDocument.InsertText(commentDocument.CreatePosition(0),
                        "J. Taylor, Enabling Voice - over - IP and RAID with sofa,  in Proceedings of NOSSDAV, Oct. 1994.\r\n" +
                        @"R.Tarjan, S.Shenker, J.Gray, A.Einstein, Q.Thomas, and X.Sato, ""Deconstructing operating systems with flanchedripper"", in Proceedings of INFOCOM, Mar. 2000.");

                    //End the comment update
                    comment.EndUpdate(commentDocument);
                }
            }
            #endregion #EditCommentContent
        }
        private void InsertComment()
        {
            #region #InsertComment
            //The target range is the specific phrase in the introduction's first paragraph
            DocumentRange[] foundRanges = richEditControl.Document.FindAll("an extensive problem in hardware and architecture is the construction of the emulation of checksums", SearchOptions.None);
            if (foundRanges.Length > 0)
            {
                //Create a new comment
                Comment comment = richEditControl.Document.Comments.Create(foundRanges[0], "Johnson Alphonso D", new DateTime(2014, 4, 25));
            }
            #endregion #InsertComment
        }


        private void InsertNestedComment()
        {
            #region #NestedComment
            Document document = richEditControl.Document;


            if (document.Comments.Count > 0)
            {
                //Create a new comment nested to the second comment in the collection
                Comment nestedComment = document.Comments.Create("Brian Zetc", DateTime.Now, document.Comments[1]);

                //Add text to the newly created comment
                SubDocument nestedCommentDocument = nestedComment.BeginUpdate();
                DocumentRange textRange = nestedCommentDocument.InsertText(nestedCommentDocument.CreatePosition(0),
                "Suffix trees are comprehensively reviewed in Wikipedia");
                nestedComment.EndUpdate(nestedCommentDocument);
            }
            #endregion #NestedComment
        }
        private void EditCommentProperties()
        {
            #region #CommentProperties
            Document document = richEditControl.Document;
            int commentCount = document.Comments.Count;

            if (commentCount > 0)
            {

                document.BeginUpdate();
                //The target is the second last comment
                Comment comment = document.Comments[document.Comments.Count - 1];

                //Change the comment's name, author and creation date
                comment.Name = "Reference";
                comment.Date = DateTime.Now;
                comment.Author = "Vicars Annie";
                document.EndUpdate();
            }
            #endregion #CommentProperties
        }

        void InitSkinGallery()
        {
        }
        void InitializeRichEditControl()
        {
        }
        private void StyleComments(Document document)
        {
            for (int i = 0; i < document.Comments.Count; i++)
            {
                SubDocument commentDocument = document.Comments[i].BeginUpdate();
                for (int j = 0; j < commentDocument.Paragraphs.Count; j++)
                {
                    commentDocument.Paragraphs[j].Style = document.ParagraphStyles["Balloon Text"];
                }
                document.Comments[i].EndUpdate(commentDocument);
            }
        }
        
    }
}