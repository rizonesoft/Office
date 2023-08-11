using DevExpress.XtraBars.Alerter;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.Toast;

/// <summary>
/// A form that displays toast notifications with different actions and types.
/// </summary>
public partial class ToastForm : DevExpress.XtraEditors.XtraForm
{
    private readonly Actions _action;

    /// <summary>
    /// Initializes a new instance of the <see cref="ToastForm"/> class.
    /// </summary>
    public ToastForm()
    {
        InitializeComponent();
    }

    /// <summary>
    /// Initializes a new instance of the <see cref="ToastForm"/> class with specified data, type, and action.
    /// </summary>
    /// <param name="toastData">The data for the toast.</param>
    /// <param name="toastType">The type of the toast.</param>
    /// <param name="action">The action to be performed on a button click (default is ShowMessageOne).</param>
    public ToastForm(ToastData toastData, ToastType toastType, Actions action = Actions.ShowMessageOne) : this()
    {
        _action = action;
        alertToast.Show(toastData, this);

        alertToast.HtmlElementMouseClick += toastType switch
        {
            ToastType.MessageToast => HandleMessageToastClick,
            ToastType.NotificationToast => HandleNotificationToastClick,
            ToastType.LanguageToast => HandleLanguageToastClick,
            ToastType.UpdateToast => HandleUpdateToastClick,
            _ => throw new ArgumentOutOfRangeException(nameof(toastType), toastType, @"Wow! You discovered a new type of toast that doesn't exist."),
        };
    }

    private void HandleToastButtonClick(AlertHtmlElementMouseEventArgs e, string buttonId, Action buttonAction)
    {
        if (e.ElementId == "dismissButton" || e.ParentHasId("dismissButton"))
        {
            e.HtmlPopup.Close();
        }
        else if (e.ElementId == buttonId || e.ParentHasId(buttonId))
        {
            buttonAction();
        }
        else
        {
            e.HtmlPopup.Close();
        }
    }

    private void HandleMessageToastClick(object sender, AlertHtmlElementMouseEventArgs e)
    {
        HandleToastButtonClick(e, "Button1", () => FileLauncher.OpenLinkInBrowser(LinkManager.MessageToastSupport));
    }

    private void HandleNotificationToastClick(object sender, AlertHtmlElementMouseEventArgs e)
    {
        HandleToastButtonClick(e, "Button1", () => ActionsManager.ExecuteAction(_action));
    }

    private void HandleLanguageToastClick(object sender, AlertHtmlElementMouseEventArgs e)
    {
        HandleToastButtonClick(e, "Button1", () => FileLauncher.OpenLinkInBrowser(LinkManager.LanguageToastLearn));
    }

    private void HandleUpdateToastClick(object sender, AlertHtmlElementMouseEventArgs e)
    {
        HandleToastButtonClick(e, "Button1", () => FileLauncher.OpenLinkInBrowser(LinkManager.UpdateToastDownload));
    }
}