//using DevExpress.XtraRichEdit.API.Layout;
//using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Portable;
using DevExpress.XtraRichEdit;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace LineNumberingExample {
    public partial class Form1 : Form {

        public Form1() {
            InitializeComponent();
            ribbonControl1.SelectedPage = exampleRibbonPage1;

            richEditControl1.DocumentLoaded += RichEditControl1_DocumentLoaded;
            richEditControl1.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
        }

        private void Form1_Load(object sender, EventArgs e) {
            richEditControl1.LoadDocument("Grimm.docx");
        }

        private void RichEditControl1_DocumentLoaded(object sender, EventArgs e) {
            richEditControl1.ActiveViewType = DevExpress.XtraRichEdit.RichEditViewType.Simple;
            #region #linenumbering
            this.richEditControl1.Views.SimpleView.Padding = new PortablePadding(60, 4, 4, 0);
            this.richEditControl1.Views.DraftView.Padding = new PortablePadding(60, 4, 4, 0);
            richEditControl1.Views.SimpleView.AllowDisplayLineNumbers = true;
            richEditControl1.Views.DraftView.AllowDisplayLineNumbers = true;

            richEditControl1.Document.Sections[0].LineNumbering.Start = 1;
            richEditControl1.Document.Sections[0].LineNumbering.CountBy = 2;
            richEditControl1.Document.Sections[0].LineNumbering.Distance = 75f;
           richEditControl1.Document.Sections[0].LineNumbering.RestartType = DevExpress.XtraRichEdit.API.Native.LineNumberingRestart.Continuous;

            richEditControl1.Document.CharacterStyles["Line Number"].FontName = "Courier";
            richEditControl1.Document.CharacterStyles["Line Number"].FontSize = 10;
            richEditControl1.Document.CharacterStyles["Line Number"].ForeColor = Color.DarkGray;
            richEditControl1.Document.CharacterStyles["Line Number"].Bold = true;
            #endregion #linenumbering
        }

        #region #BeforePagePaint
        private void RichEditControl1_BeforePagePaint(object sender, DevExpress.XtraRichEdit.BeforePagePaintEventArgs e) {
            if (e.CanvasOwnerType == DevExpress.XtraRichEdit.API.Layout.CanvasOwnerType.Printer) {
                return;
            }
            DevExpress.XtraRichEdit.API.Native.CharacterStyle style = richEditControl1.Document.CharacterStyles["Line Number"];
            MyPagePainter customPagePainter = new MyPagePainter(richEditControl1, SystemColors.Info, style);
            customPagePainter.LineNumberPadding = 60;
            e.Painter = customPagePainter;
        }
        #endregion #BeforePagePaint

        private void barCheckLineNumberBackColoring_CheckedChanged(object sender, DevExpress.XtraBars.ItemClickEventArgs e) {
            if (barCheckLineNumberBackColoring.Checked)
                richEditControl1.BeforePagePaint += RichEditControl1_BeforePagePaint;
            else
                richEditControl1.BeforePagePaint -= RichEditControl1_BeforePagePaint;
            richEditControl1.Refresh();
        }
        
        #region #DocumentFormatted
        private void DocumentLayout_DocumentFormatted(object sender, EventArgs e) {
            this.BeginInvoke((MethodInvoker)(() =>
            {
                if (this.Visible) {
                    MyLayoutVisitor visitor = new MyLayoutVisitor(richEditControl1.Document);
                    int pageCount = richEditControl1.DocumentLayout.GetFormattedPageCount();

                    for (int i = 0; i < pageCount; i++) {
                        visitor.Visit(richEditControl1.DocumentLayout.GetPage(i));
                    }
                    resultBarStaticItem.Caption = String.Format("Document has {0} lines", visitor.RowIndex);
                }
            }));
        }
        #endregion #DocumentFormatted

    }
}
