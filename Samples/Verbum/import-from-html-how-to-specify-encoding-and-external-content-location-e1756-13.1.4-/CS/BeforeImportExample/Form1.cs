using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
#region #usings
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Import;
#endregion #usings

namespace BeforeImport {
    public partial class Form1 : Form {
        string imgPath;
        Encoding cur_Encoding;

        public Form1() {
            InitializeComponent();
            labelControl1.Text = "Use radio buttons to switch folder containing images";
            labelControl2.Text = "Select correct encoding and press the button to load Cyrillic text";
            LoadSampleHTML();
            InitEncodings();
        }

        private void InitEncodings() {
            cmbEncodings.Properties.Items.BeginUpdate();
            cmbEncodings.Properties.Items.Add("koi8-r");
            cmbEncodings.Properties.Items.Add("koi8-u");
            cmbEncodings.Properties.Items.Add("windows-1251");
            cmbEncodings.Properties.Items.Add("cp866");
            cmbEncodings.Properties.Items.EndUpdate();


        }

        void LoadSampleHTML() {
            imgPath = rgImgPath.EditValue.ToString();
            richEditControl1.LoadDocument("sample.htm", DocumentFormat.Html);
        }

        void LoadSampleText() {
            if(cmbEncodings.SelectedItem == null)
                cur_Encoding = Encoding.Unicode;
            else
                cur_Encoding = Encoding.GetEncoding(cmbEncodings.SelectedItem.ToString());
            richEditControl2.LoadDocument("TerribleRevengeKOI8R.txt", DocumentFormat.PlainText);
        }

        #region #beforeimport
        private void richEditControl1_BeforeImport(object sender, BeforeImportEventArgs e) {
            if(e.DocumentFormat == DocumentFormat.Html) {
                e.Options.SourceUri = "file:///" + Application.StartupPath + imgPath;
            }
        }
        private void richEditControl2_BeforeImport(object sender, BeforeImportEventArgs e) {
            if(e.DocumentFormat == DocumentFormat.PlainText) {
                ((PlainTextDocumentImporterOptions)e.Options).Encoding = cur_Encoding;
            }
        }
        #endregion #beforeimport
        private void rgImgPath_SelectedIndexChanged(object sender, EventArgs e) {
            LoadSampleHTML();
        }

        private void btnLoadRTF_Click(object sender, EventArgs e) {
            LoadSampleText();
        }

    }
}