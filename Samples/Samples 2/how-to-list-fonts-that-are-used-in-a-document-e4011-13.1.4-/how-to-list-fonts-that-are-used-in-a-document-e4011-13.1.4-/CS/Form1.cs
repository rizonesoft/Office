using System;
using System.Collections.Generic;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;

namespace RichEditCheckFonts {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            richEditControl1.LoadDocument("test.rtf");
        }

        private void button1_Click(object sender, EventArgs e) {
            List<string> fonts = GetUsedFonts();

            MessageBox.Show(string.Join(", ", fonts.ToArray()), "Used fonts");
        }

        private List<string> GetUsedFonts() {
            List<string> fonts = new List<string>();
            
            Document document = richEditControl1.Document;

            document.BeginUpdate();
            int length = richEditControl1.Document.Range.Length;

            for (int i = 0; i <= length - 2; i++) {
                DocumentRange range = document.CreateRange(i, 1);
                CharacterProperties cp = document.BeginUpdateCharacters(range);

                if (!fonts.Contains(cp.FontName))
                    fonts.Add(cp.FontName);

                document.EndUpdateCharacters(cp);
            }

            document.EndUpdate();

            return fonts;
        }
    }
}