using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraTreeList.Columns;
using DevExpress.XtraTreeList.Nodes;
using DevExpress.XtraRichEdit.API.Native;
using System.Diagnostics;
using DevExpress.XtraBars.Ribbon;

namespace WindowsFormsApplication1 {
    public partial class Form1 : RibbonForm {
        public Form1() {
            InitializeComponent();            
        }

        void richEditControl1_DocumentLoaded(object sender, EventArgs e) {
            treeList1.Nodes.Clear();
            Dictionary<int, TreeListNode> parents = new Dictionary<int, TreeListNode>();
            foreach(Paragraph item in richEditControl1.Document.Paragraphs) {
                if(item.OutlineLevel == 0) continue;
                string description = richEditControl1.Document.GetText(item.Range);
                int level = item.OutlineLevel;

                TreeListNode newNode;
                if(parents.ContainsKey(level - 1))
                    newNode = treeList1.AppendNode(new object[] { description }, parents[level - 1]);
                else
                    newNode = treeList1.AppendNode(new object[] { description }, null);
                parents[level] = newNode;
                newNode.Tag = item.Range;  
            }
            treeList1.ExpandAll();
        }

        private void Form1_Load(object sender, EventArgs e) {
            TreeListColumn descriptionColumn = treeList1.Columns.Add();
            descriptionColumn.FieldName = "Description";
            descriptionColumn.VisibleIndex = 0;

            treeList1.OptionsBehavior.Editable = false;
            treeList1.FocusedNodeChanged += new DevExpress.XtraTreeList.FocusedNodeChangedEventHandler(treeList1_FocusedNodeChanged);

            richEditControl1.DocumentLoaded += new EventHandler(richEditControl1_DocumentLoaded);
            richEditControl1.LoadDocument("BookmarkTemplate.docx");
        }

        void treeList1_FocusedNodeChanged(object sender, DevExpress.XtraTreeList.FocusedNodeChangedEventArgs e) {
            BeginInvoke(new MethodInvoker(delegate {
                if(e.Node != null) {                                        
                    richEditControl1.Document.CaretPosition = (e.Node.Tag as DocumentRange).Start;
                    richEditControl1.Document.Selection = (e.Node.Tag as DocumentRange);
                    richEditControl1.ScrollToCaret();
                }
            }));            
        }
    }
}
