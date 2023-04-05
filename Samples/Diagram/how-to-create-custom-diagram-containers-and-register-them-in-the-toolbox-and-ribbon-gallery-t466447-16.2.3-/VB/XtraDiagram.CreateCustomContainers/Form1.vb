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
Imports System.IO
Imports System.Reflection

Namespace XtraDiagram.CreateCustomContainers
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        Private Const MyContainersStencilName As String = "MyContainers"
        Private Shared ReadOnly containerDescriptions() As ContainerShapeDescription
        Shared Sub New()
            Using stream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("XtraDiagram.CreateCustomContainers.CustomContainers.xml")
                containerDescriptions = ShapeDescriptions.LoadDescriptionsFromXml(stream).OfType(Of ContainerShapeDescription)().ToArray()
            End Using
            DiagramContainerGalleryRegistrator.RegisterContainerShapes(containerDescriptions)
        End Sub
        Public Sub New()
            InitializeComponent()
            Dim customContainersStencil = DiagramStencil.Create(MyContainersStencilName, "Custom Containers", containerDescriptions)
            diagramControl1.OptionsBehavior.Stencils = New DiagramStencilCollection(DiagramToolboxRegistrator.Stencils.Concat( { customContainersStencil }))
            diagramControl1.SelectedStencils = New StencilCollection(MyContainersStencilName, BasicShapes.StencilId)
        End Sub
        Protected Overrides Sub OnLoad(ByVal e As EventArgs)
            MyBase.OnLoad(e)
            Me.diagramControl1.InitializeRibbon(Me.ribbonControl1)
        End Sub
    End Class

End Namespace
