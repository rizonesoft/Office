using DevExpress.XtraRichEdit;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit.API.Native;

namespace XtraRichEdit_TrackChanges
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            this.Controls.Add(richEditControl1.CreateRibbon());
            richEditControl1.LoadDocument("DocumentWithRevisions.docx");
            richEditControl1.TrackedMovesConflict += DocumentProcessor_TrackedMovesConflict;
            richEditControl1.Document.SaveDocument("DocumentWithRevisions.docx", DocumentFormat.OpenXml);
            SpecifyDisplayOptions();
            CreateNewRevision();
            AcceptAndRejectRevisions();
        }

        private void CreateNewRevision()
        {
            richEditControl1.Document.TrackChanges.Enabled = true;
            richEditControl1.Document.TrackChanges.TrackFormatting = true;
            //Format the specific phrase in the document:
            //This modification is added an a new revision:
            DocumentRange[] targetPhrases = richEditControl1.Document.FindAll("We measured hard disk space as a function of USB key space on an IBM PC Junior.", SearchOptions.None);
            CharacterProperties characterProperties = richEditControl1.Document.BeginUpdateCharacters(targetPhrases[0]);
            characterProperties.FontName = "Arial";
            characterProperties.Italic = true;
            richEditControl1.Document.EndUpdateCharacters(characterProperties);
        }

        private void AcceptAndRejectRevisions()
        {
            RevisionCollection documentRevisions = richEditControl1.Document.Revisions;

            //Reject all revisions in the firts page's header:
            SubDocument header = richEditControl1.Document.Sections[0].BeginUpdateHeader(HeaderFooterType.First);
            documentRevisions.RejectAll(header);
            richEditControl1.Document.Sections[0].EndUpdateHeader(header);

            //Reject all revisions from the specific author on the first section:
            var sectionRevisions = documentRevisions.Get(richEditControl1.Document.Sections[0].Range).Where(x => x.Author == "Janet Leverling");

            foreach (Revision revision in sectionRevisions)
                revision.Reject();

            //Accept all format changes:
            documentRevisions.AcceptAll(x => x.Type == RevisionType.CharacterPropertyChanged || x.Type == RevisionType.ParagraphPropertyChanged || x.Type == RevisionType.SectionPropertyChanged);

        }

        private void SpecifyDisplayOptions()
        {
            TrackChangesOptions trackChangesOptions = richEditControl1.Options.Annotations.TrackChanges;

            //Specify how revisions should be displyed in the document:

            trackChangesOptions.DisplayForReviewMode = DisplayForReviewMode.AllMarkup;
            trackChangesOptions.DisplayFormatting = DisplayFormatting.ColorOnly;
            trackChangesOptions.FormattingColor = RevisionColor.ClassicBlue;
            trackChangesOptions.DisplayInsertionStyle = DisplayInsertionStyle.Underline;
            trackChangesOptions.InsertionColor = RevisionColor.DarkRed;

            richEditControl1.Options.Annotations.Author = "Anne Dodsworth";

            //Disable showing revisions from all authors
            richEditControl1.Options.Annotations.ShowAllAuthors = false;

            //Remove authors whose revisions should not be displayed:
            richEditControl1.Options.Annotations.VisibleAuthors.Remove("Michael Suyama");
        }

        private static void DocumentProcessor_TrackedMovesConflict(object sender, TrackedMovesConflictEventArgs e)
        {
            //Compare the length of the original and new location ranges
            //Keep text from the location whose range is the smallest
            e.ResolveMode = (e.OriginalLocationRange.Length <= e.NewLocationRange.Length) ? TrackedMovesConflictResolveMode.KeepOriginalLocationText : TrackedMovesConflictResolveMode.KeepNewLocationText;
        }

    }
}
