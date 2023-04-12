namespace Rizonesoft.Office.MessagesEx
{
    using DevExpress.XtraBars.Alerter;
    using DevExpress.XtraEditors;
    using Utilities;

    /// <summary>
    /// MessageForm class inherits from DevExpress.XtraEditors.DirectXForm.
    /// This form is responsible for displaying messages to the user.
    /// </summary>
    public partial class MessageForm : DirectXForm
    {

        /// <summary>
        /// Default constructor initializes the components.
        /// </summary>
        public MessageForm() => InitializeComponent();

        /// <summary>
        /// Constructor that takes a MessageData object as a parameter.
        /// Initializes the components and sets up event handlers.
        /// </summary>
        /// <param name="messageData">MessageData object containing message information.</param>
        public MessageForm(MessageData messageData) : this()
        {
            messageAlertControl.HtmlElementMouseClick += HandleHtmlElementMouseClick;
            messageAlertControl.Show(messageData, this);
        }

        /// <summary>
        /// Handles HtmlElementMouseClick event for messageAlertControl.
        /// Performs actions based on the clicked element's ID.
        /// </summary>
        /// <param name="sender">Event sender.</param>
        /// <param name="e">Event arguments containing information about the clicked element.</param>
        private static void HandleHtmlElementMouseClick(object? sender, AlertHtmlElementMouseEventArgs e)
        {
            if (e.ElementId == "dismissButton" || e.ParentHasId("dismissButton"))
            {
                Settings.Settings.SaveSetting($"Rizonesoft\\{RizonesoftEx.ProductName}\\General", "UpdateMessage", "False");
                e.HtmlPopup.Close();
            }
            else if (e.ElementId == "updateButton" || e.ParentHasId("updateButton"))
            {
                System.Diagnostics.Process.Start("https://www.rizonesoft.com");
            }
            else if (e.ElementId == "closeButton" || e.ParentHasId("closeButton"))
            {
                e.HtmlPopup.Close();
            }
        }

        /// <summary>
        /// Handles the FormClosing event for messageAlertControl.
        /// Prevents the form from closing if the close reason is time-up.
        /// </summary>
        /// <param name="sender">Event sender.</param>
        /// <param name="e">Event arguments containing information about the form closing.</param>
        private void MessageAlertControl_FormClosing(object? sender, AlertFormClosingEventArgs e)
        {
            if (e.CloseReason == AlertFormCloseReason.TimeUp) e.Cancel = true;
        }

    }
}