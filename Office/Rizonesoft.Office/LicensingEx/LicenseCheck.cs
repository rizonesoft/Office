using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.LicensingEx
{
    public static class LicenseCheck
    {
        public static bool IsLicensed()
        {
            string? licenseKey = LicensingEx.LicenseHelper.GetRegister(GlobalProperties.LicenseRegPath, "License");
            if (licenseKey != null && LicensingEx.LicenseHelper.IsLicensed(licenseKey, "Rizonesoft.Office.lDatabase.lic"))
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
