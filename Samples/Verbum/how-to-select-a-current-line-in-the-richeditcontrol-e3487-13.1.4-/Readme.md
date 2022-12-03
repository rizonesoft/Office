<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128611205/13.1.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E3487)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# How to select a current line in the RichEditControl


<p>This example illustrates the use of the <strong>StartOfLineCommand</strong> and <strong>EndOfLineCommand</strong> that allows you to determine start and end positions of the current line. It is important to distinguish <strong>line</strong> and <strong>paragraph</strong> terms because they are different in the context of the RichEditControl. <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument9556"><u>Paragraph</u></a> represents a single paragraph in a document. Paragraphs are delimited by the <strong>\r\n</strong> character pair. As for the line, it is a range of non-breakable text (i.e. a range of text that is not wrapped to the next row). There is no special API for lines and you should use the aforementioned commands to work with them.</p>

<br/>


