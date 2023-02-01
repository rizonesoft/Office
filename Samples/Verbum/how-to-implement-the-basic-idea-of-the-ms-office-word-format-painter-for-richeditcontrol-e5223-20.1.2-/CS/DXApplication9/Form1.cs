// Developer Express Code Central Example:
// How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
// 
// This example demonstrates how to copy the characters and paragraphs properties
// and apply formatting to the selected text. Try the Format Painter button on the
// ribbon Home tab.
// 
// To obtain the selected text range, the
// RichEditDocument.Document.Selection property is used. The characters and
// paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
// handler. Then, they are stored in the CharacterPropertiesObject and
// ParagraphPropertiesObject object containers.
// 
// In order to change the current
// RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
// the custom MouseCursorCalculator class Calculate method for clarification.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E5223

using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraBars.Helpers;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;


namespace DXApplication9
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            InitSkinGallery();
            InitializeRichEditControl();
            ribbonControl.SelectedPage = homeRibbonPage1;
            string path = @"DemoDoc.docx";

            richEditControl.LoadDocument(path,DocumentFormat.OpenXml);
        }

        void richEditControl_MouseUp(object sender, MouseEventArgs e)
        {
            if(barCheckItem1.Checked) {
                ApplyFormatToSelectedText();
                barCheckItem1.Checked = false;
            }
        }

        void InitSkinGallery()
        {
            SkinHelper.InitSkinGallery(rgbiSkins, true);
        }
        void InitializeRichEditControl()
        {
            richEditControl.StartHeaderFooterEditing += richEditControl_StartHeaderFooterEditing;
            richEditControl.SelectionChanged += richEditControl_SelectionChanged;
            richEditControl.FinishHeaderFooterEditing += richEditControl_FinishHeaderFooterEditing;
        }

        void richEditControl_StartHeaderFooterEditing(object sender, DevExpress.XtraRichEdit.HeaderFooterEditingEventArgs e)
        {
            headerFooterToolsRibbonPageCategory1.Visible = true;
            ribbonControl.SelectedPage = headerFooterToolsDesignRibbonPage1;
        }
        void richEditControl_FinishHeaderFooterEditing(object sender, DevExpress.XtraRichEdit.HeaderFooterEditingEventArgs e)
        {
            headerFooterToolsRibbonPageCategory1.Visible = false;
        }
        void richEditControl_SelectionChanged(object sender, EventArgs e)
        {
            tableToolsRibbonPageCategory1.Visible = richEditControl.IsSelectionInTable();
            floatingPictureToolsRibbonPageCategory1.Visible = richEditControl.IsFloatingObjectSelected;
        }

        DocumentRange sourceSelectedRange;
        private void SaveSelectedRange()
        {
            DocumentRange selection = richEditControl.Document.Selection;
            SubDocument subDocument = selection.BeginUpdateDocument();
            sourceSelectedRange = subDocument.CreateRange(selection.Start, richEditControl.Document.Selection.Length);
            selection.EndUpdateDocument(subDocument);
        }
        private void barCheckItem1_CheckedChanged(object sender, ItemClickEventArgs e)
        {
            if (barCheckItem1.Checked)
            {
                SaveSelectedRange();
                richEditControl.FormatCalculatorEnabled = true;
            }
            else
                richEditControl.FormatCalculatorEnabled = false;
           
        }

        private void ApplyFormatToSelectedText()
        {
            DocumentRange targetSelectedRange = richEditControl.Document.Selection;

            richEditControl.BeginUpdate();
            SubDocument targetSubDocument = targetSelectedRange.BeginUpdateDocument();
            SubDocument subDocument = sourceSelectedRange.BeginUpdateDocument();

            DevExpress.XtraRichEdit.API.Native.CharacterProperties targetCharactersProperties = targetSubDocument.BeginUpdateCharacters(targetSelectedRange);
            DevExpress.XtraRichEdit.API.Native.CharacterProperties sourceCharactersProperties = subDocument.BeginUpdateCharacters(sourceSelectedRange);
            targetCharactersProperties.Assign(sourceCharactersProperties);
            subDocument.EndUpdateCharacters(sourceCharactersProperties);
            targetSubDocument.EndUpdateCharacters(targetCharactersProperties);

            DevExpress.XtraRichEdit.API.Native.ParagraphProperties targetParagraphProperties = targetSubDocument.BeginUpdateParagraphs(targetSelectedRange);
            DevExpress.XtraRichEdit.API.Native.ParagraphProperties sourceParagraphProperties = subDocument.BeginUpdateParagraphs(sourceSelectedRange);
            targetParagraphProperties.Assign(sourceParagraphProperties);
            subDocument.EndUpdateParagraphs(sourceParagraphProperties);
            targetSubDocument.EndUpdateParagraphs(targetParagraphProperties);

            sourceSelectedRange.EndUpdateDocument(subDocument);
            targetSelectedRange.EndUpdateDocument(targetSubDocument);
            richEditControl.EndUpdate();
        }

  

    }
 
}