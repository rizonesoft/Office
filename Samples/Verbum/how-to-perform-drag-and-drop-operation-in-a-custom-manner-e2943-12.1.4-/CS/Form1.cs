using System.Drawing;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Office.Utils;

namespace RichListDragDrop {
    public partial class Form1 : Form {
        private Graphics richEditGraphics = null;
        private bool customDragDropTarget = false;

        public Form1() {
            InitializeComponent();
        }

        private void listBox1_MouseDown(object sender, MouseEventArgs e) {
            if (listBox1.Items.Count == 0)
                return;

            customDragDropTarget = true;

            int index = listBox1.IndexFromPoint(e.X, e.Y);
            string item = listBox1.Items[index].ToString();
            DragDropEffects dde1 = DoDragDrop(item, DragDropEffects.Copy);

            customDragDropTarget = false;
        }

        private void richEditControl1_DragEnter(object sender, DragEventArgs e) {
            if (e.Data.GetDataPresent(DataFormats.StringFormat))
                e.Effect = DragDropEffects.Copy;
        }

        private void richEditControl1_DragOver(object sender, DragEventArgs e) {
            if (!customDragDropTarget)
                return;

            Point docPoint = Units.PixelsToDocuments(richEditControl1.PointToClient(Form.MousePosition),
                richEditControl1.DpiX, richEditControl1.DpiY);

            DocumentPosition pos = richEditControl1.GetPositionFromPoint(docPoint);
            
            if (pos == null) 
                return;
            
            Rectangle rect = Units.DocumentsToPixels(richEditControl1.GetBoundsFromPosition(pos),
                richEditControl1.DpiX, richEditControl1.DpiY);

            richEditControl1.Document.CaretPosition = pos;

            if (richEditGraphics == null)
                richEditGraphics = richEditControl1.CreateGraphics();

            rect.Width = 2;
            richEditControl1.Refresh();
            richEditGraphics.FillRectangle(Brushes.Blue, rect);
            richEditControl1.ScrollToCaret();
        }

        private void richEditControl1_DragDrop(object sender, DragEventArgs e) {
            if (!customDragDropTarget)
                return;

            string text = (string)e.Data.GetData(DataFormats.StringFormat);

            richEditControl1.Document.InsertText(
                richEditControl1.Document.CaretPosition, text);
        }
    }
}