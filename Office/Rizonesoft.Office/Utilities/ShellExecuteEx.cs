namespace Rizonesoft.Office.Utilities
{
    using DevExpress.XtraEditors;
    using System;
    using System.Diagnostics;

    public static class ShellExecuteEx
    {

        /// <summary>
        /// Open a PDF document using the default PDF reader.
        /// </summary>
        /// <param name="fileName"></param>
        public static void OpenPdfDocument(string fileName)
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
                Logging.Logger.Error(ex, $"Error opening PDF document: {fileName}");
            }

        }


    }
}
