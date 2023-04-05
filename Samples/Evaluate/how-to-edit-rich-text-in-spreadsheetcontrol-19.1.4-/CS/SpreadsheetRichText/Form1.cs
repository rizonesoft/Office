using System;
using DevExpress.XtraBars.Helpers;
using DevExpress.XtraBars.Ribbon;
using DevExpress.Spreadsheet;
using DevExpress.XtraSpreadsheet.Menu;

namespace SpreadsheetRichText
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            InitSkinGallery();
            Worksheet worksheet = spreadsheetControl.ActiveWorksheet;
            RichTextString richText = new RichTextString();

            richText.AddTextRun("Rich ", new RichTextRunFont("Arial", 14, System.Drawing.Color.FromArgb(0xc5, 0x9f, 0xc9)));
            richText.AddTextRun("text ", new RichTextRunFont("Tahoma", 14, System.Drawing.Color.FromArgb(0x2c, 0x60, 0x8e)));
            richText.AddTextRun("formatting", new RichTextRunFont("Castellar", 14, System.Drawing.Color.FromArgb(0x2f, 0x24, 0x4f)));
            worksheet["B2"].SetRichText(richText);
            worksheet["B5"].SetValueFromText("This is the plain text\nUse the context menu to set rich text formatting");
            worksheet["B5"].Alignment.WrapText = true;
            worksheet.Columns[1].WidthInCharacters = 50;
        }
        void InitSkinGallery()
        {
            SkinHelper.InitSkinGallery(rgbiSkins, true);
        }

        private void spreadsheetControl_CellBeginEdit(object sender, DevExpress.XtraSpreadsheet.SpreadsheetCellCancelEventArgs e)
        {
            if (e.Cell.HasRichText)
            {
                e.Cancel = true;
                using (RichTextEditForm richEditForm = new RichTextEditForm(e.Cell))
                    richEditForm.ShowDialog();
            }
        }

        private void spreadsheetControl_PopupMenuShowing(object sender, DevExpress.XtraSpreadsheet.PopupMenuShowingEventArgs e)
        {
            if(e.MenuType == DevExpress.XtraSpreadsheet.SpreadsheetMenuType.Cell)
            {
                Cell activeCell = spreadsheetControl.ActiveCell;
                if (activeCell.Value.IsEmpty || (!activeCell.HasFormula && activeCell.Value.IsText))
                {
                    SpreadsheetMenuItem setRichTextItem = new SpreadsheetMenuItem("Set Rich Text", new EventHandler(SetRichTextItemClick));
                    e.Menu.Items.Add(setRichTextItem);
                }
            }
        }

        private void SetRichTextItemClick(object sender, EventArgs e)
        {
            using (RichTextEditForm richEditForm = new RichTextEditForm(spreadsheetControl.ActiveCell))
                richEditForm.ShowDialog();
        }
    }
}