using DevExpress.Skins;
using DevExpress.UserSkins;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using Rizonesoft.Office.Session;
using Rizonesoft.Office.Session.Data;

namespace Session
{
    internal static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            try
            {
                Application.Run(new MainForm());
            }
            catch (InvalidOperationException ex)
            {
                if (ex.Message == "No writable folder selected for the database.")
                {
                    // Exit the application if the database folder is not writable
                    Application.Exit();
                }
            }
        }
    }
}
