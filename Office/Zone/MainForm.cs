using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using DevExpress.XtraLayout;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.UI.Ribbon;
using Rizonesoft.Office.Zone.Controls;
using Rizonesoft.Office.Zone.Language;
using Timer = System.Timers.Timer;

namespace Rizonesoft.Office.Zone;

public sealed partial class MainForm : RibbonFormBase
{
    private const int ProgramCardControlCount = 33;
    private readonly LayoutControlItem[] _layoutControlItems;
    private readonly Dictionary<OfficeProgram, ProgramCardControl> _programCardControlMapping;
    private readonly ProgramCardControl[] _programCardControls;
    private RibbonGroupOptions _ribbonOptionsGroup;
    private RibbonPageSupport _ribbonSupportPage;

    public MainForm()
    {
        SplashScreenHelper.ShowSplashScreen(this);

        InitializeComponent();
        InitializeRibbonButtons();
        AfterInitializeComponents();

        _programCardControlMapping = new Dictionary<OfficeProgram, ProgramCardControl>();
        SetupSuperTipSvgIcons();

        _programCardControls = new ProgramCardControl[ProgramCardControlCount];
        _layoutControlItems = new LayoutControlItem[ProgramCardControlCount];

        AddProgramCardControlsToLayout();
        UpdateUI(false);

        RegisterEventHandlers();
        CheckUnavailablePrograms();
    }

    protected override void OnClosed(EventArgs e)
    {
        base.OnClosed(e);
        SaveSettings();
    }

    private void InitializeRibbonButtons()
    {
        _ribbonOptionsGroup = new RibbonGroupOptions(this, ribbonMain, ribGroupOptions);
        _ribbonSupportPage = new RibbonPageSupport(ribbonMain);

        foreach (OfficeProgram officeProgram in Enum.GetValues(typeof(OfficeProgram)))
        {
            var programButtonItem = GetProgramButtonItem(officeProgram);
            if (programButtonItem == null) continue;
            ConfigureRibbonProgramButtons(programButtonItem, officeProgram);
            programButtonItem.ItemClick += (_, _) => OfficeProgramButton_Click(officeProgram);
        }
    }

    private static void ConfigureRibbonProgramButtons(BarItem programButtonItem, OfficeProgram officeProgram)
    {
        programButtonItem.ImageOptions.SvgImage = ProgramSvgImage.GetSvgImage(officeProgram);
        programButtonItem.Caption = officeProgram.ToString();
    }

    private BarItem GetProgramButtonItem(OfficeProgram officeProgram)
    {
        return officeProgram switch
        {
            OfficeProgram.Verbum => bbItemVerbum,
            OfficeProgram.Evaluate => bbItemEvaluate,
            OfficeProgram.Flow => bbItemFlow,
            OfficeProgram.Imagine => bbItemImagine,
            OfficeProgram.Action => bbItemAction,
            OfficeProgram.Session => bbItemSession,
            OfficeProgram.Komplete => bbItemKomplete,
            OfficeProgram.Mission => bbItemMission,
            OfficeProgram.Qapture => bbItemQapture,
            OfficeProgram.Duplicare => bbItemDuplicare,
            OfficeProgram.Scholar => bbItemScholar,
            OfficeProgram.Xhibit => bbItemXhibit,
            OfficeProgram.Nerve => bbItemNerve,
            OfficeProgram.Globe => bbItemGlobe,
            OfficeProgram.Mia => bbItemMia,
            OfficeProgram.Voice => bbItemVoice,
            OfficeProgram.Wealth => bbItemWealth,
            OfficeProgram.Merchant => bbItemMerchant,
            OfficeProgram.Booking => bbItemBooking,
            OfficeProgram.Lead => bbItemLead,
            OfficeProgram.Yield => bbItemYield,
            OfficeProgram.Have => bbItemHave,
            OfficeProgram.Assure => bbItemAssure,
            OfficeProgram.Operate => bbItemOperate,
            OfficeProgram.Soap => bbItemSoap,
            OfficeProgram.Repo => bbItemRepo,
            OfficeProgram.Filer => bbItemFiler,
            OfficeProgram.Clock => bbItemClock,
            _ => null
        };
    }

    private void OfficeProgramButton_Click(OfficeProgram officeProgram)
    {
        var executablePath = Path.Join(AppDomain.CurrentDomain.BaseDirectory, $"{officeProgram}.exe");

        if (!File.Exists(executablePath))
        {
            XtraMessageBox.Show(
                $"We're in hot pursuit of the elusive '{officeProgram}', but it's proving to be quite the slippery character, " +
                $"always staying one step ahead. Rest assured, " +
                $"our determination is unwavering. " +
                $"Hang in there while we continue our chase and bring it to function.", "Coming Soon",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        var overlayManager = new OverlayManager();
        var control = _programCardControlMapping[officeProgram];
        if (control.Visible) { overlayManager.ShowOverlay(control); }
        try
        {
            using Process programProcess = new();
            programProcess.StartInfo.FileName = executablePath;
            programProcess.Start();

            if (!control.Visible) return;
            // Set up a timer to close the overlay after a specified interval (e.g., 3000 milliseconds or 3 seconds)
            var closeOverlayTimer = new Timer(3000);
            closeOverlayTimer.Elapsed += (_, _) =>
            {
                overlayManager.DisposeOverlay();
                closeOverlayTimer.Dispose();
            };
            closeOverlayTimer.Start();
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "Something went wrong.", ex);
        }

    }

    private void RegisterEventHandlers()
    {
        LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
        foreach (var entry in _programCardControlMapping) AddProgramCardClickedEventHandler(entry.Value, entry.Key);
    }

    private void AddProgramCardClickedEventHandler(ProgramCardControl programCardControl, OfficeProgram officeProgram)
    {
        programCardControl.ProgramCardClicked +=
            (_, _) => ProgramCardControl_ProgramCardClicked(officeProgram);
    }

    private void LanguageManager_LanguageChanged(object sender, EventArgs e)
    {
        UpdateUI(true);
    }

    private void SetupSuperTipSvgIcons()
    {
        SuperTipHelper.SetupSuperTipSvgIconsForItems(tabNavPrograms);
    }

    private void UpdateUI(bool ShowOverlay)
    {
        var overlayManager = new OverlayManager();
        if (ShowOverlay) overlayManager.ShowOverlay(this);

        _programCardControlMapping.Clear();
        ribPageHome.Text = Strings.RibbonPage_Home;
        ribGroupPrograms.Text = Strings.RibbonGroup_Programs;

        for (var i = 0; i < ProgramCardControlCount; i++)
        {
            _programCardControls[i].OffText = Strings.ProgramCardControl_OffText;
            _programCardControls[i].OnText = Strings.ProgramCardControl_OnText;
        }


        tabNavPrograms.Caption = Strings.RibbonGroup_Programs;
        SuperTipHelper.UpdateSuperTip(tabNavPrograms.SuperTip,
            string.Format(Strings.RibbonGroup_Programs, OfficeProgram.Scholar),
            Strings.Office_Scholar_Description);

        // Programs
        ConfigureProgramCardControl(_programCardControls[0], OfficeProgram.Verbum);
        ConfigureProgramCardControl(_programCardControls[1], OfficeProgram.Evaluate);
        ConfigureProgramCardControl(_programCardControls[2], OfficeProgram.Flow);
        ConfigureProgramCardControl(_programCardControls[3], OfficeProgram.Imagine);
        ConfigureProgramCardControl(_programCardControls[4], OfficeProgram.Action);
        ConfigureProgramCardControl(_programCardControls[5], OfficeProgram.Session);
        ConfigureProgramCardControl(_programCardControls[6], OfficeProgram.Komplete);
        ConfigureProgramCardControl(_programCardControls[7], OfficeProgram.Mission);

        // Accessories
        ConfigureProgramCardControl(_programCardControls[8], OfficeProgram.Qapture);
        ConfigureProgramCardControl(_programCardControls[9], OfficeProgram.Duplicare);
        ConfigureProgramCardControl(_programCardControls[10], OfficeProgram.Scholar);
        ConfigureProgramCardControl(_programCardControls[11], OfficeProgram.Xhibit);
        // Explore
        ConfigureProgramCardControl(_programCardControls[12], OfficeProgram.Nerve);
        ConfigureProgramCardControl(_programCardControls[13], OfficeProgram.Globe);
        ConfigureProgramCardControl(_programCardControls[14], OfficeProgram.Mia);
        ConfigureProgramCardControl(_programCardControls[15], OfficeProgram.Voice);
        // Business
        ConfigureProgramCardControl(_programCardControls[16], OfficeProgram.Wealth);
        ConfigureProgramCardControl(_programCardControls[17], OfficeProgram.Merchant);
        ConfigureProgramCardControl(_programCardControls[18], OfficeProgram.Booking);
        ConfigureProgramCardControl(_programCardControls[19], OfficeProgram.Lead);
        ConfigureProgramCardControl(_programCardControls[20], OfficeProgram.Yield);
        ConfigureProgramCardControl(_programCardControls[21], OfficeProgram.Have);
        ConfigureProgramCardControl(_programCardControls[22], OfficeProgram.Assure);
        ConfigureProgramCardControl(_programCardControls[23], OfficeProgram.Operate);
        ConfigureProgramCardControl(_programCardControls[24], OfficeProgram.ImagineBI);
        // Utilities
        ConfigureProgramCardControl(_programCardControls[28], OfficeProgram.Soap);
        ConfigureProgramCardControl(_programCardControls[29], OfficeProgram.Repo);
        ConfigureProgramCardControl(_programCardControls[30], OfficeProgram.Filer);
        ConfigureProgramCardControl(_programCardControls[31], OfficeProgram.Clock);

        ribGroupOptions.Text = Strings.RibbonGroup_Options;
        if (ShowOverlay) overlayManager.DisposeOverlay();

        lacPrograms.Refresh();
    }

    private static (ProgramCardControl, LayoutControlItem) CreateProgramCardControl()
    {
        var programCardControl = new ProgramCardControl { HoverBorderColor = Color.FromArgb(255, 13, 171, 182) };
        var layoutControlItem = new LayoutControlItem { Control = programCardControl, TextVisible = false };

        return (programCardControl, layoutControlItem);
    }

    private void ConfigureProgramCardControl(ProgramCardControl programCardControl, OfficeProgram officeProgram)
    {
        programCardControl.HoverBorderColor = ProgramColorManager.GetPredefinedColor(officeProgram);
        programCardControl.Description = Strings.ResourceManager.GetString($"Office_{officeProgram}_Description");
        programCardControl.SvgImage = ProgramSvgImage.GetSvgImage(officeProgram);
        programCardControl.Caption =
            string.Format(Strings.ResourceManager.GetString($"Office_{officeProgram}_Title") ?? "Caption",
                officeProgram);
        programCardControl.OffText = Strings.ProgramCardControl_OffText;
        programCardControl.OnText = Strings.ProgramCardControl_OnText;
        _programCardControlMapping.Add(officeProgram, programCardControl);

    }


    private void ProgramCardControl_ProgramCardClicked(OfficeProgram officeProgram)
    {
        OfficeProgramButton_Click(officeProgram);
    }

    private void AddProgramCardControlsToLayout()
    {
        for (var i = 0; i < ProgramCardControlCount; i++)
            (_programCardControls[i], _layoutControlItems[i]) = CreateProgramCardControl();

        AddControlsToLayout(lacPrograms, 2, _layoutControlItems.Take(8).ToArray());
        AddControlsToLayout(lacAccessories, 1, _layoutControlItems.Skip(8).Take(4).ToArray());
        AddControlsToLayout(lacExplore, 1, _layoutControlItems.Skip(12).Take(4).ToArray());
        AddControlsToLayout(lacBusiness, 3, _layoutControlItems.Skip(16).Take(12).ToArray());
        AddControlsToLayout(lacUtilities, 1, _layoutControlItems.Skip(28).Take(4).ToArray());
    }

    private static void AddControlsToLayout(LayoutControl layoutControl, int numRows,
        params LayoutControlItem[] layoutControlItems)
    {
        var numCols = layoutControlItems.Length / numRows;

        layoutControl.BeginUpdate();

        for (var i = 0; i < layoutControlItems.Length; i++)
        {
            var rowIndex = i / numCols;
            var colIndex = i % numCols;

            layoutControlItems[i].OptionsTableLayoutItem.ColumnIndex = colIndex;
            layoutControlItems[i].OptionsTableLayoutItem.RowIndex = rowIndex;
        }

        // ReSharper disable once CoVariantArrayConversion
        layoutControl.Root.AddRange(layoutControlItems);
        layoutControl.EndUpdate();

        // layoutControlItems[0].Visibility = LayoutVisibility.Never;
    }

    private void CheckUnavailablePrograms()
    {
        try
        {
            foreach (OfficeProgram officeProgram in Enum.GetValues(typeof(OfficeProgram)))
            {
                var executablePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, $"{officeProgram}.exe");

                if (File.Exists(executablePath)) continue;
                var programButtonItem = GetProgramButtonItem(officeProgram);
                if (programButtonItem != null) programButtonItem.Enabled = false;

                if (_programCardControlMapping.TryGetValue(officeProgram, out var programCardControl))
                    programCardControl.Enabled = false;
            }
        }
        catch (Exception e)
        {
            MessageBox.Show(e.Message);
            throw;
        }
    }

    private void MainForm_Shown(object sender, EventArgs e)
    {
        SplashScreenHelper.CloseSplashScreen();
    }

    private void MainForm_Load(object sender, EventArgs e)
    {
        FormGeometry.GeometryFromString(CommonSettings.Geometry, this);
        ribbonMain.Toolbar.RestoreLayoutFromRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
    }

    private void SaveSettings()
    {
        CommonSettings.Geometry = FormGeometry.GeometryToString(this);
        ribbonMain.Toolbar.SaveLayoutToRegistry($"{ProgramConfiguration.RegistryPath}\\Interface");
    }
}