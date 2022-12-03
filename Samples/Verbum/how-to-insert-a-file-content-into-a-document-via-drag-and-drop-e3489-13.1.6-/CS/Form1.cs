using System.Drawing;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Office.Utils;

namespace RichEditInsertDroppedFile {
    public partial class Form1 : Form {
        private Graphics richEditGraphics = null;

        public Form1() {
            InitializeComponent();
        }

        private void richEditControl1_DragEnter(object sender, DragEventArgs e) {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop))
                return;
            
            richEditControl1.Options.Behavior.Drop = DevExpress.XtraRichEdit.DocumentCapability.Disabled;
            e.Effect = DragDropEffects.Copy;
        }

        private void richEditControl1_DragOver(object sender, DragEventArgs e) {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop))
                return;

            Point docPoint = Units.PixelsToDocuments(richEditControl1.PointToClient(Form.MousePosition),
                richEditControl1.DpiX, richEditControl1.DpiY);

            DocumentPosition pos = richEditControl1.GetPositionFromPoint(docPoint);
            if(pos != null) {
                Rectangle rect = Units.DocumentsToPixels(richEditControl1.GetBoundsFromPosition(pos),
                    richEditControl1.DpiX, richEditControl1.DpiY);

                richEditControl1.Document.CaretPosition = pos;

                if(richEditGraphics == null)
                    richEditGraphics = richEditControl1.CreateGraphics();

                rect.Width = 2;
                richEditControl1.Refresh();
                richEditGraphics.FillRectangle(Brushes.Blue, rect);
                richEditControl1.ScrollToCaret();                
            }
        }

        private void richEditControl1_DragDrop(object sender, DragEventArgs e) {
            if (!e.Data.GetDataPresent(DataFormats.FileDrop))
                return;
            
            string path = ((string[])e.Data.GetData(DataFormats.FileDrop))[0];
            RichEditDocumentServer server = new RichEditDocumentServer();

            server.LoadDocument(path);

            richEditControl1.Document.BeginUpdate();
            DocumentRange rangeInsertedContent = richEditControl1.Document.InsertDocumentContent(
                richEditControl1.Document.CaretPosition, server.Document.Range);
            DocumentRange rangeNewLine = richEditControl1.Document.CreateRange(rangeInsertedContent.End.ToInt() - 1, 1);
            richEditControl1.Document.Delete(rangeNewLine);
            richEditControl1.Document.EndUpdate();

            richEditControl1.Options.Behavior.Drop = DevExpress.XtraRichEdit.DocumentCapability.Enabled;
        }
    }
}