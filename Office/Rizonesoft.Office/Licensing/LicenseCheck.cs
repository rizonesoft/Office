using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.Licensing
{
    public static class LicenseCheck
    {
        public static bool IsLicensed()
        {
            string licenseRegistryPath = @"HKEY_CURRENT_USER\Software\Rizonesoft\Office";
            string licenseRegistryValue = "License";

            string licenseKey = Licensing.LicenseHelper.GetRegister(licenseRegistryPath, licenseRegistryValue);
            if (licenseKey != null && Licensing.LicenseHelper.IsLicensed(licenseKey, "Rizonesoft.Office.License.lic"))
            {
                return true;
            }
            else
            {
                return false;
            }
        }
    }
}
