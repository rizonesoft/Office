<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/172920413/18.2.6%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T830456)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
# How to show custom tooltips in SpreadsheetControl

This example demonstrates how to implement custom tooltips for SpreadsheetControl cells using the [ToolTipController](https://docs.devexpress.com/WindowsForms/DevExpress.Utils.ToolTipController) component. 
Add this component to the form, assign ToolTipController to the [SpreadsheetControl.ToolTipController](https://docs.devexpress.com/WindowsForms/DevExpress.XtraSpreadsheet.SpreadsheetControl.ToolTipController) property and handle the [ToolTipController.GetActiveObjectInfo](https://docs.devexpress.com/WindowsForms/DevExpress.Utils.ToolTipController.GetActiveObjectInfo) event to build the tooltip.

Use the [SpreadsheetControl.GetCellFromPoint](https://docs.devexpress.com/WindowsForms/DevExpress.XtraSpreadsheet.SpreadsheetControl.GetCellFromPoint(System.Drawing.PointF)) method to obtain a cell over which the mouse hovers and show cell data in the tooltip.
