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

namespace XtraDiagram.CreateCustomShapes {
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm {
        public Form1() {
            InitializeComponent();
            RegisterCustomShapes();
            this.diagramControl1.SelectedStencils = new StencilCollection(new string[] { "CustomShapes" });
        }
        protected override void OnLoad(EventArgs e) {
            base.OnLoad(e);
            this.diagramControl1.InitializeRibbon(this.ribbonControl1);
        }

        void RegisterCustomShapes() {
            var shapesDictionary = new ResourceDictionary() {
                Source = new Uri("DiagramResources.xaml", UriKind.RelativeOrAbsolute)
            };
            var stencil = DiagramStencil.Create("CustomShapes", "Custom Shapes", shapesDictionary, shapeName => shapeName);
            DiagramToolboxRegistrator.RegisterStencil(stencil);
        }
    }
    
}
