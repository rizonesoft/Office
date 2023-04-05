using DevExpress.Spreadsheet;
using DevExpress.XtraBars;
using DevExpress.XtraSpreadsheet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsFormsApplication1
{
    public class FormatPainterProvider
    {
        SpreadsheetControl spreadsheetControl;
        BarCheckItem biFormatPainter;
        CellRange sourceCell = null;
        FormatPainterMode formatPainterMode = FormatPainterMode.None;
        enum FormatPainterMode { SingleAction, MultipleActions, None }
        public void RegisterFormatPainter(SpreadsheetControl spreadsheet, BarCheckItem biFormatPainter)
        {
            spreadsheetControl = spreadsheet;
            this.biFormatPainter = biFormatPainter;
            spreadsheet.MouseUp += spreadsheetControl1_MouseUp;
            spreadsheet.PreviewKeyDown += spreadsheetControl1_PreviewKeyDown;
            spreadsheet.SelectionChanged += spreadsheetControl1_SelectionChanged;
            spreadsheet.CellBeginEdit += spreadsheetControl1_CellBeginEdit;
            spreadsheet.SheetRemoving += Spreadsheet_SheetRemoving;
            biFormatPainter.CheckedChanged += barCheckItem1_CheckedChanged;
            biFormatPainter.ItemDoubleClick += barCheckItem1_ItemDoubleClick;

        }
        private void Spreadsheet_SheetRemoving(object sender, SheetRemovingEventArgs e)
        {
            if (sourceCell != null && e.SheetName == sourceCell.Worksheet.Name)
                biFormatPainter.Checked = false;
        }
        private void barCheckItem1_CheckedChanged(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            bool shouldCopyFormat = biFormatPainter.Checked;
            sourceCell = shouldCopyFormat ? spreadsheetControl.SelectedCell : null;

            formatPainterMode = shouldCopyFormat ? FormatPainterMode.SingleAction : FormatPainterMode.None;
        }

        private void spreadsheetControl1_MouseUp(object sender, MouseEventArgs e)
        {
            if (IsFormatPainterActivated())
                ApplyFormat();
        }

        private bool IsFormatPainterActivated()
        {
            if (formatPainterMode == FormatPainterMode.None || sourceCell == null)
                return false;

            return true;
        }
        private void ApplyFormat()
        {
            spreadsheetControl.Selection.CopyFrom(sourceCell, PasteSpecial.Formats);
            if (formatPainterMode == FormatPainterMode.SingleAction)
                biFormatPainter.Checked = false;
        }

        private void barCheckItem1_ItemDoubleClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            biFormatPainter.Checked = true;
            formatPainterMode = FormatPainterMode.MultipleActions;
        }

        private void spreadsheetControl1_PreviewKeyDown(object sender, PreviewKeyDownEventArgs e)
        {
            if (!IsFormatPainterActivated()) return;

            if (e.KeyCode == Keys.Escape)
            {
                biFormatPainter.Checked = false;
            }
        }

        private void spreadsheetControl1_SelectionChanged(object sender, EventArgs e)
        {
            if (spreadsheetControl.SelectedShape != null || spreadsheetControl.SelectedComment != null)
            {
                biFormatPainter.Enabled = false;
                biFormatPainter.Checked = false;
            }
            else
                biFormatPainter.Enabled = true;
        }

        private void spreadsheetControl1_CellBeginEdit(object sender, DevExpress.XtraSpreadsheet.SpreadsheetCellCancelEventArgs e)
        {
            if (IsFormatPainterActivated())
            {
                ApplyFormat();
                e.Cancel = true;
            }
            else
                biFormatPainter.Enabled = false;
        }
        
    }
    
}
