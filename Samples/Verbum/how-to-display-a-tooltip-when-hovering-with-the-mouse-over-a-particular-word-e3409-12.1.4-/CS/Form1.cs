using System.Drawing;
using System.Windows.Forms;
using DevExpress.Utils;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.Office.Utils;

namespace RichEditWordTooltip {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            SetTestHeaderContent();
        }

        private void richEditControl1_MouseMove(object sender, MouseEventArgs e) {
            Point docPoint = Units.PixelsToDocuments(e.Location, richEditControl1.DpiX, richEditControl1.DpiY);
            DocumentPosition pos = richEditControl1.GetPositionFromPoint(docPoint);

            if (pos == null)
                return;

            DocumentPosition start = pos;
            DocumentPosition end = pos;

            SubDocument doc = richEditControl1.Document.CaretPosition.BeginUpdateDocument();

            for (int i = 0; i < doc.Range.End.ToInt(); i++) {
                if (start.ToInt() - i < 0) {
                    start = doc.Range.Start;
                    break;
                }

                DocumentRange range = doc.CreateRange(start.ToInt() - i, i + 1);
                string str = doc.GetText(range);
                
                if (ContainsPunctuationOrWhiteSpace(str)) {
                    start = doc.CreatePosition(range.Start.ToInt() + 1);
                    break;
                }
            }

            for (int i = 0; i < doc.Range.End.ToInt(); i++) {
                if (end.ToInt() + i > doc.Range.End.ToInt()) {
                    end = doc.Range.End;
                    break;
                }
                
                DocumentRange range = doc.CreateRange(end.ToInt(), i + 1);
                string str = doc.GetText(range);

                if (ContainsPunctuationOrWhiteSpace(str)) {
                    end = doc.CreatePosition(range.End.ToInt() - 1);
                    break;
                }
            }

            if (end.ToInt() < start.ToInt())
                return;

            DocumentRange wordRange = doc.CreateRange(start, end.ToInt() - start.ToInt());
            string word = doc.GetText(wordRange);

            richEditControl1.Document.CaretPosition.EndUpdateDocument(doc);

            ShowToolTip(word);
        }

        protected bool ContainsPunctuationOrWhiteSpace(string str) {
            for (int i = 0; i < str.Length; i++) {
                if (char.IsPunctuation(str[i]) || char.IsWhiteSpace(str[i]))
                    return true;
            }
            return false;
        }

        private void ShowToolTip(string word) {
            ToolTipControlInfo info = new ToolTipControlInfo(word, word);
            info.ToolTipPosition = Form.MousePosition;
            toolTipController1.ShowHint(info);
        }

        private void SetTestHeaderContent() {
            Section firstSection = richEditControl1.Document.Sections[0];
            SubDocument doc = firstSection.BeginUpdateHeader(HeaderFooterType.Odd);
            doc.InsertText(doc.Range.Start, "Page header");
            richEditControl1.Document.Sections[0].EndUpdateHeader(doc);
        }
    }
}