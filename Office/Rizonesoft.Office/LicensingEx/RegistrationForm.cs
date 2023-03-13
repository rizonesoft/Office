using Rizonesoft.Office.Utilities;
using System.Text.RegularExpressions;

namespace Rizonesoft.Office.LicensingEx
{

    public partial class RegistrationForm : DevExpress.XtraEditors.DirectXForm
    {
        string cleanKey = string.Empty;

        public RegistrationForm()
        {

            InitializeComponent();
            CheckActivationStatus();

        }

        private static RegistrationForm? formInstance;

        public static RegistrationForm? CheckInstance
        {
            get
            {
                return formInstance;
            }
        }

        // Create a public static property that will create an instance of the form and return it
        public static RegistrationForm CreateInstance
        {
            get
            {
                formInstance ??= new RegistrationForm();
                return formInstance;
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            formInstance = null;
            base.OnClosed(e);
        }

        private void ActivateButton_Click(object sender, EventArgs e)
        {
            if (cleanKey.Length == 32)
            {
                if (LicenseHelper.IsLicensed(cleanKey, "Rizonesoft.Office.lDatabase.lic"))
                {
                    LicenseHelper.SetRegister(RizonesoftEx.LicenseRegPath, "License", cleanKey);
                    CheckActivationStatus();
                }
                else
                {
                    ActivateLabel.Text = "Invalid license key!";
                    ActivateLabel.ForeColor = Color.DarkRed;
                }


            }
        }

        private void TextLicenseCode_TextChanged(object sender, EventArgs e)
        {
            cleanKey = MyRegex().Replace(textLicenseCode.Text, "");

            if (cleanKey.Length == 32)
            {
                if (ActivateButton.Enabled == false)
                {
                    ActivateButton.Enabled = true;
                }
            }
            else
            {
                if (ActivateButton.Enabled == true)
                {
                    ActivateButton.Enabled = false;
                }
            }
        }

        private void RemoveActivationLink_Click(object sender, EventArgs e)
        {
            LicenseHelper.SetRegister(RizonesoftEx.LicenseRegPath, "License", string.Empty);
            CheckActivationStatus();

        }

        [GeneratedRegex("[ ().-]+")]
        private static partial Regex MyRegex();

        private void PasteButton_Click(object sender, EventArgs e)
        {
            string clipText;

            if (Clipboard.ContainsText())
            {
                clipText = Clipboard.GetText();
                cleanKey = MyRegex().Replace(clipText, "");
                textLicenseCode.Text = cleanKey;
                textLicenseCode.Focus();
            }

        }

        private void CheckActivationStatus()
        {
            bool IsLicensed = LicenseCheck.IsLicensed();

            if (IsLicensed)
            {
                IconOptions.SvgImage = coreSVGImageCollection[1];
                Text = "License activated!";
                mainSVGImageBox.SvgImage = coreSVGImageCollection[1];
                ActivateLabel.Text = "License activated!";
                ActivateLabel.ForeColor = Color.DarkGreen;

            }
            else
            {
                IconOptions.SvgImage = coreSVGImageCollection[0];
                Text = "License not activated!";
                mainSVGImageBox.SvgImage = coreSVGImageCollection[0];
                ActivateLabel.Text = "License not activated!";
                ActivateLabel.ForeColor = Color.DarkRed;
            }

            PasteButton.Visible = !IsLicensed;
            ActivateButton.Visible = !IsLicensed;
            PurchaseButton.Visible = !IsLicensed;
            textLicenseCode.Visible = !IsLicensed;
            RemoveActivationLink.Visible = IsLicensed;
            ThanksLabel.Visible = IsLicensed;

        }

        private void RegistrationForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            // this.DialogResult = DialogResult.OK;
        }

    }
}