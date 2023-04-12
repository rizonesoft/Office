namespace Rizonesoft.Office.Nerve.BrowserControl
{
    using CefSharp;
    using CefSharp.WinForms;

    /// <summary>
    /// The BrowserInitializer class is responsible for initializing and managing
    /// browser settings for the ChromiumWebBrowser.
    /// </summary>
    public class BrowserInitializer
    {
        // The ChromiumWebBrowser instance to be initialized and managed
        private readonly ChromiumWebBrowser _chromiumWebBrowser;

        /// <summary>
        /// Initializes a new instance of the BrowserInitializer class.
        /// </summary>
        /// <param name="chromiumWebBrowser">The ChromiumWebBrowser instance to be initialized and managed.</param>
        public BrowserInitializer(ChromiumWebBrowser chromiumWebBrowser)
        {
            _chromiumWebBrowser = chromiumWebBrowser;
        }

        /// <summary>
        /// Initializes the browser settings and loads the initial URL.
        /// </summary>
        public void Initialize()
        {
            InitializeCefSettings();
            InitializeBrowser();
        }

        /// <summary>
        /// Initializes the CefSharp settings for the application.
        /// </summary>
        private void InitializeCefSettings()
        {
            var settings = new CefSettings
            {
                CachePath = @"C:\cache\",
                UserDataPath = @"C:\user-data\",
                PersistSessionCookies = true,
                PersistUserPreferences = true
            };

            Cef.Initialize(settings);
        }

        /// <summary>
        /// Initializes the ChromiumWebBrowser instance with the initial URL.
        /// </summary>
        private void InitializeBrowser()
        {
            _chromiumWebBrowser.Load("https://chat.openai.com/chat");
        }
    }
}
