using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;

namespace WindowsFormsApplication1
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.SelectionChanged += richEditControl1_SelectionChanged;
            richEditControl1.DocumentLayout.DocumentFormatted += DocumentLayout_DocumentFormatted;
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            richEditControl1.LoadDocument("SampleDocument.rtf");
        }

        void DocumentLayout_DocumentFormatted(object sender, EventArgs e)
        {
            this.BeginInvoke((MethodInvoker)(() => 
                {
                    if (this.Visible)
                    {
                        CustomLayoutVisitor visitor = new CustomLayoutVisitor(richEditControl1.Document);
                        List<PageLayoutInfo> list = richEditControl1.ActiveView.GetVisiblePageLayoutInfos();

                        for (int i = 0; i < list.Count; i++)
                        {
                            visitor.Reset();
                            visitor.Visit(richEditControl1.DocumentLayout.GetPage(list[i].PageIndex));
                        }

                        UpdateStaticItems(richEditControl1);
                    }
                }));
        }

        void richEditControl1_SelectionChanged(object sender, EventArgs e)
        {            
            RichEditControl richEdit = sender as RichEditControl;

            if (richEdit.DocumentLayout.IsDocumentFormattingCompleted)
            {
                int currentPageIndex = richEdit.Views.PrintLayoutView.CurrentPageIndex;
                barStaticItem3.Caption = string.Format("Current page: {0}", currentPageIndex + 1);

                CustomLayoutVisitor visitor = new CustomLayoutVisitor(richEdit.Document);

                for (int i = 0; i < richEdit.DocumentLayout.GetPageCount(); i++)
                {
                    visitor.Reset();
                    LayoutPage page = richEdit.DocumentLayout.GetPage(i);
                    visitor.Visit(page);

                    if (visitor.IsFound)
                        break;
                }

                if (visitor.IsFound)
                {
                    barStaticItem4.Caption = string.Format("Current line: {0}", visitor.RowIndex);
                    barStaticItem5.Caption = string.Format("Current column: {0}", visitor.ColIndex);
                }
            }
        }  

        private int GetWordCount(RichEditControl richEdit)
        {
            DocumentIterator iterator = new DocumentIterator(richEdit.Document, true);
            StaticsticsVisitor visitor = new StaticsticsVisitor();
            while (iterator.MoveNext())
                iterator.Current.Accept(visitor);

            return visitor.WordCount;
        }

        private int GetPageCount(RichEditControl richEdit)
        {
            return richEdit.DocumentLayout.GetPageCount();
        }

        private void UpdateStaticItems(RichEditControl richEdit)
        {
            barStaticItem1.Caption = string.Format("Page count: {0}", GetPageCount(richEdit));
            barStaticItem2.Caption = string.Format("Word count: {0}", GetWordCount(richEdit));   
        }
        
    }    
}
