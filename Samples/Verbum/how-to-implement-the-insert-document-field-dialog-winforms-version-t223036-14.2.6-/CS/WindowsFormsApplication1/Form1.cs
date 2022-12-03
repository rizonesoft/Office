using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraBars.Ribbon;
using WindowsFormsApplication1.InsertFieldModules;

namespace WindowsFormsApplication1 {
    public partial class Form1 : RibbonForm {
        public Form1() {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e) {
            richEditControl1.RegisterInsertFieldDialogCommand(ribbonPageGroup1, null);
        }
    }
}
