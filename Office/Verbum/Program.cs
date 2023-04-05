// ReSharper disable StructuredMessageTemplateProblem
namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraEditors;
    using ExceptionHandlers;
    using Interprocess;
    using Rizonesoft.Office.Utilities;
    using Utilities;
    using System;
    using System.Drawing;
    using System.Globalization;
    using System.Threading;
    using System.Windows.Forms;

    internal static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        private static void Main(string[] args)
        {
            var culture = CultureInfo.CreateSpecificCulture("en");
            CultureInfo.DefaultThreadCurrentCulture = culture;
            CultureInfo.DefaultThreadCurrentUICulture = culture;

            // ReSharper disable once UnusedParameter.Local
            Application.ThreadException += (sender, e) => new ExceptionForm(e.Exception).ShowDialog();
            // ReSharper disable once UnusedParameter.Local
            AppDomain.CurrentDomain.UnhandledException += (sender, e) => new ExceptionForm((e.ExceptionObject as Exception)!).ShowDialog();
            Logging.ConfigureLogging();

            try
            {
                
                bool grantedOwnership;
                try
                {
                    // ReSharper disable once UnusedVariable
                    Mutex applicationMutex = new(true, @"Global\8058515D-BD1A-4DD0-8380-50900A2824AD", out grantedOwnership);
                }
                catch (UnauthorizedAccessException)
                {
                    grantedOwnership = false;
                }

                // get first parameter as a file name
                var fileName = string.Empty;
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

                    XtraForm mainForm = new MainForm(fileName);
                    Application.Run(mainForm);
                }
                else
                {
                    // Create a new instance of the class:
                    var copyData = new CopyData();
                    // Create the named channels to send and receive on.
                    copyData.Channels.Add("DocChannel");
                    copyData.Channels["DocChannel"].Send(fileName);
                    // return;
                }
            }
            catch (Exception ex)
            {
                ErrorMessage.Show("Woops!", $"{StcVerbum.ProductName} was unable to start.");
                Logging.Logger.Fatal($"{StcVerbum.ProductName} was unable to start.", ex);
            }
        }

    }
}
