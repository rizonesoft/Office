using DevExpress.LookAndFeel;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.UI.Ribbon.Buttons;

/// <summary>
/// Manages themes for the application.
/// </summary>
public class ToggleModeButton
{
    private const string LightPalletteName = "Clearness";
    private const string DarkPalletteName = "Darkness";
    private const string LightModeSvgResourceName = "Rizonesoft.Office.UI.Resources.Sun.svg";
    private const string DarkModeSvgResourceName = "Rizonesoft.Office.UI.Resources.Moon.svg";

    private bool _isDarkMode;
    private readonly Control _ownerControl;

    /// <summary>
    /// Initializes a new instance of the <see cref="ToggleModeButton"/> class.
    /// </summary>
    /// <param name="ownerControl">The owner control for displaying the overlay during theme changes.</param>
    public ToggleModeButton(Control ownerControl)
    {
        _ownerControl = ownerControl;
        _isDarkMode = LoadThemeModeAsync().Result;
    }

    /// <summary>
    /// Initializes the toggle mode button.
    /// </summary>
    /// <param name="barButtonItem">The BarButtonItem representing the toggle mode button.</param>
    public void Initialize(BarButtonItem barButtonItem)
    {
        barButtonItem.ItemClick += HandleToggleModeButtonClick;
    }

    /// <summary>
    /// Toggles the theme mode between dark and light.
    /// </summary>
    /// <param name="barButtonItem">The bar button item to update the icon for.</param>
    /// <param name="ownerControl">The owner control for displaying the overlay.</param>
    public async Task ToggleModeAsync(BarButtonItem barButtonItem, Control? ownerControl)
    {
        _isDarkMode = !_isDarkMode;
        await SaveThemeModeAsync(_isDarkMode);
        ApplyThemeMode(barButtonItem, ownerControl, true);
    }

    /// <summary>
    /// Applies the current theme mode.
    /// </summary>
    /// <param name="barButtonItem">The bar button item to update the icon for.</param>
    /// <param name="ownerControl">The owner control for displaying the overlay.</param>
    /// <param name="showOverlay">Indicates whether to show the overlay during theme change.</param>
    public void ApplyThemeMode(BarButtonItem? barButtonItem = null, Control? ownerControl = null,
        bool showOverlay = false)
    {
        var overlayManager = new OverlayManager();

        if (showOverlay && ownerControl != null)
        {
            overlayManager.ShowOverlay(ownerControl);
        }

        try
        {
            if (_isDarkMode)
            {
                SetPaletteMode(DarkPalletteName);
                if (barButtonItem == null) return;
                barButtonItem.ImageOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource(LightModeSvgResourceName);
                UpdateToggleModeButton(barButtonItem);
            }
            else
            {
                SetPaletteMode(LightPalletteName);
                if (barButtonItem == null) return;
                barButtonItem.ImageOptions.SvgImage = ImageResourceLoader.LoadSvgImageFromResource(DarkModeSvgResourceName);
                UpdateToggleModeButton(barButtonItem);
            }
        }
        finally
        {
            overlayManager.DisposeOverlay();
        }

    }

    private static void SetPaletteMode(string palletteName)
    {
        var currentSkinName = UserLookAndFeel.Default.SkinName;
        WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(currentSkinName, palletteName);
        LookAndFeelHelper.ForceDefaultLookAndFeelChanged();
    }

    private static Task<bool> LoadThemeModeAsync()
    {
        return Task.FromResult(GlobalSettings.IsDarkMode);
    }

    private static Task SaveThemeModeAsync(bool isDarkMode)
    {
        GlobalSettings.IsDarkMode = isDarkMode;
        return Task.CompletedTask;
    }

    /// <summary>
    /// Handles the click event for the toggle mode button.
    /// </summary>
    /// <param name="sender">The object that raised the event.</param>
    /// <param name="e">Event arguments.</param>
    private async void HandleToggleModeButtonClick(object sender, ItemClickEventArgs e)
    {
        if (e.Item is BarButtonItem barButtonItem)
        {
            // Assuming you have access to the ownerControl instance, you can replace it with the actual instance you have.
            await ToggleModeAsync(barButtonItem, _ownerControl);
        }
    }

    /// <summary>
    /// Updates the toggle mode button text based on the current theme mode.
    /// </summary>
    /// <param name="barButtonItem">The BarButtonItem representing the toggle mode button.</param>
    public void UpdateToggleModeButton(BarButtonItem barButtonItem)
    {
        barButtonItem.Caption = _isDarkMode ? Strings.ThemeManager_Button_Light_mode : Strings.ThemeManager_Button_Dark_mode;
    }

}