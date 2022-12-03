<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610590/14.2.6%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T223036)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/WindowsFormsApplication1/Form1.cs) (VB: [Form1.vb](./VB/WindowsFormsApplication1/Form1.vb))
* [InsertFieldDialog.cs](./CS/WindowsFormsApplication1/InsertFieldModules/InsertFieldDialog.cs) (VB: [InsertFieldDialog.vb](./VB/WindowsFormsApplication1/InsertFieldModules/InsertFieldDialog.vb))
* [InsertFieldRichEditHelper.cs](./CS/WindowsFormsApplication1/InsertFieldModules/InsertFieldRichEditHelper.cs) (VB: [InsertFieldRichEditHelper.vb](./VB/WindowsFormsApplication1/InsertFieldModules/InsertFieldRichEditHelper.vb))
* [ucCREATEDATE.cs](./CS/WindowsFormsApplication1/InsertFieldModules/ucCREATEDATE.cs) (VB: [ucCREATEDATE.vb](./VB/WindowsFormsApplication1/InsertFieldModules/ucCREATEDATE.vb))
* [ucDOCVARIABLE.cs](./CS/WindowsFormsApplication1/InsertFieldModules/ucDOCVARIABLE.cs) (VB: [ucDOCVARIABLE.vb](./VB/WindowsFormsApplication1/InsertFieldModules/ucDOCVARIABLE.vb))
* [ucIFFIELD.cs](./CS/WindowsFormsApplication1/InsertFieldModules/ucIFFIELD.cs) (VB: [ucIFFIELD.vb](./VB/WindowsFormsApplication1/InsertFieldModules/ucIFFIELD.vb))
* [ucPAGENUMBER.cs](./CS/WindowsFormsApplication1/InsertFieldModules/ucPAGENUMBER.cs) (VB: [ucPAGENUMBER.vb](./VB/WindowsFormsApplication1/InsertFieldModules/ucPAGENUMBER.vb))
<!-- default file list end -->
# How to implement the "Insert Document Field" dialog (WinForms version)


<p>This example demonstrates how to implement a custom "Insert Document Field" dialog to insert fields with corresponding formatting attributes into RichEditControl documents.<br />All fields are inserted into a current document position using the <a href="https://documentation.devexpress.com/#WPF/CustomDocument10467">SubDocument.Fields.Create</a> method. The key point here is that you need to obtain a corresponding sub-document which is related to the caret position, since the caret can be located in the main document, its header or footer.<br />To obtain a corresponding sub-document, the <a href="https://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeDocumentRange_BeginUpdateDocumenttopic">DocumentPosition.BeginUpdateDocument</a> method is used.<br />Also, this example demonstrates how to insert expressions and results of the "<strong>IF" </strong>field<strong> </strong>calculation as nested document fields (there is a corresponding option near the "left expression", "right expression", "true result" and "false result" of the "<strong>IF" </strong>field attributes).<br /><br /></p>
<p>To built the solution demonstrated in this sample into an existing application, copy all modules and the "insertFieldIcon.png" image located in the <strong>InsertFieldModules </strong>folder and use a corresponding <strong>RegisterInsertFieldDialogCommand</strong> extension method to add the "Insert Field" command onto a current Ribbon control:<br /><strong>CS<br /></strong></p>


```cs
richEditControl1.RegisterInsertFieldDialogCommand(ribbonPageGroup1, null);
```


<p><strong>VB<br /></strong></p>


```vb
richEditControl1.RegisterInsertFieldDialogCommand(ribbonPageGroup1, Nothing)
```


<p><strong> </strong></p>

<br/>


