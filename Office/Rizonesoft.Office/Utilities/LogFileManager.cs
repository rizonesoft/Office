using DevExpress.XtraEditors;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Language;
using System.Diagnostics;
using System.IO;

namespace Rizonesoft.Office.Utilities;

/// <summary>
/// Provides utility methods to manage log files and directories.
/// </summary>
public class LogFileManager
{

    /// <summary>
    /// Opens the log directory using the default file explorer.
    /// </summary>
    public static void OpenLogDirectory()
    {
        var logDirectoryPath = Path.GetDirectoryName(GlobalConfiguration.LogFilePath);

        if (logDirectoryPath != null)
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = logDirectoryPath,
                UseShellExecute = true,
                Verb = "open"
            });
        }
        else
        {
            XtraMessageBox.Show(
                Strings.SettingsForm_BtnOpenLog_ErrorMessage,
                Strings.SettingsForm_BtnOpenLog_ErrorMessageTitle,
                MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }

    /// <summary>
    /// Cleans the log directory by deleting all log files after user confirmation.
    /// </summary>
    public static void CleanLogDirectory()
    {
        var logDirectoryPath = Path.GetDirectoryName(GlobalConfiguration.LogFilePath);

        if (logDirectoryPath != null)
        {
            var result = XtraMessageBox.Show(
                Strings.SettingsForm_BtnCleanLog_Confirm_Message,
                Strings.SettingsForm_BtnCleanLog_Confirm_MessageTitle,
                MessageBoxButtons.YesNo, MessageBoxIcon.Warning);

            if (result != DialogResult.Yes) return;
            var logFiles = Directory.GetFiles(logDirectoryPath, "*.log");

            foreach (var logFile in logFiles)
            {
                File.Delete(logFile);
            }
        }
        else
        {
            XtraMessageBox.Show(
                Strings.SettingsForm_BtnOpenLog_ErrorMessage,
                Strings.SettingsForm_BtnOpenLog_ErrorMessageTitle,
                MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }
}