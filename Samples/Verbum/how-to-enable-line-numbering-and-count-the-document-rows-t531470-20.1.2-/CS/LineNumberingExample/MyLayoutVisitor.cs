using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using System;

namespace LineNumberingExample {
    #region #MyLayoutVisitor
    public class MyLayoutVisitor : LayoutVisitor {
        Document document;

        public int RowIndex { get; private set; }

        public MyLayoutVisitor(Document doc) {
            this.document = doc;
            RowIndex = 0;
        }

        protected override void VisitRow(LayoutRow row) {
            RowIndex++;
            base.VisitRow(row);
        }
    }
    #endregion #MyLayoutVisitor
}