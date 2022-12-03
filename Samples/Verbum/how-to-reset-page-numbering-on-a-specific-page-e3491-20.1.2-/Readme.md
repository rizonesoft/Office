<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128611056/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E3491)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [StringSample.cs](./CS/StringSample.cs) (VB: [StringSample.vb](./VB/StringSample.vb))
<!-- default file list end -->
# How to reset page numbering on a specific page


<p>This example illustrates how to reset page numbering (in the document header) on a specific page. To achieve this goal, add a new <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument9553"><u>Section</u></a> to a document and set its PageNumbering.Start property (see <a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeSectionPageNumbering_Starttopic"><u>SectionPageNumbering.Start</u></a>) to 1. Note that page numbering is setup by creating a <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument9716"><u>PAGE</u></a> field in the document header. The entire document is generated programmatically.</p>

<br/>


