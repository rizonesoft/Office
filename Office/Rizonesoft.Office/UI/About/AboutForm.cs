using DevExpress.XtraEditors;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.UI.About
{
    /// <summary>
    /// 
    /// </summary>
    public partial class AboutForm : DirectXFormBase
    {
        private static readonly string? ProgramName = ProgramConfiguration.ProgramName;

        /// <summary>
        /// 
        /// </summary>
        public AboutForm()
        {
            const string companyName = GlobalConfiguration.CompanyName;
            var progVersionFull = ProgramConfiguration.Version?.fullVersion;
            var progVersionMajor = ProgramConfiguration.Version?.major;
            var officeVersion = GlobalConfiguration.ProductVersion;
            var runtimeVersion = RuntimeHelper.RuntimeVersion;

            InitializeComponent();

            Text = $@"About {ProgramName} {progVersionMajor}";

            programSvgImage.SvgImage = ImageResourceLoader.LoadSvgImageFromResource($"Rizonesoft.Office.Programs.Resources.{ProgramName}.svg");
            programNameLabel.Text = ProgramName;
            programVersionLabel.Text = $@"Version {progVersionFull}";
            officeVersionDataLabel.Text = officeVersion;
            runtimeDataLabel.Text = runtimeVersion;
        }

        /// <summary>
        /// 
        /// </summary>
        public sealed override string Text
        {
            get => base.Text;
            set => base.Text = value;
        }

        private void OkButton_Click(object sender, EventArgs e)
        {
            Close();
        }

        private void SautinSoftSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.Sautinsoft);
        }

        private void RizonesoftHomeLink_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutHomePage);
        }

        private void PayPalLink_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutDonate);
        }

        private void GitHubSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutGitHub);
        }

        private void XSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutTwitterX);
        }

        private void FacebookSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutFacebook);
        }

        private void DiscordSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutDiscord);
        }

        private void MailSvgImage_Click(object sender, EventArgs e)
        {
            FileLauncher.OpenLinkInBrowser(LinkManager.AboutMail);
        }
    }
}