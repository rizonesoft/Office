<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610204/16.1.9%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T467150)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [CustomLayoutVisitor.cs](./CS/WindowsFormsApplication1/CustomLayoutVisitor.cs) (VB: [CustomLayoutVisitor.vb](./VB/WindowsFormsApplication1/CustomLayoutVisitor.vb))
* [Form1.cs](./CS/WindowsFormsApplication1/Form1.cs) (VB: [Form1.vb](./VB/WindowsFormsApplication1/Form1.vb))
<!-- default file list end -->
# How to emulate the MS Word information status bar when using RichEditControl


<p>This example demonstrates how to implement an information status bar that mimics the MS Word status bar:<br><img src="https://raw.githubusercontent.com/DevExpress-Examples/how-to-emulate-the-ms-word-information-status-bar-when-using-richeditcontrol-t467150/16.1.9+/media/150534eb-cd19-11e6-80bf-00155d62480c.png"></p>
<p>This task is accomplished by using the RichEditControl's DocumentLayout API. Review the following help topic for additional information:<br><a href="https://documentation.devexpress.com/#WindowsForms/CustomDocument114069">Layout API</a></p>
<p>In this example, we use different approaches to collect required information:</p>

* The <a href="https://documentation.devexpress.com/CoreLibraries/clsDevExpressXtraRichEditAPINativeDocumentIteratortopic.aspx">DocumentIterator</a> class to obtain the total word count.
* A custom <a href="https://documentation.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditAPILayoutLayoutVisitortopic">LayoutVisitor</a> descendant to get the caret position (the line and column indices).
<p><strong>See also:</strong><br><a href="https://www.devexpress.com/Support/Center/p/T245818">Layout API - Simple Example</a><br><a href="https://www.devexpress.com/Support/Center/p/T266080">Document Layout API - Practical usage</a></p>
