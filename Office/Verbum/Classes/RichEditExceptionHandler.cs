using DevExpress.XtraRichEdit;
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using DevExpress.XtraEditors;

namespace Rizonesoft.Office.Verbum.Classes
{
    /// <summary>
    /// Handles exceptions for RichEditControl.
    /// </summary>
    public class RichEditExceptionHandler
    {
        private readonly RichEditControl control;

        /// <summary>
        /// Initializes a new instance of the <see cref="RichEditExceptionHandler"/> class.
        /// </summary>
        /// <param name="control">The RichEditControl to handle exceptions for.</param>
        /// <exception cref="ArgumentNullException">Thrown when control is null.</exception>
        public RichEditExceptionHandler(RichEditControl control)
        {
            this.control = control ?? throw new ArgumentNullException(nameof(control));
        }

        /// <summary>
        /// Installs the exception handler for the control.
        /// </summary>
        public void Install()
        {
            control.UnhandledException += OnRichEditControlUnhandledException;
        }

        /// <summary>
        /// Handles the UnhandledException event of the RichEditControl.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RichEditUnhandledExceptionEventArgs"/> instance containing the event data.</param>
        private static void OnRichEditControlUnhandledException(object sender, RichEditUnhandledExceptionEventArgs e)
        {
            if (e.Exception == null) 
                return;

            string title;
            switch (e.Exception)
            {
                case RichEditUnsupportedFormatException:
                    title = "Unsupported Document!";
                    break;
                case ExternalException:
                    title = "Something went wrong!";
                    break;
                case IOException:
                    title = "IO Error!";
                    break;
                default:
                    return;
            }
            
            XtraMessageBox.Show(e.Exception.Message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            e.Handled = true;
        }
    }
}
