using DevExpress.Diagram.Core;
using DevExpress.XtraDiagram;
using DevExpress.XtraDiagram.Extensions;
using DevExpress.XtraGrid.Views.Grid.ViewInfo;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CustomDiagramToolboxExample
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            var toolboxItems = new ObservableCollection<DiagramShape>();
            foreach (var shape in BasicShapes.Stencil.Shapes)
            {
                toolboxItems.Add(new DiagramShape() { Shape = shape });
            }
            gridControl1.DataSource = toolboxItems;
        }
        int shapeTextOffset = 60;
        Point mouseDownLocation;
        GridHitInfo gridHitInfo;
        private void GridView1_CustomDrawCell(object sender, DevExpress.XtraGrid.Views.Base.RowCellCustomDrawEventArgs e)
        {
            DiagramShape shapeItem = gridView1.GetRow(e.RowHandle) as DiagramShape;
            if (shapeItem == null)
                return;
            GraphicsState transState = e.Graphics.Save();
            try
            {
                e.Appearance.DrawString(e.Cache, e.DisplayText, new Rectangle(e.Bounds.X + shapeTextOffset, e.Bounds.Y, e.Bounds.Width - shapeTextOffset, e.Bounds.Height));
                e.Cache.TranslateTransform(e.Bounds.X, e.Bounds.Y);
                shapeItem.Width = 40;
                shapeItem.Height = e.Bounds.Height;
                diagramControl1.DrawDetachedItem(shapeItem, e.Cache);
                e.Handled = true;
            }
            finally
            {
                e.Graphics.Restore(transState);
            }
        }
        private void gridControl1_MouseDown(object sender, MouseEventArgs e)
        {
            gridHitInfo = gridView1.CalcHitInfo(e.Location);
            mouseDownLocation = e.Location;
        }
        private void gridControl1_MouseMove(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left && CanStartDragDrop(e.Location))
            {
                StartDragDrop();
            }
        }
        private void gridControl1_MouseLeave(object sender, EventArgs e)
        {
            if (gridHitInfo != null)
                gridHitInfo.View.ResetCursor();
            gridHitInfo = null;
        }
        private bool CanStartDragDrop(Point location)
        {
            return gridHitInfo.InDataRow && (Math.Abs(location.X - mouseDownLocation.X) > 2 || Math.Abs(location.Y - mouseDownLocation.Y) > 2);
        }
        public void StartDragDrop()
        {
            var draggedItem = (DiagramShape)gridHitInfo.View.GetRow(gridHitInfo.RowHandle);
            var tool = new FactoryItemTool("", () => "", diagram => new DiagramShape(draggedItem.Shape), new System.Windows.Size(150, 100));
            diagramControl1.Commands.Execute(DiagramCommandsBase.StartDragToolCommand, tool, null);
        }
    }
}
