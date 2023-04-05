using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraSpreadsheet;
using DevExpress.XtraSpreadsheet.Commands;

namespace SpreadsheetCustomCommand
{
    #region #customcommand
    public class CustomFormatClearContentsCommand : FormatClearContentsCommand {
        public CustomFormatClearContentsCommand(ISpreadsheetControl control)
            : base(control) {
        }

        protected override void ExecuteCore() {
            MessageBox.Show("Custom command executed");
            base.ExecuteCore();
        }
    }
    #endregion #customcommand
}
