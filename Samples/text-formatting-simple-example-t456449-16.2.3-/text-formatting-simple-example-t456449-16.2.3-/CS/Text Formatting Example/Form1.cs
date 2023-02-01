using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.Skins;
using DevExpress.LookAndFeel;
using DevExpress.UserSkins;
using DevExpress.XtraBars.Helpers;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Office.Utils;


namespace Text_Formatting_Example
{
    public partial class Form1 : RibbonForm
    {
        
        public Form1()
        {
            InitializeComponent();
            InitSkinGallery();
            InitializeRichEditControl();
            ribbonControl.SelectedPage = homeRibbonPage1;
            richEditControl.LoadDocument("Document.docx");
            FormatTitleChar(richEditControl.Document);
            FormatTitleParagraph(richEditControl.Document);
            LinkedAnnotationStyle(richEditControl.Document);
            CreateChapterStyle(richEditControl.Document);         
        }
        void InitSkinGallery()
        {
            SkinHelper.InitSkinGallery(rgbiSkins, true);
        }
        void InitializeRichEditControl() {}
        private void FormatTitleChar(Document document)
        {
            #region #FormatTitleCharacters
            //The target range is the first paragraph
            DocumentRange range = document.Paragraphs[0].Range;

            //Provide access to the character properties
            CharacterProperties titleFormatting = document.BeginUpdateCharacters(range);
            
            //Set the character size, font name and color
            titleFormatting.FontSize = 20;
            titleFormatting.FontName = "Helvetica";
            titleFormatting.ForeColor = Color.DarkBlue;

            document.EndUpdateCharacters(titleFormatting);
            #endregion #FormatTitleCharacters
        }

        private void FormatTitleParagraph(Document document)
        {
            #region #FormatTitleParagraph
            //The target range is the first paragraph
            DocumentRange titleParagraph = document.Paragraphs[0].Range;

            //Provide access to the paragraph options 
            ParagraphProperties titleParagraphFormatting = document.BeginUpdateParagraphs(titleParagraph);
            
            //Set the paragraph alignment
            titleParagraphFormatting.Alignment = ParagraphAlignment.Center;

            //Set left indent at 0.5".
            //Default unit is 1/300 of an inch (a document unit).
            titleParagraphFormatting.LeftIndent = Units.InchesToDocumentsF(0.5f);
            titleParagraphFormatting.SpacingAfter = Units.InchesToDocumentsF(0.3f);

            //Set tab stop at 1.5"
            TabInfoCollection tbiColl = titleParagraphFormatting.BeginUpdateTabs(true);
            TabInfo tbi = new TabInfo();
            tbi.Alignment = TabAlignmentType.Center;
            tbi.Position = Units.InchesToDocumentsF(1.5f);
            tbiColl.Add(tbi);
            titleParagraphFormatting.EndUpdateTabs(tbiColl);

            document.EndUpdateParagraphs(titleParagraphFormatting);
            #endregion #FormatTitleParagraph
        }

        private void CreateChapterStyle(Document document)
        {
            #region #ChapterStyle
            //Open the document for editing
            document.BeginUpdate();

            //Create a new paragraph style instance
            //and specify the required properties
            ParagraphStyle chapterStyle = document.ParagraphStyles.CreateNew();
            chapterStyle.Name = "MyTitleStyle";
            chapterStyle.ForeColor = Color.SteelBlue;
            chapterStyle.FontSize = 16;
            chapterStyle.FontName = "Segoe UI Semilight";
            chapterStyle.Alignment = ParagraphAlignment.Left;
            chapterStyle.SpacingBefore = Units.InchesToDocumentsF(0.2f);
            chapterStyle.SpacingAfter = Units.InchesToDocumentsF(0.2f);
            chapterStyle.OutlineLevel = 2;

            //Add the object to the document collection
            document.ParagraphStyles.Add(chapterStyle);

            //Finalize the editing
            document.EndUpdate();

            //Apply the created style to every chapter in the document 
            for (int i = 0; i < document.Paragraphs.Count; i++)
            {
                string var = document.GetText(document.Paragraphs[i].Range);
                if (var.Contains("Chapter "))
                {
                    document.Paragraphs[i].Style = chapterStyle;
                }
            }
            return;
            #endregion #ChapterStyle
        }

        private void LinkedAnnotationStyle(Document document)
        {
            #region #AnnotationStyle
            ParagraphStyle annotationStyle = document.ParagraphStyles["Annotation"];

            document.BeginUpdate();

            //Create a new paragraph style
            //and set the required settings
            annotationStyle = document.ParagraphStyles.CreateNew();
            annotationStyle.Name = "Annotation";
            annotationStyle.Alignment = ParagraphAlignment.Right;            
            annotationStyle.LineSpacingMultiplier = 1.5f;
            annotationStyle.FirstLineIndentType = ParagraphFirstLineIndent.Hanging;
            annotationStyle.FirstLineIndent = 3;
            document.ParagraphStyles.Add(annotationStyle);

            //Create a new character style and link it
            //to the custom paragraph style
            CharacterStyle annotationCharStyle = document.CharacterStyles.CreateNew();
            annotationCharStyle.Name = "AnnotationChar";
            document.CharacterStyles.Add(annotationCharStyle);
            annotationCharStyle.LinkedStyle = annotationStyle;

            //Specify the style options
            annotationCharStyle.Italic = true;
            annotationCharStyle.FontSize = 12;
            annotationCharStyle.FontName = "Segoe UI";
            annotationCharStyle.ForeColor = Color.Gray;
            document.EndUpdate();

            //Apply the created style to the fisrt paragraph of the annotation
            document.Paragraphs[1].Style = annotationStyle;

            //Apply the linked style to the range of the annotation's second paragraph
            CharacterProperties annotationProperties = document.BeginUpdateCharacters(document.Paragraphs[2].Range);
            annotationProperties.Style = annotationCharStyle;
            document.EndUpdateCharacters(annotationProperties);
            #endregion #AnnotationStyle
        }
    }
}