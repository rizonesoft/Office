using System;
using System.IO;
using System.Diagnostics;
using System.Collections.Generic;
using DevExpress.Office;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Services;
using DevExpress.XtraRichEdit.API.Native;

namespace LinkUpdater {
    class Program {
        static void Main(string[] args) {
            RichEditDocumentServer server = new RichEditDocumentServer();
            // Create an instance of the class implementing the IPdfLinkUpdater interface.
            LinkUpdater linkUpdater = new LinkUpdater();
            server.AddService(typeof(ILinkUpdater), linkUpdater);
            RegisterAnchor(server.Document, linkUpdater, "1.html");
            server.Document.AppendText(new string(Characters.PageBreak, 1));
            RegisterAnchor(server.Document, linkUpdater, "2.html");
            // Export the document to PDF and open the resultant file.
            string resultPath = "..\\..\\result.pdf";
            using (Stream stream = File.Create(resultPath))
                server.ExportToPdf(stream);
            Process.Start(Path.GetFullPath(resultPath));
        }

        static void RegisterAnchor(Document doc, LinkUpdater linkUpdater, string uri) {
            string guid = Guid.NewGuid().ToString();
            // Create a bookmark that will be the target of the hyperlink.
            doc.Bookmarks.Create(doc.CaretPosition, 0, guid);
            // Redirect the URI to the bookmark within the document.
            linkUpdater.RedirectUri(uri, guid);
            // Appends the content of the specified HTML file to the document.  
            doc.AppendDocumentContent(string.Format("..\\..\\html\\{0}", uri), DocumentFormat.Html);
        }
    }

    class LinkUpdater : ILinkUpdater {
        readonly Dictionary<string, string> map = new Dictionary<string, string>();
        public string ResolveBookmarkTitle(string bookmarkName, string currentTitle) { 
            return currentTitle;
        }
        public void RedirectUri(string uri, string anchor)
        {
            map[uri] = anchor;
        }

        public string UpdateLinkToPage(string uri, string anchor) {
            string newAnchor;
            if (map.TryGetValue(uri, out newAnchor))
                return newAnchor;
            return anchor;
        }
        public string UpdateLinkToUri(string uri) {
            if (map.ContainsKey(uri))
                return string.Empty;
            return uri;
        }
    }
}
