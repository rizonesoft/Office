using DevExpress.XtraEditors;
using Rizonesoft.Office.Localization;
using System.Globalization;

namespace Rizonesoft.Office.UI.Forms
{
    /// <summary>
    /// A base class for all DevExpress DirectX forms that require localization. It subscribes to the LanguageManager.LanguageChanged event
    /// and updates the form's language automatically when the event is fired.
    /// </summary>
    public class DirectXFormBase : DirectXForm
    {
        /// <summary>
        /// Initializes a new instance of the DevExpressLocalizedDirectXFormBase class.
        /// </summary>
        public DirectXFormBase()
        {
            UpdateLanguage();
            LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
        }

        /// <summary>
        /// Updates the form's language based on the current language code stored in the LanguageManager.
        /// </summary>
        private void UpdateLanguage()
        {
            var newCulture = new CultureInfo(LanguageManager.LanguageCode);
            Thread.CurrentThread.CurrentCulture = newCulture;
            Thread.CurrentThread.CurrentUICulture = newCulture;
        }

        /// <summary>
        /// Event handler for the LanguageManager.LanguageChanged event.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">An EventArgs that contains the event data.</param>
        private void LanguageManager_LanguageChanged(object? sender, EventArgs e)
        {
            UpdateLanguage();
        }

        /// <summary>
        /// Overridden Dispose method to unsubscribe from the LanguageManager.LanguageChanged event.
        /// </summary>
        /// <param name="disposing">True to release both managed and unmanaged resources; false to release only unmanaged resources.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                LanguageManager.LanguageChanged -= LanguageManager_LanguageChanged;
            }
            base.Dispose(disposing);
        }
    }
}

