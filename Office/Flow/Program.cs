using System;
using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Windows.Forms;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;

namespace Rizonesoft.Office.Flow
{
  
    internal static class Program
    {
        private const string CopyChannelName = "ReportChannel";

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        private static void Main(string[] args)
        {
            Mutex applicationMutex = null;
            bool grantedOwnership;
            try
            {
                applicationMutex = new Mutex(true, ProgramMutexManager.GetProgramMutex(OfficeProgram.Flow), out grantedOwnership);
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
                    ProgramConfiguration.Configure(OfficeProgram.Flow);

                    using var mainForm = new DesignForm(fileName);
                    Application.Run(mainForm);
                }
                catch (Exception ex)
                {
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
