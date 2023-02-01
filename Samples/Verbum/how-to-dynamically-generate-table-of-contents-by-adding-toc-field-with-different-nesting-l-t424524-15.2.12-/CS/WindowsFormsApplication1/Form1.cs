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
using DevExpress.XtraRichEdit.API.Native;

namespace WindowsFormsApplication1 {
    public partial class Form1 : RibbonForm {
        public Form1() {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e) {
            richEditControl1.CreateNewDocument();
        }

        private void simpleButton1_Click(object sender, EventArgs e) {
            if(textEdit1.Text.Trim() == "" || memoEdit1.Text.Trim() == "") return;

            bool isTocInserted = false;
            for(int i = 0; i < richEditControl1.Document.Fields.Count; i++) {
                Field currentField = richEditControl1.Document.Fields[i];
                string fieldCode = richEditControl1.Document.GetText(currentField.CodeRange);
                if(fieldCode.Contains("TOC")) {
                    isTocInserted = true;
                    break;
                }
            }

            if(isTocInserted) {
                TOCContentHelper.AppendNewDocumentFragment(textEdit1.Text.Trim(), memoEdit1.Text.Trim(), richEditControl1.Document, Convert.ToInt32(spinEdit1.EditValue), true);
            }
            else {
                TOCContentHelper.InsertTOC("\\h", richEditControl1.Document);
                TOCContentHelper.AppendNewDocumentFragment(textEdit1.Text.Trim(), memoEdit1.Text.Trim(), richEditControl1.Document, Convert.ToInt32(spinEdit1.EditValue), false);
                TOCContentHelper.InsertPageNumber(richEditControl1.Document);
            }
            richEditControl1.Document.Fields.Update();
            TOCContentHelper.UpdateTOCFieldFormatting(richEditControl1.Document);
        }
    }
}
