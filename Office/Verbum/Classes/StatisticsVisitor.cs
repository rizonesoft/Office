using DevExpress.XtraRichEdit.API.Native;
using System;
using System.Text;

namespace Rizonesoft.Office.Verbum.Classes
{
    /// <summary>
    /// Represents a visitor that can traverse the document and collect statistics.
    /// </summary>
    public class StaticsticsVisitor : DocumentVisitorBase
    {
        private readonly StringBuilder _buffer = new StringBuilder();
        private readonly bool _includeTextboxes;
        private static readonly char[] separators = { ' ', '.', '!', '?' };

        public StaticsticsVisitor(bool includeTextboxes)
        {
            _includeTextboxes = includeTextboxes;
        }

        private void FinishParagraph()
        {
            var text = _buffer.ToString();
            var spaces = 0;
            var words = 0;
            var characters = 0;

            foreach (var word in text.Split(separators, StringSplitOptions.RemoveEmptyEntries))
            {
                characters += word.Length;
                words++;
                spaces++;
            }

            NoSpacesCharacterCount += characters;
            WithSpacesCharacterCount += characters + spaces - 1;
            WordCount += words;

            if (!string.IsNullOrWhiteSpace(text))
            {
                ParagraphCount++;
            }

            _buffer.Length = 0;
        }

        /// <summary>
        /// Visits the text in the document.
        /// </summary>
        public override void Visit(DocumentText text)
        {
            try
            {
                _buffer.Append(text?.Text);
            }
            catch (Exception ex)
            {
                // handle exception
            }
        }

        /// <summary>
        /// Visits the text box in the document.
        /// </summary>
        public override void Visit(DocumentTextBox textBox)
        {
            try
            {
                if (!_includeTextboxes || textBox == null)
                {
                    return;
                }

                var iterator = textBox.GetIterator(true);
                var visitor = new StaticsticsVisitor(false);

                while (iterator.MoveNext())
                {
                    iterator.Current?.Accept(visitor);
                }

                NoSpacesCharacterCount += visitor.NoSpacesCharacterCount;
                WithSpacesCharacterCount += visitor.WithSpacesCharacterCount;
                WordCount += visitor.WordCount;
                ParagraphCount += visitor.ParagraphCount;
            }
            catch (Exception ex)
            {
                // handle exception
            }
        }

        /// <summary>
        /// Visits the end of the section in the document.
        /// </summary>
        public override void Visit(DocumentSectionEnd sectionEnd)
        {
            FinishParagraph();
        }

        /// <summary>
        /// Visits the end of the paragraph in the document.
        /// </summary>
        public override void Visit(DocumentParagraphEnd paragraphEnd)
        {
            FinishParagraph();
        }

        /// <summary>
        /// Gets the count of characters without spaces.
        /// </summary>
        public int NoSpacesCharacterCount { get; set; }

        /// <summary>
        /// Gets the count of paragraphs.
        /// </summary>
        public int ParagraphCount { get; set; }

        /// <summary>
        /// Gets the count of characters with spaces.
        /// </summary>
       public int WithSpacesCharacterCount { get; set; }

        /// <summary>
        /// Gets the count of words.
        /// </summary>
        public int WordCount { get; private set; }
    }
}
