using System.Threading.Tasks;
using CefSharp;
using CefSharp.WinForms;

namespace Rizonesoft.Office.Nerve.BrowserControl
{
    /// <summary>
    /// The BrowserScriptExecutor class is responsible for executing JavaScript
    /// code in the context of the ChromiumWebBrowser.
    /// </summary>
    public class BrowserScriptExecutor
    {
        private readonly ChromiumWebBrowser _chromiumWebBrowser;

        /// <summary>
        /// Initializes a new instance of the BrowserScriptExecutor class.
        /// </summary>
        /// <param name="chromiumWebBrowser">The ChromiumWebBrowser instance used to execute JavaScript.</param>
        public BrowserScriptExecutor(ChromiumWebBrowser chromiumWebBrowser)
        {
            _chromiumWebBrowser = chromiumWebBrowser;
        }

        public async Task<object> ExecuteScriptAsync(string script)
        {
            var result = await _chromiumWebBrowser.EvaluateScriptAsync(script);
            return result.Success ? result.Result : null;
        }

        public async Task<string> ExecuteScriptAsyncToString(string script)
        {
            var result = await _chromiumWebBrowser.EvaluateScriptAsync(script);
            return result.Success ? (string)result.Result : string.Empty;
        }
    }
}
