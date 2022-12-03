<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610546/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E5223)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/DXApplication9/Form1.cs) (VB: [Form1.vb](./VB/DXApplication9/Form1.vb))
* [MyRichEditControl.cs](./CS/DXApplication9/MyRichEditControl.cs) (VB: [MyRichEditControl.vb](./VB/DXApplication9/MyRichEditControl.vb))
* [Program.cs](./CS/DXApplication9/Program.cs) (VB: [Program.vb](./VB/DXApplication9/Program.vb))
<!-- default file list end -->
# How to implement the basic idea of the MS Office Word "Format Painter" for RichEditControl


<p>This example demonstrates how to copy the characters and paragraphs properties and apply formatting to the selected text. Try the Format Painter button on the ribbon Home tab. </p>


<h3>Description</h3>

<p>To obtain the selected text range, the RichEditDocument.Document.Selection property is used. The characters and paragraphs properties are copied using the&nbsp; DevExpress.XtraRichEdit.API.Native.CharacterPropertiesBase.Assign and&nbsp;DevExpress.XtraRichEdit.API.Native.ParagraphPropertiesBase.Assign methods.</p>
<br>
<p>In order to change the current RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check the custom MouseCursorCalculator class Calculate method for clarification.</p>

<br/>


