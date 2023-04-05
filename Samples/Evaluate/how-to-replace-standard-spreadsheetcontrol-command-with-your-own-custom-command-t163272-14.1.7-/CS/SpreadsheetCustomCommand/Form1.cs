using System;
using System.Collections.Generic;
using System.Linq;
using DevExpress.XtraSpreadsheet.Services;


namespace SpreadsheetCustomCommand
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        #region #substituteservice
        private void SubstituteService() {
            ISpreadsheetCommandFactoryService service = (ISpreadsheetCommandFactoryService)spreadsheetControl1.GetService(typeof(ISpreadsheetCommandFactoryService));
            CustomService customService = new CustomService(service);
            spreadsheetControl1.ReplaceService<ISpreadsheetCommandFactoryService>(customService);
            customService.Control = spreadsheetControl1;
        }
        #endregion #substituteservice

        public Form1()
        {
            InitializeComponent();
            SubstituteService();
        }
    }
}