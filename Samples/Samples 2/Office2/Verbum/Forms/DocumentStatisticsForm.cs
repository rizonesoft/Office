using System;
using System.Linq;
using System.Text;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit.API.Native;


namespace Rizonesoft.Office.Verbum.Forms
{
    public partial class DocumentStatisticsForm : XtraForm
    {
        readonly SubDocument document;

        public DocumentStatisticsForm(SubDocument document, bool includeTextboxes)
        {
            InitializeComponent();
            this.document = document;
            this.chkIncludeTextboxes.Checked = includeTextboxes;
            CalculateStatistics();
        }

        public bool IncludeTextboxes { get { return chkIncludeTextboxes.Checked; } }

        private void chkIncludeTextboxes_CheckedChanged(object sender, EventArgs e)
        {

        }

        void CalculateStatistics()
        {
            DocumentIterator iterator = new DocumentIterator(this.document, true);
            StaticsticsVisitor visitor = new StaticsticsVisitor(IncludeTextboxes);
            while (iterator.MoveNext())
                iterator.Current.Accept(visitor);
            this.lblNoSpacesCharactersCount.Text = String.Format("{0,5}", visitor.NoSpacesCharacterCount);
            this.lblWithSpacesCharactersCount.Text = String.Format("{0,5}", visitor.WithSpacesCharacterCount);
            this.lblWordsCount.Text = String.Format("{0,5}", visitor.WordCount);
            this.lblParagraphsCount.Text = String.Format("{0,5}", visitor.ParagraphCount);
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }

    public class StaticsticsVisitor : DocumentVisitorBase
    {
        readonly StringBuilder _buffer;
        readonly bool includeTextboxes;
        int _noSpacesCharacterCount;
        int _withSpacesCharacterCount;
        int _wordCount;
        int _paragraphCount;

        public StaticsticsVisitor(bool includeTextboxes)
        {
            this._buffer = new StringBuilder();
            this.includeTextboxes = includeTextboxes;
        }

        StringBuilder Buffer { get { return _buffer; } }
        public int NoSpacesCharacterCount { get { return _noSpacesCharacterCount; } }
        public int WithSpacesCharacterCount { get { return _withSpacesCharacterCount; } }
        public int WordCount { get { return _wordCount; } }
        public int ParagraphCount { get { return _paragraphCount; } }

        public override void Visit(DocumentText text)
        {
            Buffer.Append(text.Text);
        }

        public override void Visit(DocumentTextBox textBox)
        {
            if (!this.includeTextboxes) return;
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
    }



}
