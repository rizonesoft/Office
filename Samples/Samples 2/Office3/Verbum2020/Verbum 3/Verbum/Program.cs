using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraEditors;

namespace Rizonesoft.Verbum
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {

            // get first parameter as a file name
            string fileName = string.Empty;
            if (args.Length > 0)
            {
                fileName = args[0];
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            MainForm mainForm = new MainForm();
            XtraForm docForm = new DocForm(fileName, mainForm.DocumentIndex);
            mainForm.AddForm(docForm);
            Application.Run(mainForm);

            return;
        }
    }
}
