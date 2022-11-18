using DevExpress.XtraRichEdit;
using System.Runtime.InteropServices;


namespace Rizonesoft.Office.Verbum.Classes
{
    public class RichEditExceptionHandler
    {
        readonly RichEditControl control;

        public RichEditExceptionHandler(RichEditControl control)
        {
            this.control = control;
        }

        public void Install()
        {
            if (control != null)
            {
                control.UnhandledException += OnRichEditControlUnhandledException;
            }
        }

        internal void OnRichEditControlUnhandledException(object sender, RichEditUnhandledExceptionEventArgs e)
        {
            try
            {
                if (e.Exception != null)
                    throw e.Exception;
            }
            catch (RichEditUnsupportedFormatException ex)
            {
                new ExceptionForm(ex).ShowDialog();
                e.Handled = true;
            }
            catch (ExternalException ex)
            {
                new ExceptionForm(ex).ShowDialog();
                e.Handled = true;
            }
            catch (System.IO.IOException ex)
            {
                new ExceptionForm(ex).ShowDialog();
                e.Handled = true;
            }
        }

       

    }
}
