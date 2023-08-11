using System;
using System.Linq;
using System.Threading;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Verbum.Language;

namespace Rizonesoft.Office.Verbum
{
    internal static class Program
    {
        private const string CopyChannelName = "DocChannel";

        /// <summary>
        /// The main entry point for the application. This program ensures only a single instance
        /// is running at a time. If a second instance is attempted, it sends a message to the running
        /// instance with the command line arguments.
        /// </summary>
        /// <param name="args">The command line arguments.</param>
        [STAThread]
        private static void Main(string[] args)
        {
            Mutex applicationMutex = null;
            bool grantedOwnership;
            try
            {
                applicationMutex = new Mutex(true, ProgramMutexManager.GetProgramMutex(OfficeProgram.Verbum), out grantedOwnership);
            }
            catch (UnauthorizedAccessException)
            {
                grantedOwnership = false;
            }

            var fileName = args?.FirstOrDefault();

            if (grantedOwnership)
            {
                try
                {
                    // Configure the application
                    ProgramConfiguration.Configure(OfficeProgram.Verbum);

                    using var mainForm = new MainForm(fileName);
                    Application.Run(mainForm);
                }
                catch (Exception ex)
                {
                    // Handle unexpected exceptions
                    XtraMessageBox.Show(string.Format(Strings.Program_Unexpected_Error_Message, ex.Message), 
                        Strings.Program_Unexpected_Error_Caption, MessageBoxButtons.OK, MessageBoxIcon.Error);
                    Serilogger.LogMessage(LogLevel.Fatal, $"{ProgramConfiguration.ProgramName} could not start!", ex);
                }
                finally
                {
                    // Ensure the Mutex is released when we're done.
                    applicationMutex.ReleaseMutex();
                    applicationMutex.Dispose();
                }
            }
            else if (!string.IsNullOrEmpty(fileName))
            {
                using var copyData = new CopyData();
                copyData.Channels?.Add(CopyChannelName);
                copyData.Channels?[CopyChannelName]?.Send(fileName);
            }
        }
    }
}
