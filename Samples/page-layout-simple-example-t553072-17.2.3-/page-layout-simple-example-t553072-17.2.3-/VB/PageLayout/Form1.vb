Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports System.Drawing.Printing
Imports DevExpress.Office.Utils

Namespace PageLayout
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            ribbonControl1.SelectedPage = pageLayoutRibbonPage1
            richEditControl1.LoadDocument("Documents//Sections.rtf", DocumentFormat.Rtf)
            DivideIntoSections(richEditControl1.Document)
            ChangePageLayout()
            CreateColumns()
        End Sub

        Private Sub DivideIntoSections(ByVal document As Document)
'            #Region "#InsertSections"
            'Insert the first section:      
            Dim position As DocumentPosition = document.Paragraphs(12).Range.End
            Dim section As Section = document.InsertSection(position)

            'Set the section break type. 
            'Press CTRL + SHIFT + 8 to view the section break
            section.StartType = SectionStartType.NextPage

            'Insert an empty section at the end of the document:
            document.AppendSection()
            document.InsertDocumentContent(document.Range.End, "Documents//Last Section.docx", DocumentFormat.OpenXml)
'            #End Region ' #InsertSections
        End Sub

        Private Sub ChangePageLayout()
'            #Region "#ChangeLayout"
            Dim sectionPage1 As SectionPage = richEditControl1.Document.Sections(0).Page

            'Change the paper kind and orientation of the first section:
            sectionPage1.PaperKind = PaperKind.A5
            sectionPage1.Landscape = True

            'Change margins of the second section:
            Dim section2 As Section = richEditControl1.Document.Sections(1)
            section2.StartType = SectionStartType.Continuous

            section2.Margins.Bottom = Units.InchesToDocumentsF(0.5F)
            section2.Margins.Top = Units.InchesToDocumentsF(0.5F)
            section2.Margins.Left = Units.InchesToDocumentsF(0.5F)
            section2.Margins.Right = Units.InchesToDocumentsF(0.5F)
'            #End Region ' #ChangeLayout

'            #Region "#ZeroHeaderFooter"
            'Delete header and footer:
            section2.Margins.HeaderOffset = 0
            section2.Margins.FooterOffset = 0
'            #End Region ' #ZeroHeaderFooter
        End Sub

        Private Sub CreateColumns()
'            #Region "#Columns"
            Dim section As Section = richEditControl1.Document.Sections(2)

            ' Create equal width column layout:
            Dim sectionColumnsLayout As SectionColumnCollection = section.Columns.CreateUniformColumns(section.Page, Units.InchesToDocumentsF(0.2F), 3)

            ' Set different column width:
            sectionColumnsLayout(0).Width = Units.InchesToDocumentsF(2F)
            sectionColumnsLayout(1).Width = Units.InchesToDocumentsF(2F)
            sectionColumnsLayout(2).Width = Units.InchesToDocumentsF(1F)

            ' Apply layout to the document:
            section.Columns.SetColumns(sectionColumnsLayout)
'            #End Region ' #Columns
        End Sub

    End Class
End Namespace
