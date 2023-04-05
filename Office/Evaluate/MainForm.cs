namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Utilities;
    using Interprocess;
    using LicensingEx;
    using MessagesEx;
    using TimeEx;
    using Rizonesoft.Office.Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.IO;
    using System.Windows.Forms;

    internal sealed partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private MruList mruList;
        private int bookIndex;
        // internal bool IsFloating;
        private readonly bool isUpdateDismiss;
        private readonly BackgroundWorker updateWorker;
        // OptionsForm optionsDlg = null;

        private BookForm CurrentDocument
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (mainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return mainTabbedMdiManager.ActiveFloatForm as BookForm;
                }

                return ActiveMdiChild as BookForm;
            }
        }

        internal MainForm(string fileName)
        {
            // WindowsFormsSettings.UseDXDialogs = DevExpress.Utils.DefaultBoolean.True;
            var sUpdateDismissed = Settings.Settings.GetSetting($"Rizonesoft\\{RizonesoftEx.ProductName}\\General", "UpdateMessage", "False");
            if (sUpdateDismissed != null) isUpdateDismiss = RizonesoftEx.StringToBoolean(sUpdateDismissed);

            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            CreateProgramDirectories();
            OnShowMdiChildCaptionInParentTitle();
            InitializeComponent();
            RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();
            RizonesoftEx.IsBetaVersion = true;

            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel,
                string.IsNullOrEmpty(fileName) ? "Creating Document" : "Loading Document");

            CreateNewWorkbook(fileName);

            if (MainRibbonControl != null)
            {
                MainRibbonControl.AutoHideEmptyItems = true;
                MainRibbonControl.SelectedPage = HomeRibbonPage;
            }

            updateWorker = new BackgroundWorker();
            updateWorker.DoWork += UpdateWorker_DoWork;
            updateWorker.RunWorkerAsync();

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Restoring Ribbon Layout");
            RestoreRibbon();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {EvaluateEx.ProductName}");

            if (isUpdateDismiss)
            {
                updateWorker.RunWorkerAsync();
            }
        }

        public static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(EvaluateEx.CurrentRegInterfacePath, "Skin", "WXI");
            string sPalette = Settings.Settings.GetSetting(EvaluateEx.CurrentRegInterfacePath, "Palette", "Calmness");

            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(EvaluateEx.UserAppDirectory))
            {
                Directory.CreateDirectory(EvaluateEx.UserAppDirectory);
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
                AddFileToMruList(fileName);
            }
        }

        public void CreateNewWorkbook(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (BookForm openForm in MdiChildren)
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

        private void NewBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewWorkbook(null);
        }

        private void OpenBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFile();
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
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
                Logging.Logger.Error(Logging.CleanMessageForLogging(sMessage));
                XtraMessageBox.Show(sMessage, "Warning", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static bool IsValidFileType(string fileName)
        {
            bool results = false;
            string fileExt = Path.GetExtension(fileName);

            List<string> fileTypes = new()
            {
                ".xlsx", ".xlsm", ".xlsm", ".xls", ".xltx", ".xltm", ".xlt", ".txt", ".csv", ".xml"
            };

            if (fileTypes.Contains(fileExt))
            {
                results = true;
            }
            return results;
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
            Logging.Logger.Info($"Open Document Result - {dlgResult}");

            // Show the dialog and get result.
            if (dlgResult == DialogResult.OK)
            {
                string fileName = openFileDlg.FileName;
                OpenFile(fileName);
                AddFileToMruList(fileName);
            }
        }

        public void AddFileToMruList(string fileName)
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
                    Logging.Logger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void CloseBarButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CurrentDocument.Close();
        }

        private void RestoreRibbon()
        {
            MainRibbonControl?.Toolbar.RestoreLayoutFromRegistry(EvaluateEx.StaticRegInterfacePath);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            MainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, EvaluateEx.CurrentRegMRUPath);
            mruList.FileSelected += MruList_FileSelected;
            CheckLicense();
        }

        private void LoadSettings()
        {
            RizonesoftEx.GeometryFromString(Settings.Settings.GetSetting(EvaluateEx.CurrentRegGeneralPath, "Geometry", string.Empty), this);
        }

        private void CheckLicense()
        {
            string formCaptionBase;
            RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();

            if (RizonesoftEx.IsBetaVersion)
            {
                formCaptionBase = $"{EvaluateEx.ProductName} {RizonesoftEx.ProductVersionMajor} ({RizonesoftEx.BetaVersionString})";
            }
            else
            {
                formCaptionBase = $"{EvaluateEx.ProductName} {RizonesoftEx.ProductVersionMajor}";
            }

            if (RizonesoftEx.IsLicensed)
            {
                Text = $"{formCaptionBase} - Business";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[1];
            }
            else
            {
                Text = $"{formCaptionBase} - Home";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[0];
            }

            DonateRibbonGroup.Visible = !RizonesoftEx.IsLicensed;
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

        private void MainRibbonControl_Merge(object sender, RibbonMergeEventArgs e)
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

        private void ChangeMainFormState(bool state)
        {
            MainForm mainForm = this;
            mainForm.HomeRibbonPage.Visible = state;
            mainForm.CloseBarButtonItem.Enabled = state;
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
            MainRibbonControl?.Toolbar.SaveLayoutToRegistry(EvaluateEx.StaticRegInterfacePath);
        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(EvaluateEx.CurrentRegGeneralPath, "Geometry", RizonesoftEx.GeometryToString(this));
        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(EvaluateEx.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(EvaluateEx.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private void LicenseButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                if (RegistrationForm.CheckInstance == null)
                {
                    if (RegistrationForm.CreateInstance.ShowDialog() == DialogResult.OK)
                    {
                        CheckLicense();
                    }
                }
                else
                {
                    // These two lines make sure the state is normal (not min or max) and give it focus.
                    RegistrationForm.CreateInstance.WindowState = FormWindowState.Normal;
                    RegistrationForm.CreateInstance.Focus();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LicenseTimer_Tick(object sender, EventArgs e)
        {
            if (LicenseCheck.IsLicensed() != RizonesoftEx.IsLicensed)
            {
                CheckLicense();
                RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();
            }

            TimeStatusButton.Caption = DateTime.Now.ToString("HH:mm tt");
        }

        private void TimeStatusButton_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                if (TimeForm.CheckInstance == null)
                {
                    TimeForm.CreateInstance.Show();
                }
                else
                {
                    // These two lines make sure the state is normal (not min or max) and give it focus.
                    TimeForm.CreateInstance.WindowState = FormWindowState.Normal;
                    TimeForm.CreateInstance.Focus();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void MainRibbonStatusBar_Click(object sender, EventArgs e)
        {
        }

        private void MainForm_DragDrop(object sender, DragEventArgs e)
        {
            MessageBox.Show("");
        }
    }
}