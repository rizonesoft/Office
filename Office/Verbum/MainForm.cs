using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSplashScreen;
using NLog;
using Rizonesoft.Office.Interprocess;
using Rizonesoft.Office.Licensing;
using Rizonesoft.Office.Verbum.Classes;
using System;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Windows.Documents;
using System.Windows.Forms;
using System.Xml;

namespace Rizonesoft.Office.Verbum
{
    public partial class MainForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        private static readonly Logger nlogger = NLog.LogManager.GetCurrentClassLogger();
        private CopyData copyData = null;

        MruList mruList;
        internal int documentIndex = 0;
        internal bool IsFloating = false;
        // bool updatedZoom = false;

        internal bool isLicensed = false;
        internal BackgroundWorker updateWorker;

        public MainForm(string fileName)
        {
            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            isLicensed = LicenseCheck.IsLicensed();

            CreateVerbumDirectories();
            ConfigureLogging();
            OnShowMdiChildCaptionInParentTitle();

            InitializeComponent();

            if(string.IsNullOrEmpty(fileName))
            {
                SplashScreenManager.Default
                    .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Creating Document");
            } else
            {
                SplashScreenManager.Default
                    .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Loading Document");
            }
            CreateNewDocument(fileName);

            updateWorker = new BackgroundWorker();
            updateWorker.DoWork += new DoWorkEventHandler(updateWorker_DoWork);
            updateWorker.RunWorkerAsync();

            MainRibbonControl.SelectedPage = homeRibbonPage;

            Initialize();
            SplashScreenManager.Default
                .SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Completed - Loading Verbum");
        }

        // private static RegistrationForm registrationDlg = null;

        private void BarRegisterItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                if(RegistrationForm.CheckInstance == null)
                {
                    RegistrationForm.CreateInstance.ShowDialog();
                } else
                {
                    // These two lines make sure the state is normal (not min or max) and give it focus.
                    RegistrationForm.CreateInstance.WindowState = FormWindowState.Normal;
                    RegistrationForm.CreateInstance.Focus();
                }
            } catch(Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ChangeMainFormState(bool State)
        {
            MainForm mainForm = this;
            mainForm.homeRibbonPage.Visible = State;
            mainForm.barCloseItem.Enabled = State;
        }

        private void ConfigureLogging()
        {
            var nlogConfig = new NLog.Config.LoggingConfiguration();
            // Targets where to log to: File and Console.
            var nlogFile = new NLog.Targets.FileTarget("logfile") { FileName = Globals.loggingFilePath };
            var nlogConsole = new NLog.Targets.ConsoleTarget("logconsole");

            // Rules for mapping loggers to targets.            
            nlogConfig.AddRule(LogLevel.Info, LogLevel.Fatal, nlogConsole);
            nlogConfig.AddRule(LogLevel.Debug, LogLevel.Fatal, nlogFile);

            // Apply config           
            LogManager.Configuration = nlogConfig;
        }

        private void CreateVerbumDirectories()
        {
            if(!Directory.Exists(Globals.userAppDataPath))
            {
                Directory.CreateDirectory(Globals.userAppDataPath);
            }
        }

        private void exceptionButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            int result = 15 / int.Parse("0");
        }

        private void Initialize()
        {
            // Create a new instance of the class:
            copyData = new CopyData();
            // Assign the handle:
            copyData.AssignHandle(Handle);
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            // Hook up event notifications whenever a message is received:
            copyData.DataReceived += new DataReceivedEventHandler(copyData_DataReceived);
        }

        #region Properties
        DocForm CurrentDocument
        {
            get
            {
                if(this.ActiveMdiChild == null)
                {
                    return null;
                }
                if(MainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return MainTabbedMdiManager.ActiveFloatForm as DocForm;
                }

                return this.ActiveMdiChild as DocForm;
            }
        }
        #endregion Properties

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

                if((updateReader.NodeType == XmlNodeType.Element) && (updateReader.Name == "office"))
                {
                    while(updateReader.Read())
                    {
                        if(updateReader.NodeType == XmlNodeType.Element)
                        {
                            elementName = updateReader.Name;
                        } else
                        {
                            if((updateReader.NodeType == XmlNodeType.Text) && (updateReader.HasValue))
                            {
                                switch(elementName)
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
            } catch(Exception ex)
            {
                Console.WriteLine(ex.Message);
            } finally
            {
                updateReader.Close();
            }

            Version applicationVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            if(applicationVersion.CompareTo(newVersion) < 0)
            {
                sReturnVersion = newVersion.Major + "." + newVersion.Minor + "." + newVersion.Build;
                // MessageBox.Show(sReturnVersion);
            }

            return string.Empty;
        }
        #endregion Updates

        #region Events
        private void MainForm_Load(object sender, System.EventArgs e)
        {
            LoadSettings();

            this.MainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, "Rizonesoft\\Verbum\\MRU");
            mruList.FileSelected += mruList_FileSelected;
            LoadDictionaries();

            if(isLicensed == true)
            {
                this.Text += " - Business";
                // barRegisterItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                // barBuyNowItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Never;
                licenseRibbonGroup.Visible = false;
            } else
            {
                this.Text += " - Home";
                // barRegisterItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                // barBuyNowItem.Visibility = DevExpress.XtraBars.BarItemVisibility.Always;
                licenseRibbonGroup.Visible = true;
            }
        }

        private void mainTabbedMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if(this.MdiChildren.Length <= 1)
            {
                ChangeMainFormState(true);
                // coreRibbonControl.SelectedPage = homeRibbonPage;
            }
        }

        private void mainTabbedMdiManager_PageRemoved(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if(this.MdiChildren.Length == 0)
            {
                ChangeMainFormState(false);
            }
        }

        private void copyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            // Display the data in the logging list box:
            if(e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewDocument(fileName);
                AddFileToMRUList(fileName);
            }
        }

        private void barNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { this.CreateNewDocument(null); }

        private void barOpenItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e) { OpenFile(); }

        private void barCloseItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        { CurrentDocument.Close(); }

        private void mainRibbonControl_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
        }

        private void barOptionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                OptionsForm optionsDlg = new OptionsForm();
                optionsDlg.Show(this);
            } catch(Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
        #endregion Events

        #region Overrides
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            SplashScreenManager.CloseForm(false);
        }

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveSettings();
        }
        #endregion Overrides

        #region Document Handling
        public void CreateNewDocument(string fileName)
        {
            // Detect whether file is already open
            if(!string.IsNullOrEmpty(fileName))
            {
                foreach(DocForm openForm in this.MdiChildren)
                {
                    if(string.Compare(openForm.FileName, fileName, true) == 0)
                    {
                        openForm.Activate();
                        return;
                    }
                }
            } else
            {
                documentIndex++;
            }

            DocForm newDoc = new DocForm();
            newDoc.OpenFile(fileName, documentIndex);
            newDoc.MdiParent = this;
            newDoc.Show();
        }

        private void OpenFileFolder(string sIniDir)
        {
            OpenFileDialog openFileDlg = new OpenFileDialog();

            if(sIniDir != string.Empty)
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
            if(dlgResult == DialogResult.OK)
            {
                string fileName = openFileDlg.FileName;
                OpenFile(fileName);
                AddFileToMRUList(fileName);
            }

            // debugLog.Info("Open Document Result - " + dlgResult.ToString());
        }

        public void OpenFile(string fileName) { CreateNewDocument(fileName); }

        internal void OpenFile() { OpenFileFolder(string.Empty); }
        #endregion Document Handling

        #region MRU
        public void AddFileToMRUList(string fileName)
        {
            if(!string.IsNullOrEmpty(fileName))
            {
                try
                {
                    mruList.AddFile(fileName);
                } catch(IOException ioEx)
                {
                    mruList.RemoveFile(fileName);
                    nlogger.Error(ioEx, "Whoops!");
                }
            }
        }

        private void mruList_FileSelected(string fileName) { OpenFile(fileName); }
        #endregion MRU

        #region Spelling
        private void LoadDictionaries()
        {
            string sAutoSpellCheck;
            string sFileNameWithEx;

            sAutoSpellCheck = Configure.Settings.GetSetting("Rizonesoft\\Verbum\\Spelling", "AutoSpellCheck", "True");
            Globals.autoSpellCheck = Utilities.StringToBoolean(sAutoSpellCheck);
            try
            {
                string[] dicFiles = Directory.GetFiles(Globals.dictionariesPath);
                foreach(string sFile in dicFiles)
                {
                    if(sFile.EndsWith(".dic"))
                    {
                        string sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);
                        string[] sFileParts = sFileNoExtension.Split('_');

                        if(!sFileParts[0].Equals("hyph"))
                        {
                            sFileNameWithEx = sFileNoExtension + ".aff";
                            AddHunspellDictionary(
                                sFile,
                                Path.Combine(Globals.dictionariesPath, sFileNameWithEx),
                                new CultureInfo(String.Format("{0}-{1}", sFileParts[0], sFileParts[1])));
                        }
                    }
                }
            } catch(Exception ex)
            {
                nlogger.Error(ex, "Woops!");
                MessageBox.Show(ex.Message, "Woops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }
        }

        private void AddHunspellDictionary(string dictionaryPath, string grammarPath, CultureInfo dicCulture)
        {
            if(File.Exists(dictionaryPath) && File.Exists(grammarPath))
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
            string userCustomDicDir = Globals.userAppDataPath + "\\Dictionaries";
            if(!Directory.Exists(userCustomDicDir))
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

        #region Settings
        private void LoadSettings()
        {
            string sGeometry;

            sGeometry = Configure.Settings.GetSetting("Rizonesoft\\Verbum\\General", "Geometry", string.Empty);
            Utilities.GeometryFromString(sGeometry, this);
        }

        private void SetSkins()
        {
            string sSkin = Configure.Settings.GetSetting("Rizonesoft\\Verbum\\Interface", "Skin", "WXI");
            string sPalette = Configure.Settings.GetSetting("Rizonesoft\\Verbum\\Interface", "Palette", "Sharpness");
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);
        }

        private void SaveSettings()
        {
            Configure.Settings.SaveSetting(
                "Rizonesoft\\Verbum\\Interface",
                "Skin",
                WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Configure.Settings.SaveSetting(
                "Rizonesoft\\Verbum\\Interface",
                "Palette",
                WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
            MainForm mainForm = this;
            Configure.Settings.SaveSetting("Rizonesoft\\Verbum\\General", "Geometry", Utilities.GeometryToString(mainForm));
            Configure.Settings.SaveSetting(
                "Rizonesoft\\Verbum\\Spelling",
                "AutoSpellCheck",
                Utilities.BooleanToString(Globals.autoSpellCheck));
        }
        #endregion Settings
    }
}
