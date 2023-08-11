using DevExpress.Skins;
using DevExpress.UserSkins;
using Rizonesoft.Office.Programs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace Rizonesoft.Office.Clock
{
    internal static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            ProgramConfiguration.Configure(OfficeProgram.Clock);
            Application.Run(new MainForm());
        }
    }
}