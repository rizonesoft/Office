namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office;
    using Rizonesoft.Office.Debugging;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.LicensingEx;
    using Rizonesoft.Office.MessagesEx;
    using Rizonesoft.Office.TimeEx;
    using Rizonesoft.Office.Utilities;
    using Rizonesoft.Office.Verbum.Classes;
    using Rizonesoft.Office.Verbum.Utilities;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Windows.Forms;
    using static DevExpress.XtraBars.Docking.AutoHideControl;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private static MruList mruList;
        internal int documentIndex;
        internal bool IsFloating;
        internal bool IsLicensed;
        internal bool IsUpdateDismiss;
        internal BackgroundWorker UpdateWorker;
        OptionsForm optionsDlg = null;



        DocForm CurrentDocument
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

        public MainForm(string fileName)
        {

            string sUpdateDismissed = Settings.Settings.GetSetting($"Rizonesoft\\{GlobalProperties.ProductName}\\General", "UpdateMessage", "True");
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
            CreateNewDocument(fileName);

            debugRibbonPage.Visible = Debugging.IsDebugging;
            mainRibbonControl.SelectedPage = homeRibbonPage;

            Initialize();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Loading Dictionaries");
            LoadDictionaries();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Restoring Ribbon Layout");
            RestoreRibbon();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcVerbum.ProductName}");

            UpdateWorker = new BackgroundWorker();
            UpdateWorker.DoWork += new DoWorkEventHandler(UpdateWorker_DoWork);

            if (IsUpdateDismiss)
            {
                UpdateWorker.RunWorkerAsync();
            }

        }

        public static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Skin", "WXI");
            string sPalette = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Palette", "Clearness");

            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcVerbum.UserAppDirectory))
            {
                Directory.CreateDirectory(StcVerbum.UserAppDirectory);
            }
        }

        private void Initialize()
        {
            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels.Add("DocChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewDocument(fileName);
                AddFileToMRUList(fileName);
            }
        }

        public void CreateNewDocument(string fileName)
        {

            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (DocForm openForm in MdiChildren.Cast<DocForm>())
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
                documentIndex++;
            }

            DocForm newDoc = new DocForm();
            newDoc.OpenFile(fileName, documentIndex);
            newDoc.MdiParent = this;
            newDoc.Show();

        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
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
                Logging.ROLogger.Error(Logging.CleanMessageForLogging(sMessage));
                XtraMessageBox.Show(sMessage, "Warning", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        static bool IsValidFileType(string fileName)
        {
            bool results = false;
            string fileExt = Path.GetExtension(fileName);

            List<string> fileTypes = new()
            {
                "docx", "docm", ".docx", "dotx", "dotm", "doc", ".dot", "odt", "rtf", "htm", ".html", "mht", "eml", "epub", "xml", "txt"
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

        private void RestoreRibbon()
        {
            mainRibbonControl?.Toolbar.RestoreLayoutFromRegistry(StcVerbum.StaticRegInterfacePath);
        }

        private void MainForm_Load(object sender, System.EventArgs e)
        {
            LoadSettings();

            mainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, StcVerbum.CurrentRegMRUPath);
            mruList.FileSelected += MruList_FileSelected;
            CheckLicense();
        }

        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void LoadSettings()
        {
            GlobalFunctions.GeometryFromString(Settings.Settings.GetSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", string.Empty), this);
        }

        private void CheckLicense()
        {
            string FormCaptionBase;

            if (GlobalProperties.IsBetaVersion)
            {
                FormCaptionBase = $"{StcVerbum.ProductName} {GlobalProperties.ProductVersionMajor} ({GlobalProperties.BetaVersionString})";
            }
            else
            {
                FormCaptionBase = $"{StcVerbum.ProductName} {GlobalProperties.ProductVersionMajor}";
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

        private void ChangeMainFormState(bool State)
        {
            MainForm mainForm = this;
            mainForm.homeRibbonPage.Visible = State;
            mainForm.barCloseItem.Enabled = State;
        }

        private void ExceptionButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            _ = 15 / int.Parse("0");
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
            mainRibbonControl?.Toolbar.SaveLayoutToRegistry(StcVerbum.StaticRegInterfacePath);

        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", GlobalFunctions.GeometryToString(this));
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", GlobalFunctions.BooleanToString(StcVerbum.AutoSpellCheck));

        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }































       

        

       

        

        private void barNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { this.CreateNewDocument(null); }

        private void barOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) { OpenFile(); }

        private void barCloseItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CurrentDocument.Close();
        }

        private void barOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {

            try
            {
                if (optionsDlg != null)
                {
                    optionsDlg.BringToFront();
                }
                else
                {
                    optionsDlg = new OptionsForm();
                    optionsDlg.Show(this);
                }

                if (optionsDlg.IsDisposed)
                {
                    optionsDlg = new OptionsForm();
                    optionsDlg.Show(this);
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void OpenFileFolder(string sIniDir)
        {

            OpenFileDialog openFileDlg = new();

            if (sIniDir != String.Empty)
            {
                openFileDlg.InitialDirectory = sIniDir;
            }

            // openFileDlg.KeepPosition = true;
            // openFileDlg.ShowDragDropConfirmation = true;
            // openFileDlg.AutoUpdateFilterDescription = false;
            openFileDlg.Filter = "All Files (*.*)|*.*|" +
                "All Supported Files (*.docx; *.docm; *.dotx; *.dotm; *.doc; *.dot; *.odt; *.rtf; *.htm; *.html; *.mht; *.eml; *.epub; *.xml; *.txt)|*.docx;*.docm;*.dotx;*.dotm;*.doc;*.dot;*.odt;*.rtf;*.htm;*.html;*.mht;*.eml;*.epub;*.xml;*.txt|" +
                "Word 2007 Document (*.docx)|*.docx|" +
                "Word Macro-Enabled Document (*.docm)|*.docm|" +
                "Word Template (*.dotx)|*.dotx|" +
                "Word Macro-Enabled Template (*.dotm)|*.dotm|" +
                "Microsoft Word Document (*.doc)|*.doc|" +
                "Word 97-2003 Template (*.dot)|*.dot|" +
                "OpenDocument Text Document (*.odt)|*.odt|" +
                "Rich Text Format (*.rtf)|*.rtf|" +
                "HyperText Markup Language Format (*.htm; *.html)|*.htm;*.html|" +
                "Web Archive, single file (*.mht)|*.mht|" +
                "Email Message (*.eml)|*.eml|" +
                "Electronic Publication (*.epub)|*.epub|" +
                "Word XML Document (*.xml)|*.xml|" +
                "Text Files (*.txt)|*.txt";
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
        }

        private void LoadDictionaries()
        {
            string sAutoSpellCheck;

            sAutoSpellCheck = Settings.Settings
                .GetSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", "True");
            StcVerbum.AutoSpellCheck = GlobalFunctions.StringToBoolean(sAutoSpellCheck);
            try
            {
                string sFileNoExtension = string.Empty;
                string sDicFilePath = string.Empty;
                string sAffFilePath = string.Empty;
                string sCultureString = string.Empty;

                string[] dicFiles = Directory.GetFiles(StcVerbum.DictionariesPath, "*", SearchOption.AllDirectories);
                foreach (string sFile in dicFiles)
                {
                    sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);

                    if ((!Path.HasExtension(sFile))
                        || (!sFile.EndsWith(".dic", StringComparison.OrdinalIgnoreCase))
                        || (sFileNoExtension.StartsWith("hyph", StringComparison.OrdinalIgnoreCase)))
                    { continue; }
                    else
                    {
                        sDicFilePath = sFile;
                        sAffFilePath = Path.ChangeExtension(sFile, ".aff");

                        if (Path.Exists(sAffFilePath))
                        {
                            sCultureString = sFileNoExtension.Replace('_', '-');
                            AddHunspellDictionary(sDicFilePath, sAffFilePath, new CultureInfo(sCultureString));
                        }
                        else
                        { continue; }
                    }
                }
            }
            catch (Exception ex)
            {
                Logging.ROLogger.Error(ex, "Woops!");
                MessageBox.Show(ex.Message, "Woops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }
        }

        private void AddHunspellDictionary(string dictionaryPath, string grammarPath, CultureInfo dicCulture)
        {
            if (File.Exists(dictionaryPath) && File.Exists(grammarPath))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary spellCheckerHunspellDic =
                    new DevExpress.XtraSpellChecker.HunspellDictionary();

                spellCheckerHunspellDic.Culture = dicCulture;
                spellCheckerHunspellDic.DictionaryPath = dictionaryPath;
                spellCheckerHunspellDic.GrammarPath = grammarPath;
                MainForm mainForm = this;
                mainForm.mainSharedDictionaryStorage.Dictionaries.Add(spellCheckerHunspellDic);
                SpellingHelper.availableDictionaries.Add(dicCulture.Name, spellCheckerHunspellDic);

                AddCustomDictionary(dictionaryPath, dicCulture);
            }
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

        private void MainRibbonControl_Click(object sender, EventArgs e)
        {

        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            // ActiveMdiChild?.Close();
        }

        private void DevBarBtnItem_ItemDoubleClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Debugging.IsDebugging = !Debugging.IsDebugging;
            debugRibbonPage.Visible = Debugging.IsDebugging;
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
            if (LicenseCheck.IsLicensed() != IsLicensed)
            {
                CheckLicense();
                IsLicensed = LicenseCheck.IsLicensed();
            }

            TimeStatusButton.Caption = DateTime.Now.ToString("HH:mm");
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

        private void mainTabbedMdiManager_SelectedPageChanged(object sender, EventArgs e)
        {

        }
    }
}
