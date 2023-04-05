<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128585339/16.1.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T381372)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [DiagramResourceKey.cs](./CS/XtraDiagram.CreateCustomShapesXaml/DiagramResourceKey.cs) (VB: [DiagramResourceKey.vb](./VB/XtraDiagram.CreateCustomShapesXaml/DiagramResourceKey.vb))
* [DiagramResources.xaml](./CS/XtraDiagram.CreateCustomShapesXaml/DiagramResources.xaml) (VB: [DiagramResources.xaml](./VB/XtraDiagram.CreateCustomShapesXaml/DiagramResources.xaml))
* [Form1.cs](./CS/XtraDiagram.CreateCustomShapesXaml/Form1.cs) (VB: [Form1.vb](./VB/XtraDiagram.CreateCustomShapesXaml/Form1.vb))
* [Program.cs](./CS/XtraDiagram.CreateCustomShapesXaml/Program.cs) (VB: [Program.vb](./VB/XtraDiagram.CreateCustomShapesXaml/Program.vb))
<!-- default file list end -->
# DiagramControl - How to create custom shapes with connection points using XAML markup


This example demonstrates how to describe custom shapes using the XAML markup instead of XML.<br><br><strong>Important note:</strong> The PresentationCore library used in this example affects the DPI awareness of WinForms applications (see <a href="https://www.devexpress.com/Support/Center/p/T346466">T346466 - DiagramControl disables DPI scaling for the entire application</a>). Use this approach only if your application is not DPI aware or the PresentationCore library is pre-loaded in the Program.Main method as follows:<br>


```cs
static void RegisterPackUriScheme() {
    new FlowDocument();
}
```


<p>In other cases, it is preferred to describe shapes using XML, as demonstrated in the following example: <a href="https://www.devexpress.com/Support/Center/p/T324404">T324404 - DiagramControl - How to create custom shapes with connection points</a>.</p>

<br/>


