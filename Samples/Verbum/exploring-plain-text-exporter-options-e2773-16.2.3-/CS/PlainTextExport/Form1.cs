using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using System.IO;
using DevExpress.XtraRichEdit.Export;

namespace PlainTextExport
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("sample.docx", DocumentFormat.OpenXml);
            #region #PlainTextDocumentExporterOptions
            richEditControl1.Options.Export.PlainText.ExportHiddenText = true;
            richEditControl1.Options.Export.PlainText.FieldCodeStartMarker = "[<";
            richEditControl1.Options.Export.PlainText.FieldCodeEndMarker = ">";
            richEditControl1.Options.Export.PlainText.FieldResultEndMarker = "]";
            richEditControl1.Options.Export.PlainText.Encoding = Encoding.GetEncoding("Windows-1252");
            #endregion #PlainTextDocumentExporterOptions
        }

        private void btnExport_Click(object sender, EventArgs e)
        {
            MemoryStream stream = new MemoryStream();
            richEditControl1.SaveDocument(stream, DocumentFormat.PlainText);
            stream.Position = 0;
            StreamReader sr = new StreamReader(stream, richEditControl1.Options.Export.PlainText.Encoding);
            memoEdit1.Text = sr.ReadToEnd();
        }
    }
}