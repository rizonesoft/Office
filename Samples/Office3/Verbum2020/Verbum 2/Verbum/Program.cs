using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using System.Threading;
using System.Collections;

namespace Rizonesoft.Verbum
{
    static class Program
    {

        static Mutex applicationMutex = null;

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {

            Application.ThreadException += new System.Threading.ThreadExceptionEventHandler(Application_ThreadException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);

            try
            {
                bool grantedOwnership;
                try
                {
                    applicationMutex = new Mutex(true, @"Global\1880838F-D7C0-44A5-85D6-84CF7D95E204", out grantedOwnership);
                }
                catch (UnauthorizedAccessException)
                {
                    // mutex was reserved by another user -> application already running
                    grantedOwnership = false;
                }

                // get first parameter as a file name
                string fileName = string.Empty;
                if (args.Length > 0)
                {
                    fileName = args[0];
                }

                // check whether there's an instance running already
                if (!grantedOwnership)
                {
                    // Create a new instance of the class:
                    CopyData copyData = new CopyData();
                    // Create the named channels to send and receive on.
                    copyData.Channels.Add("DocChannel");
                    copyData.Channels["DocChannel"].Send(fileName);
                    return;
                }
                else
                {
                    Application.EnableVisualStyles();
                    Application.SetCompatibleTextRenderingDefault(false);

                    DevExpress.Skins.SkinManager.EnableFormSkins();

                    MainForm mainForm = new MainForm();
                    XtraForm docForm = new DocumentForm(fileName, mainForm.DocumentIndex);
                    mainForm.AddForm(docForm);
                    Application.Run(mainForm);

                    return;
                }
            }
            catch (Exception ex)
            {
                Application_ThreadException(MainForm.ActiveForm, new ThreadExceptionEventArgs(ex));
            }

        }

        private static void Application_ThreadException(object sender, ThreadExceptionEventArgs e)
        {
            new exceptionForm(e.Exception).ShowDialog();
        }

        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            new exceptionForm(e.ExceptionObject as Exception).ShowDialog();
        }

    }
}