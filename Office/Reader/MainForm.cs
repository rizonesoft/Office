namespace Rizonesoft.Office.Reader
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.Licensing;
    using Rizonesoft.Office.Reader.Utilities;
    using Rizonesoft.Office.ROUtilities;
    using System;
    using System.ComponentModel;
    using System.IO;
    using System.Linq;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private static MruList mruList;
        internal int viewerIndex;
        internal bool IsFloating;
        internal bool isLicensed;
        internal BackgroundWorker updateWorker;

        #region Properties

        ViewerForm CurrentViewer
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

        #endregion Properties

        public MainForm(string fileName)
        {
            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            isLicensed = LicenseCheck.IsLicensed();
            OnShowMdiChildCaptionInParentTitle();
            CreateProgramDirectories();
            InitializeComponent();
            base.Text = $"{StcReader.ProductName} {ROGlobals.ProductVersionYear}";

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcReader.ProductName}");
            CreateNewViewer(fileName);

        }

        #region Overrides

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            SaveRestoreRibbon(false);
            SplashScreenManager.CloseForm(false);
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveRestoreRibbon(true);
            SaveSettings();
            SaveSkins();
        }

        #endregion Overrides

        #region Initialize

        private void Initialize()
        {
            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels.Add("PDFChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("PDFChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewViewer(fileName);
                AddFileToMRUList(fileName);
            }
        }

        public static void AddFileToMRUList(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                try
                {
                    mruList.AddFile(fileName);
                }
                catch (IOException ioEx)
                {
                    mruList.RemoveFile(fileName);
                    ROLogging.ROLogger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            // OpenFile(fileName);
        }

        #endregion Initialize

        #region Viewer Processing

        public void CreateNewViewer(string fileName)
        {

            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (ViewerForm openForm in MdiChildren.Cast<ViewerForm>())
                {
                    if (string.Compare(openForm.FileName, fileName, true) == 0)
                    {
                        openForm.Activate();
                        return;
                    }
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

        #endregion Viewer Processing

        #region Settings

        private void LoadSettings()
        {
            ROFunctions.GeometryFromString(ROSettings.Settings.GetSetting(StcReader.CurrentRegGeneralPath, "Geometry", string.Empty), this);

        }

        private void SaveSettings()
        {
            ROSettings.Settings.SaveSetting(StcReader.CurrentRegGeneralPath, "Geometry", ROFunctions.GeometryToString(this));

        }

        private static void SetSkins()
        {
            string sSkin = ROSettings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Skin", "Office 2019 Colorful");
            string sPalette = ROSettings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Palette", "Fire Brick");
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);

        }

        private static void SaveSkins()
        {
            ROSettings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            ROSettings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private bool SaveRestoreRibbon(bool SaveRibbon)
        {
            if (mainRibbonControl != null)
            {
                switch (SaveRibbon)
                {
                    case true:
                        mainRibbonControl.Toolbar.SaveLayoutToRegistry(StcReader.StaticRegInterfacePath);
                        return true;
                    case false:
                        mainRibbonControl.Toolbar.RestoreLayoutFromRegistry(StcReader.StaticRegInterfacePath);
                        return true;
                }
            }

            return false;

        }

        #endregion Settings

        #region Configurations

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcReader.UserAppDirectory))
            {
                Directory.CreateDirectory(StcReader.UserAppDirectory);
            }
        }

        #endregion Configurations

    }
}
