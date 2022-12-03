using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;

namespace RichEditResetPageNumbering {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            // Fill first section with text
            for (int i = 0; i < 5; i++) {
                richEditControl1.Document.AppendText(StringSample.SampleText);
            }

            // Add page numbering to the document
            Section firstSection = richEditControl1.Document.Sections[0];
            SubDocument doc = firstSection.BeginUpdateHeader();
            doc.InsertText(doc.CreatePosition(doc.Range.End.ToInt()), "Page ");
            doc.Fields.Create(doc.CreatePosition(doc.Range.End.ToInt()), "PAGE");
            doc.Fields.Update();
            firstSection.EndUpdateHeader(doc);

            // Add a new section and configure its page numbering
            richEditControl1.Document.AppendSection();
            richEditControl1.Document.Sections[richEditControl1.Document.Sections.Count - 1].PageNumbering.FirstPageNumber = 1;
            richEditControl1.Document.AppendText(StringSample.SampleText);
        }
    }
}