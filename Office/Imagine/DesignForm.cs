using System;
using System.Windows.Forms;
using DevExpress.XtraReports.Security;
using DevExpress.XtraReports.UI;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.UI.Ribbon;

namespace Rizonesoft.Office.Imagine
{
    public partial class DesignForm : RibbonFormBase
    {
        private readonly CopyData copyData;
        private RibbonPageSupport pageRibbonSupport;

        public static bool IsLicensed { get; private set; }

        private const string CopyChannelName = "DesignChannel";

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveSettings();
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName != null && !e.ChannelName.Equals(CopyChannelName)) return;
            if (WindowState == FormWindowState.Minimized)
            {
                WindowState = FormWindowState.Normal;
            }

            var fileName = (string)e.Data;
            // CreateNewDocument(fileName);
            // AddFileToMruList(fileName);
            Activate();
        }

        public DesignForm(string fileName)
        {
            SplashScreenHelper.ShowSplashScreen(this);
            Opacity = 0;

            InitializeComponent();
            AfterInitializeComponents();
            InitializeRibbon();

            // ScriptPermissionManager.GlobalInstance = new ScriptPermissionManager(ExecutionMode.Unrestricted);

            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels?.Add(CopyChannelName);
            copyData.DataReceived += CopyData_DataReceived;

            FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
            mainRibbon.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
            xrDesignDockManager1.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Docking");
            DevExpress.XtraReports.Configuration.Settings.Default.StorageOptions.RootDirectory = CommonSettings.InitialOpenDir;
        }

        private void InitializeRibbon()
        {
            //ribbonMain.ForceInitialize();
            //_ = new RibbonGroupOptions(this, ribbonMain, OptionsRibbonGroup)
            //{
            //IsLanguageDropdownVisible = false
            //};
            pageRibbonSupport = new RibbonPageSupport(mainRibbon);

        }

        private void DesignForm_Shown(object sender, EventArgs e)
        {
            SplashScreenHelper.CloseSplashScreen();
            Opacity = 1;
        }

        private void SaveSettings()
        {
            CommonSettings.Geometry = FormGeometry.GeometryToString(this);
            mainRibbon.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
            if (commandBarItem2.Down == false && mainRibbon.SelectedPage != pageRibbonSupport.SupportPage)
            {
                xrDesignDockManager1.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Docking");
            }
        }

        private void DesignForm_Load(object sender, EventArgs e)
        {


        }
    }
}
