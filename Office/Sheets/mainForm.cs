using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSplashScreen;
using Rizonesoft.Office.Sheets.Classes;
using System;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Windows.Forms;
using System.Xml;
using DevExpress.Utils.About;
using System.ServiceModel.Channels;
using Rizonesoft.Office.Licensing;
using NLog;
using Rizonesoft.Office.Interprocess;

namespace Rizonesoft.Office.Sheets
{
    public partial class MainForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        private static NLog.Logger nlogger = NLog.LogManager.GetCurrentClassLogger();
        private CopyData copyData = null;

        MruList mruList;

        internal bool isLicensed = false;
        internal int bookIndex = 0;
        internal bool IsFloating = false;
        internal BackgroundWorker updateWorker;


        public MainForm(string fileName)
        {

            isLicensed = LicenseCheck.IsLicensed();
            CreateSheetsDirectories();
            ConfigureLogging();
            OnShowMdiChildCaptionInParentTitle();

            InitializeComponent();

            CreateNewDocument(fileName);

            Initialize();

        }

        private void CreateSheetsDirectories()
        {
            if (!Directory.Exists(Globals.userAppDataPath))
            {
                Directory.CreateDirectory(Globals.userAppDataPath);
            }

        }

        private void Initialize()
        {
            // Create a new instance of the class:
            copyData = new CopyData();
            // Assign the handle:
            copyData.AssignHandle(Handle);
            // Create the named channels to send and receive on.
            copyData.Channels.Add("WorkbookChannel");
            // Hook up event notifications whenever a message is received:
            copyData.DataReceived += new DataReceivedEventHandler(copyData_DataReceived);

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


        #region Settings

        private void LoadSettings()
        {
            string sSkin;
            string sPalette;
            string sGeometry;

            sSkin = Settings.GetSetting("Rizonesoft\\Sheets\\Interface", "Skin", "Office 2019 Colorful");
            sPalette = Settings.GetSetting("Rizonesoft\\Sheets\\Interface", "Palette", "Forest");
            sGeometry = Settings.GetSetting("Rizonesoft\\Sheets\\General", "Geometry", string.Empty);

            MainForm formIn = this;
            Utilities.GeometryFromString(sGeometry, formIn);
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);

        }

        private void SaveSettings()
        {
            Settings.SaveSetting("Rizonesoft\\Sheets\\Interface", "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.SaveSetting("Rizonesoft\\Sheets\\Interface", "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
            Settings.SaveSetting("Rizonesoft\\Sheets\\General", "Geometry", Utilities.GeometryToString(this));
        }

        #endregion Settings


        #region Workbook Processing

        public void CreateNewDocument(string fileName)
        {
            // Detect whether file is already open
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
            CreateNewDocument(fileName);
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }


        #endregion Workbook Processing


        #region Events

        private void copyData_DataReceived(object sender, DataReceivedEventArgs e)
        {

            // Display the data in the logging list box:
            if (e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewDocument(fileName);
                AddFileToMRUList(fileName);
            }

        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            LoadSettings();

            this.MainRibbonControl.ForceInitialize();
            mruList = new MruList("MRU", mruPopupMenu, 10, "Rizonesoft\\Verbum\\MRU");
            mruList.FileSelected += mruList_FileSelected;
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
        }

        private void mruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        #endregion Events


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
                    nlogger.Error(ioEx, "Whoops!");
                }
            }
        }


        private void MainRibbonControl_Merge(object sender, DevExpress.XtraBars.Ribbon.RibbonMergeEventArgs e)
        {
            RibbonControl parentRibbon = sender as RibbonControl;
            RibbonControl childRibbon = e.MergedChild;
            parentRibbon.StatusBar.MergeStatusBar(childRibbon.StatusBar);
        }

        
    }
}
