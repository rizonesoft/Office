using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using System.Drawing.Printing;
using DevExpress.Office.Utils;

namespace PageLayout
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            ribbonControl1.SelectedPage = pageLayoutRibbonPage1;
            richEditControl1.LoadDocument("Documents//Sections.rtf", DocumentFormat.Rtf);
            DivideIntoSections(richEditControl1.Document);
            ChangePageLayout();
            CreateColumns();
        }

        private void DivideIntoSections(Document document)
        {
            #region #InsertSections
            //Insert the first section:      
            DocumentPosition position = document.Paragraphs[12].Range.End;
            Section section = document.InsertSection(position);

            //Set the section break type. 
            //Press CTRL + SHIFT + 8 to view the section break
            section.StartType = SectionStartType.NextPage;

            //Insert an empty section at the end of the document:
            document.AppendSection();
            document.InsertDocumentContent(document.Range.End, "Documents//Last Section.docx", DocumentFormat.OpenXml);
            #endregion #InsertSections
        }

        private void ChangePageLayout()
        {
            #region #ChangeLayout
            SectionPage sectionPage1 = richEditControl1.Document.Sections[0].Page;

            //Change the paper kind and orientation of the first section:
            sectionPage1.PaperKind = PaperKind.A5;
            sectionPage1.Landscape = true;

            //Change margins of the second section:
            Section section2 = richEditControl1.Document.Sections[1];
            section2.StartType = SectionStartType.Continuous;

            section2.Margins.Bottom = Units.InchesToDocumentsF(0.5f);
            section2.Margins.Top = Units.InchesToDocumentsF(0.5f);
            section2.Margins.Left = Units.InchesToDocumentsF(0.5f);
            section2.Margins.Right = Units.InchesToDocumentsF(0.5f);
            #endregion #ChangeLayout

            #region #ZeroHeaderFooter
            //Delete header and footer:
            section2.Margins.HeaderOffset = 0;
            section2.Margins.FooterOffset = 0;
            #endregion #ZeroHeaderFooter
        }

        private void CreateColumns()
        {
            #region #Columns
            Section section = richEditControl1.Document.Sections[2];

            // Create equal width column layout:
            SectionColumnCollection sectionColumnsLayout = section.Columns.CreateUniformColumns(section.Page, Units.InchesToDocumentsF(0.2f), 3);

            // Set different column width:
            sectionColumnsLayout[0].Width = Units.InchesToDocumentsF(2f);
            sectionColumnsLayout[1].Width = Units.InchesToDocumentsF(2f);
            sectionColumnsLayout[2].Width = Units.InchesToDocumentsF(1f);

            // Apply layout to the document:
            section.Columns.SetColumns(sectionColumnsLayout);
            #endregion #Columns
        }

    }
}
