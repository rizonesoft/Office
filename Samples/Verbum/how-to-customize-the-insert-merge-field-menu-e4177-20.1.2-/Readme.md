<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128609910/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E4177)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [CustomInsertMergeFieldItem.cs](./CS/CustomInsertMergeFieldItem.cs) (VB: [CustomInsertMergeFieldItem.vb](./VB/CustomInsertMergeFieldItem.vb))
* [DataBindingController.cs](./CS/DataBindingController.cs) (VB: [DataBindingController.vb](./VB/DataBindingController.vb))
* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# How to customize the "Insert Merge Field" menu


<p>This example illustrates how to customize the "Insert Merge Field" menu to group merge field names with identical prefixes (Employees and Customers in this example) into submenus. 
We completely replaced a built-in InsertMergeFieldItem with a custom one. You can find its implementation in the CustomInsertMergeFieldItem.cs (CustomInsertMergeFieldItem.vb for VB.NET) code file. </p>
 
<p>In this example the <strong>DataBindingController </strong>class generates menu items/subitems from the mail merge data source on the fly.
These items are added to a <a href="http://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsPopupMenutopic"><u>popup menu</u></a>. </p>
 
<p>When a custom menu item is clicked, the<strong>CustomInsertMergeFieldMenuItem</strong><strong>'s</strong><strong> </strong><strong>OnClick</strong> method is executed to insert the current merge field.
Take a moment to look at the <a href="https://www.devexpress.com/Support/Center/p/Q327983">Create DOCVARIABLE in code</a> and <a href="https://www.devexpress.com/Support/Center/p/E4004">How to create nested fields programmatically</a> code examples to learn more on this subject. </p>
 
<p>When the custom "Insert Merge Field" Ribbon item is clicked, the built-in "Insert Merge Field" form is shown. See the <strong>CustomInsertMergeFieldItem</strong><strong>'s</strong> <strong>OnClick </strong>method implementation for clarification.
You can implement and display your own dialog here if necessary. </p>
 
<p>Note that the custom "Insert Merge Field" Ribbon item uses resources (images) from the project's "Images" folder to initialize the BarButtomItem.LargeGlyph and BarButtonItem.Glyph properties. Customize the LargeGlyph and Glyph properties of the CustomInsertMergeFieldItem class to use another source for images. </p>

<p>Here is a screenshot that illustrates a sample application in action:</p><p><img src="https://raw.githubusercontent.com/DevExpress-Examples/how-to-customize-the-insert-merge-field-menu-e4177/13.1.4+/media/4c2ca3c3-807f-41d3-8934-88fe103f4b80.png"></p>

<br/>


