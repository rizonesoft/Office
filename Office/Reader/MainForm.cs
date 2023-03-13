namespace Rizonesoft.Office.Reader
{
    using DevExpress.XtraBars.Ribbon;
    using DevExpress.XtraEditors;
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Interprocess;
    using Rizonesoft.Office.Reader.Utilities;
    using Rizonesoft.Office.Utilities;
    using System;
    using System.ComponentModel;
    using System.IO;
    using System.Linq;
    using System.Windows.Forms;

    public partial class MainForm : RibbonForm
    {
        private CopyData copyData;
        private static MruList mruList;
        internal int viewerIndex;
        internal bool IsFloating;
        internal bool isLicensed;
        internal BackgroundWorker updateWorker;

        #region Properties

        ViewerForm CurrentViewer
        {
            get
            {
                if (ActiveMdiChild == null)
                {
                    return null;
                }
                if (mainTabbedMdiManager.ActiveFloatForm != null)
                {
                    return mainTabbedMdiManager.ActiveFloatForm as ViewerForm;
                }

                return ActiveMdiChild as ViewerForm;
            }
        }

        #endregion Properties

        public MainForm(string fileName)
        {
            SetSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreenForm), true, true, false);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, "Initializing");
            OnShowMdiChildCaptionInParentTitle();
            CreateProgramDirectories();
            InitializeComponent();
            base.Text = $"{StcReader.ProductName} {RizonesoftEx.ProductVersionMajor}";
            Initialize();
            CreateNewViewer(StcReader.WelcomePDFPath);
            SplashScreenManager.Default.SendCommand(SplashScreenForm.SplashScreenCommand.SetStatusLabel, $"Completed - Loading {StcReader.ProductName}");
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            
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
            copyData.Channels.Add("PDFChannel");
            copyData.DataReceived += new DataReceivedEventHandler(CopyData_DataReceived);
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName.Equals("PDFChannel"))
            {
                string fileName = (string)e.Data;
                CreateNewViewer(fileName);
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
                    Logging.logger.Error(ioEx, "Unable to add filename to MRU list.");
                }
            }
        }

        private void MruList_FileSelected(string fileName)
        {
            // OpenFile(fileName);
        }

        #endregion Initialize

        #region Viewer Processing

        public void CreateNewViewer(string fileName)
        {

            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (ViewerForm openForm in MdiChildren.Cast<ViewerForm>())
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
                viewerIndex++;
            }
             
            ViewerForm newViewer = new();
            newViewer.OpenFile(fileName, viewerIndex);
            newViewer.MdiParent = this;
            newViewer.Show();
        }

        public void OpenFile(string fileName)
        {
            CreateNewViewer(fileName);
        }

        internal void OpenFile()
        {
            OpenFileFolder(string.Empty);
        }

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
                // AddFileToMRUList(fileName);
            }
        }

        #endregion Viewer Processing

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

        #region Settings

        private void LoadSettings()
        {
            RizonesoftEx.GeometryFromString(Settings.Settings.GetSetting(StcReader.CurrentRegGeneralPath, "Geometry", string.Empty), this);

        }

        private void SaveSettings()
        {
            Settings.Settings.SaveSetting(StcReader.CurrentRegGeneralPath, "Geometry", RizonesoftEx.GeometryToString(this));

        }

        private static void SetSkins()
        {
            string sSkin = Settings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Skin", "Office 2019 Colorful");
            string sPalette = Settings.Settings.GetSetting(StcReader.CurrentRegInterfacePath, "Palette", "Fire Brick");
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle(sSkin, sPalette);

        }

        private static void SaveSkins()
        {
            Settings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.Settings.SaveSetting(StcReader.CurrentRegInterfacePath, "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        private bool SaveRestoreRibbon(bool SaveRibbon)
        {
            if (mainRibbonControl != null)
            {
                switch (SaveRibbon)
                {
                    case true:
                        mainRibbonControl.Toolbar.SaveLayoutToRegistry(StcReader.StaticRegInterfacePath);
                        return true;
                    case false:
                        mainRibbonControl.Toolbar.RestoreLayoutFromRegistry(StcReader.StaticRegInterfacePath);
                        return true;
                }
            }

            return false;

        }

        #endregion Settings

        #region Configurations

        private static void CreateProgramDirectories()
        {
            if (!Directory.Exists(StcReader.UserAppDirectory))
            {
                Directory.CreateDirectory(StcReader.UserAppDirectory);
            }
        }




        #endregion Configurations

        
    }
}
