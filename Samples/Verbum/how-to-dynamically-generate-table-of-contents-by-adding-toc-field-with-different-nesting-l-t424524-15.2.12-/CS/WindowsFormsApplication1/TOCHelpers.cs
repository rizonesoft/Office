using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using DevExpress.Office;
using DevExpress.XtraRichEdit.API.Native;

namespace WindowsFormsApplication1 {
    public static class TOCContentHelper {
 
        public static void AppendNewDocumentFragment(string headerText, string fragmentText, Document doc, int headerLevel, bool isPageBreakRequired) {
            if(headerLevel == 1 && isPageBreakRequired) doc.AppendText(Characters.PageBreak.ToString());

            Paragraph headerParagraph = doc.Paragraphs.Append();
            SetParagraphStyleSettings(doc, headerParagraph, headerLevel);
            DocumentRange headerRange = doc.AppendText(headerText);
            Paragraph singleParagraph = doc.Paragraphs.Append();
            SetParagraphStyleSettings(doc, singleParagraph, 0);
            ChangeHeaderCharacterProperties(doc, headerRange, headerLevel);
            doc.AppendText(fragmentText);            
        }

        static void ChangeHeaderCharacterProperties(Document doc, DocumentRange headerRange, int headerLevel) {
            CharacterProperties cp = doc.BeginUpdateCharacters(headerRange);
            cp.ForeColor = Color.Blue;

            if(headerLevel == 1) {
                cp.Bold = true;
                cp.FontSize = 16;
            }
            if(headerLevel == 2) {
                cp.Bold = true;
                cp.FontSize = 12;
            }
            if(headerLevel == 3) {
                cp.Bold = false;
                cp.FontSize = 12;
            }
            doc.EndUpdateCharacters(cp);
        }

        static void SetParagraphStyleSettings(Document doc, Paragraph currentParagraph, int level) {
            if(level > 0) {
                string styleName = "Paragraph Level " + level.ToString();
                ParagraphStyle paragraphStyle = doc.ParagraphStyles[styleName];

                if(paragraphStyle == null) {
                    paragraphStyle = doc.ParagraphStyles.CreateNew();
                    paragraphStyle.Name = styleName;
                    paragraphStyle.Parent = doc.ParagraphStyles["Normal"];
                    paragraphStyle.OutlineLevel = level;
                    doc.ParagraphStyles.Add(paragraphStyle);
                }
                currentParagraph.Style = paragraphStyle;
            }
            else {
                currentParagraph.Style = doc.ParagraphStyles["Normal"];
            }
        }

        public static void InsertPageNumber(Document someDocument) {
            for(int i = 1; i < someDocument.Sections.Count; i++) {
                Section currentSection = someDocument.Sections[i];

                SubDocument myFooter = currentSection.BeginUpdateFooter();
                DocumentRange range = myFooter.InsertText(myFooter.CreatePosition(0), " PAGE NUMBER ");
                Field fld = myFooter.Fields.Create(range.End, "PAGE");
                myFooter.Fields.Update();

                ParagraphProperties pp = myFooter.BeginUpdateParagraphs(myFooter.Range);
                pp.Alignment = ParagraphAlignment.Right;
                myFooter.EndUpdateParagraphs(pp);

                currentSection.EndUpdateFooter(myFooter);
            }
        }

        public static void InsertTOC(string switches, Document doc) {
            DocumentRange documentHeader = doc.InsertText(doc.Range.End, "INSTALL GUIDE\r\n");
            ParagraphProperties pp = doc.BeginUpdateParagraphs(documentHeader);
            pp.Reset();
            pp.Alignment = ParagraphAlignment.Center;
            doc.EndUpdateParagraphs(pp);

            CharacterProperties cp = doc.BeginUpdateCharacters(documentHeader);
            cp.ForeColor = Color.Red;
            cp.Bold = true;
            cp.FontSize = 16;
            doc.EndUpdateCharacters(cp);


            Field field = doc.Fields.Create(documentHeader.End, "TOC " + switches);
            doc.InsertSection(field.Range.End);
            field.Update();
        }

        public static void UpdateTOCFieldFormatting(Document doc) {
            if(doc.ParagraphStyles["TOC 1"] != null) {
                doc.ParagraphStyles["TOC 1"].Bold = true;
                doc.ParagraphStyles["TOC 1"].FontSize = 16;
                doc.ParagraphStyles["TOC 1"].LeftIndent = 0f;
            }
            if(doc.ParagraphStyles["TOC 2"] != null) {
                doc.ParagraphStyles["TOC 2"].Bold = true;
                doc.ParagraphStyles["TOC 2"].FontSize = 12;
                doc.ParagraphStyles["TOC 2"].LeftIndent = 0f;
            }
            if(doc.ParagraphStyles["TOC 3"] != null) {
                doc.ParagraphStyles["TOC 3"].Bold = false;
                doc.ParagraphStyles["TOC 3"].FontSize = 12;
                doc.ParagraphStyles["TOC 3"].LeftIndent = 0f;
            }
        }
    }
}
