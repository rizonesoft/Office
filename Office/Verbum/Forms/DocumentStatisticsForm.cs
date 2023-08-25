using DevExpress.XtraRichEdit.API.Native;
using Rizonesoft.Office.Verbum.Classes;
using System;
using System.Threading;

namespace Rizonesoft.Office.Verbum.Forms
{
    /// <summary>
    /// Represents a form that shows the document statistics.
    /// </summary>
    public partial class DocumentStatisticsForm : DevExpress.XtraEditors.XtraForm
    {
        private readonly SubDocument _subDocument;

        public DocumentStatisticsForm(SubDocument document, bool includeTextboxes)
        {
            InitializeComponent();
            _subDocument = document ?? throw new ArgumentNullException(nameof(document));
            IncludeTextboxes = includeTextboxes;
            CalculateStatistics();
        }

        private void CalculateStatistics()
        {

            try
            {
                var iterator = new DocumentIterator(_subDocument, true);
                var visitor = new StaticsticsVisitor(IncludeTextboxes);

                while (iterator.MoveNext())
                {
                    iterator.Current?.Accept(visitor);
                }

                lblNoSpacesCharactersCount.Text = $@"{visitor.NoSpacesCharacterCount,5}";
                lblWithSpacesCharactersCount.Text = $@"{visitor.WithSpacesCharacterCount,5}";
                lblWordsCount.Text = $@"{visitor.WordCount,5}";
                lblParagraphsCount.Text = $@"{visitor.ParagraphCount,5}";
            }
            catch (OperationCanceledException)
            {
                // handle cancellation
            }
            catch (Exception ex)
            {
                // handle other exceptions
            }
        }

        /// <summary>
        /// Gets or sets a value indicating whether to include text boxes in the statistics.
        /// </summary>
        public bool IncludeTextboxes
        {
            get => chkIncludeTextboxes.Checked;
            set => chkIncludeTextboxes.Checked = value;
        }

        private void BtnClose_Click(object sender, EventArgs e)
        {
            Close();
        }

        private void ChkIncludeTextboxes_CheckStateChanged(object sender, EventArgs e)
        {
            CalculateStatistics();
        }
    }
}
