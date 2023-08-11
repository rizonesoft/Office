using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Toast;
using System;
using System.Net.NetworkInformation;
using System.Windows.Forms;

namespace Rizonesoft.Office.Zone;

/// <summary>
/// Represents the main Program class for the Rizonesoft Office Zone application.
/// </summary>
internal static class Program
{
    /// <summary>
    /// The main entry point for the application.
    /// </summary>
    [STAThread]
    private static void Main() // private static void Main(string[] args)
    {
        // Configure the application
        ProgramConfiguration.Configure(OfficeProgram.Zone);

        // Run the main form
        using var mainForm = new MainForm();
        Application.Run(mainForm);

    }
}