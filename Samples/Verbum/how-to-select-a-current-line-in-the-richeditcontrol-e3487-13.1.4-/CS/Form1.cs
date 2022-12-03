using System;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.API.Native;

namespace RichEditSelectSpecificLine {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e) {
            SelectCurrentLine();
        }

        private void SelectCurrentLine() {
            StartOfLineCommand startOfLineCommand = new StartOfLineCommand(richEditControl1);
            EndOfLineCommand endOfLineCommand = new EndOfLineCommand(richEditControl1);

            startOfLineCommand.Execute();

            int start = richEditControl1.Document.CaretPosition.ToInt();

            endOfLineCommand.Execute();

            int length = richEditControl1.Document.CaretPosition.ToInt() - start;

            DocumentRange range = richEditControl1.Document.CreateRange(start, length);
            DocumentRange range2 = richEditControl1.Document.CreateRange(start, length + 1);

            string text = richEditControl1.Document.GetText(range2);

            if (text.EndsWith(Environment.NewLine))
                richEditControl1.Document.Selection = range2;
            else
                richEditControl1.Document.Selection = range;
        }
    }
}