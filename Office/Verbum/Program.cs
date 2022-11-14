using DevExpress.XtraEditors;
using NLog;
using System;
using System.Threading;
using System.Windows.Forms;

namespace Rizonesoft.Office.Verbum
{
    internal static class Program
    {
        private static readonly NLog.Logger Logger = NLog.LogManager.GetCurrentClassLogger();
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
                    // version 4 UUID
                    applicationMutex = new Mutex(true, @"Global\8058515D-BD1A-4DD0-8380-50900A2824AD", out grantedOwnership);
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

                    WindowsFormsSettings.DefaultRibbonStyle = DefaultRibbonControlStyle.Office2019;
                    Application.EnableVisualStyles();
                    Application.SetCompatibleTextRenderingDefault(false);
                    DevExpress.Skins.SkinManager.EnableFormSkins();
                    DevExpress.UserSkins.BonusSkins.Register();

                    XtraForm mainForm = new MainForm(fileName);
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
            new ExceptionForm(e.Exception).ShowDialog();
        }

        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            new ExceptionForm(e.ExceptionObject as Exception).ShowDialog();
        }

    }
}
