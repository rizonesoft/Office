<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128585369/16.2.3%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T466447)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* **[CustomContainers.xml](./CS/XtraDiagram.CreateCustomContainers/CustomContainers.xml) (VB: [CustomContainers.xml](./VB/XtraDiagram.CreateCustomContainers/CustomContainers.xml))**
* [Form1.cs](./CS/XtraDiagram.CreateCustomContainers/Form1.cs) (VB: [Form1.vb](./VB/XtraDiagram.CreateCustomContainers/Form1.vb))
<!-- default file list end -->
# How to create custom diagram containers and register them in the toolbox and ribbon gallery


In this example, we show how to create containers with custom headers and padding. <br>DiagramControl supports a special language for defining containers. The root element that contains a container description is <em>ContainerShapeTemplate</em>. This element describes a container contour and may contain several segments

* <em>Start</em>. Specifies the start point
* <em>Line</em>. Defines a line with start and end points
* <em>Arc</em>. Defines an arc with start and end points<br><br>To define a container's header editor position, use the EditorBounds property. To specify a padding, set the ActualPadding property.<br>To register custom containers in the ribbon gallery, use the DiagramContainerGalleryRegistrator.RegisterContainerShapes method.

<br/>


