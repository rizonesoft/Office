<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610603/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E2931)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# How to implement the next/previous word selection commands


<p>This example demonstrates how to select the next/previous word in the RichEditControl programmatically. The approach from the <a href="https://www.devexpress.com/Support/Center/p/E2857">How to change the shortcut key assigned to a command</a> example is used to substitute IKeyboardHandlerService in order to execute the next/previous word commands via shortcuts (F6/F7 in this example). The actual command implementation is based of the following built-in commands:</p><p>NextWordCommand<br />
PreviousWordCommand<br />
ExtendNextWordCommand</p>

<br/>


