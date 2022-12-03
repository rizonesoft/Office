<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610693/17.1.9%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T600135)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/RichEditControl_CheckBox/Form1.cs) (VB: [Form1.vb](./VB/RichEditControl_CheckBox/Form1.vb))
<!-- default file list end -->
# How to insert a CheckBox into a RichEditControl document


<p>This example demonstrates how to imitate a CheckBox control in a document by inserting Unicode characters and allow changing the CheckBox state on a mouse click.</p>
<p>Use the <a href="https://documentation.devexpress.com/#corelibraries/DevExpressXtraRichEditHitTestManagerMembersTopicAll">HitTestManager.HitTest</a> method to get the <a href="https://documentation.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditRichEditHitTestResulttopic">RichEditHitTestResult</a> object providing information about a specific document element which is located under the mouse cursor. Retrieve the layout element using the <a href="https://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditRichEditHitTestResult_LayoutElementtopic">RichEditHitTestResult.LayoutElement</a> property, check whether this element is a CheckBox character, and change its checked state by replacing the clicked character with another one.</p>

<br/>


