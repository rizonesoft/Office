using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.Diagram.Core;
using DevExpress.Diagram.Core.Shapes;
using System.Windows;
using System.IO;
using System.Reflection;

namespace XtraDiagram.CreateCustomContainers {
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm {
        const string MyContainersStencilName = "MyContainers";
        static readonly ContainerShapeDescription[] containerDescriptions;
        static Form1() {
            using(var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("XtraDiagram.CreateCustomContainers.CustomContainers.xml")) {
                containerDescriptions = ShapeDescriptions.LoadDescriptionsFromXml(stream).OfType<ContainerShapeDescription>().ToArray();
            }
            DiagramContainerGalleryRegistrator.RegisterContainerShapes(containerDescriptions);
        }
        public Form1() {
            InitializeComponent();
            var customContainersStencil = DiagramStencil.Create(MyContainersStencilName, "Custom Containers", containerDescriptions);
            diagramControl1.OptionsBehavior.Stencils = new DiagramStencilCollection(DiagramToolboxRegistrator.Stencils.Concat(new[] { customContainersStencil }));
            diagramControl1.SelectedStencils = new StencilCollection(MyContainersStencilName, BasicShapes.StencilId);
        }
        protected override void OnLoad(EventArgs e) {
            base.OnLoad(e);
            this.diagramControl1.InitializeRibbon(this.ribbonControl1);
        }
    }

}
