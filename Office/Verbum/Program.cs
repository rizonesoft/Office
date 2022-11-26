namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraEditors;
    using Rizonesoft.Office.ExceptionHandlers;
    using Rizonesoft.Office.Interprocess;
    using System;
    using System.Drawing;
    using System.Threading;
    using System.Windows.Forms;

    internal static class Program
    {
        private static void Application_ThreadException(object sender, ThreadExceptionEventArgs e)
        { new ExceptionForm(e.Exception).ShowDialog(); }

        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        { new ExceptionForm(e.ExceptionObject as Exception).ShowDialog(); }

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {
            Application.ThreadException += new ThreadExceptionEventHandler(Application_ThreadException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(
                CurrentDomain_UnhandledException);

            try
            {
                bool grantedOwnership;
                try
                {
                    // version 4 UUID
                    Mutex applicationMutex = new(
                        true,
                        @"Global\8058515D-BD1A-4DD0-8380-50900A2824AD",
                        out grantedOwnership);
                } catch(UnauthorizedAccessException)
                {
                    // mutex was reserved by another user -> application already running
                    grantedOwnership = false;
                }

                // get first parameter as a file name
                string fileName = string.Empty;
                if(args.Length > 0)
                {
                    fileName = args[0];
                }

                // check whether there's an instance running already
                if(!grantedOwnership)
                {
                    // Create a new instance of the class:
                    CopyData copyData = new CopyData();
                    // Create the named channels to send and receive on.
                    copyData.Channels.Add("DocChannel");
                    copyData.Channels["DocChannel"].Send(fileName);
                    // return;
                } else
                {
                    if(!SystemInformation.TerminalServerSession && Screen.AllScreens.Length > 1)
                    {
                        WindowsFormsSettings.SetPerMonitorDpiAware();
                    } else
                    {
                        WindowsFormsSettings.SetDPIAware();
                    }

                    WindowsFormsSettings.EnableFormSkins();
                    WindowsFormsSettings.ForceDirectXPaint();
                    WindowsFormsSettings.DefaultRibbonStyle = DefaultRibbonControlStyle.Office2019;
                    WindowsFormsSettings.AllowPixelScrolling = DevExpress.Utils.DefaultBoolean.True;
                    DevExpress.Utils.AppearanceObject.DefaultFont = new Font("Segoe UI", 8.25F);

                    DevExpress.Skins.SkinManager.EnableFormSkins();
                    DevExpress.UserSkins.BonusSkins.Register();

                    XtraForm mainForm = new MainForm(fileName);
                    Application.Run(mainForm);
                    return;
                }
            } catch(Exception ex)
            {
                Application_ThreadException(MainForm.ActiveForm, new ThreadExceptionEventArgs(ex));
            }
        }
    }
}
