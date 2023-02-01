<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# How to list fonts that are used in a document


<p>This example illustrates how to list fonts that are used in a document loaded into RichEditControl. To accomplish this task iterate through all characters in the document and examine a font name of every character by using the approach from the <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument5890"><u>How to: Change Formatting of Selected Text</u></a> help section. You can also use this technique if you wish to examine any formatting options (e.g., font color, bold flag) in the document.<br><br>Starting with version 16.1, it's possible to use the  <a href="http://help.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditAPINativeDocumentIteratortopic">Document Iterator</a> object to iterate through <a href="http://help.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditAPINativeDocumentTexttopic">DocumentText</a> elements in a document and list fonts applied to these elements. Refer to the <a href="https://www.devexpress.com/Support/Center/p/T438475">How to use Document Iterator to obtain a list of fonts that are used in a document</a> example illustrating how to use <strong>DocumentIterator</strong> in this scenario.</p>

<br/>


