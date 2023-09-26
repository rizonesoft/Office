using DevExpress.XtraEditors;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;

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

            InitializeComponent();

            Text = $@"About {companyName} {ProgramName}";
        }

        /// <summary>
        /// 
        /// </summary>
        public sealed override string Text
        {
            get => base.Text;
            set => base.Text = value;
        }
    }
}