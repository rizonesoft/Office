<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128609846/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E3665)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
# How to customize copy and paste commands


<p>This example illustrates how to override <strong>CopySelectionCommand</strong> and <strong>PasteSelectionCommand</strong> behavior via the <strong>IRichEditCommandFactoryService</strong> substitution. This approach is based on the <a href="https://www.devexpress.com/Support/Center/p/E2224">How to replace standard XtraRichEdit command with your own custom command</a> example.</p><p>Customized <strong>CopySelectionCommand </strong>contains code for copying selection to the <a href="http://msdn.microsoft.com/en-us/library/system.windows.clipboard.aspx"><u>Clipboard</u></a> in an <a href="http://msdn.microsoft.com/en-us/library/aa767917(v=vs.85).aspx"><u>HTML Clipboard Format</u></a> (see the <strong>HtmlHelper.GetHtmlClipboardFormat()</strong> method). This allows you to copy RichEditControl content and paste it directly to a certain control that can accept HTML-formatted data from the Clipboard (e. g. <a href="http://documentation.devexpress.com/#AspNet/clsDevExpressWebASPxHtmlEditorASPxHtmlEditortopic"><u>ASPxHtmlEditor</u></a>). Note that images are embedded into resultant HTML according to the <a href="http://en.wikipedia.org/wiki/Data_URI_scheme"><u>Data URI scheme</u></a> specification to avoid dependency on the image location (it may not be resolved by the target application). Please note that RichEditControl supports copying data in the HTML Clipboard format in <strong>v20.2.5</strong> and newer versions. To enable this functionality, use the <a href="https://docs.devexpress.com/OfficeFileAPI/DevExpress.XtraRichEdit.DataFormatOptions.AllowHtml"><u>ClipboardFormats.AllowHtml</u></a> option.
  
<p>As for customized <strong>PasteSelectionCommand</strong>, it simply retrieves plain (unformatted) text from the Clipboard and pastes this text into the RichEditControl.</p><p><strong>See Also:</strong><br />
<a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeSubDocument_GetTexttopic"><u>SubDocument.GetText Method</u></a><br />
<a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeSubDocument_GetRtfTexttopic"><u>SubDocument.GetRtfText Method</u></a><br />
<a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeSubDocument_GetHtmlTexttopic"><u>SubDocument.GetHtmlText Method</u></a></p>

<br/>


