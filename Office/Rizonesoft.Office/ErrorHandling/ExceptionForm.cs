using Rizonesoft.Office.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.Utilities;
using System.Resources;
using Timer = System.Windows.Forms.Timer;

namespace Rizonesoft.Office.ErrorHandling;

/// <summary>
/// ExceptionForm class displays an error message and exception details,
/// and allows the user to recover after a certain period of time.
/// </summary>
public partial class ExceptionForm : DirectXFormBase
{
    private const int CountdownSeconds = 60;
    private int _countdown;
    private readonly Timer _autoCloseTimer = new() { Interval = 1000 };

    /// <summary>
    /// Initializes a new instance of the ExceptionForm class.
    /// </summary>
    /// <param name="ex">The exception to display.</param>
    /// <exception cref="ArgumentNullException">Thrown when the provided exception is null.</exception>
    public ExceptionForm(Exception ex)
    {
        if (ex == null) throw new ArgumentNullException(nameof(ex));

        InitializeComponent();
        LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
        LoadLocalizedResources();

        _countdown = CountdownSeconds;
        _autoCloseTimer.Tick += AutoCloseTimer_Tick;
        _autoCloseTimer.Start();

        InitializeExceptionDetails(ex);
    }

    /// <summary>
    /// Initializes exception details and sets UI components' properties.
    /// </summary>
    /// <param name="ex">The exception to display.</param>
    private void InitializeExceptionDetails(Exception ex)
    {
        lblMessage.ImageOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.ErrorHandling.Resources.WarningError.svg");
        IconOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.ErrorHandling.Resources.Error.svg");
        lblMessage.ImageOptions.SvgImageSize = new Size(48, 48);
        memoExceptionDetails.Text = ExceptionHandler.ExceptionToString(ex);

        lblPrivacyStatement.ImageOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.ErrorHandling.Resources.Security.svg");
        lblPrivacyStatement.ImageOptions.SvgImageSize = new Size(48, 48);
    }

    private void LoadLocalizedResources()
    {
        Text = Strings.ExceptionForm_Title;
        lblMessage.Text = Strings.ExceptionForm_Description;
        lblPrivacyStatement.Text = Strings.ExceptionForm_Privacy_Notice;
        UpdateRecoverButtonText();
        btnTerminate.Text = Strings.ExceptionForm_Button_Terminate;
    }

    private void LanguageManager_LanguageChanged(object? sender, EventArgs e)
    {
        LoadLocalizedResources();
    }

    private void AutoCloseTimer_Tick(object? sender, EventArgs e)
    {
        UpdateCountdown();
    }

    private void UpdateCountdown()
    {
        _countdown--;
        UpdateRecoverButtonText();

        if (_countdown <= 0)
        {
            StopTimerAndClose();
        }
    }

    private void UpdateRecoverButtonText()
    {
        btnRecover.Text = string.Format(Strings.ExceptionForm_Button_Recover, _countdown);
    }

    private void BtnRecover_Click(object sender, EventArgs e)
    {
        StopTimerAndClose();
    }

    private void StopTimerAndClose()
    {
        _autoCloseTimer.Stop();
        DialogResult = DialogResult.OK;
        Close();
    }

    private void MemoExceptionDetails_Enter(object sender, EventArgs e)
    {
        _autoCloseTimer.Stop();
    }

    private void MemoExceptionDetails_Leave(object sender, EventArgs e)
    {
        _autoCloseTimer.Start();
    }

    private void btnCopy_Click(object sender, EventArgs e)
    {
        memoExceptionDetails.SelectAll();
        memoExceptionDetails.Copy();
    }
}