using System.IO;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Licensing;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Update;
using Rizonesoft.Office.Utilities;
using RibbonControl = DevExpress.XtraBars.Ribbon.RibbonControl;

namespace Rizonesoft.Office.UI.Ribbon
{
    /// <summary>
    /// Represents a Ribbon Support Page, which includes various Ribbon items and events.
    /// </summary>
    public class RibbonPageSupport : IDisposable
    {
        private bool disposed;

        private readonly RibbonPage ribPageSupport;

        public RibbonPage SupportPage => ribPageSupport;
       
        private readonly RibbonPageGroup ribGroupDiscover;
        private readonly RibbonPageGroup ribGroupUpdate;
        private readonly RibbonPageGroup ribGroupContribute;
        private readonly RibbonPageGroup ribGroupLicense;
        private readonly RibbonPageGroup ribGroupDebug;
        private readonly RibbonPageGroup ribGroupAbout;
        private readonly BarButtonItem barItemHome;
        private readonly BarButtonItem barItemHelpDocs;
        private readonly BarButtonItem barItemSupport;
        private readonly BarButtonItem barItemRegistration;
        private readonly BarButtonItem barItemUpdate;

        /// <summary>
        /// Gets the RibbonControl that this page support belongs to.
        /// </summary>
        public RibbonControl RibbonControl { get; init; }

        /// <summary>
        /// Initializes a new instance of the <see cref="RibbonPageSupport"/> class.
        /// </summary>
        /// <param name="ribbonControl">An instance of <see cref="RibbonControl"/>.</param>
        /// <exception cref="ArgumentNullException">Thrown when <paramref name="ribbonControl"/> is null.</exception>
        public RibbonPageSupport(RibbonControl ribbonControl)
        {
            RibbonControl = ribbonControl ?? throw new ArgumentNullException(nameof(ribbonControl));
            ribPageSupport = new RibbonPage(Strings.RibbonPageSupport)
            {
                MergeOrder = 99
            };

            ribGroupDiscover = new RibbonPageGroup(Strings.RibbonPageSupport_Discover);
            ribGroupUpdate = new RibbonPageGroup(Strings.RibbonPageSupport_Update);
            ribGroupContribute = new RibbonPageGroup(Strings.RibbonPageSupport_Contribute);
            ribGroupLicense = new RibbonPageGroup(Strings.RibbonPageSupport_Registration);
            ribGroupDebug = new RibbonPageGroup(Strings.RibbonPageSupport_Debug);
            ribGroupAbout = new RibbonPageGroup(Strings.RibbonPageSupport_About);

            barItemHome = CreateButtonItem(ribbonControl, string.Format(Strings.RibbonButtonItem_Home, GlobalConfiguration.CompanyName), "Globe.svg", BarItemHome_Click);
            SuperTipHelper.CreateSuperTooltip(barItemHome, Strings.RibbonButtonSuperTip_Home, LinkManager.ButtonHomeSuperTip);
            barItemHelpDocs = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_HelpDocs, "Help.svg", BarItemHelpDocs_Click);
            SuperTipHelper.CreateSuperTooltip(barItemHelpDocs, Strings.RibbonButtonSuperTip_HelpDocs, LinkManager.ButtonHelpDocsSuperTip);
            barItemSupport = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_Support, "Support.svg", BarItemSupport_Click);
            SuperTipHelper.CreateSuperTooltip(barItemSupport, Strings.RibbonButtonSuperTip_Support, LinkManager.ButtonSupportSuperTip);
            barItemUpdate = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_Update, "Update.svg", BarItemUpdate_Click);
            SuperTipHelper.CreateSuperTooltip(barItemUpdate, Strings.RibbonButtonSuperTip_Update, LinkManager.ButtonUpdateSuperTip);
            var barItemLicense = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_License, "Key.svg", BarItemLicense_Click);
            SuperTipHelper.CreateSuperTooltip(barItemLicense, string.Format(Strings.RibbonButtonSuperTip_License, ProgramConfiguration.CompanyName, ProgramConfiguration.ProgramName), LinkManager.ButtonLicenseeSuperTip);
            barItemRegistration = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_GetLicense, "Gift.svg", BarItemRegistration_Click);
            SuperTipHelper.CreateSuperTooltip(barItemRegistration, Strings.RibbonButtonSuperTip_GetLicense, LinkManager.ButtonGetLicenseSuperTip);
            var barItemSuggestions = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_Suggestions, "Suggestions.svg", BarItemSuggestions_Click);
            SuperTipHelper.CreateSuperTooltip(barItemSuggestions, Strings.RibbonButtonSuperTip_Suggestions, LinkManager.ButtonSuggestionsSuperTip);
            var barItemDonate = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_Donate, "Donate.svg", BarItemDonate_Click);
            SuperTipHelper.CreateSuperTooltip(barItemDonate, Strings.RibbonButtonSuperTip_Donate, LinkManager.ButtonDonateSuperTip);
            var barItemException = CreateButtonItem(ribbonControl, Strings.RibbonButtonItem_Exception, "Exception.svg", BarButtonItem_ItemClick);
            SuperTipHelper.CreateSuperTooltip(barItemException, Strings.RibbonButtonSuperTip_Exception, LinkManager.ButtonExceptionSuperTip);
            var barItemAbout = CreateButtonItem(ribbonControl, "About", "About.svg", BarItemAbout_Click);

            ribGroupDiscover.ItemLinks.AddRange(barItemHome, barItemHelpDocs, barItemSupport);
            ribGroupUpdate.ItemLinks.Add(barItemUpdate);
            ribGroupContribute.ItemLinks.AddRange(barItemSuggestions, barItemDonate);
            ribGroupLicense.ItemLinks.AddRange(barItemLicense, barItemRegistration);
            ribGroupDebug.ItemLinks.Add(barItemException);
            ribGroupAbout.ItemLinks.Add(barItemAbout);

            ribPageSupport.Groups.AddRange(new[] { ribGroupDiscover, ribGroupUpdate, ribGroupLicense, ribGroupContribute, ribGroupDebug, ribGroupAbout });
            ribbonControl.Pages.Add(ribPageSupport);
            ribbonControl.PageHeaderItemLinks.Add(barItemSuggestions);

            LanguageManager.LanguageChanged += UpdateLanguage;
            _ = CheckForUpdates(true);
            LicenseHelper.LicenseKeyUpdated += OnLicenseKeyUpdated;
            LicenseHelper.SetLicenseCode(GlobalSettings.LicenseCode);
            ConfigureLicense();
        }

        /// <summary>
        /// Releases all resources used by the current instance of the <see cref="RibbonPageSupport"/> class.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Releases all resources used by the current instance of the <see cref="RibbonPageSupport"/> class.
        /// </summary>
        /// <param name="disposing">True to release both managed and unmanaged resources; false to release only unmanaged resources.</param>
        protected virtual void Dispose(bool disposing)
        {
            if (disposed) return;
            if (disposing)
            {
                // Unsubscribe from events
                LanguageManager.LanguageChanged -= UpdateLanguage;
                barItemHome.ItemClick -= BarItemHome_Click;
                barItemHelpDocs.ItemClick -= BarItemHelpDocs_Click;
                barItemSupport.ItemClick -= BarItemSupport_Click;
                barItemUpdate.ItemClick -= BarItemUpdate_Click;
            }

            disposed = true;
        }

        ~RibbonPageSupport()
        {
            Dispose(false);
        }


        /// <summary>
        /// Creates a BarButtonItem with the specified parameters.
        /// </summary>
        /// <param name="ribbonControl">The Ribbon control.</param>
        /// <param name="caption">The caption of the BarButtonItem.</param>
        /// <param name="svgImage">The SVG image for the BarButtonItem.</param>
        /// <param name="clickHandler">The click event handler for the BarButtonItem.</param>
        /// <returns>A BarButtonItem with the specified parameters.</returns>
        private static BarButtonItem CreateButtonItem(RibbonControl ribbonControl, string caption, string svgImage,
            ItemClickEventHandler clickHandler)
        {
            var item = new BarButtonItem(ribbonControl.Manager, caption)
            {

                Id = ribbonControl.Manager.GetNewItemId()
            };
            item.ImageOptions.SvgImage =
                ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.UI.Resources." + svgImage);
            item.ItemClick += clickHandler;
            return item;
        }

        private static void BarItemHome_Click(object sender, ItemClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.HomePageButton);
        }

        private static void BarItemHelpDocs_Click(object sender, ItemClickEventArgs e)
        {
            var baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
            var manualPath = Path.Combine(baseDirectory, "Documentation", "Office Unleashed.pdf");
            FileLauncher.OpenPdfInScholar(manualPath);
        }

        private static void BarItemSupport_Click(object sender, ItemClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.SupportButton);
        }

        private async void BarItemUpdate_Click(object sender, ItemClickEventArgs e)
        {
            barItemUpdate.Enabled = false;
            await CheckForUpdates();
            barItemUpdate.Enabled = true;
        }

        private static void BarItemSuggestions_Click(object sender, ItemClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.SuggestionsButton);
        }

        private void BarItemLicense_Click(object sender, ItemClickEventArgs e)
        {
            try
            {
                if (LicenseForm.CheckInstance == null)
                {
                    if (LicenseForm.CreateInstance.ShowDialog() != DialogResult.OK) return;
                    ConfigureLicense();
                }
                else
                {
                    // These two lines make sure the state is normal (not min or max) and give it focus.
                    LicenseForm.CreateInstance.WindowState = FormWindowState.Normal;
                    LicenseForm.CreateInstance.Focus();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, @"Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void BarItemRegistration_Click(object sender, ItemClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.RegistrationButton);
        }

        private static void BarItemDonate_Click(object sender, ItemClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.DonateButton);
        }

        private void BarButtonItem_ItemClick(object? sender, ItemClickEventArgs e)
        {
            throw new NotImplementedException($"Test Exception");
        }

        private void BarItemAbout_Click(object sender, ItemClickEventArgs e)
        {
            // Implement the action for this event
        }

        private async Task CheckForUpdates(bool delay = false)
        {
            try
            {
                if (delay)
                {
                    await Task.Delay(TimeSpan.FromSeconds(20));  // delay for 20 seconds
                }

                await OfficeUpdate.GetOfficeUpdateAsync(RibbonControl);
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, "Update check failed!", ex);
            }
        }

        private async void ConfigureLicense()        
        {
            var isLicensed = await LicenseHelper.CheckLicenseAsync();
            barItemRegistration.Visibility = isLicensed ? BarItemVisibility.Never : BarItemVisibility.Always;
        }

        /// <summary>
        /// Updates the language of the RibbonPageSupport.
        /// </summary>
        private void UpdateLanguage(object? sender, EventArgs e)
        {
            ribPageSupport.Text = Strings.RibbonPageSupport;
            ribGroupDiscover.Text = Strings.RibbonPageSupport_Discover;
            ribGroupUpdate.Text = Strings.RibbonPageSupport_Update;
            ribGroupContribute.Text = Strings.RibbonPageSupport_Contribute;
            ribGroupLicense.Text = Strings.RibbonPageSupport_Registration;
            ribGroupDebug.Text = Strings.RibbonPageSupport_Debug;
            ribGroupAbout.Text = Strings.RibbonPageSupport_About;

            barItemHome.Caption = string.Format(Strings.RibbonButtonItem_Home, GlobalConfiguration.CompanyName);
            SuperTipHelper.UpdateSuperTipTextAndFooter(barItemHelpDocs, Strings.RibbonButtonSuperTip_Home, LinkManager.ButtonHelpDocsSuperTip);
            barItemHelpDocs.Caption = Strings.RibbonButtonItem_HelpDocs;
            SuperTipHelper.UpdateSuperTipTextAndFooter(barItemHelpDocs, Strings.RibbonButtonSuperTip_HelpDocs, LinkManager.ButtonHelpDocsSuperTip);
            barItemSupport.Caption = Strings.RibbonButtonItem_Support;
            SuperTipHelper.UpdateSuperTipTextAndFooter(barItemSupport, Strings.RibbonButtonSuperTip_Support, LinkManager.ButtonSupportSuperTip);
            barItemUpdate.Caption = Strings.RibbonButtonItem_Update;
            SuperTipHelper.UpdateSuperTipTextAndFooter(barItemUpdate, Strings.RibbonButtonSuperTip_Update, LinkManager.ButtonUpdateSuperTip);

        }

        private void OnLicenseKeyUpdated()
        {
            ConfigureLicense();
        }

    }
}