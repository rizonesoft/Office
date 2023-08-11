using DevExpress.XtraBars;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.UI.Ribbon.Buttons
{
    /// <summary>
    /// Represents a Settings button in the ribbon.
    /// </summary>
    public class ButtonItemSettings : ButtonItemBase
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="ButtonItemSettings"/> class.
        /// </summary>
        /// <param name="barButtonItem">The BarButtonItem to configure.</param>
        /// <exception cref="ArgumentNullException">Thrown when barButtonItem is null.</exception>
        public ButtonItemSettings(BarButtonItem barButtonItem) : base(barButtonItem)
        {
        }

        /// <summary>
        /// Configures the BarButtonItem with appropriate settings.
        /// </summary>
        protected override void InitializeBarButtonItem()
        {
            _barButtonItem.ImageOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.UI.Resources.Settings.svg");
            _barButtonItem.Caption = Strings.RibbonButtonItem_Settings;
            _barButtonItem.ItemClick += BarButtonItem_ItemClick;
        }

        /// <summary>
        /// Handles the ItemClick event of the BarButtonItem.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="ItemClickEventArgs"/> instance containing the event data.</param>
        private void BarButtonItem_ItemClick(object? sender, ItemClickEventArgs e)
        {
            OnButtonClick();
        }

        /// <summary>
        /// Executes the action associated with the button click.
        /// </summary>
        protected override void OnButtonClick()
        {
            using var settingsForm = new SettingsForm
            {
                StartPosition = FormStartPosition.CenterParent,
            };

            settingsForm.ShowDialog();
            settingsForm.Dispose();
        }

        /// <summary>
        /// Updates the language of the BarButtonItem.
        /// </summary>
        /// <exception cref="ArgumentNullException">Thrown when barButtonItem is null.</exception>
        protected override void UpdateLanguage()
        {
            _barButtonItem.Caption = Strings.RibbonButtonItem_Settings;
        }
    }
}
