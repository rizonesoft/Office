using Rizonesoft.Office.Licensing;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.UI.Ribbon;
using Rizonesoft.Office.Utilities;
using System;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Verbum.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings;
using System.Threading.Tasks;
using System.Globalization;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraSpellChecker;
using Rizonesoft.Office.Verbum.Classes;

namespace Rizonesoft.Office.Verbum
{
    public partial class MainForm : RibbonFormBase
    {
        private readonly CopyData copyData;
        // private bool isFloating;
        private int documentIndex;
        private static MruList _mruList;
        public static bool IsLicensed { get; private set; }
        private readonly ThreadTimer timer;

        #region Properties

        private DocForm CurrentDocument
        {
            get
            {
                if (ActiveMdiChild is not DocForm && CoreMdiManager.ActiveFloatForm is not DocForm)
                {
                    return null;
                }

                return CoreMdiManager.ActiveFloatForm as DocForm ?? ActiveMdiChild as DocForm;
            }
        }

        #endregion Properties

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName != null && !e.ChannelName.Equals("DocChannel")) return;
            if (WindowState == FormWindowState.Minimized)
            {
                WindowState = FormWindowState.Normal;
            }

            var fileName = (string)e.Data;
            CreateNewDocument(fileName);
            AddFileToMruList(fileName);
            Activate();
        }

        /// <summary>
        /// Initializes a new instance of the MainForm class.
        /// </summary>
        public MainForm(string fileName)
        {
            SplashScreenHelper.ShowSplashScreen(this);

            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels?.Add("DocChannel");
            copyData.DataReceived += CopyData_DataReceived;

            InitializeComponent();
            AfterInitializeComponents();

            InitializeRibbon();
            UpdateUi(false);
            LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
            LicenseHelper.LicenseKeyUpdated += OnLicenseKeyUpdated;

            ControlConfig.SetDefaultMdiManagerConfig(CoreMdiManager, this);
            CreateNewDocument(fileName);
            _ = InitializeLicenseAsync();

            try
            {
                LoadDictionaries();
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, "An error occurred while loading the dictionaries.", ex);
                XtraMessageBox.Show(ex.Message, "Woops!", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            // CloseSaveBtn.ItemClick += CloseSaveBtn_ItemClick;
            // CloseBtn.ItemClick += CloseBtn_ItemClick;

            timer = new ThreadTimer(TimerOnTick, 1000);
            timer.Start();
        }

        private void TimerOnTick()
        {
            var now = DateTime.Now;
            var timeString = now.ToString("HH:mm");
            Invoke(new Action(() => TimeStatusButton.Caption = timeString));
        }

        private static async Task InitializeLicenseAsync()
        {
            try
            {
                IsLicensed = await LicenseHelper.CheckLicenseAsync();
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, "An error occurred while checking the license.", ex);
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            timer.Dispose();
            base.OnFormClosing(e);
        }

        protected override void OnClosed(EventArgs e)
        {
            SaveSettings();
            base.OnClosed(e);
        }

        private void InitializeRibbon()
        {
            MainRibbon.ForceInitialize();
            _ = new RibbonGroupOptions(this, MainRibbon, OptionsRibbonGroup)
            {
                IsLanguageDropdownVisible = false
            };
            _ = new RibbonPageSupport(MainRibbon);
        }

        private void UpdateUi(bool showOverlay)
        {
            var overlayManager = new OverlayManager();
            if (showOverlay) overlayManager.ShowOverlay(this);

            FileRibbonPage.Text = Dialogs.RibbonPage_File;
            CommonRibbonGroup.Text = Dialogs.RibbonGroup_Common;
            ExportToRibbonGroup.Text = Dialogs.RibbonGroup_Export_To;
            InfoRibbonGroup.Text = Dialogs.RibbonGroup_Info;
            OptionsRibbonGroup.Text = Dialogs.RibbonGroup_Options;

            if (showOverlay) overlayManager.DisposeOverlay();
        }

        /// <summary>
        /// Method to add file to the MRU list.
        /// </summary>
        /// <param name="fileName">Name of the file to add.</param>
        public static void AddFileToMruList(string fileName)
        {
            if (string.IsNullOrEmpty(fileName)) return;
            try
            {
                _mruList?.AddFile(fileName);
            }
            catch (IOException ioEx)
            {
                Serilogger.LogMessage(LogLevel.Warning, "The file could not be found.", ioEx);
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, "An error occurred while adding the file to the MRU list.", ex);
            }
        }

        private void CreateNewDocument(string fileName)
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
                documentIndex++;
            }

            DocForm newDocForm = new(fileName)
            {
                MdiParent = this,
                // FileName = fileName
            };
            newDocForm.OpenFile(fileName, documentIndex);
            newDocForm.Show();

        }

        private void OpenFile(string fileName)
        {
            var overlayManager = new OverlayManager();
            overlayManager.ShowOverlay(this);
            CreateNewDocument(fileName);
            overlayManager.DisposeOverlay();
        }

        private void OpenFileFolder(string initialDirectory)
        {
            var openFileDlg = new OpenFileDialog
            {
                Filter = Dialogs.OpenFileFolder_Filter,
                FilterIndex = 1,
                Title = Dialogs.OpenFileFolder_Title,
                CheckFileExists = true,
                CheckPathExists = true,
                Multiselect = false,
                SupportMultiDottedExtensions = true,
                ValidateNames = true,
                RestoreDirectory = true,
                AddExtension = true,
                DefaultExt = "docx",
                FileName = initialDirectory,

            };

            if (initialDirectory != string.Empty)
            {
                openFileDlg.InitialDirectory = initialDirectory;
            }

            var dlgResult = openFileDlg.ShowDialog();

            // Show the dialog and get result.
            if (dlgResult != DialogResult.OK) return;
            var fileName = openFileDlg.FileName;
            AddFileToMruList(fileName);
            OpenFile(fileName);

        }

        /// <summary>
        /// Loads dictionaries from the configured path and adds them to the shared dictionary store.
        /// </summary>
        private void LoadDictionaries()
        {
            if (string.IsNullOrWhiteSpace(ProgramConfiguration.DictionariesPath)) return;
            var dicFiles = Directory.EnumerateFiles(ProgramConfiguration.DictionariesPath, "*", SearchOption.AllDirectories);

            foreach (var file in dicFiles)
            {
                var fileName = Path.GetFileNameWithoutExtension(file);
                if (!file.EndsWith(".dic", StringComparison.OrdinalIgnoreCase) || fileName.StartsWith("hyph", StringComparison.OrdinalIgnoreCase)) continue;
                var affFilePath = Path.ChangeExtension(file, ".aff");
                if (!File.Exists(affFilePath)) continue;
                var culture = new CultureInfo(fileName.Replace('_', '-'));
                AddHunspellDictionary(file, affFilePath, culture);
            }
        }

        /// <summary>
        /// Adds a Hunspell dictionary and corresponding custom dictionary to the shared store.
        /// </summary>
        /// <param name="dictionaryPath">Path to the Hunspell dictionary.</param>
        /// <param name="grammarPath">Path to the corresponding .aff file.</param>
        /// <param name="culture">Culture associated with the dictionary.</param>
        private void AddHunspellDictionary(string dictionaryPath, string grammarPath, CultureInfo culture)
        {
            if (!File.Exists(dictionaryPath) || !File.Exists(grammarPath)) return;

            var hunspellDictionary = new HunspellDictionary { Culture = culture, DictionaryPath = dictionaryPath, GrammarPath = grammarPath };

            sharedDictionaryStore.Dictionaries.Add(hunspellDictionary);
            SpellingHelper.AvailableDictionaries.Add(culture.Name, hunspellDictionary);

            AddCustomDictionary(dictionaryPath, culture);
        }

        /// <summary>
        /// Adds a custom dictionary to the shared store.
        /// </summary>
        /// <param name="dictionaryPath">Path to the corresponding Hunspell dictionary.</param>
        /// <param name="culture">Culture associated with the dictionary.</param>
        private void AddCustomDictionary(string dictionaryPath, CultureInfo culture)
        {
            var customDicDir = ProgramConfiguration.CustomDictionariesPath ?? Path.Combine(Path.GetTempPath(), "CustomDictionaries");
            Directory.CreateDirectory(customDicDir); // This does nothing if the directory already exists

            var baseFileName = "custom_" + Path.GetFileNameWithoutExtension(dictionaryPath);

            var customDictionary = new SpellCheckerCustomDictionary
            {
                AlphabetPath = Path.Combine(customDicDir, baseFileName + ".txt"),
                DictionaryPath = Path.Combine(customDicDir, baseFileName + ".dic"),
                Culture = culture
            };

            sharedDictionaryStore.Dictionaries.Add(customDictionary);
        }


        private void SaveSettings()
        {
            CommonSettings.Geometry = FormGeometry.GeometryToString(this);
            MainRibbon.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
            MainRibbon.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");

            try
            {
                if (ProgramConfiguration.SettingsFilePath != null)
                {
                    _mruList = new MruList(MruPopupMenu, 10, new MruRegistryHandler());
                    _mruList.Initialize();
                    _mruList.FileSelected += MruList_FileSelected;
                }
            }
            catch (Exception ex)
            {
                // Handle or log the exception here.
                Console.WriteLine(ex.Message);
            }
        }

        private void MainForm_Shown(object sender, EventArgs e)
        {
            SplashScreenHelper.CloseSplashScreen();
        }

        private void LanguageManager_LanguageChanged(object sender, EventArgs e)
        {
            UpdateUi(true);
        }

        private void OnLicenseKeyUpdated()
        {
            // React to the license key update here
        }

        private void OpenDropdownBtn_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFileFolder(Environment.CurrentDirectory);
        }


        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void NewBarBtn_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewDocument(null);
        }

        private void CloseDocBarBtn_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            if (CurrentDocument == null) return;
            CurrentDocument.SaveFile();
            CurrentDocument.Close();
        }

        private void TimeStatusButton_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            var clockPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Clock.exe");
            FileLauncher.RunExecutable(clockPath);
        }

        private void CoreMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (sender is not DevExpress.XtraTabbedMdi.XtraTabbedMdiManager)
                throw new ArgumentNullException(nameof(sender));
            UpdateMainFormState();
        }

        private void CoreMdiManager_PageRemoved(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (sender is not DevExpress.XtraTabbedMdi.XtraTabbedMdiManager)
                throw new ArgumentNullException(nameof(sender));
            UpdateMainFormState();
        }

        private void UpdateMainFormState()
        {
            var state = MdiChildren.Length > 0;
            MdiChildrenListItem.Enabled = state;
            ExportToRibbonGroup.Visible = state;
            InfoRibbonGroup.Visible = state;
            CloseSaveBarItem.Enabled = state;

        }

        private void MainRibbon_Merge(object sender, RibbonMergeEventArgs e)
        {
            var parentRibbon = sender as RibbonControl;
            var childRibbon = e.MergedChild;
            if (parentRibbon?.StatusBar != null && childRibbon.StatusBar != null)
            {
                parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
            }
        }
    }
}