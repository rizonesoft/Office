namespace Rizonesoft.Office.MessagesEx
{
    using DevExpress.Utils.Svg;
    using System;

    /// <summary>
    /// MessageData record represents a message with a caption, message, and an icon.
    /// It is designed to be used with the MessageForm to display messages to the user.
    /// </summary>
    public record MessageData
    {
        /// <summary>
        /// Initializes a new instance of the MessageData record.
        /// </summary>
        /// <param name="caption">The caption of the message.</param>
        /// <param name="message">The message text to display.</param>
        /// <param name="messageIcon">The icon to display with the message.</param>
        /// <exception cref="ArgumentNullException">Thrown when the messageIcon is null.</exception>
        public MessageData(string? caption, string? message, SvgImage? messageIcon)
        {
            Caption = caption ?? string.Empty;
            Message = message ?? string.Empty;
            MessageIcon = messageIcon ?? throw new ArgumentNullException(nameof(messageIcon));
        }

        /// <summary>
        /// Gets or initializes the caption of the message.
        /// </summary>
        public string Caption { get; init; }

        /// <summary>
        /// Gets or initializes the message text to display.
        /// </summary>
        public string Message { get; init; }

        /// <summary>
        /// Gets or initializes the icon to display with the message.
        /// </summary>
        public SvgImage MessageIcon { get; init; }
    }
}
