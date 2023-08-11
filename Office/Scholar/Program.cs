using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Windows.Forms;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;

using Syncfusion.Licensing;

namespace Rizonesoft.Office.Scholar;

/// <summary>
/// This class is the main entry point of the Rizonesoft.Office.Scholar program.
/// </summary>
internal static class Program
{
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
            applicationMutex = new Mutex(true, ProgramMutexManager.GetProgramMutex(OfficeProgram.Scholar), out grantedOwnership);
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
                const string syncfusionLicenseKey = "MjYwNjE2NkAzMjMyMmUzMDJlMzBrNWRVcWxEZnNoc0VieHdma2QrQjhVbFY4VGV1eDZXMkdyVHBINkQ3VFNVPQ==";
                SyncfusionLicenseProvider.RegisterLicense(syncfusionLicenseKey);

                // Configure the application
                ProgramConfiguration.Configure(OfficeProgram.Scholar);

                var baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
                var defaultPath = Path.Combine(baseDirectory, "Documentation", "Samples", "file-sample_150kB.pdf");

                // Check if the file exists
                if (!File.Exists(defaultPath))
                {
                    defaultPath = null;
                }

                // Use provided fileName if it's not null, otherwise use default demo path.
                var fileToOpen = fileName ?? defaultPath;
                using var mainForm = new MainForm(fileToOpen);
                Application.Run(mainForm);
            }
            finally
            {
                // Ensure the Mutex is released when we're done.
                applicationMutex.ReleaseMutex();
                applicationMutex.Dispose();
            }
        }
        else
        {
            using var copyData = new CopyData();
            copyData.Channels?.Add("DocChannel");
            copyData.Channels?["DocChannel"]?.Send(fileName);
        }
    }

}