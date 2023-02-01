Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Services
Imports System.Diagnostics
Imports System.IO

Namespace BookmarkTitleUpdater
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            ribbonControl.SelectedPage = fileRibbonPage1

            ' Load a document into the RichEditControl.
            richEditControl.LoadDocument("Documents\Grimm.docx", DocumentFormat.OpenXml)

            ' Specify that all bookmarks for which there are references in a document
            ' should be displayed in the Bookmarks panel of PDF Viewer after the document is exported to PDF.
            richEditControl.Options.Bookmarks.DisplayBookmarksInPdfNavigationPane = PdfBookmarkDisplayMode.All

            ' Create a service which displays a bookmark name instead of the bookmarked text range in the Bookmarks panel of PDF Viewer.
            Dim bookmarkTitleUpdater As New BookmarkTitleUpdater()
            ' Add the created service to the service container.
            richEditControl.AddService(GetType(ILinkUpdater), bookmarkTitleUpdater)
        End Sub

        Private Sub exportToPdfBarButtonItem1_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles exportToPdfBarButtonItem1.ItemClick
            Using pdfFileStream As New FileStream("Document_PDF.pdf", FileMode.Create)
                richEditControl.ExportToPdf(pdfFileStream)
            End Using
            Process.Start("Document_PDF.pdf")
        End Sub
    End Class
End Namespace