using DevExpress.Skins;
using DevExpress.UserSkins;
using DevExpress.XtraEditors;
using Rizonesoft.Office.ExceptionHandlers;
using Rizonesoft.Office.Interprocess;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Windows.Forms;

namespace Rizonesoft.Office.Sheets
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
                    applicationMutex = new Mutex(true, @"Global\E9153B79-9393-4982-9240-C5A2DD95BF6A", out grantedOwnership);
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
                    copyData.Channels.Add("WorkbookChannel");
                    copyData.Channels["WorkbookChannel"].Send(fileName);
                    // return;
                }
                else
                {
                    Application.EnableVisualStyles();
                    Application.SetCompatibleTextRenderingDefault(false);

                    WindowsFormsSettings.DefaultRibbonStyle = DefaultRibbonControlStyle.Office2019;
                    WindowsFormsSettings.UseDXDialogs = DevExpress.Utils.DefaultBoolean.True;
                    WindowsFormsSettings.ForceDirectXPaint();
                    if (!SystemInformation.TerminalServerSession && Screen.AllScreens.Length > 1)
                    {
                        WindowsFormsSettings.SetPerMonitorDpiAware();
                    }
                    else
                    {
                        WindowsFormsSettings.SetDPIAware();
                    }


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
