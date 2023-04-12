using CefSharp;
using System;
using System.Windows.Forms;
using DevExpress.XtraBars;
using System.Threading.Tasks;
using DevExpress.XtraEditors;
using DevExpress.LookAndFeel;
using Rizonesoft.Office.Nerve.BrowserControl;


namespace Rizonesoft.Office.Nerve
{
    /// <summary>
    /// Main form for the Rizonesoft.Office.Nerve application.
    /// </summary>
    public partial class MainForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        private readonly Timer checkSelectionTimer;
        private readonly BrowserInitializer browserInitializer;

        /// <summary>
        /// Gets a value indicating whether the ChromiumWebBrowser is disposed.
        /// </summary>
        public bool IsChromiumWebBrowserDisposed => chromiumWebBrowser1.IsDisposed;


        /// <summary>
        /// Initializes a new instance of the <see cref="MainForm"/> class.
        /// </summary>
        public MainForm()
        {
            InitializeComponent();

            browserInitializer = new BrowserInitializer(chromiumWebBrowser1);
            browserInitializer.Initialize();

            RegisterEventHandlers();
            //modeToggleButton.ItemClick += async (sender, e) => { await ClickLinkByTextAsync("Clear conversations"); };

            checkSelectionTimer = new Timer
            {
                Interval = 300
            };

            checkSelectionTimer.Tick += async (_, _) => { await UpdateCopyButtonStateAsync(); };
        }


        private void RegisterEventHandlers()
        {
            chromiumWebBrowser1.StatusMessage += ChromiumWebBrowser_StatusMessage;
            chromiumWebBrowser1.LoadingStateChanged += ChromiumWebBrowser_LoadingStateChanged;
            chromiumWebBrowser1.AddressChanged += ChromiumWebBrowser_AddressChanged;
            chromiumWebBrowser1.FrameLoadEnd += ChromiumWebBrowser1_FrameLoadEnd;
            modeToggleButton.ItemClick += modeToggleButton_Click;
        }




        private async void modeToggleButton_Click(object sender, ItemClickEventArgs e)
        {
            string currentMode = await GetCurrentModeAsync();
            if (string.IsNullOrEmpty(currentMode))
            {
                return;
            }

            string targetMode = currentMode == "Light mode" ? "Dark mode" : "Light mode";
            string clickedLinkText = await ClickLinkByTextAsync(targetMode);

            if (!string.IsNullOrEmpty(clickedLinkText))
            {
                UpdateModeButton(clickedLinkText);
                this.BeginInvoke((Action)(() => SetLookAndFeel(clickedLinkText)));
            }
        }

        private void UpdateModeButton(string currentMode)
        {
            if (currentMode == "Light mode")
            {
                modeToggleButton.Caption = "Dark mode";
                modeToggleButton.ImageOptions.SvgImage = BrowserSvgImageCollection[1];
            }
            else
            {
                modeToggleButton.Caption = "Light mode";
                modeToggleButton.ImageOptions.SvgImage = BrowserSvgImageCollection[0];
            }
        }

        private async Task<string> GetCurrentModeAsync()
        {
            string script = $@"
    (function() {{
        var links = document.getElementsByTagName('a');
        var darkModeLinkVisible = false;
        var lightModeLinkVisible = false;
        
        for (var i = 0; i < links.length; i++) {{
            if (links[i].textContent.trim() === 'Dark mode') {{
                darkModeLinkVisible = true;
            }} else if (links[i].textContent.trim() === 'Light mode') {{
                lightModeLinkVisible = true;
            }}
        }}
        
        if (darkModeLinkVisible) {{
            return 'Light mode';
        }} else if (lightModeLinkVisible) {{
            return 'Dark mode';
        }} else {{
            return '';
        }}
    }})();";

            var result = await chromiumWebBrowser1.EvaluateScriptAsync(script);
            return result.Success ? (string)result.Result : string.Empty;
        }

        private async Task<string> ClickLinkByTextAsync(string linkText)
        {
            string script = $@"
            (function() {{
                var links = document.getElementsByTagName('a');
                var clickedLinkText = '';
                for (var i = 0; i < links.length; i++) {{
                    if (links[i].textContent.trim() === '{linkText}') {{
                        links[i].click();
                        clickedLinkText = links[i].textContent.trim();
                        break;
                    }}
                }}
                return clickedLinkText;
            }})();";

            var result = await chromiumWebBrowser1.EvaluateScriptAsync(script);
            return result.Success ? (string)result.Result : string.Empty;
        }

        private async void ChromiumWebBrowser1_FrameLoadEnd(object? sender, FrameLoadEndEventArgs e)
        {
            if (!e.Frame.IsMain) return;
            checkSelectionTimer.Enabled = true;
            var currentMode = await GetCurrentModeAsync();
            if (!string.IsNullOrEmpty(currentMode))
            {
                UpdateModeButton(currentMode);
                BeginInvoke(() => SetLookAndFeel(currentMode));
                modeToggleButton.Enabled = true; // Enable the mode button
            }
            else
            {
                modeToggleButton.Enabled = false; // Disable the mode button
            }

            // Hide the Dark mode and Light mode links on the website
            await HideModeLinksAsync();
            // Add this line to ensure the loading state is properly updated
            loadingEditItem.Visibility = BarItemVisibility.Never;
        }

        private async Task HideModeLinksAsync()
        {
            string script = @"
        (function() {
            var links = document.getElementsByTagName('a');
            for (var i = 0; i < links.length; i++) {
                if (links[i].textContent.trim() === 'Dark mode' || links[i].textContent.trim() === 'Light mode') {
                    links[i].style.display = 'none';
                }
            }
        })();";

            await chromiumWebBrowser1.EvaluateScriptAsync(script);
        }

        private async Task SetWebsiteModeAsync(string targetMode)
        {
            string clickedLinkText = await ClickLinkByTextAsync(targetMode);

            if (!string.IsNullOrEmpty(clickedLinkText))
            {
                UpdateModeButton(clickedLinkText);
                SetLookAndFeel(clickedLinkText);
            }
        }


        private void SetLookAndFeel(string mode)
        {
            switch (mode)
            {
                case "Light mode":
                    WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle("WXI", "Clearness");
                    break;
                case "Dark mode":
                    WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle("WXI", "Darkness");
                    break;
            }

            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();
        }

        private async void CopyButtonItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            await CopySelectedTextAsync();
        }


        private async Task GetSelectedTextAsync()
        {
            string script = "window.getSelection().toString()";
            var selectedText = await chromiumWebBrowser1.EvaluateScriptAsync(script);

            if (selectedText != null && selectedText.Success && selectedText.Result != null)
            {
                string result = selectedText.Result.ToString();
                MessageBox.Show(result, "Selected Text");
            }
        }

        private async Task UpdateCopyButtonStateAsync()
        {
            if (IsChromiumWebBrowserDisposed) return;

            string script = "window.getSelection().toString()";
            var selectedText = await chromiumWebBrowser1.EvaluateScriptAsync(script);

            if (selectedText != null && selectedText.Success && selectedText.Result != null)
            {
                copyButtonItem.Enabled = !string.IsNullOrEmpty(selectedText.Result.ToString());
            }
            else
            {
                copyButtonItem.Enabled = false;
            }
        }

        private async Task CopySelectedTextAsync()
        {
            string script = "document.execCommand('copy')";
            await chromiumWebBrowser1.EvaluateScriptAsync(script);
        }


        private void ChromiumWebBrowser_StatusMessage(object? sender, StatusMessageEventArgs e)
        {
            messageStatusItem.Caption = e.Value;
        }

        private void ChromiumWebBrowser_LoadingStateChanged(object? sender, LoadingStateChangedEventArgs e)
        {
            // Show the loading animation
            loadingEditItem.Visibility = e.IsLoading ? BarItemVisibility.Always : BarItemVisibility.Never;
        }


        private void ChromiumWebBrowser_AddressChanged(object? sender, AddressChangedEventArgs e)
        {
            // Update status bar with base URL of website being loaded
            messageStatusItem.Caption = e.Address;
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            Cef.Shutdown();
        }

        private async void Form1_Load(object sender, EventArgs e)
        {
        }
    }
}