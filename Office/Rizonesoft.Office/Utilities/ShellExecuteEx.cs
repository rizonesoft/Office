namespace Rizonesoft.Office.Utilities
{
    using DevExpress.XtraEditors;
    using System;
    using System.Diagnostics;

    /// <summary>
    /// ShellExecuteEx class provides methods for executing shell operations, such as opening files using the default application.
    /// </summary>
    public static class ShellExecuteEx
    {
        /// <summary>
        /// Opens a PDF document using the default PDF reader.
        /// </summary>
        /// <param name="fileName">The file path of the PDF document to open.</param>
        public static void OpenPdfDocument(string fileName)
        {
            try
            {
                using Process process = new()
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
