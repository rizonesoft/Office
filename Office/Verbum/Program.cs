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
    using System.Linq;

    internal static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        private static void Main(string[] args)
        {
            CultureInfo.DefaultThreadCurrentCulture = CultureInfo.CreateSpecificCulture("en");
            CultureInfo.DefaultThreadCurrentUICulture = CultureInfo.CreateSpecificCulture("en");

            Application.ThreadException += (_, e) =>
            {
                using var form = new ExceptionForm(e.Exception);
                form.ShowDialog();
            };
            AppDomain.CurrentDomain.UnhandledException += (_, e) =>
            {
                using var form = new ExceptionForm(e.ExceptionObject as Exception ?? new Exception());
                form.ShowDialog();
            };
            Logging.ConfigureLogging();

            try
            {
                bool grantedOwnership;
                try
                {
                    using var applicationMutex = new Mutex(true, @"Global\8058515D-BD1A-4DD0-8380-50900A2824AD", out grantedOwnership);
                }
                catch (UnauthorizedAccessException)
                {
                    grantedOwnership = false;
                }

                var fileName = args?.FirstOrDefault();

                if (grantedOwnership)
                {
                    ConfigureApplication();

                    using var mainForm = CreateMainForm(fileName);
                    Application.Run(mainForm);
                }
                else
                {
                    using var copyData = new CopyData();
                    copyData.Channels?.Add("DocChannel");
                    copyData.Channels?["DocChannel"]?.Send(fileName);
                }
            }
            catch (Exception ex)
            {
                ErrorMessage.Show("Woops!", $"{StcVerbum.ProductName} was unable to start.");
                Logging.Logger.Fatal($"{StcVerbum.ProductName} was unable to start.", ex);
            }
        }

        private static void ConfigureApplication()
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
        }

        private static XtraForm CreateMainForm(string fileName)
        {
            return new MainForm(fileName);
        }

    }
}
