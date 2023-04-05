<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/193709120/19.1.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T828665)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
# How to edit rich text in SpreadsheetControl
The main idea of this example is to create a custom form with RichEditControl inside and show this form instead of SpreadsheetControl's built-in in-place editor to edit a cell's rich text using the RichEditControl component's facilities. In this example, the custom edit form is shown on an attempt to open an in-place editor for cells with rich text (it's invoked in the [CellBeginEdit](https://docs.devexpress.com/WindowsForms/DevExpress.XtraSpreadsheet.SpreadsheetControl.CellBeginEdit) event handler). Also, it is possible to show this form by clicking the “Set Rich Text” [context menu](https://docs.devexpress.com/WindowsForms/16378/controls-and-libraries/spreadsheet/examples/customization/how-to-customize-or-hide-the-popup-menu) item.

It's necessary to solve two tasks at the custom form's level to make it edit the cell's rich text:
 1. Load and show the cell's rich text in RichEditControl when an end-user opens a custom form.
 2. Post changes from RichEditControl to the Spreadsheet cell once the user finishes editing rich text and closes the form.

The solution for the first task is to transform the cell rich text from the Spreadsheet model to the RichEdit document model. Split cell rich text into [runs](https://docs.devexpress.com/OfficeFileAPI/DevExpress.Spreadsheet.RichTextString.Runs)  (text parts with unique formatting) using the Spreadsheet API, look through the run collection, and build a document using the RichEdit API:
 - Append each run's text to the RichEditControl document;
 - Create [CharacterProperties](https://docs.devexpress.com/OfficeFileAPI/DevExpress.XtraRichEdit.API.Native.CharacterProperties) based on run font settings;
 - Apply character properties to the inserted text part

Now the end-user can edit the rich text in RichEditControl using the Bars UI.

To submit changes on form closing, transform RichEditControl's model back to the Spreadsheet model and build a new Spreadsheet cell value as follows:
 - Split the RichEditControl document into text runs using a custom [Document Visitor](https://docs.devexpress.com/OfficeFileAPI/DevExpress.XtraRichEdit.API.Native.DocumentVisitorBase) class;
 - Transform each text run into a Spreadsheet [RichTextRun](https://docs.devexpress.com/OfficeFileAPI/DevExpress.Spreadsheet.RichTextRun) object;
 - Combine all RichTextRun objects into [RichTextString](https://docs.devexpress.com/OfficeFileAPI/DevExpress.Spreadsheet.RichTextString);
 - Assign [RichTextString](https://docs.devexpress.com/OfficeFileAPI/DevExpress.Spreadsheet.RichTextString) as a cell value using the [Range.SetRichText](https://docs.devexpress.com/OfficeFileAPI/DevExpress.Spreadsheet.Range.SetRichText(DevExpress.Spreadsheet.RichTextString)) method.


See also:  
[How to: Apply Rich Formatting to Cell Text](https://docs.devexpress.com/WindowsForms/120599/controls-and-libraries/spreadsheet/examples/formatting/how-to-apply-rich-formatting-to-cell-text)

[How to: Retrieve the List of Document Fonts using the Visitor-Iterator Pattern](https://docs.devexpress.com/WindowsForms/116746/controls-and-libraries/rich-text-editor/examples/automation/how-to-retrieve-the-list-of-document-fonts-using-the-visitor-iterator-pattern)
