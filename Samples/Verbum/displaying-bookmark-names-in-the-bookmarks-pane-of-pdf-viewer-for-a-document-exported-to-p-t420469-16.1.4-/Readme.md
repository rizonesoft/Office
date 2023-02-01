<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128609081/16.1.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T420469)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [BookmarkTitleUpdater.cs](./CS/BookmarkTitleUpdater/BookmarkTitleUpdater.cs) (VB: [BookmarkTitleUpdater.vb](./VB/BookmarkTitleUpdater/BookmarkTitleUpdater.vb))
* [Form1.cs](./CS/BookmarkTitleUpdater/Form1.cs) (VB: [Form1.vb](./VB/BookmarkTitleUpdater/Form1.vb))
<!-- default file list end -->
# Displaying bookmark names in the Bookmarks pane of PDF Viewer for a document exported to PDF


This example demonstrates how to create a service that implements the <strong>DevExpress.XtraRichEdit.Services.ILinkUpdater</strong> interface to change titles used to display document bookmarks in the <strong>Bookmarks</strong> pane of PDF Viewer after a document is exported to PDF.  <br>By default, when the <a href="https://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditBookmarkOptions_DisplayBookmarksInPdfNavigationPanetopic">BookmarkOptions.DisplayBookmarksInPdfNavigationPane</a> property is set to <em>All</em> or <em>TocBookmarks</em>, the <strong>Bookmarks</strong> pane displays not a name of a bookmark but the first 512 symbols of text to which the bookmark is assigned. To change this default behavior and display bookmark names in the <strong>Bookmarks</strong> pane, implement the <strong>ResolveBookmarkTitle</strong> method of the <strong>ILinkUpdater</strong> interface.<br><img src="https://raw.githubusercontent.com/DevExpress-Examples/displaying-bookmark-names-in-the-bookmarks-pane-of-pdf-viewer-for-a-document-exported-to-p-t420469/16.1.4+/media/76a10bc3-6def-11e6-80bf-00155d62480c.png">

<br/>


