using DevExpress.Utils;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Ribbon;
using Rizonesoft.Office.Utilities;
using Syncfusion.Pdf;
using Syncfusion.Pdf.Parsing;
using System;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraBars.Ribbon;
using Rizonesoft.Office.UI.Forms;

namespace Rizonesoft.Office.Scholar;

/// <summary>
/// Represents the main form of the Scholar application.
/// </summary>
public sealed partial class MainForm : RibbonFormBase
{
    private readonly CopyData copyData;
    private int viewerIndex;
    private static MruList _mruList;
    private readonly SvgImageCollection extensionsSvgImages;


    private DocForm CurrentDocument
    {
        get
        {
            if (ActiveMdiChild == null)
            {
                return null;
            }
            if (mainMdiManager.ActiveFloatForm != null)
            {
                return mainMdiManager.ActiveFloatForm as DocForm;
            }

            return ActiveMdiChild as DocForm;
        }
    }

    private void CopyData_DataReceived(object sender, DataReceivedEventArgs e)
    {
        if (e.ChannelName != null && !e.ChannelName.Equals("DocChannel")) return;
        if (WindowState == FormWindowState.Minimized)
        {
            WindowState = FormWindowState.Normal;
        }

        var fileName = (string)e.Data;
        CreateNewViewer(fileName);
        AddFileToMruList(fileName);
        Activate();

        // MessageBox.Show(@"Eureka! We've struck data! Filename: " + fileName);
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

        extensionsSvgImages = new SvgImageCollection();
        InitializeSvgImages();

        InitializeComponent();
        AfterInitializeComponents();

        InitializeRibbon();
        UpdateUi();

        ControlConfig.SetDefaultMdiManagerConfig(mainMdiManager, this);
        CreateNewViewer(fileName);
    }

    protected override void OnClosed(EventArgs e)
    {
        base.OnClosed(e);
        SaveSettings();
    }

    private void UpdateUi()
    {
        HomeRibbonPage.Text = Dialogs.RibbonMain_Home;
    }

    public static void AddFileToMruList(string fileName)
    {
        if (string.IsNullOrEmpty(fileName)) return;
        try
        {
            _mruList?.AddFile(fileName);
        }
        catch (Exception ioEx)
        {
            Serilogger.LogMessage(LogLevel.Warning, "The file could not be found.", ioEx);
        }
    }

    private void InitializeSvgImages()
    {
        extensionsSvgImages.Add("exporttopdf", "image://svgimages/export/exporttopdf.svg");
        extensionsSvgImages.Add("new", "image://svgimages/actions/new.svg");
    }

    private void CreateNewViewer(string fileName)
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
            viewerIndex++;
        }

        DocForm newViewer = new()
        {
            MdiParent = this
        };
        newViewer.OpenFile(fileName, viewerIndex);
        newViewer.Show();
    }

    private void OpenFile(string fileName)
    {
        CreateNewViewer(fileName);
    }

    internal void OpenFile()
    {
        OpenFileFolder(string.Empty);
    }

    private void OpenFileFolder(string sIniDir)
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
            DefaultExt = "pdf",
            FileName = sIniDir,

        };

        if (sIniDir != string.Empty)
        {
            openFileDlg.InitialDirectory = sIniDir;
        }

        var dlgResult = openFileDlg.ShowDialog();

        // Show the dialog and get result.
        if (dlgResult != DialogResult.OK) return;
        var fileName = openFileDlg.FileName;
        AddFileToMruList(fileName);
        OpenFile(fileName);

    }

    private void InitializeRibbon()
    {
        ribbonMain.ForceInitialize();
        _ = new RibbonGroupOptions(this, ribbonMain, OptionsRibbonGroup)
        {
            IsLanguageDropdownVisible = false
        };
        _ = new RibbonPageSupport(ribbonMain);
    }

    private void MainForm_Shown(object sender, EventArgs e)
    {
        SplashScreenHelper.CloseSplashScreen();
    }

    private void MainForm_Load(object sender, EventArgs e)
    {
        FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
        ribbonMain.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");

        try
        {
            if (ProgramConfiguration.SettingsFilePath != null)
            {
                _mruList = new MruList(mruPopupMenu, 10, new MruRegistryHandler());
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

    private void SaveSettings()
    {
        CommonSettings.Geometry = FormGeometry.GeometryToString(this);
        ribbonMain.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
    }

    private void SaveRibbon()
    {

    }

    private void MruList_FileSelected(string fileName)
    {
        OpenFile(fileName);
    }

    private void OpenBarItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
    {
        OpenFileFolder(Environment.CurrentDirectory);
    }

    private void CompressBarButton_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
    {
        byte[] inputFile = File.ReadAllBytes(CurrentDocument.FileName);

        PdfLoadedDocument ldoc = new PdfLoadedDocument(inputFile);
        PdfCompressionOptions options = new PdfCompressionOptions();

        options.CompressImages = true;
        options.ImageQuality = 8;
        options.OptimizeFont = true;
        options.OptimizePageContents = true;
        options.RemoveMetadata = true;

        ldoc.CompressionOptions = options;

        using (MemoryStream ms = new MemoryStream())
        {
            ldoc.Save(ms);

            // Show "Save As" dialog to allow the user to choose the save location and file name.
            SaveFileDialog saveFileDialog = new SaveFileDialog();
            saveFileDialog.Filter = "PDF files (*.pdf)|*.pdf|All files (*.*)|*.*";
            saveFileDialog.FileName = "compressed_" + Path.GetFileName(CurrentDocument.FileName);

            if (saveFileDialog.ShowDialog() == DialogResult.OK)
            {
                // Save the compressed PDF to the selected file path.
                File.WriteAllBytes(saveFileDialog.FileName, ms.ToArray());
                MessageBox.Show("Compression complete. File saved to: " + saveFileDialog.FileName);
            }
        }
    }

    private void MainMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
    {
        if (e.Page.MdiChild is DocForm docForm)
        {
            docForm.FileNameChanged += DocForm_FileNameChanged;
        }
    }

    private void DocForm_FileNameChanged(object sender, EventArgs e)
    {
        if (sender is DocForm childDocForm)
        {
            UpdateTabImageForBookForm(childDocForm);
        }
    }

    private void UpdateTabImageForBookForm(DocForm childDocForm)
    {
        if (childDocForm == null) return;

        var fileName = childDocForm.FileName;
        var extension = Path.GetExtension(fileName);
        var tabPage = mainMdiManager.Pages[childDocForm];

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