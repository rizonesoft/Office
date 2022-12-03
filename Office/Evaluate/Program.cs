namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.XtraEditors;
    using Rizonesoft.Office.Evaluate.Utilities;
    using Rizonesoft.Office.ExceptionHandlers;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.ROUtilities;
    using System;
    using System.Drawing;
    using System.Threading;
    using System.Windows.Forms;

    internal static class Program
    {

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {

            Application.ThreadException += new ThreadExceptionEventHandler(Application_ThreadException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);
            ROLogging.ConfigureLogging();

            try
            {

                bool grantedOwnership;
                try
                {
                    Mutex applicationMutex = new(true, @"Global\E9153B79-9393-4982-9240-C5A2DD95BF6A", out grantedOwnership);
                }
                catch (UnauthorizedAccessException)
                {
                    grantedOwnership = false;
                }

                // get first parameter as a file name
                string fileName = string.Empty;
                if (args.Length > 0)
                {
                    fileName = args[0];
                }

                // check whether there's an instance running already
                if (grantedOwnership)
                {
                    WindowsFormsSettings.EnableFormSkins();
                    WindowsFormsSettings.ForceDirectXPaint();
                    WindowsFormsSettings.DefaultRibbonStyle = DefaultRibbonControlStyle.Office2019;
                    WindowsFormsSettings.AllowPixelScrolling = DevExpress.Utils.DefaultBoolean.True;
                    if (!SystemInformation.TerminalServerSession && Screen.AllScreens.Length > 1)
                    {
                        WindowsFormsSettings.SetPerMonitorDpiAware();
                    }
                    else
                    {
                        WindowsFormsSettings.SetDPIAware();
                    }

                    DevExpress.Utils.AppearanceObject.DefaultFont = new Font("Segoe UI", 8.25F);
                    DevExpress.Skins.SkinManager.EnableFormSkins();
                    DevExpress.UserSkins.BonusSkins.Register();

                    XtraForm mainForm = new MainForm(fileName);
                    Application.Run(mainForm);
                }
                else
                {
                    // Create a new instance of the class:
                    CopyData copyData = new CopyData();
                    // Create the named channels to send and receive on.
                    copyData.Channels.Add("WorkbookChannel");
                    copyData.Channels["WorkbookChannel"].Send(fileName);
                    // return;
                }

            }
            catch (Exception ex)
            {
                ROErrorMessage.Show("Woops!", $"{StcEvaluate.ProductName} was unable to start.");
                ROLogging.ROLogger.Fatal($"{StcEvaluate.ProductName} was unable to start.", ex);
            }

        }

        private static void Application_ThreadException(object sender, ThreadExceptionEventArgs e) => new ExceptionForm(e.Exception).ShowDialog();
        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e) => new ExceptionForm(e.ExceptionObject as Exception).ShowDialog();
    }
}
