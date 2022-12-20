namespace Rizonesoft.Office.Flow
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Flow.Utilities;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.Utilities;
    using System;
    using System.ComponentModel;
    using System.IO;
    using System.Linq;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private static MruList mruList;
        internal int diagramIndex;
        internal bool IsFloating;
        internal bool isLicensed;
        internal BackgroundWorker updateWorker;

        #region Properties

        DiagramForm CurrentViewer
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (mainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return mainTabbedMdiManager.ActiveFloatForm as DiagramForm;
                }

                return ActiveMdiChild as DiagramForm;
            }
        }

        #endregion Properties

        public MainForm(string fileName)
        {
            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            OnShowMdiChildCaptionInParentTitle();
            CreateProgramDirectories();
            InitializeComponent();
            base.Text = $"{StcFlow.ProductName} {GlobalProperties.ProductVersionMajor}";

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcFlow.ProductName}");
            CreateNewDiagram(fileName);

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
            copyData.Channels.Add("DiagramChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("DiagramChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewDiagram(fileName);
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
                    Logging.ROLogger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            //OpenFile(fileName);
        }

        #endregion Initialize

        #region Diagram Processing

        public void CreateNewDiagram(string fileName)
        {

            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (DiagramForm openForm in MdiChildren.Cast<DiagramForm>())
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
                diagramIndex++;
            }

            DiagramForm newViewer = new();
            newViewer.OpenFile(fileName, diagramIndex);
            newViewer.MdiParent = this;
            newViewer.Show();
        }

        #endregion Diagram Processing

        #region Merging

        private void MainRibbonControl_Merge(object sender, RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
        }

        #endregion Merging

        #region Settings

        private void LoadSettings()
        {
            GlobalFunctions.GeometryFromString(Settings.Settings.GetSetting(StcFlow.CurrentRegGeneralPath, "Geometry", string.Empty), this);

        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcFlow.CurrentRegGeneralPath, "Geometry", GlobalFunctions.GeometryToString(this));

        }

        private static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(StcFlow.CurrentRegInterfacePath, "Skin", "Office 2019 Colorful");
            string sPalette = Settings.Settings.GetSetting(StcFlow.CurrentRegInterfacePath, "Palette", "Amber");
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);

        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcFlow.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcFlow.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private bool SaveRestoreRibbon(bool SaveRibbon)
        {
            if (mainRibbonControl != null)
            {
                switch (SaveRibbon)
                {
                    case true:
                        mainRibbonControl.Toolbar.SaveLayoutToRegistry(StcFlow.StaticRegInterfacePath);
                        return true;
                    case false:
                        mainRibbonControl.Toolbar.RestoreLayoutFromRegistry(StcFlow.StaticRegInterfacePath);
                        return true;
                }
            }

            return false;

        }

        #endregion Settings

        #region Configurations

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcFlow.UserAppDirectory))
            {
                Directory.CreateDirectory(StcFlow.UserAppDirectory);
            }
        }

        #endregion Configurations

        
    }
}
