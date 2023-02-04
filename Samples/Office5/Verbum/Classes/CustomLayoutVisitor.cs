namespace Rizonesoft.Office.Verbum.Classes
{
    using DevExpress.XtraRichEdit.API.Layout;
    using DevExpress.XtraRichEdit.API.Native;


    public class CustomLayoutVisitor : LayoutVisitor
    {
        Document document;
        int colIndex;
        bool isFound;
        int rowIndex;

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

        public int ColIndex
        {
            get => colIndex;
            private set
            {
                if(colIndex == value)
                {
                    return;
                }

                colIndex = value;
            }
        }

        public bool IsFound
        {
            get => isFound;
            private set
            {
                if(isFound == value)
                {
                    return;
                }

                isFound = value;
            }
        }

        public int RowIndex
        {
            get => rowIndex;
            private set
            {
                if(rowIndex == value)
                {
                    return;
                }

                rowIndex = value;
            }
        }
    }
}
