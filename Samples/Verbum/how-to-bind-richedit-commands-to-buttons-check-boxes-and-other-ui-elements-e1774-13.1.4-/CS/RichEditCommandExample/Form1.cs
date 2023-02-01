using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
#region #usings
using DevExpress.Utils.Commands;
using DevExpress.XtraRichEdit.Commands;
#endregion #usings

namespace RichEditCommandExample {
    public partial class Form1 : Form {
        public Form1() {

            InitializeComponent();

            #region #commandbuttonusage
            btnUndo.Initialize(richEditControl1, RichEditCommandId.Undo);
            #endregion #commandbuttonusage

            #region #commandbuttonadapterusage
            CommandButtonAdapter redoAdapter = new CommandButtonAdapter();
            redoAdapter.Initialize(richEditControl1, RichEditCommandId.Undo);
            redoAdapter.Button = btnRedo;
            redoAdapter.CommandId = RichEditCommandId.Redo;
            redoAdapter.RichEditControl = richEditControl1;
            #endregion #commandbuttonadapterusage

            CommandCheckBoxAdapter fontBoldAdapter = new CommandCheckBoxAdapter();
            fontBoldAdapter.CommandId = RichEditCommandId.ToggleFontBold;
            fontBoldAdapter.RichEditControl = richEditControl1;
            fontBoldAdapter.CheckBox = chkToggleFontBold;
            
        }

        private void btnToggleReadOnly_Click(object sender, EventArgs e) {
            richEditControl1.ReadOnly = !richEditControl1.ReadOnly;
        }
    }
}