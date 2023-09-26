using System.Net.Http;
using System.Reflection;
using System.Xml.Linq;
using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Toast;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.Update;

/// <summary>
/// OfficeUpdate class is responsible for checking and notifying about updates to the Office application.
/// </summary>
public static class OfficeUpdate
{
    private const string UpdateXmlUrl = "https://cdn2.rizonesoft.com/update/office.xml";
    private const string DefaultDownloadUrl = "https://www.rizonesoft.com/downloads/rizonesoft-office/update/";
    private static bool _messageShown;
    private static readonly HttpClient HttpClient = new();

    /// <summary>
    /// Check for an Office update and notify the user if one exists.
    /// </summary>
    /// <param name="ribbonControl">The ribbon control to show the update message on.</param>
    /// <returns>An empty string if no update was found, otherwise the new version number.</returns>
    public static async Task<string> GetOfficeUpdateAsync(RibbonControl ribbonControl)
    {
        Version? newVersion = null;
        string downloadUrl = DefaultDownloadUrl;

        try
        {
            var response = await HttpClient.GetStringAsync(UpdateXmlUrl).ConfigureAwait(false);
            var document = XDocument.Parse(response);

            var versionElement = document.Root?.Element("version");
            var urlElement = document.Root?.Element("url");
            if (versionElement != null)
            {
                newVersion = new Version(versionElement.Value);
                downloadUrl = urlElement?.Value ?? DefaultDownloadUrl;
            }
        }
        catch (HttpRequestException ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "HTTP request failed!", ex);
            return string.Empty;
        }

        var applicationVersion = Assembly.GetExecutingAssembly().GetName().Version;

        if (newVersion == null || applicationVersion == null || applicationVersion.CompareTo(newVersion) >= 0)
        {
            return string.Empty;
        }

        if (!_messageShown)
        {
            ShowMessage(ribbonControl, newVersion, downloadUrl);
            _messageShown = true;
        }

        return $"{newVersion.Major}.{newVersion.Minor}.{newVersion.Build}";
    }

    /// <summary>
    /// Shows the update message on the specified ribbon control.
    /// </summary>
    /// <param name="ribbonControl">The ribbon control to show the message on.</param>
    /// <param name="newVersion">The new version that is available.</param>
    /// <param name="downloadUrl">The download URL for the new version.</param>
    private static void ShowMessage(RibbonControl ribbonControl, IFormattable newVersion, string downloadUrl)
    {

        var args = new RibbonMessageArgs
        {
            Caption = Strings.OfficeUpdate_Caption,
            Text = string.Format(Strings.OfficeUpdate_Message, newVersion),
            Buttons = new[] { DialogResult.OK },
            ImageOptions =
            {
                SvgImage = ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.UI.Resources.Globe.svg")
            }
        };

        args.Showing += Args_Showing;

        // Define the event handler with a lambda expression and store it in a variable
        void Handler(object s, RibbonMessageClosedArgs e) => Ribbon_MessageClosed(s, e, downloadUrl);

        ribbonControl.ShowMessage(args);
        ribbonControl.MessageClosed += Handler;
    }

    private static void Ribbon_MessageClosed(object sender, RibbonMessageClosedArgs e, string downloadUrl)
    {
        if (e.Result == DialogResult.OK)
        {
            FileLauncher.OpenLinkInBrowser(downloadUrl);
        }

        // Unsubscribe from MessageClosed event
        if (sender is RibbonControl ribbonControl)
        {
            // Define the event handler with a lambda expression and store it in a variable
            void Handler(object s, RibbonMessageClosedArgs eventArgs) => Ribbon_MessageClosed(s, e, downloadUrl);

            ribbonControl.MessageClosed -= Handler;
        }
        _messageShown = false;
    }

    private static void Args_Showing(object? sender, RibbonMessageShowingArgs e)
    {
        e.Buttons[DialogResult.OK].Caption = Strings.OfficeUpdate_Button;
    }
}
