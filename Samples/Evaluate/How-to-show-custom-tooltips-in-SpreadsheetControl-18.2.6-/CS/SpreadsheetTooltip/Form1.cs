using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.Spreadsheet;
using DevExpress.Utils;

namespace SpreadsheetTooltip
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm
    {
        public Form1()
        {
            InitializeComponent();
            spreadsheetControl1.ToolTipController = toolTipController1;
            toolTipController1.GetActiveObjectInfo += ToolTipController1_GetActiveObjectInfo;

            spreadsheetControl1.LoadDocument("template.xlsx");
        }

        private void ToolTipController1_GetActiveObjectInfo(object sender, DevExpress.Utils.ToolTipControllerGetActiveObjectInfoEventArgs e)
        {
            if (e.SelectedControl != spreadsheetControl1)
                return;
            Cell cell = spreadsheetControl1.GetCellFromPoint(new PointF(e.ControlMousePosition.X, e.ControlMousePosition.Y));
            if (cell == null) return;

            if (cell.IsMerged)
                cell = cell.GetMergedRanges().First()[0];
            if(!cell.Value.IsEmpty)
            {
                ToolTipControlInfo info = new ToolTipControlInfo(cell, string.Empty);
                info.ToolTipType = ToolTipType.SuperTip;
                SuperToolTip sToolTip = new SuperToolTip();
                ToolTipItem item = new ToolTipItem();
                item.Font = new Font("Arial", 10);
                item.ImageOptions.SvgImage = svgImageCollection1[cell.Value.Type.ToString().ToLower()];
                item.Text = PrepareCellTooltip(cell);
                sToolTip.Items.Add(item);
                info.SuperTip = sToolTip;
                e.Info = info;
            }
        }
        private string PrepareCellTooltip(Cell cell)
        {
            string cellReference = cell.GetReferenceA1();
            string cellDataType = cell.Value.Type.ToString();
            string cellDisplayText = cell.DisplayText;
            return String.Format("Cell reference: {0}\r\nData type: {1}\r\nValue: {2}", cellReference, cellDataType, cellDisplayText);
        }
    }
}
