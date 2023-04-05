using System;
using DevExpress.Spreadsheet;
using DevExpress.XtraRichEdit.API.Native;

namespace SpreadsheetRichText
{
    public partial class RichTextEditForm : DevExpress.XtraEditors.XtraForm
    {
        private Cell cell;
        public RichTextEditForm(Cell cell)
        {
            InitializeComponent();
            this.cell = cell;
            InitRichEditControl();
        }
        private void InitRichEditControl()
        {

            richEditControl1.BeginUpdate();
            if (cell.HasRichText)
            {
                RichTextString richText = cell.GetRichText();
                Document document = richEditControl1.Document;
                foreach (RichTextRun run in richText.Runs)
                {
                    DocumentRange range = document.InsertText(document.Range.End, run.Text);
                    CharacterProperties cp = document.BeginUpdateCharacters(range);
                    cp.Bold = run.Font.Bold;
                    cp.ForeColor = run.Font.Color;
                    cp.Italic = run.Font.Italic;
                    cp.FontName = run.Font.Name;
                    cp.FontSize = (float)run.Font.Size;
                    cp.Strikeout = run.Font.Strikethrough ? StrikeoutType.Single : StrikeoutType.None;
                    switch (run.Font.Script)
                    {
                        case ScriptType.Subscript:
                            cp.Subscript = true;
                            break;
                        case ScriptType.Superscript:
                            cp.Superscript = true;
                            break;
                        default:
                            cp.Subscript = false;
                            cp.Superscript = false;
                            break;
                    }
                    switch (run.Font.UnderlineType)
                    {
                        case DevExpress.Spreadsheet.UnderlineType.Single:
                            cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.Single;
                            break;
                        case DevExpress.Spreadsheet.UnderlineType.Double:
                            cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.Double;
                            break;
                        default:
                            cp.Underline = DevExpress.XtraRichEdit.API.Native.UnderlineType.None;
                            break;
                    }
                    document.EndUpdateCharacters(cp);
                }
            }
            else
                richEditControl1.Text = cell.DisplayText;
            richEditControl1.EndUpdate();
        }

        private void OKButton_Click(object sender, EventArgs e)
        {
            CustomDocumentVisitor visitor = new CustomDocumentVisitor(richEditControl1.Document.Range.End.ToInt());
            DocumentIterator iterator = new DocumentIterator(richEditControl1.Document, true);
            while (iterator.MoveNext())
            {
                iterator.Current.Accept(visitor);
            }
            RichTextString richText = visitor.RichText;
            cell.SetRichText(richText);
            if (richEditControl1.Document.Paragraphs.Count > 1)
                cell.Alignment.WrapText = true;
        }
    }
}