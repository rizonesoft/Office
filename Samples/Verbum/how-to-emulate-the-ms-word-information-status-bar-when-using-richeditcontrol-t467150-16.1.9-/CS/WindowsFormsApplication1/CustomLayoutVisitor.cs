using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Layout;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Reflection;
using System.Text;

namespace WindowsFormsApplication1
{
    public class StaticsticsVisitor : DocumentVisitorBase
    {
        readonly StringBuilder buffer;
        
        public int WordCount { get; private set; }
        protected StringBuilder Buffer { get { return buffer; } }

        public StaticsticsVisitor()
        {
            WordCount = 0;
            this.buffer = new StringBuilder();
        }

        public override void Visit(DocumentText text)
        {
            Buffer.Append(text.Text);
        }

        public override void Visit(DocumentParagraphEnd paragraphEnd)
        {
            FinishParagraph();
        }

        void FinishParagraph()
        {
            string text = Buffer.ToString();
            this.WordCount += text.Split(new char[] { ' ', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries).Length;
            Buffer.Length = 0;
        }
    }

    public class CustomLayoutVisitor : LayoutVisitor
    {
        Document document;

        public CustomLayoutVisitor(Document doc)
        {
            this.document = doc;
            RowIndex = 0;
            ColIndex = 0;
            IsFound = false;
        }

        protected override void VisitRow(LayoutRow row)
        {
            if (!IsFound)
            {
                RowIndex++;
                if (row.Range.Contains(document.CaretPosition.ToInt()))
                {
                    IsFound = true;
                    ColIndex = document.CaretPosition.ToInt() - row.Range.Start;
                }
            }
            base.VisitRow(row);
        }

        public void Reset()
        {
            RowIndex = 0;
            ColIndex = 0;
        }

        public int ColIndex { get; private set; }
        public int RowIndex { get; private set; }
        public bool IsFound { get; private set; }
    }
}
