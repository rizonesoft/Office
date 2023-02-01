Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.Skins
Imports DevExpress.LookAndFeel
Imports DevExpress.UserSkins
Imports DevExpress.XtraBars.Helpers
Imports DevExpress.XtraBars
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.Office.Utils


Namespace Text_Formatting_Example
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            InitSkinGallery()
            InitializeRichEditControl()
            ribbonControl.SelectedPage = homeRibbonPage1
            richEditControl.LoadDocument("Document.docx")
            FormatTitleChar(richEditControl.Document)
            FormatTitleParagraph(richEditControl.Document)
            LinkedAnnotationStyle(richEditControl.Document)
            CreateChapterStyle(richEditControl.Document)
        End Sub
        Private Sub InitSkinGallery()
            SkinHelper.InitSkinGallery(rgbiSkins, True)
        End Sub
        Private Sub InitializeRichEditControl()
        End Sub
        Private Sub FormatTitleChar(ByVal document As Document)
'            #Region "#FormatTitleCharacters"
            'The target range is the first paragraph
            Dim range As DocumentRange = document.Paragraphs(0).Range

            'Provide access to the character properties
            Dim titleFormatting As CharacterProperties = document.BeginUpdateCharacters(range)

            'Set the character size, font name and color
            titleFormatting.FontSize = 20
            titleFormatting.FontName = "Helvetica"
            titleFormatting.ForeColor = Color.DarkBlue

            document.EndUpdateCharacters(titleFormatting)
'            #End Region ' #FormatTitleCharacters
        End Sub

        Private Sub FormatTitleParagraph(ByVal document As Document)
'            #Region "#FormatTitleParagraph"
            'The target range is the first paragraph
            Dim titleParagraph As DocumentRange = document.Paragraphs(0).Range

            'Provide access to the paragraph options 
            Dim titleParagraphFormatting As ParagraphProperties = document.BeginUpdateParagraphs(titleParagraph)

            'Set the paragraph alignment
            titleParagraphFormatting.Alignment = ParagraphAlignment.Center

            'Set left indent at 0.5".
            'Default unit is 1/300 of an inch (a document unit).
            titleParagraphFormatting.LeftIndent = Units.InchesToDocumentsF(0.5F)
            titleParagraphFormatting.SpacingAfter = Units.InchesToDocumentsF(0.3F)

            'Set tab stop at 1.5"
            Dim tbiColl As TabInfoCollection = titleParagraphFormatting.BeginUpdateTabs(True)
            Dim tbi As New TabInfo()
            tbi.Alignment = TabAlignmentType.Center
            tbi.Position = Units.InchesToDocumentsF(1.5F)
            tbiColl.Add(tbi)
            titleParagraphFormatting.EndUpdateTabs(tbiColl)

            document.EndUpdateParagraphs(titleParagraphFormatting)
'            #End Region ' #FormatTitleParagraph
        End Sub

        Private Sub CreateChapterStyle(ByVal document As Document)
'            #Region "#ChapterStyle"
            'Open the document for editing
            document.BeginUpdate()

            'Create a new paragraph style instance
            'and specify the required properties
            Dim chapterStyle As ParagraphStyle = document.ParagraphStyles.CreateNew()
            chapterStyle.Name = "MyTitleStyle"
            chapterStyle.ForeColor = Color.SteelBlue
            chapterStyle.FontSize = 16
            chapterStyle.FontName = "Segoe UI Semilight"
            chapterStyle.Alignment = ParagraphAlignment.Left
            chapterStyle.SpacingBefore = Units.InchesToDocumentsF(0.2F)
            chapterStyle.SpacingAfter = Units.InchesToDocumentsF(0.2F)
            chapterStyle.OutlineLevel = 2

            'Add the object to the document collection
            document.ParagraphStyles.Add(chapterStyle)

            'Finalize the editing
            document.EndUpdate()

            'Apply the created style to every chapter in the document 
            For i As Integer = 0 To document.Paragraphs.Count - 1
                Dim var As String = document.GetText(document.Paragraphs(i).Range)
                If var.Contains("Chapter ") Then
                    document.Paragraphs(i).Style = chapterStyle
                End If
            Next i
            Return
'            #End Region ' #ChapterStyle
        End Sub

        Private Sub LinkedAnnotationStyle(ByVal document As Document)
'            #Region "#AnnotationStyle"
            Dim annotationStyle As ParagraphStyle = document.ParagraphStyles("Annotation")

            document.BeginUpdate()

            'Create a new paragraph style
            'and set the required settings
            annotationStyle = document.ParagraphStyles.CreateNew()
            annotationStyle.Name = "Annotation"
            annotationStyle.Alignment = ParagraphAlignment.Right
            annotationStyle.LineSpacingMultiplier = 1.5F
            annotationStyle.FirstLineIndentType = ParagraphFirstLineIndent.Hanging
            annotationStyle.FirstLineIndent = 3
            document.ParagraphStyles.Add(annotationStyle)

            'Create a new character style and link it
            'to the custom paragraph style
            Dim annotationCharStyle As CharacterStyle = document.CharacterStyles.CreateNew()
            annotationCharStyle.Name = "AnnotationChar"
            document.CharacterStyles.Add(annotationCharStyle)
            annotationCharStyle.LinkedStyle = annotationStyle

            'Specify the style options
            annotationCharStyle.Italic = True
            annotationCharStyle.FontSize = 12
            annotationCharStyle.FontName = "Segoe UI"
            annotationCharStyle.ForeColor = Color.Gray
            document.EndUpdate()

            'Apply the created style to the fisrt paragraph of the annotation
            document.Paragraphs(1).Style = annotationStyle

            'Apply the linked style to the range of the annotation's second paragraph
            Dim annotationProperties As CharacterProperties = document.BeginUpdateCharacters(document.Paragraphs(2).Range)
            annotationProperties.Style = annotationCharStyle
            document.EndUpdateCharacters(annotationProperties)
'            #End Region ' #AnnotationStyle
        End Sub
    End Class
End Namespace