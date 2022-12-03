<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610959/15.2.9%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T318281)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Program.cs](./CS/LinkUpdater/Program.cs) (VB: [Program.vb](./VB/LinkUpdater/Program.vb))
<!-- default file list end -->
# How to redirect hyperlinks within an exported PDF document


<p>This example demonstrates how to implement the <strong>DevExpress.XtraRichEdit.Services.IPdfLinkUpdater</strong> interface to redirect hyperlinks within an exported PDF document. In particular, this example merges two HTML files containing cross references into a single PDF document and updates external hyperlinks so that they point to bookmarks within the document.</p>
<p><br><strong>Starting from 15.2.9:</strong><br>The <strong>IPdfLinkUpdater</strong> interface has been renamed to <strong>ILinkUpdater</strong> and its functionality has been extended to include the <strong>ResolveBookmarkTitle</strong> method, which allows you to change the titles used to display document bookmarks in the <em>Bookmarks</em> panel of a PDF Viewer after the document is exported to PDF.</p>

<br/>


