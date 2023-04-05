using DevExpress.Spreadsheet;
using DevExpress.XtraEditors;
using DevExpress.XtraSpreadsheet.Services;
using System;
using System.Linq;


namespace DXApplication15
{
    public partial class Form1 : XtraForm
    {
        public Form1() {
            InitializeComponent();
            spreadsheetControl.LoadDocument("data.xlsx");
       
            SubstituteService();
        }
       
        
        
        private void SubstituteService() {
            ISpreadsheetCommandFactoryService service = (ISpreadsheetCommandFactoryService)spreadsheetControl.GetService(typeof(ISpreadsheetCommandFactoryService));
            CustomCommandFactoryService customService = new CustomCommandFactoryService(service);
            spreadsheetControl.ReplaceService<ISpreadsheetCommandFactoryService>(customService);
            customService.Control = spreadsheetControl;
        }

      

    }
 

   
}