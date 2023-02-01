using DevExpress.XtraRichEdit.Services;

namespace BookmarkTitleUpdater
{
    public class BookmarkTitleUpdater : ILinkUpdater
    {
        public string ResolveBookmarkTitle(string bookmarkName, string currentTitle)
        {
            return bookmarkName;
        }

        public string UpdateLinkToPage(string uri, string anchor)
        {
            return anchor;
        }

        public string UpdateLinkToUri(string uri)
        {
            return uri;
        }
    }
}
