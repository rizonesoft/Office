namespace Rizonesoft.Office.Verbum
{
    using DevExpress.LookAndFeel;
    using DevExpress.Utils.DPI;
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraEditors.ColorWheel;
    using DevExpress.XtraSpellChecker;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office;
    using Rizonesoft.Office.Debugging;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.Utilities;
    using Rizonesoft.Office.Verbum.Classes;
    using Rizonesoft.Office.Verbum.Utilities;
    using System;
    using System.ComponentModel;
    using System.Drawing;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Windows.Forms;
    using System.Xml;
    using XmlNodeType = System.Xml.XmlNodeType;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private static MruList mruList;
        internal int documentIndex;
        internal bool IsFloating;
        internal bool isLicensed;
        internal BackgroundWorker updateWorker;

        #region Properties
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

        #endregion Properties

        public MainForm(string fileName)
        {

            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            CreateProgramDirectories();
            OnShowMdiChildCaptionInParentTitle();
            InitializeComponent();

            GlobalProperties.IsBetaVersion = true;
            base.Text = $"{StcVerbum.ProductName} {GlobalProperties.ProductVersionMajor}{GlobalProperties.BetaVersionString}";

            if (string.IsNullOrEmpty(fileName))
            {
                SplashScreenManager.Default
                    .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Creating Document");
            }
            else
            {
                SplashScreenManager.Default
                    .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Loading Document");
            }
            CreateNewDocument(fileName);

            debugRibbonPage.Visible = Debugging.IsDebugging;
            updateWorker = new BackgroundWorker();
            updateWorker.DoWork += new DoWorkEventHandler(updateWorker_DoWork);
            updateWorker.RunWorkerAsync();

            mainRibbonControl.SelectedPage = homeRibbonPage;

            Initialize();
            SplashScreenManager.Default
                    .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Loading Dictionaries");
            LoadDictionaries();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Restoring Ribbon Layout");
            RestoreRibbon();
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcVerbum.ProductName}");

        }

        private void MainForm_Load(object sender, System.EventArgs e)
        {
            LoadSettings();

            mainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, StcVerbum.CurrentRegMRUPath);
            mruList.FileSelected += MruList_FileSelected;

        }

        private void ChangeMainFormState(bool State)
        {
            MainForm mainForm = this;
            mainForm.homeRibbonPage.Visible = State;
            mainForm.barCloseItem.Enabled = State;
        }

        #region Overrides

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            SplashScreenManager.CloseForm(false);
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveRibbon();
            SaveSettings();
            SaveSkins();
        }

        #endregion Overrides

        #region Initialize

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
            OpenFile(fileName);
        }

        #endregion Initialize

        #region Document Processing

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

        public void OpenFile(string fileName) => CreateNewDocument(fileName);

        internal void OpenFile() { OpenFileFolder(string.Empty); }



        #endregion Document Processing

        #region Merging

        private void MainRibbonControl_Merge(object sender, RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            if ((parentRibbon.StatusBar != null) && (childRibbon.StatusBar != null))
            {
                parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
            }
        }

        #endregion Merging

        #region Configurations

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcVerbum.UserAppDirectory))
            {
                Directory.CreateDirectory(StcVerbum.UserAppDirectory);
            }
        }

        private void LoadSettings()
        {
            GlobalFunctions.GeometryFromString(Settings.Settings.GetSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", string.Empty), this);

        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegGeneralPath, "Geometry", GlobalFunctions.GeometryToString(this));
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegSpellingPath, "AutoSpellCheck", GlobalFunctions.BooleanToString(StcVerbum.AutoSpellCheck));

        }

        public static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Skin", "WXI");
            string sPalette = Settings.Settings.GetSetting(StcVerbum.CurrentRegInterfacePath, "Palette", "Clearness");

            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcVerbum.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private void SaveRibbon()
        {
            if (mainRibbonControl != null)
            {
                mainRibbonControl.Toolbar.SaveLayoutToRegistry(StcVerbum.StaticRegInterfacePath);
            }

        }

        private void RestoreRibbon()
        {
            if (mainRibbonControl != null)
            {
                mainRibbonControl.Toolbar.RestoreLayoutFromRegistry(StcVerbum.StaticRegInterfacePath);
            }
        }

        #endregion Configurations

        #region Updates
        internal void updateWorker_DoWork(object sender, DoWorkEventArgs e)
        { OfficeUpdate("https://www.rizonesoft.com/update/office22.xml"); }

        public static string OfficeUpdate(string updateXML)
        {
            string downloadUrl = string.Empty;
            Version newVersion = null;
            string updateXmlURL = "https://www.rizonesoft.com/update/office22.xml";
            XmlTextReader updateReader = null;
            string sReturnVersion = string.Empty;

            try
            {
                updateReader = new XmlTextReader(updateXmlURL);
                updateReader.MoveToContent();
                string elementName = string.Empty;

                if ((updateReader.NodeType == XmlNodeType.Element) && (updateReader.Name == "office"))
                {
                    while (updateReader.Read())
                    {
                        if (updateReader.NodeType == XmlNodeType.Element)
                        {
                            elementName = updateReader.Name;
                        }
                        else
                        {
                            if ((updateReader.NodeType == XmlNodeType.Text) && (updateReader.HasValue))
                            {
                                switch (elementName)
                                {
                                    case "version":
                                        newVersion = new Version(updateReader.Value);
                                        break;

                                    case "url":
                                        downloadUrl = updateReader.Value;
                                        break;
                                }
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            finally
            {
                updateReader.Close();
            }

            Version applicationVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            if (applicationVersion.CompareTo(newVersion) < 0)
            {
                sReturnVersion = newVersion.Major + "." + newVersion.Minor + "." + newVersion.Build;
                // MessageBox.Show(sReturnVersion);
            }

            return string.Empty;
        }
        #endregion Updates

        #region Debugging

        private void exceptionButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            int result = 15 / int.Parse("0");
        }

        #endregion Debugging















        #region Events


        private void mainTabbedMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (this.MdiChildren.Length <= 1)
            {
                ChangeMainFormState(true);
            }
        }

        private void mainTabbedMdiManager_PageRemoved(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (this.MdiChildren.Length == 0)
            {
                ChangeMainFormState(false);
            }
        }



        private void barNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { this.CreateNewDocument(null); }

        private void barOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) { OpenFile(); }

        private void barCloseItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { CurrentDocument.Close(); }

        private void barOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                OptionsForm optionsDlg = new OptionsForm();
                optionsDlg.Show(this);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
        #endregion Events


        #region Document Handling


        private void OpenFileFolder(string sIniDir)
        {
            OpenFileDialog openFileDlg = new OpenFileDialog();

            if (sIniDir != string.Empty)
            {
                openFileDlg.InitialDirectory = sIniDir;
            }

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

            // debugLog.Info("Open Document Result - " + dlgResult.ToString());
        }




        #endregion Document Handling




        #region Spelling
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
        #endregion Spelling

        private void MainRibbonControl_Click(object sender, EventArgs e)
        {
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
        }



        private void DevBarBtnItem_ItemDoubleClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Debugging.IsDebugging = !Debugging.IsDebugging;
            debugRibbonPage.Visible = Debugging.IsDebugging;
        }

    }
}
