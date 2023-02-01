using System;
using System.Drawing;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Portable.Input;

namespace RichEditTOCGeneration {
    public partial class Form1 : Form {
        public Document Document { get { return richEditControl1.Document; } }
        private delegate void TOCEntryFound(DocumentPosition location, int level);

        public Form1() {
            InitializeComponent();
            richEditControl1.Options.Hyperlinks.ModifierKeys = PortableKeys.None;
            btnLoadTemplate_Click(btnLoadTemplate, EventArgs.Empty);
        }

        private void btnLoadTemplate_Click(object sender, EventArgs e) {
            richEditControl1.LoadDocument("Employees.rtf");
        }

        private void btnShowAllFieldCodes_Click(object sender, EventArgs e) {
            new ShowAllFieldCodesCommand(richEditControl1).Execute();
        }

        private void btnStyles_Click(object sender, EventArgs e) {
            Document.BeginUpdate();
            ApplyStyles();
            InsertTOC("\\h", true);
            Document.EndUpdate();
        }

        private void btnOutlineLevels_Click(object sender, EventArgs e) {
            Document.BeginUpdate();
            AssignOutlineLevels();
            InsertTOC("\\h \\u", true);
            Document.EndUpdate();
        }

        private void btnTCFields_Click(object sender, EventArgs e) {
            Document.BeginUpdate();
            AddTCFields();
            InsertTOC("\\h \\f defaultGroup", true);
            Document.Fields.Update();
            Document.EndUpdate();
        }

        private void ApplyStyles() {
            SearchForTOCEntries(delegate(DocumentPosition location, int level) {
                Document.Paragraphs.Get(location).Style = GetStyleForLevel(level);
            });
        }

        private void AssignOutlineLevels() {
            SearchForTOCEntries(delegate(DocumentPosition location, int level) {
                Document.Paragraphs.Get(location).OutlineLevel = level;
            });
        }

        private void AddTCFields() {
            SearchForTOCEntries(delegate(DocumentPosition location, int level) {
                Document.Fields.Create(location, string.Format("TC \"{0}\" \\f {1} \\l {2}", 
                    Document.GetText(Document.Paragraphs.Get(location).Range), "defaultGroup", level));
            });
        }

        private void SearchForTOCEntries(TOCEntryFound callback) {
            for (int i = 0; i < Document.Paragraphs.Count; i++) {
                DocumentRange range = Document.CreateRange(Document.Paragraphs[i].Range.Start, 1);
                CharacterProperties cp = Document.BeginUpdateCharacters(range);
                int level = 0;

                if (cp.FontSize.Equals(14f))
                    level = 1;
                if (cp.FontSize.Equals(13f))
                    level = 2;
                if (cp.FontSize.Equals(11f))
                    level = 3;

                Document.EndUpdateCharacters(cp);

                if (level != 0)
                    callback(range.Start, level);
            }
        }

        private void InsertTOC(string switches, bool insertHeading) {
            if (insertHeading)
                InsertContentHeading();

            Field field = Document.Fields.Create(Document.Paragraphs[(insertHeading ? 1 : 0)].Range.Start, "TOC " + switches);
            CharacterProperties cp = Document.BeginUpdateCharacters(field.Range);
            cp.Bold = false;
            cp.FontSize = 12;
            cp.ForeColor = Color.Blue;
            Document.EndUpdateCharacters(cp);
            Document.InsertSection(field.Range.End);
            field.Update();
        }

        private void InsertContentHeading() {
            DocumentRange range = Document.InsertText(Document.Range.Start, "Contents\r\n");
            CharacterProperties cp = Document.BeginUpdateCharacters(range);
            cp.FontSize = 18;
            cp.ForeColor = Color.DarkBlue;
            Document.EndUpdateCharacters(cp);
            Document.Paragraphs[0].Alignment = ParagraphAlignment.Center;
            Document.Paragraphs[0].Style = Document.ParagraphStyles["Normal"];
            Document.Paragraphs[0].OutlineLevel = 0;
        }

        private ParagraphStyle GetStyleForLevel(int level) {
            string styleName = "Paragraph Level " + level.ToString();
            ParagraphStyle paragraphStyle = Document.ParagraphStyles[styleName];

            if (paragraphStyle == null) {
                paragraphStyle = Document.ParagraphStyles.CreateNew();
                paragraphStyle.Name = styleName;
                paragraphStyle.Parent = Document.ParagraphStyles["Normal"];
                paragraphStyle.OutlineLevel = level;
                Document.ParagraphStyles.Add(paragraphStyle);
            }

            return paragraphStyle;
        }
    }
}