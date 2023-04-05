<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/253856911/20.1.3%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T878107)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
# How to create a custom toolbox for WinForms DiagramControl

DiagramControl provides the DrawDetachedItem method to draw diagram items outside of the canvas area. This allows you to use any suitable control as a diagram toolbox. In this example, we use GridControl.

To start dragging an item when a user clicks a grid row, call the StartDragTool command. To draw a diagram item at a specific position, use the TranslateTransform method.



