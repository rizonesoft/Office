using DevExpress.Utils.Svg;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.Toast
{
    /// <summary>
    /// Helper class to create and display toast notifications of various types.
    /// </summary>
    public static class ToastHelper
    {
        private const string ToastResourcesPath = "Rizonesoft.Office.Toast.Resources.";

        private static readonly SvgImage CloseButtonIcon =
            ImageResourceLoader.LoadSvgImageFromResource(ToastResourcesPath + "Close.svg");

        /// <summary>
        /// Creates and shows an error toast notification.
        /// </summary>
        /// <param name="errorCaption">The caption for the error toast.</param>
        /// <param name="errorMessage">The error message for the error toast.</param>
        public static void CreateErrorToast(string errorCaption, string errorMessage)
        {
            CreateToast("Error.svg", errorCaption, errorMessage, ToastType.MessageToast);
        }

        /// <summary>
        /// Creates and shows a debugging toast notification.
        /// </summary>
        /// <param name="debugCaption">The caption for the debugging toast.</param>
        /// <param name="debugMessage">The debugging message for the debugging toast.</param>
        public static void CreateDebuggingToast(string debugCaption, string debugMessage)
        {
            CreateToast("Debugging.svg", debugCaption, debugMessage, ToastType.MessageToast);
        }

        /// <summary>
        /// Creates and shows an information toast notification.
        /// </summary>
        /// <param name="infoCaption">The caption for the information toast.</param>
        /// <param name="infoMessage">The information message for the information toast.</param>
        public static void CreateInformationToast(string infoCaption, string infoMessage)
        {
            CreateToast("Info.svg", infoCaption, infoMessage, ToastType.MessageToast);
        }

        /// <summary>
        /// Creates and shows a warning toast notification.
        /// </summary>
        /// <param name="warningCaption">The caption for the warning toast.</param>
        /// <param name="warningMessage">The warning message for the warning toast.</param>
        public static void CreateWarningToast(string warningCaption, string warningMessage)
        {
            CreateToast("Warning.svg", warningCaption, warningMessage, ToastType.MessageToast);
        }

        /// <summary>
        /// Creates and shows a fatal toast notification.
        /// </summary>
        /// <param name="fatalCaption">The caption for the fatal toast.</param>
        /// <param name="fatalMessage">The fatal message for the fatal toast.</param>
        public static void CreateFatalToast(string fatalCaption, string fatalMessage)
        {
            CreateToast("Skull.svg", fatalCaption, fatalMessage, ToastType.MessageToast);
        }

        /// <summary>
        /// Creates and shows an update toast with the specified caption and message.
        /// </summary>
        /// <param name="updateCaption">The caption for the update toast.</param>
        /// <param name="updateMessage">The message for the update toast.</param>
        public static void CreateUpdateToast(string updateCaption, string updateMessage)
        {
            CreateToast("Globe.svg", updateCaption, updateMessage, ToastType.UpdateToast, "Download");
        }

        /// <summary>
        /// Creates and shows a notification toast.
        /// </summary>
        /// <param name="notificationCaption">The caption for the notification toast.</param>
        /// <param name="notificationMessage">The notification message for the notification toast.</param>
        /// <param name="stringButtonCaption">The button caption for the notification toast.</param>
        public static void CreateNotificationToast(string notificationCaption, string notificationMessage,
            string stringButtonCaption)
        {
            CreateToast("Notification.svg", notificationCaption, notificationMessage, ToastType.NotificationToast,
                stringButtonCaption);
        }

        /// <summary>
        /// Creates and shows a language toast.
        /// </summary>
        /// <param name="flagIcon">The flag icon for the language toast.</param>
        public static void CreateLanguageToast(SvgImage? flagIcon)
        {
            var toastData = new ToastData(
                ImageResourceLoader.LoadSvgImageFromResource(ToastResourcesPath + "Notification.svg"),
                Strings.Toast_LanguageChanged_Header, CloseButtonIcon, flagIcon,
                Strings.Toast_LanguageChanged, Strings.Toast_Button_LearnMore,
                Strings.Toast_Button_Dismiss);
            var toastForm = new ToastForm(toastData, ToastType.LanguageToast);
            toastForm.Show();
        }

        /// <summary>
        /// Creates and shows a toast notification.
        /// </summary>
        /// <param name="iconResource">The icon resource for the toast.</param>
        /// <param name="caption">The caption for the toast.</param>
        /// <param name="message">The message for the toast.</param>
        /// <param name="toastType">The type of the toast.</param>
        /// <param name="buttonCaption">The button caption for the toast (optional).</param>
        private static void CreateToast(string iconResource, string caption, string message, ToastType toastType,
            string buttonCaption = "Support")
        {
            var icon = ImageResourceLoader.LoadSvgImageFromResource(ToastResourcesPath + iconResource);

            ToastData toastData = new(
                icon, caption, CloseButtonIcon,
                icon, message,
                buttonCaption, "Dismiss");

            var toastForm = new ToastForm(toastData, toastType);
            toastForm.Show();
        }
    }
}
