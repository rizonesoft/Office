using Rizonesoft.Office.Settings;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Collections.Generic;
using Rizonesoft.Office.ErrorHandling;

namespace Rizonesoft.Office.Licensing
{
    /// <summary>
    /// Helper class for managing licenses.
    /// </summary>
    public static class LicenseHelper
    {
        private const string LicenseKeyResourcePath = "Rizonesoft.Office.Licensing.lDatabase.lic";
        private static bool? _isLicensed;
        private static string? _licenseCode;
        private static string InvalidLicenseKeyMessage = "Invalid license key. The key must be 32 characters long after removing whitespace and '-' characters.";

        // Define an event to be called when the license key is updated
        public static event Action LicenseKeyUpdated;

        /// <summary>
        /// Gets the license code.
        /// </summary>
        public static string LicenseCode => _licenseCode ??= GlobalSettings.LicenseCode;

        /// <summary>
        /// Validates a license key.
        /// </summary>
        /// <param name="licenseKey">The license key to validate.</param>
        /// <returns>The validated license key.</returns>
        /// <exception cref="ArgumentException">Thrown if the license key is invalid.</exception>
        private static string ValidateLicenseKey(string licenseKey)
        {
            licenseKey = licenseKey.Replace("-", "").Replace(" ", "");

            if (licenseKey.Length != 32)
            {
                throw new ArgumentException(InvalidLicenseKeyMessage, nameof(licenseKey));
            }

            return licenseKey;
        }

        /// <summary>
        /// Sets the license code and refreshes the license status.
        /// If no license code is provided, the license code is read from the global settings.
        /// </summary>
        /// <param name="licenseCode">The new license code. If null, the license code is read from the global settings.</param>
        public static bool SetLicenseCode(string? licenseCode = null)
        {
            try
            {
                _licenseCode = ValidateLicenseKey(licenseCode ?? GlobalSettings.LicenseCode);
                _isLicensed = null; // Reset the license status so it's refreshed the next time it's accessed.
                LicenseKeyUpdated?.Invoke();
                return true;
            }
            catch (ArgumentException ex)
            {
                Serilogger.LogMessage(LogLevel.Error, "Something went wrong while setting the license.", ex);
                return false;
            }
        }

        /// <summary>
        /// Removes the license code and resets the license status.
        /// </summary>
        public static void UnsetLicenseCode()
        {
            _licenseCode = null;
            _isLicensed = null;
            GlobalSettings.LicenseCode = "";

            LicenseKeyUpdated?.Invoke();
        }

        /// <summary>
        /// Asynchronously checks whether the application is licensed.
        /// </summary>
        /// <returns>true if the application is licensed; otherwise, false.</returns>
        public static async Task<bool> CheckLicenseAsync()
        {
            HashSet<string> licenseKeys;
            try
            {
                licenseKeys = new HashSet<string>(await GetLicenseKeysFromResourceAsync());
            }
            catch (Exception ex)
            {
                // Log exception
                throw new ApplicationException("Well, this is embarrassing. We've encountered an error while verifying your license. Please try again later or contact our support.", ex);
            }

            using var sha256Hash = SHA256.Create();
            return licenseKeys.Contains(GetSha256Hash(sha256Hash, LicenseCode).ToUpper());
        }

        /// <summary>
        /// Asynchronously gets the license keys from an embedded resource.
        /// </summary>
        /// <returns>An array of license keys.</returns>
        private static async Task<IEnumerable<string>> GetLicenseKeysFromResourceAsync()
        {
            var assembly = Assembly.GetExecutingAssembly();
            await using var resourceStream = assembly.GetManifestResourceStream(LicenseKeyResourcePath)
                                             ?? throw new FileNotFoundException("We've encountered a glitch in the matrix. Your license verification failed. Please try again or contact our support. Resource file {LicenseKeyResourcePath} not found.");
            using var resourceReader = new StreamReader(resourceStream);
            var licenseData = await resourceReader.ReadToEndAsync();

            return licenseData.Split(Environment.NewLine, StringSplitOptions.RemoveEmptyEntries);
        }

        /// <summary>
        /// Creates an SHA256 hash from the specified input string.
        /// </summary>
        /// <param name="sha256Hash">The SHA256 instance to use.</param>
        /// <param name="input">The string to hash.</param>
        /// <returns>The SHA256 hash of the input string.</returns>
        private static string GetSha256Hash(SHA256 sha256Hash, string input)
        {
            var data = sha256Hash.ComputeHash(Encoding.UTF8.GetBytes(input));
            return BitConverter.ToString(data).Replace("-", "").ToLowerInvariant();
        }
    }
}
