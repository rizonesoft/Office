using DevExpress.Utils;
using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Utilities;
using System.Globalization;
using Rizonesoft.Office.ErrorHandling;

namespace Rizonesoft.Office.UI.Forms;

/// <summary>
/// Represents a base form with Ribbon control.
/// </summary>
public class RibbonFormBase : RibbonForm
{
    /// <inheritdoc/>
    protected override bool SupportAdvancedTitlePainting => true;

    /// <summary>
    /// Initializes a new instance of the RibbonFormBase class.
    /// </summary>
    public RibbonFormBase()
    {
        IconOptions.ShowIcon = false;
        LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
        ToolTipController.DefaultController.HyperlinkClick += DefaultController_HyperlinkClick;
        UpdateLanguage();
    }

    /// <summary>
    /// Performs post-initialization of components.
    /// </summary>
    public void AfterInitializeComponents()
    {
        AppearanceObject.DefaultFont = new Font("Segoe UI", 8.25F);
        Text = $@"{ProgramConfiguration.ProgramName} {ProgramConfiguration.Version?.major} {EnvironmentManager.Get("BETA_STRING")}";
    }

    private static void UpdateLanguage()
    {
        try
        {
            var newCulture = new CultureInfo(LanguageManager.LanguageCode);
            Thread.CurrentThread.CurrentCulture = newCulture;
            Thread.CurrentThread.CurrentUICulture = newCulture;
        }
        catch (CultureNotFoundException ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "Unable to update the language.", ex);
        }
    }

    private void LanguageManager_LanguageChanged(object? sender, EventArgs e)
    {
        UpdateLanguage();
    }

    private static void DefaultController_HyperlinkClick(object sender, HyperlinkClickEventArgs e)
    {
        FileLauncher.OpenLinkInBrowser(e.Link);
    }

    /// <summary>
    /// Disposes the resources used by the RibbonFormBase.
    /// </summary>
    // protected override void Dispose(bool disposing)
    // {
        // if (disposing)
        // {
            // LanguageManager.LanguageChanged -= LanguageManager_LanguageChanged;
            // LicenseHelper.LicenseKeyUpdated -= OnLicenseKeyUpdated;
            // ToolTipController.DefaultController.HyperlinkClick -= DefaultController_HyperlinkClick;
        // }
        // base.Dispose(disposing);
    // }
}
