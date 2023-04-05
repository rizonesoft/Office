using System.Diagnostics;
using System.IO;

namespace Rizonesoft.Office.ExceptionHandlers;

using Utilities;

public sealed partial class ExceptionForm : DevExpress.XtraEditors.DirectXForm
{
    public ExceptionForm()
    {
        InitializeComponent();
        // bugMemoEdit.Text = ExceptionHandler.EnvironmentToString();
    }

    public ExceptionForm(Exception? ex)
    {
        InitializeComponent();
        bugMemoEdit.Text =
            string.Format(Resources.Office.ExceptionForm_bugMemoEdit, ExceptionHandler.EnvironmentToString(), ExceptionHandler.ExceptionToString(ex));
        Logging.Logger.Error(ex, "Whoops!");
    }

    private void cancelButton_Click(object sender, EventArgs e)
    {
        Close();
    }

    private void copyButton_Click(object sender, EventArgs e)
    {
        bugMemoEdit.Focus();
        bugMemoEdit.Copy();
    }

    private void loggingButton_Click(object sender, EventArgs e)
    {
        var loggingPath = Path.Combine(RizonesoftEx.UserAppDirectory, "Logging");

        if (Directory.Exists(loggingPath))
        {
            var startInfo = new ProcessStartInfo
            {
                Arguments = loggingPath,
                FileName = "explorer.exe"
            };

            Process.Start(startInfo);
        }
        else
        {
            MessageBox.Show(string.Format(Resources.Office.ExceptionForm_Directory_does_not_exist, loggingPath));
        }
    }
}