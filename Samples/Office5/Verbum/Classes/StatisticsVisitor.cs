using DevExpress.XtraRichEdit.API.Native;
using System;
using System.Linq;
using System.Text;

namespace Rizonesoft.Office.Verbum.Classes
{
    public class StaticsticsVisitor : DocumentVisitorBase
    {
        readonly StringBuilder _buffer;
        int _noSpacesCharacterCount;
        int _paragraphCount;
        int _withSpacesCharacterCount;
        int _wordCount;
        readonly bool includeTextboxes;

        public StaticsticsVisitor(bool includeTextboxes)
        {
            this._buffer = new StringBuilder();
            this.includeTextboxes = includeTextboxes;
        }

        void FinishParagraph()
        {
            string text = Buffer.ToString();
            this._noSpacesCharacterCount += text.Count(c => !Char.IsWhiteSpace(c));
            this._withSpacesCharacterCount += text.Length;
            this._wordCount += text.Split(new char[] { ' ', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries).Length;
            if (!string.IsNullOrWhiteSpace(text))
                this._paragraphCount++;
            Buffer.Length = 0;
        }

        StringBuilder Buffer
        {
            get
            {
                return _buffer;
            }
        }

        public override void Visit(DocumentText text)
        {
            Buffer.Append(text.Text);
        }

        public override void Visit(DocumentTextBox textBox)
        {
            if (!this.includeTextboxes)
            {
                return;
            }
            DocumentIterator iterator = textBox.GetIterator(true);
            StaticsticsVisitor visitor = new StaticsticsVisitor(false);
            while (iterator.MoveNext())
                iterator.Current.Accept(visitor);
            this._noSpacesCharacterCount += visitor.NoSpacesCharacterCount;
            this._withSpacesCharacterCount += visitor.WithSpacesCharacterCount;
            this._wordCount += visitor.WordCount;
            this._paragraphCount += visitor.ParagraphCount;
        }

        public override void Visit(DocumentSectionEnd sectionEnd)
        {
            FinishParagraph();
        }

        public override void Visit(DocumentParagraphEnd paragraphEnd)
        {
            FinishParagraph();
        }

        public int NoSpacesCharacterCount
        {
            get
            {
                return _noSpacesCharacterCount;
            }
        }

        public int ParagraphCount
        {
            get
            {
                return _paragraphCount;
            }
        }

        public int WithSpacesCharacterCount
        {
            get
            {
                return _withSpacesCharacterCount;
            }
        }

        public int WordCount
        {
            get
            {
                return _wordCount;
            }
        }

    }

}
