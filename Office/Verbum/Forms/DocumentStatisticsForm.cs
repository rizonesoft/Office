using DevExpress.XtraRichEdit.API.Native;
using Rizonesoft.Office.Verbum.Classes;
using System;
using System.Linq;


namespace Rizonesoft.Office.Verbum.Forms
{
    public partial class DocumentStatisticsForm : DevExpress.XtraEditors.XtraForm
    {
        readonly SubDocument document;

        public DocumentStatisticsForm(SubDocument document, bool includeTextboxes)
        {
            InitializeComponent();
            this.document = document;
            this.chkIncludeTextboxes.Checked = includeTextboxes;
            CalculateStatistics();
        }

        void CalculateStatistics()
        {
            DocumentIterator iterator = new DocumentIterator(this.document, true);
            StaticsticsVisitor visitor = new StaticsticsVisitor(IncludeTextboxes);

            while(iterator.MoveNext())
            {
                iterator.Current.Accept(visitor);
            }

            this.lblNoSpacesCharactersCount.Text = String.Format("{0,5}", visitor.NoSpacesCharacterCount);
            this.lblWithSpacesCharactersCount.Text = String.Format("{0,5}", visitor.WithSpacesCharacterCount);
            this.lblWordsCount.Text = String.Format("{0,5}", visitor.WordCount);
            this.lblParagraphsCount.Text = String.Format("{0,5}", visitor.ParagraphCount);
        }

        void OnCloseClick(object sender, EventArgs e) { this.Close(); }

        public bool IncludeTextboxes { get { return chkIncludeTextboxes.Checked; } }
    }
}