namespace Rizonesoft.Office.Verbum.Forms
{
    using DevExpress.XtraRichEdit.API.Native;
    using Rizonesoft.Office.Verbum.Classes;
    using System;

    public partial class DocumentStatisticsForm : DevExpress.XtraEditors.XtraForm
    {
        readonly SubDocument subDocument;

        public DocumentStatisticsForm(SubDocument document, bool includeTextboxes)
        {
            InitializeComponent();
            subDocument = document;
            chkIncludeTextboxes.Checked = includeTextboxes;
            CalculateStatistics();
        }

        void CalculateStatistics()
        {
            DocumentIterator iterator = new(subDocument, true);
            StaticsticsVisitor visitor = new(IncludeTextboxes);

            while(iterator.MoveNext())
            {
                iterator.Current.Accept(visitor);
            }

            lblNoSpacesCharactersCount.Text = $"{visitor.NoSpacesCharacterCount,5}";
            lblWithSpacesCharactersCount.Text = $"{visitor.WithSpacesCharacterCount,5}";
            lblWordsCount.Text = $"{visitor.WordCount,5}";
            lblParagraphsCount.Text = $"{visitor.ParagraphCount,5}";
        }

        public bool IncludeTextboxes { get => chkIncludeTextboxes.Checked; set
            {
                if (chkIncludeTextboxes.Checked == value)
                {
                    return;
                }

                chkIncludeTextboxes.Checked = value;
            }
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