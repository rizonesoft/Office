using DevExpress.Utils.Svg;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.Toast;

/// <summary>
/// Represents data used for creating toast notifications that will blow minds, shatter expectations, and change lives.
/// </summary>
public record ToastData
{
    private static readonly SvgImage defaultHeaderIcon =
        ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Toast.Resources.Notification.svg");

    /// <summary>
    /// Constructs a new instance of <see cref="ToastData"/>.
    /// </summary>
    /// <param name="headerIcon">The header icon, or the default icon if null.</param>
    /// <param name="headerCaption">The header caption, or an empty string if null.</param>
    /// <param name="closeButtonIcon">The close button icon, or the default icon if null.</param>
    /// <param name="messageIcon">The message icon, or the default icon if null.</param>
    /// <param name="message">The message, or an empty string if null.</param>
    /// <param name="button1Caption">The caption of button 1, or an empty string if null.</param>
    /// <param name="button2Caption">The caption of button 2, or an empty string if null.</param>
    public ToastData(SvgImage? headerIcon, string? headerCaption, SvgImage? closeButtonIcon, SvgImage? messageIcon,
        string? message, string? button1Caption, string? button2Caption)
    {
        HeaderIcon = headerIcon ?? defaultHeaderIcon;
        HeaderCaption = headerCaption ?? string.Empty;
        CloseButtonIcon = closeButtonIcon ?? defaultHeaderIcon;
        MessageIcon = messageIcon ?? defaultHeaderIcon;
        Message = message ?? string.Empty;
        Button1Caption = button1Caption ?? string.Empty;
        Button2Caption = button2Caption ?? string.Empty;
    }

    /// <summary>
    /// Gets or sets the header icon that will captivate the user's soul.
    /// </summary>
    public SvgImage HeaderIcon { get; init; }

    /// <summary>
    /// Gets or sets the header caption that will make Shakespeare weep with envy.
    /// </summary>
    public string HeaderCaption { get; init; }

    /// <summary>
    /// Gets or sets the close button icon that users will find irresistible to click.
    /// </summary>
    public SvgImage CloseButtonIcon { get; init; }

    /// <summary>
    /// Gets or sets the message icon that speaks a thousand words, and then some.
    /// </summary>
    public SvgImage MessageIcon { get; init; }

    /// <summary>
    /// Gets or sets the message that will spark a revolution in the user's mind.
    /// </summary>
    public string Message { get; init; }

    /// <summary>
    /// Gets or sets the caption of button 1 that will entice users to click with fervor.
    /// </summary>
    public string Button1Caption { get; init; }

    /// <summary>
    /// Gets or sets the caption of button 2 that will seduce users into submission.
    /// </summary>
    public string Button2Caption { get; init; }
}