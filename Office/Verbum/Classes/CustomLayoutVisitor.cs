using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;

namespace Rizonesoft.Office.Verbum.Classes
{
    /// <summary>
    /// Represents a custom layout visitor for a document.
    /// </summary>
    public class CustomLayoutVisitor : LayoutVisitor
    {
        private Document Document { get; }
        public int ColIndex { get; private set; }
        public bool IsFound { get; private set; }
        public int RowIndex { get; private set; }

        /// <summary>
        /// Initializes a new instance of the CustomLayoutVisitor class.
        /// </summary>
        /// <param name="doc">The document to visit.</param>
        public CustomLayoutVisitor(Document doc)
        {
            Document = doc;
            Reset();
        }

        /// <summary>
        /// Visits a row in the layout of the document.
        /// </summary>
        /// <param name="row">The layout row to visit.</param>
        protected override void VisitRow(LayoutRow row)
        {
            if (!IsFound)
            {
                RowIndex++;
                if (row.Range.Contains(Document.CaretPosition.ToInt()))
                {
                    IsFound = true;
                    ColIndex = Document.CaretPosition.ToInt() - row.Range.Start;
                }
            }

            base.VisitRow(row);
        }

        /// <summary>
        /// Resets the visitor to its initial state.
        /// </summary>
        public void Reset()
        {
            RowIndex = 0;
            ColIndex = 0;
            IsFound = false;
        }
    }
}