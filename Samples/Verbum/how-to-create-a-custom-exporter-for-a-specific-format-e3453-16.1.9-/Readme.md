<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128609573/16.1.9%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E3453)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [BBCExporter.cs](./CS/BBCExporter.cs) (VB: [BBCExporter.vb](./VB/BBCExporter.vb))
* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
<!-- default file list end -->
# How to create a custom exporter for a specific format


<p>This example illustrates how to create and register a custom DocumentModelExporter for a <a href="http://www.bbcode.org/"><u>BBCode</u></a> format. It supports a number of basic BBCode tags (including hyperlinks and images). The major export functionality is implemented in overridden Export* methods of the <strong>BBCodeExporter</strong> class.</p>

<br/>


