using Rizonesoft.Office.Verbum.Forms;

namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSplashScreen;
    using Office;
    using Debugging;
    using Interprocess;
    using LicensingEx;
    using MessagesEx;
    using TimeEx;
    using Rizonesoft.Office.Utilities;
    using Classes;
    using Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Windows.Forms;

    public sealed partial class MainForm : RibbonForm
    {
        internal int DocumentIndex;
        internal bool IsFloating;
        internal bool IsUpdateDismiss;
        internal BackgroundWorker UpdateWorker;
        private static MruList _mruList;
        private CopyData copyData;
        private OptionsForm optionsDlg;

        public MainForm(string fileName)
        {
            // WindowsFormsSettings.UseDXDialogs = DevExpress.Utils.DefaultBoolean.True;
            var sUpdateDismissed = Settings.Settings.GetSetting($"Rizonesoft\\{RizonesoftEx.ProductName}\\General",
                "UpdateMessage", "True");
            IsUpdateDismiss = RizonesoftEx.StringToBoolean(sUpdateDismissed ?? "False");

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
            CreateNewDocument(fileName);

            debugRibbonPage.Visible = Debugging.IsDebugging;
            if (mainRibbonControl != null)
            {
                // mainRibbonControl.AutoHideEmptyItems = true;
                mainRibbonControl.SelectedPage = homeRibbonPage;
            }

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL, "Loading Dictionaries");
            LoadDictionaries();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL, "Restoring Ribbon Layout");
            RestoreRibbon();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.WS_SET_STATUS_LABEL, $"Completed - Loading {StcVerbum.ProductName}");

            UpdateWorker = new BackgroundWorker();
            UpdateWorker.DoWork += UpdateWorker_DoWork;

            if (IsUpdateDismiss)
            {
                UpdateWorker.RunWorkerAsync();
            }
        }

        private DocForm CurrentDocument
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (mainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return mainTabbedMdiManager.ActiveFloatForm as DocForm;
                }

                return ActiveMdiChild as DocForm;
            }
        }
        public static void AddFileToMruList(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                try
                {
                    _mruList.AddFile(fileName);
                }
                catch (IOException ioEx)
                {
                    _mruList.RemoveFile(fileName);
                    Logging.logger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        public static void SetSkins()
        {
            var sSkin = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Skin", "WXI");
            var sPalette = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Palette", "Clearness");

            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        public void CreateNewDocument(string fileName)
        {


            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (var openForm in MdiChildren.Cast<DocForm>())
                {
                    if (string.Compare(openForm.FileName, fileName, StringComparison.OrdinalIgnoreCase) != 0) continue;
                    openForm.Activate();
                    return;
                }
            }
            else
            {
                DocumentIndex++;
            }

            var newDoc = new DocForm();
            newDoc.OpenFile(fileName, DocumentIndex);
            newDoc.MdiParent = this;
            newDoc.Show();
        }

        public void OpenFile(string fileName)
        {
            if (IsValidFileType(fileName))
            {
                CreateNewDocument(fileName);
            }
            else
            {
                string sMessage = $"Cannot open the file '{fileName}'\nbecause the file format or file extension is not valid.";
                Logging.logger.Error(Logging.CleanMessageForLogging(sMessage));
                XtraMessageBox.Show(sMessage, "Warning", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }

        internal void UpdateWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            OfficeUpdate.CheckForUpdates();
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
            SplashScreenManager.CloseForm(false);
        }

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcVerbum.UserAppDirectory))
            {
                Directory.CreateDirectory(StcVerbum.UserAppDirectory);
            }
        }

        private static bool IsValidFileType(string fileName)
        {
            bool results = false;
            string fileExt = Path.GetExtension(fileName);

            List<string> fileTypes = new()
            {
                ".docx", ".docm", ".docx", ".dotx", ".dotm", ".doc", ".dot", ".odt", ".rtf", ".htm", ".html", ".mht", ".eml", ".epub", ".xml", ".txt"
            };

            if (fileTypes.Contains(fileExt))
            {
                results = true;
            }
            return results;
        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private void AddCustomDictionary(string dictionaryPath, CultureInfo customCulture)
        {
            string userCustomDicDir = StcVerbum.UserAppDirectory + "\\Dictionaries";
            if (!Directory.Exists(userCustomDicDir))
            {
                Directory.CreateDirectory(userCustomDicDir);
            }

            SpellCheckerCustomDictionary customDictionary = new SpellCheckerCustomDictionary();
            customDictionary.AlphabetPath = userCustomDicDir +
                "\\custom_" +
                Path.GetFileNameWithoutExtension(dictionaryPath) +
                ".txt";
            customDictionary.DictionaryPath = userCustomDicDir +
                "\\custom_" +
                Path.GetFileNameWithoutExtension(dictionaryPath) +
                ".dic";
            customDictionary.Culture = customCulture;
            MainForm mainForm = this;
            mainForm.mainSharedDictionaryStorage.Dictionaries.Add(customDictionary);
        }

        private void AddHunspellDictionary(string dictionaryPath, string grammarPath, CultureInfo dicCulture)
        {
            if (File.Exists(dictionaryPath) && File.Exists(grammarPath))
            {
                HunspellDictionary spellCheckerHunspellDic =
                    new HunspellDictionary() { Culture = dicCulture, DictionaryPath = dictionaryPath, GrammarPath = grammarPath };
                MainForm mainForm = this;
                mainForm.mainSharedDictionaryStorage.Dictionaries.Add(spellCheckerHunspellDic);
                SpellingHelper.availableDictionaries.Add(dicCulture.Name, spellCheckerHunspellDic);

                AddCustomDictionary(dictionaryPath, dicCulture);
            }
        }

        private void BarCloseItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CurrentDocument.Close();
        }

        private void BarNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewDocument(null);
        }

        private void barOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFile();
        }

        private void barOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            optionsDlg = new OptionsForm();
            optionsDlg.ShowDialog();

            //if (OptionsForm.CheckInstance == null)
            //{
            //OptionsForm.CreateInstance.Show();
            //}
            //else
            //{
            // These two lines make sure the state is normal (not min or max) and give it focus.
            //OptionsForm.CreateInstance.WindowState = FormWindowState.Normal;
            //OptionsForm.CreateInstance.Focus();


            // }

        }

        private void ChangeMainFormState(bool state)
        {
            var mainForm = this;
            mainForm.homeRibbonPage.Visible = state;
            mainForm.barCloseItem.Enabled = state;
        }

        private void CheckLicense()
        {
            var formCaptionBase = RizonesoftEx.IsBetaVersion ? $"{StcVerbum.ProductName} {RizonesoftEx.ProductVersionMajor} ({RizonesoftEx.BetaVersionString})" : $"{StcVerbum.ProductName} {RizonesoftEx.ProductVersionMajor}";

            if (LicenseCheck.IsLicensed())
            {
                Text = $@"{formCaptionBase} - Business";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[1];
            }
            else
            {
                Text = $@"{formCaptionBase} - Home";
                GetLicenseButtonItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                LicenseButtonItem.ImageOptions.SvgImage = ribbonSVGImageCollection[0];
            }

            RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();
            DonateRibbonGroup.Visible = !RizonesoftEx.IsLicensed;
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewDocument(fileName);
                AddFileToMruList(fileName);
            }
        }

        private void DevBarBtnItem_ItemDoubleClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Debugging.IsDebugging = !Debugging.IsDebugging;
            debugRibbonPage.Visible = Debugging.IsDebugging;
        }

        private void ExceptionButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            _ = 15 / int.Parse("0");
        }

        private void Initialize()
        {
            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels.Add("DocChannel");
            copyData.DataReceived += CopyData_DataReceived;
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
                MessageBox.Show(ex.Message, @"Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LicenseTimer_Tick(object sender, EventArgs e)
        {
            if (LicenseCheck.IsLicensed() != RizonesoftEx.IsLicensed)
            {
                CheckLicense();
                RizonesoftEx.IsLicensed = LicenseCheck.IsLicensed();
            }

            TimeStatusButton.Caption = DateTime.Now.ToString("HH:mm");
        }

        private void LoadDictionaries()
        {
            var sAutoSpellCheck = Settings.Settings
                .GetSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", "True");
            StcVerbum.AutoSpellCheck = RizonesoftEx.StringToBoolean(sAutoSpellCheck ?? "False");
            try
            {
                var dicFiles = Directory.GetFiles(StcVerbum.DictionariesPath, "*", SearchOption.AllDirectories);
                foreach (var sFile in dicFiles)
                {
                    var sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);

                    if ((!Path.HasExtension(sFile))
                        || (!sFile.EndsWith(".dic", StringComparison.OrdinalIgnoreCase))
                        || (sFileNoExtension.StartsWith("hyph", StringComparison.OrdinalIgnoreCase)))
                    {
                    }
                    else
                    {
                        var sAffFilePath = Path.ChangeExtension(sFile, ".aff");

                        if (!Path.Exists(sAffFilePath)) continue;
                        var sCultureString = sFileNoExtension.Replace('_', '-');
                        AddHunspellDictionary(sFile, sAffFilePath, new CultureInfo(sCultureString));
                    }
                }
            }
            catch (Exception ex)
            {
                Logging.logger.Error(ex, "Woops!");
                MessageBox.Show(ex.Message, @"Woops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LoadSettings()
        {
            RizonesoftEx.GeometryFromString(Settings.Settings.GetSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", string.Empty) ?? string.Empty, this);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            mainRibbonControl.ForceInitialize();
            _mruList = new MruList("MRU", mruPopupMenu, 10, StcVerbum.CurrentRegMRUPath);
            _mruList.FileSelected += MruList_FileSelected;
            CheckLicense();
        }

        private void MainRibbonControl_Click(object sender, EventArgs e)
        {
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

        private void mainTabbedMdiManager_SelectedPageChanged(object sender, EventArgs e)
        {
        }

        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void OpenFileFolder(string sIniDir)
        {
            OpenFileDialog openFileDlg = new();

            if (sIniDir != string.Empty)
            {
                openFileDlg.InitialDirectory = sIniDir;
            }

            // openFileDlg.KeepPosition = true;
            // openFileDlg.ShowDragDropConfirmation = true;
            // openFileDlg.AutoUpdateFilterDescription = false;
            openFileDlg.Filter = Resources.Verbum.MainForm_OpenFileFolder_Filter;
            openFileDlg.FilterIndex = 3;
            openFileDlg.Title = Resources.Verbum.MainForm_OpenFileFolder_Title;

            DialogResult dlgResult = openFileDlg.ShowDialog();
            Logging.logger.Info("Open Document Result - " + dlgResult.ToString());

            // Show the dialog and get result.
            if (dlgResult == DialogResult.OK)
            {
                string fileName = openFileDlg.FileName;
                OpenFile(fileName);
                AddFileToMruList(fileName);
            }
        }
        private void RestoreRibbon()
        {
            mainRibbonControl?.Toolbar.RestoreLayoutFromRegistry(StcVerbum.StaticRegInterfacePath);
        }
        private void SaveRibbon()
        {
            mainRibbonControl?.Toolbar.SaveLayoutToRegistry(StcVerbum.StaticRegInterfacePath);
        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", RizonesoftEx.GeometryToString(this));
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", RizonesoftEx.BooleanToString(StcVerbum.AutoSpellCheck));
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
    }
}