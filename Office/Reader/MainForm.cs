namespace Rizonesoft.Office.Reader
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Interprocess;
    using LicensingEx;
    using MessagesEx;
    using Rizonesoft.Office.Utilities;
    using System;
    using System.IO;
    using System.Linq;
    using System.Windows.Forms;
    using Utilities;

    internal sealed partial class MainForm : RibbonForm
    {
        // private bool IsFloating;
        // private bool IsLicensed;
        private static MruList _mruList;
        private CopyData copyData;
        private int viewerIndex;

        protected override bool SupportAdvancedTitlePainting => true;

        public MainForm(string fileName)
        {
            // WindowsFormsSettings.UseDXDialogs = DevExpress.Utils.DefaultBoolean.True;
            var sUpdateDismissed = Settings.Settings.GetSetting($"Rizonesoft\\{RizonesoftEx.ProductName}\\General",
                "UpdateMessage", "True");
            var isUpdateDismiss = RizonesoftEx.StringToBoolean(sUpdateDismissed ?? "False");

            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL, "Initializing");
            CreateProgramDirectories();
            OnShowMdiChildCaptionInParentTitle();
            InitializeComponent();
            RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();
            RizonesoftEx.IsBetaVersion = true;

            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL,
                string.IsNullOrEmpty(fileName) ? "Creating Document" : "Loading Document");
            CreateNewViewer(fileName);

            Text = $@"{StcReader.ProductName} {RizonesoftEx.ProductVersionMajor}";
            Initialize();
            // mCreateNewViewer(StcReader.WelcomePDFPath);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL, $"Completed - Loading {StcReader.ProductName}");

            if (isUpdateDismiss)
            {
                OfficeUpdate.CheckForUpdates();
            }
        }

        private ViewerForm CurrentViewer
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (mainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return mainTabbedMdiManager.ActiveFloatForm as ViewerForm;
                }

                return ActiveMdiChild as ViewerForm;
            }
        }

        private static void AddFileToMruList(string fileName)
        {
            if (string.IsNullOrEmpty(fileName)) return;
            try
            {
                _mruList.AddFile(fileName);
            }
            catch (Exception ex)
            {
                _mruList.RemoveFile(fileName);
                Logging.Logger.Error(ex, "Unable to add filename to MRU list.");
            }
        }

        private void CreateNewViewer(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (var openForm in MdiChildren.Cast<ViewerForm>())
                {
                    if (string.Compare(openForm.FileName, fileName, StringComparison.OrdinalIgnoreCase) != 0) continue;
                    openForm.Activate();
                    return;
                }
            }
            else
            {
                viewerIndex++;
            }

            ViewerForm newViewer = new();
            newViewer.OpenFile(fileName, viewerIndex);
            newViewer.MdiParent = this;
            newViewer.Show();
        }

        private void OpenFile(string fileName)
        {
            CreateNewViewer(fileName);
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveRibbon();
            SaveSettings();
            SaveSkins();
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            RestoreRibbon();
            SplashScreenManager.CloseForm(false);
        }

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcReader.UserAppDirectory))
            {
                Directory.CreateDirectory(StcReader.UserAppDirectory);
            }
        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private static void SetSkins()
        {
            var sSkin = Settings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Skin", "WXI");
            var sPalette = Settings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Palette", "Freshness");
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("PDFChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewViewer(fileName);
                AddFileToMruList(fileName);
            }
        }

        private void Initialize()
        {
            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels?.Add("PDFChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void LoadSettings()
        {
            RizonesoftEx.GeometryFromString(Settings.Settings.GetSetting(StcReader.CurrentRegGeneralPath, "Geometry", string.Empty) ?? string.Empty, this);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            mainRibbonControl.ForceInitialize();
            _mruList = new MruList("MRU", mruPopupMenu, 10, StcReader.CurrentRegMruPath);
            _mruList.FileSelected += MruList_FileSelected;
            // CheckLicense();
        }

        private void MainRibbonControl_Merge(object sender, RibbonMergeEventArgs e)
        {
            var parentRibbon = sender as RibbonControl;
            var childRibbon = e.MergedChild;
            if (parentRibbon?.StatusBar != null && childRibbon.StatusBar != null)
            {
                parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            if (string.IsNullOrEmpty(fileName)) return;
            if (File.Exists(fileName))
            {
                OpenFile(fileName);
            }
            else
            {
                if (XtraMessageBox.Show(
                        $"Could not find \"{fileName}\"! It is gone. " +
                        "It vanished. It is no more, or maybe you moved it? " +
                        "Not sure what is going on here, but I know that entry does not belong on the \"Most Recently Used Documents\" list.\n\nWould you like me to remove it?",
                        @"Could not find that document.",
                        MessageBoxButtons.YesNo,
                        MessageBoxIcon.Exclamation) ==
                    DialogResult.Yes)
                {
                    _mruList.RemoveFile(fileName);
                }
            };
        }

        private void OpenFileFolder(string sIniDir)
        {

            var openFileDlg = new OpenFileDialog
            {
                CheckFileExists = true,
                CheckPathExists = true,
                Multiselect = false,
                SupportMultiDottedExtensions = true,
                ValidateNames = true,
                RestoreDirectory = true,
                AddExtension = true,
                DefaultExt = "pdf",
                FileName = sIniDir,
                ShowHelp = true
            };

            if (sIniDir != string.Empty)
            {
                openFileDlg.InitialDirectory = sIniDir;
            }

            openFileDlg.Filter = "PDF Document (*.pdf)|*.pdf";
            openFileDlg.FilterIndex = 1;
            openFileDlg.Title = "Select a Document";

            var dlgResult = openFileDlg.ShowDialog();

            // Show the dialog and get result.
            if (dlgResult != DialogResult.OK) return;
            var fileName = openFileDlg.FileName;
            OpenFile(fileName);
            AddFileToMruList(fileName);
        }

        private void RestoreRibbon()
        {
            mainRibbonControl?.Toolbar.RestoreLayoutFromRegistry(StcReader.StaticRegInterfacePath);
        }

        private void SaveRibbon()
        {
            mainRibbonControl?.Toolbar.SaveLayoutToRegistry(StcReader.StaticRegInterfacePath);
        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcReader.CurrentRegGeneralPath, "Geometry", RizonesoftEx.GeometryToString(this));
        }

        private void barOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFile();
        }
    }
}