
namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Evaluate.Utilities;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.LicensingEx;
    using Rizonesoft.Office.MessagesEx;
    using Rizonesoft.Office.Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.IO;
    using System.Windows.Forms;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        MruList mruList;
        internal int bookIndex;
        internal bool IsFloating;
        internal bool IsLicensed;
        internal bool IsUpdateDismiss;
        internal BackgroundWorker UpdateWorker;
        // OptionsForm optionsDlg = null;

        BookForm CurrentDocument
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (MainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return MainTabbedMdiManager.ActiveFloatForm as BookForm;
                }

                return ActiveMdiChild as BookForm;
            }
        }

        public MainForm(string fileName)
        {
            string sUpdateDismissed = Settings.Settings.GetSetting($"Rizonesoft\\{GlobalProperties.ProductName}\\General", "UpdateMessage", "False");
            IsUpdateDismiss = GlobalFunctions.StringToBoolean(sUpdateDismissed);

            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            CreateProgramDirectories();
            OnShowMdiChildCaptionInParentTitle();
            InitializeComponent();
            IsLicensed = LicenseCheck.IsLicensed();
            GlobalProperties.IsBetaVersion = true;

            if (string.IsNullOrEmpty(fileName))
            {
                SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Creating Document");
            }
            else
            {
                SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Loading Document");
            }
            CreateNewWorkbook(fileName);
            MainRibbonControl.SelectedPage = HomeRibbonPage;

            UpdateWorker = new BackgroundWorker();
            UpdateWorker.DoWork += new DoWorkEventHandler(UpdateWorker_DoWork);
            UpdateWorker.RunWorkerAsync();

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Restoring Ribbon Layout");
            RestoreRibbon();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcEvaluate.ProductName}");

            if (IsUpdateDismiss)
            {
                UpdateWorker.RunWorkerAsync();
            }

        }

        public static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(StcEvaluate.CurrentRegInterfacePath, "Skin", "WXI");
            string sPalette = Settings.Settings.GetSetting(StcEvaluate.CurrentRegInterfacePath, "Palette", "Calmness");

            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcEvaluate.UserAppDirectory))
            {
                Directory.CreateDirectory(StcEvaluate.UserAppDirectory);
            }
        }

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

        public void OpenFile(string fileName)
        {
            if (IsValidFileType(fileName))
            {
                CreateNewWorkbook(fileName);
            }
            else
            {
                string sMessage = $"Cannot open the file '{fileName}'\nbecause the file format or file extension is not valid.";
                Logging.ROLogger.Error(Logging.CleanMessageForLogging(sMessage));
                XtraMessageBox.Show(sMessage, "Warning", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            CreateNewWorkbook(fileName);
        }

        static bool IsValidFileType(string fileName)
        {
            bool results = false;
            string fileExt = Path.GetExtension(fileName);

            List<string> fileTypes = new()
            {
                "xlsx", "xlsm", "xlsm", "xls", "xltx", "xltm", "xlt", "txt", "csv", "xml"
            };
            //etc

            for (int i = 0; i < fileTypes.Count; i++)
            {
                if (string.Compare(fileExt, fileTypes[i], true) == 0)
                {
                    results = true;
                    break;
                    //or just return true;
                }
            }

            return results;
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
                    Logging.ROLogger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void RestoreRibbon()
        {
            MainRibbonControl?.Toolbar.RestoreLayoutFromRegistry(StcEvaluate.StaticRegInterfacePath);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            this.MainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, StcEvaluate.CurrentRegMRUPath);
            mruList.FileSelected += MruList_FileSelected;
            CheckLicense();
        }

        private void LoadSettings()
        {
            GlobalFunctions.GeometryFromString(Office.Settings.Settings.GetSetting(StcEvaluate.CurrentRegGeneralPath, "Geometry", string.Empty), this);
        }

        private void CheckLicense()
        {
            string FormCaptionBase;

            if (GlobalProperties.IsBetaVersion)
            {
                FormCaptionBase = $"{StcEvaluate.ProductName} {GlobalProperties.ProductVersionMajor} ({GlobalProperties.BetaVersionString})";
            }
            else
            {
                FormCaptionBase = $"{StcEvaluate.ProductName} {GlobalProperties.ProductVersionMajor}";
            }

            if (LicenseCheck.IsLicensed())
            {
                Text = $"{FormCaptionBase} - Business";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[1];
                DonateRibbonGroup.Visible = false;
            }
            else
            {
                Text = $"{FormCaptionBase} - Home";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[0];
                DonateRibbonGroup.Visible = true;
            }
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            SplashScreenManager.CloseForm(false);
        }

        internal void UpdateWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            OfficeUpdate.CheckForUpdates();
        }

        private void MainRibbonControl_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            if ((parentRibbon.StatusBar != null) && (childRibbon.StatusBar != null))
            {
                parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
            }
        }

        private void MainTabbedMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (MdiChildren.Length <= 1)
            {
                ChangeMainFormState(true);
            }
        }

        private void MainTabbedMdiManager_PageRemoved(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (MdiChildren.Length == 0)
            {
                ChangeMainFormState(false);
            }
        }

        private void ChangeMainFormState(bool State)
        {
            MainForm mainForm = this;
            mainForm.HomeRibbonPage.Visible = State;
            mainForm.CloseBarButtonItem.Enabled = State;
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveRibbon();
            SaveSettings();
            SaveSkins();
        }

        private void SaveRibbon()
        {
            MainRibbonControl?.Toolbar.SaveLayoutToRegistry(StcEvaluate.StaticRegInterfacePath);

        }

        private void SaveSettings()
        {
            Office.Settings.Settings.SaveSetting(StcEvaluate.CurrentRegGeneralPath, "Geometry", GlobalFunctions.GeometryToString(this));

        }

        private static void SaveSkins()
        {
            Office.Settings.Settings.SaveSetting(StcEvaluate.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Office.Settings.Settings.SaveSetting(StcEvaluate.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }



















        private void OpenBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFile();
        }

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

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }


        private void NewBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewWorkbook(null);
        }


    }
}
