using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using System.Drawing;

namespace LineNumberingExample {
    #region #MyPagePainter
    public class MyPagePainter : PagePainter {
        RichEditControl richEditControl;
        int previousColumnIndex = -1;
        Font lineNumberFont;

        public MyPagePainter(RichEditControl richEdit)
            : base() {
            richEditControl = richEdit;
        }

        public MyPagePainter(RichEditControl richEdit, Color backColor, CharacterStyle style) 
            : base() {
            richEditControl = richEdit;
            NumberingHighlightColor = backColor;
            NumberingFontName = style.FontName;
            NumberingFontSize = style.FontSize ?? 10F;
            NumberingFontColor = style.ForeColor ?? Color.Black;
        }

        public string NumberingFontName { get; set; }
        public float NumberingFontSize { get; set; }
        public Color NumberingFontColor { get; set; }
        public Color NumberingHighlightColor { get; set; }
        public int LineNumberPadding { get; set; }

        public override void DrawPage(LayoutPage page) {
            lineNumberFont = new Font(NumberingFontName, NumberingFontSize, FontStyle.Regular);
            base.DrawPage(page);
            lineNumberFont.Dispose();
        }
 
        public override void DrawPageArea(LayoutPageArea pageArea) {
            Rectangle lineNumberBounds = new Rectangle(new Point(-LineNumberPadding, 0), new Size(LineNumberPadding, pageArea.Bounds.Height));
            Canvas.FillRectangle(new RichEditBrush(NumberingHighlightColor), lineNumberBounds);
            base.DrawPageArea(pageArea);
            previousColumnIndex = -1;
        }
        public override void DrawColumn(LayoutColumn column) {
            LayoutPageArea pageArea = column.GetParentByType<LayoutPageArea>();
            if (pageArea != null) {
                int leftBoundary = 0;
                if (previousColumnIndex >= 0) {
                    leftBoundary = pageArea.Columns[previousColumnIndex].Bounds.Right;
                }
                if (column.LineNumbers.Count > 0) {
                    HighlightLineNumberingArea(column, leftBoundary);
                }
                previousColumnIndex++;
            }
            base.DrawColumn(column);
        }

        public override void DrawLineNumberBox(LineNumberBox lineNumberBox) {
            Canvas.DrawString(lineNumberBox.Text, lineNumberFont, new RichEditBrush(NumberingFontColor), lineNumberBox.Bounds, this.richEditControl.LayoutUnit);
        }

        void HighlightLineNumberingArea(LayoutColumn column, int leftBoundary) {
                LayoutPage page = column.GetParentByType<LayoutPage>();
            Rectangle marginBounds = new Rectangle(new Point(leftBoundary, 0), new Size(column.Bounds.X - leftBoundary, page.Bounds.Height));
            Canvas.FillRectangle(new RichEditBrush(NumberingHighlightColor), marginBounds);
        }
    }
    #endregion #MyPagePainter
}