using DevExpress.XtraSpreadsheet;
using DevExpress.XtraSpreadsheet.Commands;
using DevExpress.XtraSpreadsheet.Services;

namespace SpreadsheetCustomCommand
{
    #region #customservice
    public class CustomService : SpreadsheetCommandFactoryServiceWrapper {
        public CustomService(ISpreadsheetCommandFactoryService service)
            : base(service) {
        }
        public SpreadsheetControl Control {get;set;}

        public override SpreadsheetCommand CreateCommand(SpreadsheetCommandId id)
        {
            if (id == SpreadsheetCommandId.FormatClearContents || id == SpreadsheetCommandId.FormatClearContentsContextMenuItem)
                return new CustomFormatClearContentsCommand(Control);

            return base.CreateCommand(id);
        }

    }
    #endregion #customservice
}
