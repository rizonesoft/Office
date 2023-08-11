using System;
using DevExpress.XtraEditors;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using DevExpress.XtraSpreadsheet;
using System.Collections.Generic;

namespace Rizonesoft.Office.Evaluate.Classes
{
    /// <summary>
    /// Provides exception handling for the SpreadsheetControl.
    /// </summary>
    public class SpreadsheetExceptionHandler : IDisposable
    {
        private readonly SpreadsheetControl control;
        private readonly Dictionary<Type, string> exceptionTitles = new()
        {
            { typeof(SpreadsheetUnsupportedFormatException), "Unsupported Document!" },
            { typeof(ExternalException), "Something went wrong!" },
            { typeof(IOException), "IO Error!" }
        };

        /// <summary>
        /// Initializes a new instance of the SpreadsheetExceptionHandler class.
        /// </summary>
        /// <param name="control">The SpreadsheetControl to attach the exception handler to.</param>
        public SpreadsheetExceptionHandler(SpreadsheetControl control)
        {
            this.control = control ?? throw new ArgumentNullException(nameof(control));
            Install();
        }

        /// <summary>
        /// Installs the unhandled exception handler to the SpreadsheetControl.
        /// </summary>
        public void Install()
        {
            control.UnhandledException += OnSpreadsheetControlUnhandledException;
        }

        /// <summary>
        /// Unsubscribes from the UnhandledException event to prevent memory leaks.
        /// </summary>
        public void Dispose()
        {
            control.UnhandledException -= OnSpreadsheetControlUnhandledException;
        }

        /// <summary>
        /// Handles unhandled exceptions from the SpreadsheetControl.
        /// </summary>
        private void OnSpreadsheetControlUnhandledException(object sender, SpreadsheetUnhandledExceptionEventArgs e)
        {
            if (e.Exception == null)
                return;

            if (!exceptionTitles.TryGetValue(e.Exception.GetType(), out var title)) return;
            XtraMessageBox.Show(e.Exception.Message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            e.Handled = true;
        }
    }
}
