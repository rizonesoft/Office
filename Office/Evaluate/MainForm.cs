namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using System;
    using System.ComponentModel;
    using System.IO;
    using System.Windows.Forms;
    using Rizonesoft.Office.Licensing;
    using Rizonesoft.Office.ROSettings;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.ROUtilities;
    using Rizonesoft.Office.Evaluate.Utilities;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        MruList mruList;
        internal int bookIndex;
        internal bool IsFloating;
        internal bool isLicensed;
        internal BackgroundWorker updateWorker;


        public MainForm(string fileName)
        {
            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            isLicensed = LicenseCheck.IsLicensed();
            OnShowMdiChildCaptionInParentTitle();
            CreateProgramDirectories();
            InitializeComponent();
            base.Text = $"{StcEvaluate.ProductName} {ROGlobals.ProductVersionYear}";

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcEvaluate.ProductName}");
            CreateNewWorkbook(fileName);

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
            copyData.Channels.Add("WorkbookChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("WorkbookChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewWorkbook(fileName);
                AddFileToMRUList(fileName);
            }
        }

        public void AddFileToMRUList(string fileName)
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
            OpenFile(fileName);
        }

        #endregion Initialize

        #region Workbook Processing

        public void CreateNewWorkbook(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (BookForm openForm in this.MdiChildren)
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
                bookIndex++;
            }

            BookForm newBook = new BookForm();
            newBook.OpenFile(fileName, bookIndex);
            newBook.MdiParent = this;
            newBook.Show();
        }

        #endregion Workbook Processing

        #region Settings

        private void LoadSettings()
        {
            ROFunctions.GeometryFromString(ROSettings.Settings.GetSetting(StcEvaluate.CurrentRegGeneralPath, "Geometry", string.Empty), this);

        }

        private void SaveSettings()
        {
            ROSettings.Settings.SaveSetting(StcEvaluate.CurrentRegGeneralPath, "Geometry", ROFunctions.GeometryToString(this));

        }

        private static void SetSkins()
        {
            string sSkin = ROSettings.Settings.GetSetting(StcEvaluate.CurrentRegInterfacePath, "Skin", "Office 2019 Colorful");
            string sPalette = ROSettings.Settings.GetSetting(StcEvaluate.CurrentRegInterfacePath, "Palette", string.Empty);
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);

        }

        private static void SaveSkins()
        {
            ROSettings.Settings.SaveSetting(StcEvaluate.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            ROSettings.Settings.SaveSetting(StcEvaluate.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private bool SaveRestoreRibbon(bool SaveRibbon)
        {
            if (mainRibbonControl != null)
            {
                switch (SaveRibbon)
                {
                    case true:
                        mainRibbonControl.Toolbar.SaveLayoutToRegistry(StcEvaluate.StaticRegInterfacePath);
                        return true;
                    case false:
                        mainRibbonControl.Toolbar.RestoreLayoutFromRegistry(StcEvaluate.StaticRegInterfacePath);
                        return true;
                }
            }

            return false;

        }

        #endregion Settings

        #region Configurations

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcEvaluate.UserAppDirectory))
            {
                Directory.CreateDirectory(StcEvaluate.UserAppDirectory);
            }
        }

        #endregion Configurations


        private void MainRibbonControl_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
        }

        private void OpenBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFile();
        }

        #region Workbook Processing

        

        private void OpenFileFolder(string sIniDir)
        {
            OpenFileDialog openFileDlg = new();

            if (sIniDir != string.Empty)
            {
                openFileDlg.InitialDirectory = sIniDir;
            }

            openFileDlg.Filter = "All Files (*.*)|*.*|" +
                "All Supported Files (*.xlsx; *.xlsm; *.xlsm; *.xls; *.xltx; *.xltm; *.xlt; *.txt; *.csv; *.xml)|*.xlsx;*.xlsm;*.xlsm;*.xls;*.xltx;*.xltm;*.xlt;*.txt;*.csv;*.xml|" +
                "Excel Workbook (*.xlsx)|*.xlsx|" +
                "Excel Macro-Enabled Workbook (*.xlsm)|*.xlsm|" +
                "Excel Binary Workbook (*.xlsm)|*.xlsb|" +
                "Excel 97-2003 Workbook (*.xls)|*.xls|" +
                "Excel Template (*.xltx)|*.xltx|" +
                "Excel Macro-Enabled Template (*.xltm)|*.xltm|" +
                "Excel 97-2003 Template (*.xlt)|*.xlt|" +
                "Text (Tab delimited) (*.txt)|*.txt|" +
                "CSV (Comma delimited) (*.csv)|*.csv|" +
                "XML Spreadsheet (*.xml)|*.xml";
            openFileDlg.FilterIndex = 3;
            openFileDlg.Title = "Select a Document";

            DialogResult dlgResult = openFileDlg.ShowDialog();

            // Show the dialog and get result.
            if (dlgResult == DialogResult.OK)
            {
                string fileName = openFileDlg.FileName;
                OpenFile(fileName);
                AddFileToMRUList(fileName);
            }

            // debugLog.Info("Open Document Result - " + dlgResult.ToString());
        }

        public void OpenFile(string fileName)
        {
            CreateNewWorkbook(fileName);
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }


        #endregion Workbook Processing


        #region Events

        private void NewBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewWorkbook(null);
        }

        

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            this.mainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, "Rizonesoft\\" + StcEvaluate.ProductName + "\\MRU");
            mruList.FileSelected += MruList_FileSelected;
            // LoadDictionaries();

            if (isLicensed == true)
            {
                this.Text += " - Business";
                // barRegisterItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                // barBuyNowItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                LicenseRibbonGroup.Visible = false;
            }
            else
            {
                this.Text += " - Home";
                // barRegisterItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                // barBuyNowItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                LicenseRibbonGroup.Visible = true;
            }

            SplashScreenManager.CloseForm(false);

        }

        

        #endregion Events

    }
}
