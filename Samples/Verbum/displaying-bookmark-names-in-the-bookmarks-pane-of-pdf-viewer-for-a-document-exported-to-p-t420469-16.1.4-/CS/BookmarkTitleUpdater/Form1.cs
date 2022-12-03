using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Services;
using System.Diagnostics;
using System.IO;

namespace BookmarkTitleUpdater
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            ribbonControl.SelectedPage = fileRibbonPage1;

            // Load a document into the RichEditControl.
            richEditControl.LoadDocument("Documents\\Grimm.docx", DocumentFormat.OpenXml);

            // Specify that all bookmarks for which there are references in a document 
            // should be displayed in the Bookmarks panel of PDF Viewer after the document is exported to PDF.
            richEditControl.Options.Bookmarks.DisplayBookmarksInPdfNavigationPane = PdfBookmarkDisplayMode.All;

            // Create a service which displays a bookmark name instead of the bookmarked text range in the Bookmarks panel of PDF Viewer.
            BookmarkTitleUpdater bookmarkTitleUpdater = new BookmarkTitleUpdater();
            // Add the created service to the service container.
            richEditControl.AddService(typeof(ILinkUpdater), bookmarkTitleUpdater);
        }

        private void exportToPdfBarButtonItem1_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            using (FileStream pdfFileStream = new FileStream("Document_PDF.pdf", FileMode.Create))
            {
                richEditControl.ExportToPdf(pdfFileStream);
            }
            Process.Start("Document_PDF.pdf");
        }
    }
}