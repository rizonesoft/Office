<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128613703/19.2.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T590741)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* **[Form1.cs](./CS/WindowsFormsApplication1/Form1.cs) (VB: [Form1.vb](./VB/WindowsFormsApplication1/Form1.vb))**
* [FormatPainterProvider.cs](./CS/WindowsFormsApplication1/FormatPainterProvider.cs) (VB: [FormatPainterProvider.vb](./VB/WindowsFormsApplication1/FormatPainterProvider.vb))
<!-- default file list end -->
# How to implement the basic idea of the Microsoft Excel "Format Painter" feature for SpreadsheetControl


<p>This example demonstrates how to copy all the formatting (a font, background, alignment, number formats and borders) from one cell and apply it to another one. Try the <strong>Format Painter</strong> button on the Ribbon <strong>Home</strong> tab. <br><br><img src="https://raw.githubusercontent.com/DevExpress-Examples/how-to-implement-the-basic-idea-of-the-microsoft-excel-format-painter-feature-for-spreadsh-t590741/17.2.3+/media/29e99ccc-6db9-449b-9844-a481dd9d17d3.png"></p>


<h3>Description</h3>

<p>To copy cell formatting from one cell range to another one, the&nbsp;<a href="https://documentation.devexpress.com/CoreLibraries/DevExpress.Spreadsheet.Range.CopyFrom.method(wtDA4Q)">Range.CopyFrom(Range, PasteSpecial)</a>&nbsp;method with&nbsp;<a href="https://documentation.devexpress.com/CoreLibraries/DevExpress.Spreadsheet.PasteSpecial.enum">Formats</a>&nbsp;as the second parameter is used.</p>

<br/>


