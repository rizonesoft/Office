using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit;

namespace WindowsFormsApplication1 {
    public partial class Form1 : RibbonForm {
        public Form1() {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e) {
            richEditControl1.LoadDocument("testDocument.rtf", DocumentFormat.Rtf);
            UpdateButtonsVisibility(0);
        }

        int GetCurrentBookMarkIndex(DevExpress.XtraRichEdit.API.Native.Document currentDoc) {
            for(int i = 0; i < currentDoc.Bookmarks.Count; i++) {
                if(currentDoc.Bookmarks[i].Range.Contains(currentDoc.CaretPosition) || currentDoc.Bookmarks[i].Range.End.ToInt() == currentDoc.CaretPosition.ToInt()) {
                    return i;
                }
            }
            return -1;        
        }

        private void barButtonItemPrev_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) {
            int currentBookMarkIndex = GetCurrentBookMarkIndex(richEditControl1.Document);
            if(currentBookMarkIndex > 0) {
                richEditControl1.Document.Bookmarks.Select(richEditControl1.Document.Bookmarks[currentBookMarkIndex - 1]);
            }
            UpdateButtonsVisibility(currentBookMarkIndex - 1);
        }

        private void barButtonItemNext_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) {
            int currentBookMarkIndex = GetCurrentBookMarkIndex(richEditControl1.Document);
            if(currentBookMarkIndex != -1 && currentBookMarkIndex < richEditControl1.Document.Bookmarks.Count - 1) {
                richEditControl1.Document.Bookmarks.Select(richEditControl1.Document.Bookmarks[currentBookMarkIndex + 1]);
            }
            UpdateButtonsVisibility(currentBookMarkIndex + 1);
        }

        void UpdateButtonsVisibility(int newBookMarkIndex) {
            barButtonItemNext.Enabled = newBookMarkIndex < (richEditControl1.Document.Bookmarks.Count - 1);
            barButtonItemPrev.Enabled = newBookMarkIndex > 0;
        }
    }
}
