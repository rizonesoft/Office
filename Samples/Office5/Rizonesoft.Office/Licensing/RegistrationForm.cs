using DevExpress.XtraEditors;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.DirectoryServices.ActiveDirectory;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Rizonesoft.Office.Licensing
{
    public partial class RegistrationForm : DevExpress.XtraEditors.DirectXForm
    {
        public RegistrationForm()
        {
            InitializeComponent();
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
                if (formInstance == null)
                {
                    formInstance = new RegistrationForm();
                }
                return formInstance;
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            formInstance = null;
            base.OnClosed(e);
        }

        private void ButtonActivate_Click(object sender, EventArgs e)
        {
            string licenseRegistryPath = @"HKEY_CURRENT_USER\Software\Rizonesoft\Office";
            string licenseRegistryValue = "License";

            Licensing.LicenseHelper.SetRegister(licenseRegistryPath, licenseRegistryValue, textLicenseCode.Text);

        }



        private void ButtonCancel_Click(object sender, EventArgs e)
        {

        }

        private void textLicenseCode_TextChanged(object sender, EventArgs e)
        {
            if (textLicenseCode.Text.Length == 32)
            {
                if (ButtonActivate.Enabled == false)
                {
                    ButtonActivate.Enabled = true;
                }
            }
            else
            {
                if (ButtonActivate.Enabled == true)
                {
                    ButtonActivate.Enabled = false;
                }
            }

        }
    }
}