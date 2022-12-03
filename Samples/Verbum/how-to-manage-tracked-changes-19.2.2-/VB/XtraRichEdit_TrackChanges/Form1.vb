Imports DevExpress.XtraRichEdit
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit.API.Native

Namespace XtraRichEdit_TrackChanges
	Partial Public Class Form1
		Inherits RibbonForm

		Public Sub New()
			InitializeComponent()
			Me.Controls.Add(richEditControl1.CreateRibbon())
			richEditControl1.LoadDocument("DocumentWithRevisions.docx")
			AddHandler richEditControl1.TrackedMovesConflict, AddressOf DocumentProcessor_TrackedMovesConflict
			richEditControl1.Document.SaveDocument("DocumentWithRevisions.docx", DocumentFormat.OpenXml)
			SpecifyDisplayOptions()
			CreateNewRevision()
			AcceptAndRejectRevisions()
		End Sub

		Private Sub CreateNewRevision()
			richEditControl1.Document.TrackChanges.Enabled = True
			richEditControl1.Document.TrackChanges.TrackFormatting = True
			'Format the specific phrase in the document:
			'This modification is added an a new revision:
			Dim targetPhrases() As DocumentRange = richEditControl1.Document.FindAll("We measured hard disk space as a function of USB key space on an IBM PC Junior.", SearchOptions.None)
			Dim characterProperties As CharacterProperties = richEditControl1.Document.BeginUpdateCharacters(targetPhrases(0))
			characterProperties.FontName = "Arial"
			characterProperties.Italic = True
			richEditControl1.Document.EndUpdateCharacters(characterProperties)
		End Sub

		Private Sub AcceptAndRejectRevisions()
			Dim documentRevisions As RevisionCollection = richEditControl1.Document.Revisions

			'Reject all revisions in the firts page's header:
			Dim header As SubDocument = richEditControl1.Document.Sections(0).BeginUpdateHeader(HeaderFooterType.First)
			documentRevisions.RejectAll(header)
			richEditControl1.Document.Sections(0).EndUpdateHeader(header)

			'Reject all revisions from the specific author on the first section:
			Dim sectionRevisions = documentRevisions.Get(richEditControl1.Document.Sections(0).Range).Where(Function(x) x.Author = "Janet Leverling")

			For Each revision As Revision In sectionRevisions
				revision.Reject()
			Next revision

			'Accept all format changes:
			documentRevisions.AcceptAll(Function(x) x.Type = RevisionType.CharacterPropertyChanged OrElse x.Type = RevisionType.ParagraphPropertyChanged OrElse x.Type = RevisionType.SectionPropertyChanged)

		End Sub

		Private Sub SpecifyDisplayOptions()
			Dim trackChangesOptions As TrackChangesOptions = richEditControl1.Options.Annotations.TrackChanges

			'Specify how revisions should be displyed in the document:

			trackChangesOptions.DisplayForReviewMode = DisplayForReviewMode.AllMarkup
			trackChangesOptions.DisplayFormatting = DisplayFormatting.ColorOnly
			trackChangesOptions.FormattingColor = RevisionColor.ClassicBlue
			trackChangesOptions.DisplayInsertionStyle = DisplayInsertionStyle.Underline
			trackChangesOptions.InsertionColor = RevisionColor.DarkRed

			richEditControl1.Options.Annotations.Author = "Anne Dodsworth"

			'Disable showing revisions from all authors
			richEditControl1.Options.Annotations.ShowAllAuthors = False

			'Remove authors whose revisions should not be displayed:
			richEditControl1.Options.Annotations.VisibleAuthors.Remove("Michael Suyama")
		End Sub

		Private Shared Sub DocumentProcessor_TrackedMovesConflict(ByVal sender As Object, ByVal e As TrackedMovesConflictEventArgs)
			'Compare the length of the original and new location ranges
			'Keep text from the location whose range is the smallest
			e.ResolveMode = If(e.OriginalLocationRange.Length <= e.NewLocationRange.Length, TrackedMovesConflictResolveMode.KeepOriginalLocationText, TrackedMovesConflictResolveMode.KeepNewLocationText)
		End Sub

	End Class
End Namespace
