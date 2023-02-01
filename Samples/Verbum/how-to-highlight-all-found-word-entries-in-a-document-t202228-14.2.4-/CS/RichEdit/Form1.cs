using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Layout.Export;

namespace RichEdit {
    public partial class Form1 : Form {
        static Form1() {
        }
        public Form1() {
            InitializeComponent();

            this.richEditControl1.CustomMarkDraw += richEditControl1_CustomMarkDraw;
            this.richEditControl1.SearchFormShowing += richEditControl1_SearchFormShowing;
        }

        void richEditControl1_SearchFormShowing(object sender, SearchFormShowingEventArgs e) {
            e.Handled = true;
            CustomSearchForm form = new CustomSearchForm(e.ControllerParameters);
            e.DialogResult = form.ShowDialog();
        }

     

      
        void richEditControl1_CustomMarkDraw(object sender, RichEditCustomMarkDrawEventArgs e) {
            if (e.VisualInfoCollection != null) {
                Dictionary<DocumentRange, Rectangle> table = new Dictionary<DocumentRange, Rectangle>();
                foreach (CustomMarkVisualInfo viewInfo in e.VisualInfoCollection) {
                    DocumentRange range = viewInfo.UserData as DocumentRange;
                    if (!table.ContainsKey(range))
                        table.Add(range, Rectangle.Empty);

                    DevExpress.XtraRichEdit.API.Native.CustomMark mark = this.richEditControl1.Document.CustomMarks.GetByVisualInfo(viewInfo);
                    Rectangle bounds = table[range];
                    Rectangle newBounds;
                    if (mark.Position == range.Start)
                        newBounds = Rectangle.FromLTRB(viewInfo.Bounds.Left, viewInfo.Bounds.Top, bounds.Right, bounds.Bottom);
                    else
                        newBounds = Rectangle.FromLTRB(bounds.Left, bounds.Top, viewInfo.Bounds.Right, viewInfo.Bounds.Bottom);
                    table[range] = newBounds;
                }
                using (Brush brush = new SolidBrush(Color.FromArgb(100, Color.Yellow))) {
                    foreach (Rectangle rect in table.Values) {
                        e.Graphics.FillRectangle(brush, rect);
                    }
                }
            }
        }

       
        private void barButtonItem1_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) {
            

            DocumentRange[] ranges = this.richEditControl1.Document.FindAll("test", DevExpress.XtraRichEdit.API.Native.SearchOptions.WholeWord);
            if (ranges != null && ranges.Length > 0) {
                foreach (DocumentRange range in ranges) {
                    this.richEditControl1.Document.CustomMarks.Create(range.Start, range);
                    this.richEditControl1.Document.CustomMarks.Create(range.End, range);
                }
            }

        }
    }



}
