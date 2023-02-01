using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Layout.Export;

namespace RichEdit {
    class CustomSearchForm : DevExpress.XtraRichEdit.Forms.SearchTextForm {
        public CustomSearchForm(DevExpress.XtraRichEdit.Forms.SearchFormControllerParameters parameters)
            : base(parameters) {
            this.cbFndSearchString.EditValueChanged += cbFndSearchString_EditValueChanged;
            this.chbFndMatchCase.CheckedChanged += chbFndMatchCase_CheckedChanged;
            this.chbFndFindWholeWord.CheckedChanged += chbFndMatchCase_CheckedChanged;
            this.FormClosed += CustomSearchForm_FormClosed;
        }

        void chbFndMatchCase_CheckedChanged(object sender, EventArgs e) {
            this.cbFndSearchString.EditValue = null;
        }

        void CustomSearchForm_FormClosed(object sender, FormClosedEventArgs e) {
            ClearCustomMarks();
            this.cbFndSearchString.EditValueChanged -= cbFndSearchString_EditValueChanged;
            this.chbFndMatchCase.CheckedChanged -= chbFndMatchCase_CheckedChanged;
            this.chbFndFindWholeWord.CheckedChanged -= chbFndMatchCase_CheckedChanged;
        }
        void cbFndSearchString_EditValueChanged(object sender, EventArgs e) {
            ClearCustomMarks();
            if(this.cbFndSearchString.EditValue != null) {
                string text = this.cbFndSearchString.EditValue.ToString();
                if(!String.IsNullOrEmpty(text))
                    CreateCustomMarks(text);
            }
        }
        void CreateCustomMarks(string text) {
            DevExpress.XtraRichEdit.API.Native.SearchOptions options = DevExpress.XtraRichEdit.API.Native.SearchOptions.None;
            if(Controller.FindWholeWord)
                options |= DevExpress.XtraRichEdit.API.Native.SearchOptions.WholeWord;
            if(Controller.CaseSensitive)
                options |= DevExpress.XtraRichEdit.API.Native.SearchOptions.CaseSensitive;
            DocumentRange[] ranges = Control.Document.FindAll(text, options);
            if(ranges != null && ranges.Length > 0) {
                foreach(DocumentRange range in ranges) {
                    Control.Document.CustomMarks.Create(range.Start, range);
                    Control.Document.CustomMarks.Create(range.End, range);
                }
            }
        }
        void ClearCustomMarks() {
            for(int i = Control.Document.CustomMarks.Count - 1; i >= 0; i--) {
                DevExpress.XtraRichEdit.API.Native.CustomMark mark = Control.Document.CustomMarks[i];
                Control.Document.CustomMarks.Remove(mark);
            }
        }
    }
}
