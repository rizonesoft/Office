using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SpreadsheetAddIn
{
    public class ExcelAppHelper : IDisposable
    {
        const string OFFICE_APP_ID = "Excel.Application";
        const string EXCEL_PROCESS_NAME = "EXCEL";
        object excelApp;
        object excelWorkbook;
        object oMissing = System.Reflection.Missing.Value;

        public object Workbook { get { return excelWorkbook; } }

        public bool Initialize(string filePath) {
            excelApp = InitializeExcelApplication();
            if (excelApp == null)
                return false;

            excelWorkbook = LoadWorkbook(filePath, excelApp);
            return excelWorkbook != null;
        }

        object InitializeExcelApplication() {
            object excelApp = null;
            CultureInfo culture = System.Threading.Thread.CurrentThread.CurrentCulture;
            try {
                System.Threading.Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");
                Type appType = Type.GetTypeFromProgID(OFFICE_APP_ID, false);
                if (appType != null) {
                    excelApp = Activator.CreateInstance(appType);
                    SetExcelAppVisible(excelApp, false);
                }
            }
            catch {
                excelApp = null;
            }
            finally {
                System.Threading.Thread.CurrentThread.CurrentCulture = culture;
            }
            return excelApp;
        }

        object LoadWorkbook(string filePath, object excelApp) {
            CultureInfo culture = System.Threading.Thread.CurrentThread.CurrentCulture;
            System.Threading.Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");
            try { return LoadWorkbookCore(filePath, excelApp); }
            catch { return null; }
            finally { System.Threading.Thread.CurrentThread.CurrentCulture = culture; }
        }

        object LoadWorkbookCore(string fileName, object application) {
            try { application.GetType().InvokeMember("DisplayAlerts", System.Reflection.BindingFlags.SetProperty, null, application, new object[] { false }); }
            catch { }
            try { application.GetType().InvokeMember("AskToUpdateLinks", System.Reflection.BindingFlags.SetProperty, null, application, new object[] { false }); }
            catch { }
            object Books = application.GetType().InvokeMember("Workbooks", System.Reflection.BindingFlags.GetProperty, null, application, null);

            object updateExternalLinks = 2; // http://msdn.microsoft.com/en-us/library/microsoft.office.interop.excel.workbooks.open(v=office.11).aspx
            object[] args = { fileName, updateExternalLinks };
            return Books.GetType().InvokeMember("Open", System.Reflection.BindingFlags.InvokeMethod, null, Books, args);
        }

        void SetExcelAppVisible(object excelApp, bool newValue) {
            excelApp.GetType().InvokeMember("Visible", System.Reflection.BindingFlags.SetProperty, null, excelApp, new object[] { newValue });
        }

        #region IDisposable Members
        public void Dispose() {
            Dispose(true);
        }
        protected virtual void Dispose(bool disposing) {
            if (disposing) {
                if (excelWorkbook != null)
                    CloseExcelWorkBook(excelWorkbook);
                if (excelApp != null)
                    TerminateAllExcelAppInstances();
            }
        }
        #endregion
        void CloseExcelWorkBook(object excelWorkbook) {
            if (excelWorkbook == null)
                return;

            CultureInfo culture = System.Threading.Thread.CurrentThread.CurrentCulture;
            System.Threading.Thread.CurrentThread.CurrentCulture = new CultureInfo("en-US");
            try {
                object[] closeArgs = { false, oMissing, oMissing };
                Type type = excelWorkbook.GetType();
                if (type == null)
                    return;
                try {
                    type.InvokeMember("Close", System.Reflection.BindingFlags.InvokeMethod, null, excelWorkbook, closeArgs);
                }
                catch {
                }
            }
            finally {
                System.Threading.Thread.CurrentThread.CurrentCulture = culture;
            }
        }

        void TerminateAllExcelAppInstances() {
            try {
                excelApp.GetType().InvokeMember("Quit", System.Reflection.BindingFlags.InvokeMethod, null, excelApp, null);
            }
            catch {
                if (excelApp != null) {
                    try { SetExcelAppVisible(excelApp, true); }
                    catch { excelApp = null; }
                }
                if (excelApp != null) {
                    try { excelApp.GetType().InvokeMember("Quit", System.Reflection.BindingFlags.InvokeMethod, null, excelApp, null); }
                    catch { excelApp = null; }
                }
            }
            excelApp = null;
        }

        public object RunMacros(string name, List<object> args) {
            args.Insert(0, name);
            try {
                return excelApp.GetType().InvokeMember("Run", System.Reflection.BindingFlags.Default | System.Reflection.BindingFlags.InvokeMethod, null, excelApp, args.ToArray());
            }
            catch {
                return null;
            }
        }
    }
}
