using System;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;

namespace RichEditToggleRibbonCategories {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();
            richEditControl1.LoadDocument("Template.rtf");
        }

        private void richEditControl1_StartHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e) {
            headerFooterToolsRibbonPageCategory1.Visible = true;
            ribbonControl1.SelectedPage = headerFooterToolsDesignRibbonPage1;
        }

        private void richEditControl1_FinishHeaderFooterEditing(object sender, HeaderFooterEditingEventArgs e) {
            headerFooterToolsRibbonPageCategory1.Visible = false;
        }

        private void richEditControl1_SelectionChanged(object sender, EventArgs e) {
            tableToolsRibbonPageCategory1.Visible = richEditControl1.IsSelectionInTable();
            floatingPictureToolsRibbonPageCategory1.Visible = richEditControl1.IsFloatingObjectSelected;
        }
    }
}