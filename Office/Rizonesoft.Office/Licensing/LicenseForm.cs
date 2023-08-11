using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.Utilities;
using Rizonesoft.Office.Programs;

namespace Rizonesoft.Office.Licensing
{

    /// <summary>
    /// This namespace represents Rizonesoft Office Licensing system.
    /// </summary>
    public partial class LicenseForm : FormBase
    {

        /// <summary>
        /// Initializes a new instance of the <see cref="LicenseForm"/> class.
        /// </summary>
        public LicenseForm()
        {
            InitializeComponent();

            LanguageManager.LanguageChanged += UpdateLanguage;
            LicenseHelper.LicenseKeyUpdated += OnLicenseKeyUpdated;
            LicenseHelper.SetLicenseCode(GlobalSettings.LicenseCode);
            ConfigureLicense();
        }


        /// <summary>
        /// Gets the singleton instance of the <see cref="LicenseForm"/>.
        /// </summary>
        public static LicenseForm? CheckInstance { get; private set; }

        /// <summary>
        /// Singleton instance for the LicenseForm. If it doesn't exist, it will be created.
        /// </summary>
        public static LicenseForm CreateInstance
        {
            get
            {
                CheckInstance ??= new LicenseForm();
                return CheckInstance;
            }
        }

        /// <summary>
        /// This method is invoked when the form is closed. It sets the singleton instance to null.
        /// </summary>
        /// <param name="e">The EventArgs associated with the OnClosed event.</param>
        protected override void OnClosed(EventArgs e)
        {
            CheckInstance = null;
            base.OnClosed(e);
        }

        private async void ActivateButton_Click(object sender, EventArgs e)
        {
            try
            {
                if (LicenseHelper.SetLicenseCode(LicenseCodeText.Text))
                {
                    if (await LicenseHelper.CheckLicenseAsync())
                    {
                        XtraMessageBox.Show(Strings.LicenseForm_LicenseValid_Message,
                            Strings.LicenseForm_LicenseValid_Title, MessageBoxButtons.OK, MessageBoxIcon.Information);
                        GlobalSettings.LicenseCode = LicenseCodeText.Text;
                    }
                    else
                    {
                        XtraMessageBox.Show(Strings.LicenseForm_LicenseInValid_Message,
                            Strings.LicenseForm_LicenseInValid_Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
            catch (ArgumentException)
            {
                XtraMessageBox.Show(Strings.LicenseForm_LicenseError_Message,
                    Strings.LicenseForm_LicenseInValid_Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }


        private async void ConfigureLicense()
        {
            var isLicensed = await LicenseHelper.CheckLicenseAsync();

            try
            {
                var securitySvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.UI.Resources.Security.svg");
                var keySvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.UI.Resources.Key.svg");

                IconOptions.SvgImage = isLicensed ? securitySvgImage : keySvgImage;
                Text = isLicensed ? Strings.LicenseForm_Activated : Strings.LicenseForm_NotActivated;
                FormSVGIcon.SvgImage = isLicensed ? securitySvgImage : keySvgImage;
                LicenseActiveLabel.Text = isLicensed ? Strings.LicenseForm_Activated : Strings.LicenseForm_NotActivated;
                ThanksLabel.Text = isLicensed ? Strings.LicenseForm_ThanksLabel : string.Format(Strings.LicenseForm_ThanksLabel_NotRegistered, 
                    ProgramConfiguration.CompanyName, ProgramConfiguration.SuiteName, LinkManager.LicenseFormGetLicense);

                var componentsToToggle = new Control[] { PasteButton, ActivateButton, GetLicenseButton, LicenseCodeText };
                foreach (var component in componentsToToggle)
                {
                    component.Visible = !isLicensed;
                }

                DeleteLicenseLink.Visible = isLicensed;

                UpdateLanguage(null, null);
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, Strings.ExceptionForm_Title, ex);
            }
        }

        private void UpdateLanguage(object? sender, EventArgs? e)
        {
            Text = Strings.LicenseForm_Title;
            DeleteLicenseLink.Text = Strings.LicenseForm_DeleteLicense;
            PasteButton.Text = Strings.LicenseForm_PasteButton;
            ActivateButton.Text = Strings.LicenseForm_ActivateButton;
            GetLicenseButton.Text = Strings.LicenseForm_GetLicenseButton;
            CloseButton.Text = Strings.LicenseForm_CloseButton;
        }

        private void OnLicenseKeyUpdated()
        {
            ConfigureLicense();
        }

        private void DeleteLicenseLink_HyperlinkClick(object sender, DevExpress.Utils.HyperlinkClickEventArgs e)
        {
            if (XtraMessageBox.Show("Are you sure you want to go back to living life on the edge, running our software without a license? We do warn you, the constant feeling of rebellion might be too much excitement to handle. If you're absolutely sure, go ahead and click 'Yes'.",
                    "Strings.LicenseForm_Confirmation", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.Yes)
            {
                LicenseHelper.UnsetLicenseCode();
            }
        }

        private void ThanksLabel_HyperlinkClick(object sender, DevExpress.Utils.HyperlinkClickEventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(e.Link);
        }
    }
}