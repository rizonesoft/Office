<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610369/14.2.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T202228)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [CustomSearchForm.cs](./CS/RichEdit/CustomSearchForm.cs) (VB: [CustomSearchForm.vb](./VB/RichEdit/CustomSearchForm.vb))
* [Form1.cs](./CS/RichEdit/Form1.cs) (VB: [Form1.vb](./VB/RichEdit/Form1.vb))
<!-- default file list end -->
# How to highlight all found word entries in a document 


<p>At the moment. a RichEditControl highlights only the currently found entry. This example demonstrates how  to highlight all the found entries. The main idea is to use the <a href="https://documentation.devexpress.com/#corelibraries/clsDevExpressXtraRichEditAPINativeCustomMarktopic">custom marks</a> feature. A custom mark is added for each found entry and drawn by the <a href="https://documentation.devexpress.com/WindowsForms/DevExpressXtraRichEditRichEditControl_CustomMarkDrawtopic.aspx">DevExpress.XtraRichEdit.RichEditControl.CustomMarkDraw</a> event.<br /><br />To manage highlighting when searching is performed using the SearchForm form - a custom SearchForm is created.  </p>

<br/>


