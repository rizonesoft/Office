using DevExpress.XtraSpreadsheet;
using DevExpress.XtraSpreadsheet.Commands;
using DevExpress.XtraSpreadsheet.Services;
using System;
using System.Linq;
using System.Windows.Forms;

namespace DXApplication15
{
    public class CustomCommandFactoryService : SpreadsheetCommandFactoryServiceWrapper
    {
        public CustomCommandFactoryService(ISpreadsheetCommandFactoryService service)
            : base(service)
        {
        }
        public SpreadsheetControl Control
        {
            get;
            set;
        }

        public override SpreadsheetCommand CreateCommand(SpreadsheetCommandId id)
        {
            if (id == SpreadsheetCommandId.DataToolsCircleInvalidData)
                return new CustomCircleInvalidDataCommand(Control);

            return base.CreateCommand(id);
        }

    }
    public class CustomCircleInvalidDataCommand : CircleInvalidDataCommand
    {
        public CustomCircleInvalidDataCommand(ISpreadsheetControl control)
            : base(control)
        {
        }
        int count = 0;
        public int ErrorsCount
        {
            get
            {
                return count;
            }
        }
        protected override void ExecuteCore()
        {
            base.ExecuteCore();
            count = this.ActiveSheet.InvalidDataCircles.Count;
            MessageBox.Show("Data valiadtion errors count = " + count);
        }
    }
}