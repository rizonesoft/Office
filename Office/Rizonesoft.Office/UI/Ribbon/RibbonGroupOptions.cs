using System.Globalization;
using System.Windows;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Toast;
using Rizonesoft.Office.UI.Ribbon.Buttons;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.UI.Ribbon
{

    /// <summary>
    /// Represents a group of options in the Ribbon UI for the Office application suite.
    /// </summary>
    public class RibbonGroupOptions
    {
        private readonly RibbonPageGroup _groupOptions;
        
        private BarButtonItem _barItemSettings;
        private BarButtonItem _barItemLanguage;
        private PopupMenu _popupLanguageMenu;

        /// <summary>
        /// Gets or sets a value indicating whether the language dropdown is visible.
        /// </summary>
        public bool IsLanguageDropdownVisible
        {
            get => _barItemLanguage.Visibility == BarItemVisibility.Always;
            set => _barItemLanguage.Visibility = value ? BarItemVisibility.Always : BarItemVisibility.Never;
        }

        /// <summary>
        /// Initializes a new instance of the RibbonGroupOptions class.
        /// </summary>
        /// <param name="ownerRibbonForm">The form that hosts the RibbonControl.</param>
        /// <param name="ownerRibbon">The RibbonControl to which this group belongs.</param>
        /// <param name="ribbonGroup">The RibbonPageGroup to which this group belongs.</param>
        public RibbonGroupOptions(RibbonForm ownerRibbonForm, RibbonControl ownerRibbon, RibbonPageGroup ribbonGroup)
        {
            if (ribbonGroup == null || ownerRibbon == null || ownerRibbonForm == null)
            {
                throw new ArgumentNullException(nameof(ribbonGroup),
                    @"You'd think developers would know not to pass a null object, right?");
            }

            _groupOptions = ribbonGroup;
            InitializeRibbonControls(ownerRibbonForm, ownerRibbon);

            LanguageManager.LanguageChanged += (_, _) => UpdateLanguage();
        }

        /// <summary>
        /// Initializes the ribbon controls for the RibbonGroupOptions.
        /// </summary>
        /// <param name="ownerRibbonForm">The form that hosts the RibbonControl.</param>
        /// <param name="ownerRibbon">The RibbonControl to which this group belongs.</param>
        private void InitializeRibbonControls(RibbonForm ownerRibbonForm, RibbonControl ownerRibbon)
        {
            _barItemSettings = CreateBarButtonItem(ownerRibbon.Manager, Strings.RibbonButtonItem_Settings, RibbonItemStyles.All);
            _barItemLanguage = CreateLanguageBarButtonItem(ownerRibbon.Manager);

            _groupOptions.Text = Strings.RibbonGroup_Options;
            _groupOptions.ItemLinks.AddRange(_barItemSettings, _barItemLanguage);

            ButtonItemBase.Create<ButtonItemSettings>(_barItemSettings);
            InitializeSuperTooltips();
        }


        /// <summary>
        /// Creates a new BarButtonItem with the specified parameters.
        /// </summary>
        /// <param name="manager">The BarManager to which the BarButtonItem belongs.</param>
        /// <param name="caption">The text displayed by the BarButtonItem.</param>
        /// <param name="style">The style of the BarButtonItem.</param>
        /// <returns>A new BarButtonItem with the specified parameters.</returns>
        private static BarButtonItem CreateBarButtonItem(BarManager manager, string caption, RibbonItemStyles style)
        {
            var barItem = new BarButtonItem(manager, caption)
            {
                RibbonStyle = style
            };
            return barItem;
        }

        /// <summary>
        /// Creates a new BarButtonItem for the language selection with a PopupMenu.
        /// </summary>
        /// <param name="manager">The BarManager to which the BarButtonItem belongs.</param>
        /// <returns>A new BarButtonItem for the language selection with a PopupMenu.</returns>
        private BarButtonItem CreateLanguageBarButtonItem(BarManager manager)
        {
            _popupLanguageMenu = new PopupMenu(manager);

            var barItem = new BarButtonItem(manager, "Language")
            {
                ButtonStyle = BarButtonStyle.DropDown,
                DropDownControl = _popupLanguageMenu,
                RibbonStyle = RibbonItemStyles.All
            };

            LanguageManager.InitializeLanguageMenu(barItem, _popupLanguageMenu);

            return barItem;
        }

        /// <summary>
        /// Initializes super tooltips for the RibbonGroupOptions UI elements.
        /// </summary>
        private void InitializeSuperTooltips()
        {
            SuperTipHelper.CreateSuperTooltip(_barItemSettings, Strings.RibbonButtonSuperTip_Settings, LinkManager.ButtonSettingsSuperTip);
            SuperTipHelper.CreateSuperTooltip(_barItemLanguage, Strings.RibbonButtonSuperTip_Language, LinkManager.ButtonLanguageSuperTip);
        }

        /// <summary>
        /// Updates the language for the RibbonGroupOptions UI elements.
        /// </summary>
        private void UpdateLanguage()
        {
            LanguageManager.UpdateLanguageDropDownButton(_barItemLanguage, CultureInfo.CurrentCulture);
            if (_barItemLanguage.ImageOptions != null)
            {
                ToastHelper.CreateLanguageToast(_barItemLanguage.ImageOptions.SvgImage);
            }
            _groupOptions.Text = Strings.RibbonGroup_Options;
        }
    }

}