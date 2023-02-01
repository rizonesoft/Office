using System;
using System.Collections;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraSpellChecker;

namespace Datum.Verbum
{

    class Assistants
    {

        public static Hashtable availableDictionaries = new Hashtable();  

        public static void OpenWebPage(string webAddress)
        {
            Process process = new Process();
            process.StartInfo.FileName = webAddress;
            process.StartInfo.Verb = "Open";
            process.StartInfo.WindowStyle = ProcessWindowStyle.Normal;
            process.Start();
        }
        
    }

    class Cataloguing
    {
        public static string UserBugFilePath = Configuration.GetUserAppDataPath() + "Rizonesoft\\Verbum\\Output.log";
        

        public static void WriteBugToFile(string Message)
        {
            string bugLine = String.Empty;
            StreamWriter swBug = null;
            bugLine = String.Format("{0:G}: {1}", System.DateTime.Now, Message);

            try
            {
                if (!File.Exists(UserBugFilePath))
                { swBug = new StreamWriter(UserBugFilePath); }
                else { swBug = File.AppendText(UserBugFilePath); }
                swBug.WriteLine(bugLine);
                swBug.Flush();
            }
            catch (Exception) {}
            finally { if (swBug != null) { swBug.Close(); } }
        }

    }

    public class RichEditUnhandledExceptionsHandler
    {
        readonly RichEditControl richControl;
        public RichEditUnhandledExceptionsHandler(RichEditControl richControl)
        {
            this.richControl = richControl;
        }
        public void Install()
        {
            if (richControl != null)
                richControl.UnhandledException += OnRichEditControlUnhandledException;
        }

        protected virtual void OnRichEditControlUnhandledException(object sender, RichEditUnhandledExceptionEventArgs e)
        {
            try
            {
                if (e.Exception != null)
                    throw e.Exception;
            }
            catch (RichEditUnsupportedFormatException ex)
            {
                XtraMessageBox.Show(ex.Message, Application.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
                e.Handled = true;
            }
            catch (ExternalException ex)
            {
                XtraMessageBox.Show(ex.Message, Application.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
                e.Handled = true;
            }
            catch (System.IO.IOException ex)
            {
                XtraMessageBox.Show(ex.Message, Application.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
                e.Handled = true;
            }
        }
    }

    public class SpellCheckerUnhandledExceptionHandler
    {
        readonly SpellChecker spellControl;
        public SpellCheckerUnhandledExceptionHandler(SpellChecker spellControl)
        {
            this.spellControl = spellControl;
        }
        public void Install()
        {
            if (spellControl != null)
                spellControl.UnhandledException += OnSpellCheckerUnhandledException;
        }

        protected virtual void OnSpellCheckerUnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            try
            {
                if (e.Exception != null)
                    throw e.Exception;
            }
            catch (NotLoadedDictionaryException ex)
            {
                XtraMessageBox.Show(ex.Message, Application.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
                e.Handled = true;
            }
            catch (Exception ex)
            {
                XtraMessageBox.Show(ex.Message, Application.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
                e.Handled = true;
            }
        }
    }

}
