namespace Rizonesoft.Office.ExceptionHandlers;

using Utilities;

public sealed partial class ExceptionForm : DevExpress.XtraEditors.DirectXForm
{
    public ExceptionForm()
    {
        InitializeComponent();
        // ReSharper disable once LocalizableElement
        bugMemoEdit.Text = $"{ExceptionHandler.EnvironmentToString()}\r\n\r\nException:";
    }

    public ExceptionForm(Exception? ex)
    {
        InitializeComponent();
        bugMemoEdit.Text =
            // ReSharper disable once LocalizableElement
            $"{ExceptionHandler.EnvironmentToString()}\r\n\r\n{ExceptionHandler.ExceptionToString(ex)}";
        Logging.logger.Error(ex, "Whoops!");
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
}