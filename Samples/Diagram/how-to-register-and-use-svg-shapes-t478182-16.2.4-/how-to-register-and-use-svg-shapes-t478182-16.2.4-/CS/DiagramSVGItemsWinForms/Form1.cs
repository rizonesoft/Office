using DevExpress.Utils;
using DevExpress.XtraDiagram;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace DiagramSVGItemsWinForms
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm
    {
        private string path;
        public Form1()
        {
            InitializeComponent();
            path = @"..\..\Icons";
            CreateToolboxItems(path);
        }

        void CreateToolboxItems(string path)
        {
            var stencil = new DevExpress.Diagram.Core.DiagramStencil("SVGStencil", "IcoMoon - Free Shapes");
            string name = string.Empty;
            foreach (string file in Directory.GetFiles(path))
            {
                try
                {
                    name = System.IO.Path.GetFileNameWithoutExtension(file);
                    using (FileStream stream = File.Open(file, FileMode.Open))
                    {
                        var shape = DevExpress.Diagram.Core.ShapeDescription.CreateSvgShape(name, name, stream)
                            .Update(getDefaultSize: () => new System.Windows.Size(100, 100))
                            .Update(getConnectionPoints: (w, h, p) => new[] { new System.Windows.Point(w / 2, h / 2) });
                        stencil.RegisterShape(shape);
                    }
                }
                catch (Exception)
                {
                    //some SVG files cannot be parsed, so swallow the exception for now.
                    //throw;
                }
            }
            DevExpress.Diagram.Core.DiagramToolboxRegistrator.RegisterStencil(stencil);
            diagramControl1.SelectedStencils.Add("SVGStencil");


            diagramControl1.Items.Add(new DiagramShape() { Shape = stencil.GetShape("aid-kit"), Width = 100, Height = 100, Position = new PointFloat(300, 300) });
        }
    }
}
