﻿namespace Rizonesoft.Office.Reader
{
    using DevExpress.XtraEditors;
    using Rizonesoft.Office.ExceptionHandlers;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.Reader.Utilities;
    using Rizonesoft.Office.Utilities;
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
            Application.ThreadException += (sender, e) => new ExceptionForm(e.Exception).ShowDialog();
            AppDomain.CurrentDomain.UnhandledException += (sender, e) => new ExceptionForm(e.ExceptionObject as Exception).ShowDialog();
            Logging.ConfigureLogging();

            try
            {
                bool grantedOwnership;
                try
                {
                    Mutex applicationMutex = new(true, @"Global\0F383F47-B48A-477B-B444-8B7882220044", out grantedOwnership);
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

                    XtraForm mainForm = new MainForm(fileName);
                    Application.Run(mainForm);
                    return;
                }
                else
                {
                    // Create a new instance of the class:
                    CopyData copyData = new CopyData();
                    // Create the named channels to send and receive on.
                    copyData.Channels.Add("PDFChannel");
                    copyData.Channels["PDFChannel"].Send(fileName);
                    // return;
                }

            }
            catch (Exception ex)
            {
                ROErrorMessage.Show("Woops!", $"{StcReader.ProductName} was unable to start.");
                Logging.ROLogger.Fatal($"{StcReader.ProductName} was unable to start.", ex);
            }

        }

    }
}
