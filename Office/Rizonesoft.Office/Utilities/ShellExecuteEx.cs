using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraVerticalGrid;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.Utilities
{
    public static class ShellExecuteEx
    {

        /// <summary>
        /// Open a PDF document using the default PDF reader.
        /// </summary>
        /// <param name="fileName"></param>
        public static void OpenPDFDocument(string fileName)
        {
            try 
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo(fileName)
                    {
                        UseShellExecute = true,
                        WindowStyle = ProcessWindowStyle.Normal,
                        ErrorDialog = true
                     }
                };
                process.Start();
            }
            catch (Exception ex)
            {
                XtraMessageBox.Show($"Error opening PDF document: {fileName}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Logging.logger.Error(ex, $"Error opening PDF document: {fileName}");
            }

        }


    }
}
