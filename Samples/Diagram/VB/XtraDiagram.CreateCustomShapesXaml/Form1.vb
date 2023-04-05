Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.Diagram.Core
Imports DevExpress.Diagram.Core.Shapes
Imports System.Windows

Namespace XtraDiagram.CreateCustomShapes
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        Public Sub New()
            InitializeComponent()
            RegisterCustomShapes()
            Me.diagramControl1.SelectedStencils = New StencilCollection(New String() { "CustomShapes" })
        End Sub
        Protected Overrides Sub OnLoad(ByVal e As EventArgs)
            MyBase.OnLoad(e)
            Me.diagramControl1.InitializeRibbon(Me.ribbonControl1)
        End Sub

        Private Sub RegisterCustomShapes()
            Dim shapesDictionary = New ResourceDictionary() With {.Source = New Uri("DiagramResources.xaml", UriKind.RelativeOrAbsolute)}
            Dim stencil = DiagramStencil.Create("CustomShapes", "Custom Shapes", shapesDictionary, Function(shapeName) shapeName)
            DiagramToolboxRegistrator.RegisterStencil(stencil)
        End Sub
    End Class

End Namespace
