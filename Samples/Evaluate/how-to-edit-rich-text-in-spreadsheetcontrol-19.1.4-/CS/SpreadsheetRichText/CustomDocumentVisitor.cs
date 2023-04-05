using DevExpress.Spreadsheet;
using DevExpress.XtraRichEdit.API.Native;

namespace SpreadsheetRichText
{
    public class CustomDocumentVisitor : DocumentVisitorBase
    {
        private RichTextString richTextString;
        private int endPosition;
        public RichTextString RichText
        {
            get { return richTextString; }
        }
        public CustomDocumentVisitor(int endPos)
        {
            richTextString = new RichTextString();
            endPosition = endPos;
        }
        public override void Visit(DocumentText text)
        {
            base.Visit(text);
            RichTextRunFont runFont = CreateRichTextRun(text.TextProperties);
            richTextString.AddTextRun(text.Text, runFont);
        }
        public override void Visit(DocumentParagraphEnd paragraphEnd)
        {
            base.Visit(paragraphEnd);
            if (endPosition - 1 != paragraphEnd.Position)
            {
                RichTextRunFont runFont = CreateRichTextRun(paragraphEnd.TextProperties);
                richTextString.AddTextRun(paragraphEnd.Text, runFont);
            }
        }
        private RichTextRunFont CreateRichTextRun(ReadOnlyTextProperties tp)
        {
            RichTextRunFont runFont = new RichTextRunFont(tp.FontName, tp.DoubleFontSize / 2, tp.ForeColor);
            runFont.Bold = tp.FontBold;
            runFont.Italic = tp.FontItalic;
            runFont.Strikethrough = tp.StrikeoutType == StrikeoutType.Single;
            switch(tp.Script)
            {
                case DevExpress.Office.CharacterFormattingScript.Subscript:
                    runFont.Script = ScriptType.Subscript;
                    break;
                case DevExpress.Office.CharacterFormattingScript.Superscript:
                    runFont.Script = ScriptType.Superscript;
                    break;
                default:
                    runFont.Script = ScriptType.None;
                    break;

            }
            switch (tp.UnderlineType)
            {
                case DevExpress.XtraRichEdit.API.Native.UnderlineType.Single:
                    runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.Single;
                    break;
                case DevExpress.XtraRichEdit.API.Native.UnderlineType.Double:
                    runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.Double;
                    break;
                default:
                    runFont.UnderlineType = DevExpress.Spreadsheet.UnderlineType.None;
                    break;
            }
            return runFont;
        }
    }
}
