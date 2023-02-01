using System;
using System.IO;
using System.Windows.Forms;

namespace RichEditBBCExporter {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            BBCodeDocumentExporter.Register(richEditControl1);

            richEditControl1.LoadDocument("test.html");
        }

        private void button1_Click(object sender, EventArgs e) {
            richEditControl1.SaveDocument("test.bbc", BBCodeDocumentFormat.Id);
        }
    }
}