using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Forms;
using System.Windows.Forms;
using Rizonesoft.Office.UI.Ribbon;
using System;
using System.Drawing;
using Rizonesoft.Office.Utilities;
using System.Linq;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.ErrorHandling;
using System.IO;
using Rizonesoft.Office.Evaluate.Language;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings;
using DevExpress.Utils;
using DevExpress.XtraTabbedMdi;



namespace Rizonesoft.Office.Evaluate
{
    public partial class MainForm : RibbonFormBase
    {

        private readonly CopyData copyData;
        private int documentIndex;
        private static MruList _mruList;
        public static bool IsLicensed { get; private set; }

        private const string CopyChannelName = "BookChannel";
        private readonly SvgImageCollection extensionsSvgImages;
        private readonly string initialFileName;

        #region Properties

        /*private BookForm CurrentBook
        {
            get
            {
                if (ActiveMdiChild is not BookForm && CoreMdiManager.ActiveFloatForm is not BookForm)
                {
                    return null;
                }

                return CoreMdiManager.ActiveFloatForm as BookForm ?? ActiveMdiChild as BookForm;
            }
        }*/

        #endregion Properties

        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            SaveSettings();
        }

        private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
        {
            if (e.ChannelName != null && !e.ChannelName.Equals(CopyChannelName)) return;
            if (WindowState == FormWindowState.Minimized)
            {
                WindowState = FormWindowState.Normal;
            }

            var fileName = (string)e.Data;
            CreateNewDocument(fileName);
            AddFileToMruList(fileName);
            Activate();
        }


        public MainForm(string fileName)
        {
            SplashScreenHelper.ShowSplashScreen(this);
            initialFileName = fileName;

            copyData = new CopyData();
            copyData.AssignHandle(Handle);
            copyData.Channels?.Add(CopyChannelName);
            copyData.DataReceived += CopyData_DataReceived;

            extensionsSvgImages = new SvgImageCollection();
            InitializeSvgImages();

            InitializeComponent();
            Opacity = 0;
            AfterInitializeComponents();

            InitializeRibbon();
            UpdateUi(false);
            LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;

            ControlConfig.SetDefaultMdiManagerConfig(CoreMdiManager, this);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
            mainRibbon.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");

            try
            {
                if (ProgramConfiguration.SettingsFilePath == null) return;
                _mruList = new MruList(MruPopupMenu, 10, new MruRegistryHandler());
                _mruList.Initialize();
                _mruList.FileSelected += MruList_FileSelected;
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, $"Failed to load MRU list from {ProgramConfiguration.SettingsFilePath}.", ex);
            }
        }

        private void SaveSettings()
        {
            CommonSettings.Geometry = FormGeometry.GeometryToString(this);
            mainRibbon.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
        }

        private void InitializeSvgImages()
        {
            extensionsSvgImages.Add("exporttoxls", "image://svgimages/export/exporttoxls.svg");
            extensionsSvgImages.Add("exporttoxlsx", "image://svgimages/export/exporttoxlsx.svg");
            extensionsSvgImages.Add("exporttocsv", "image://svgimages/export/exporttocsv.svg");
            extensionsSvgImages.Add("exporttotxt", "image://svgimages/export/exporttotxt.svg");
            extensionsSvgImages.Add("new", "image://svgimages/actions/new.svg");
        }

        private void MruList_FileSelected(string fileName)
        {
            OpenFile(fileName);
        }

        private void InitializeRibbon()
        {
            mainRibbon.ForceInitialize();
            _ = new RibbonGroupOptions(this, mainRibbon, OptionsRibbonGroup)
            {
                IsLanguageDropdownVisible = false
            };
            _ = new RibbonPageSupport(mainRibbon);
        }

        private void UpdateUi(bool showOverlay)
        {
            var overlayManager = new OverlayManager();
            if (showOverlay) overlayManager.ShowOverlay(this);

            FileRibbonPage.Text = Dialogs.RibbonPage_File;
            CommonRibbonGroup.Text = Dialogs.RibbonGroup_Common;

            if (showOverlay) overlayManager.DisposeOverlay();
        }

        private void MainForm_Shown(object sender, EventArgs e)
        {
            CreateNewDocument(initialFileName);
            SplashScreenHelper.CloseSplashScreen();
            Opacity = 1;
        }

        private void CreateNewDocument(string fileName)
        {
            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (var openForm in MdiChildren.Cast<BookForm>())
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

            BookForm newBookForm = new(fileName)
            {
                MdiParent = this,
            };

            newBookForm.Show();
            newBookForm.OpenFile(fileName, documentIndex);
            UpdateTabImageForBookForm(newBookForm);
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
                DefaultExt = "xlsx",
                FileName = initialDirectory,

            };

            if (initialDirectory != string.Empty)
            {
                openFileDlg.InitialDirectory = initialDirectory;
            }

            if (openFileDlg.ShowDialog() != DialogResult.OK) return;

            var fileName = openFileDlg.FileName;
            AddFileToMruList(fileName);
            OpenFile(fileName);

        }

        private void OpenFile(string fileName)
        {
            var overlayManager = new OverlayManager();
            overlayManager.ShowOverlay(this);
            CreateNewDocument(fileName);
            overlayManager.DisposeOverlay();
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

        private void NewBarBtn_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewDocument(null);
        }

        private void CoreMdiManager_PageAdded(object sender, MdiTabPageEventArgs e)
        {
            if (e.Page.MdiChild is BookForm bookForm)
            {
                bookForm.FileNameChanged += BookForm_FileNameChanged;
            }
        }

        private void BookForm_FileNameChanged(object sender, EventArgs e)
        {
            if (sender is BookForm childBookForm)
            {
                UpdateTabImageForBookForm(childBookForm);
            }
        }

        private void UpdateTabImageForBookForm(BookForm childBookForm)
        {
            if (childBookForm == null) return;

            var fileName = childBookForm.FileName;
            var extension = Path.GetExtension(fileName);
            var tabPage = CoreMdiManager.Pages[childBookForm];

            if (tabPage == null) return;
            if (!string.IsNullOrWhiteSpace(extension))
            {
                var svgImage = ImageResourceLoader.GetIconForExtension(extension);
                tabPage.ImageOptions.SvgImage = extensionsSvgImages[svgImage];
            }
            else
            {
                tabPage.ImageOptions.SvgImage = extensionsSvgImages["new"];
            }

            tabPage.ImageOptions.SvgImageSize = new Size(24, 24);
        }
    }
}
