using DevExpress.XtraBars.Navigation;
using Rizonesoft.Office.Language;

namespace Rizonesoft.Office.Settings
{
    partial class SettingsForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SettingsForm));
            DevExpress.XtraEditors.Controls.ImageListBoxItemImageOptions imageListBoxItemImageOptions1 = new DevExpress.XtraEditors.Controls.ImageListBoxItemImageOptions();
            tablePanel2 = new DevExpress.Utils.Layout.TablePanel();
            lblLocalDescription = new DevExpress.XtraEditors.LabelControl();
            lblCurrCult = new DevExpress.XtraEditors.LabelControl();
            lblCurrLang = new DevExpress.XtraEditors.LabelControl();
            lblCurrCultLabel = new DevExpress.XtraEditors.LabelControl();
            lblCurrLangLabel = new DevExpress.XtraEditors.LabelControl();
            lblSelectLanguage = new DevExpress.XtraEditors.LabelControl();
            languageList = new DevExpress.XtraEditors.ImageListBoxControl();
            BtnCleanLog = new DevExpress.XtraEditors.SimpleButton();
            layoutControl1 = new DevExpress.XtraLayout.LayoutControl();
            BtnOpenLog = new DevExpress.XtraEditors.SimpleButton();
            toolTipSettingsController = new DevExpress.Utils.ToolTipController(components);
            SpinLoggingFileLimit = new DevExpress.XtraEditors.SpinEdit();
            groupRollingInterval = new DevExpress.XtraEditors.GroupControl();
            radGroupInterval = new DevExpress.XtraEditors.RadioGroup();
            Root = new DevExpress.XtraLayout.LayoutControlGroup();
            layoutControlItem1 = new DevExpress.XtraLayout.LayoutControlItem();
            FileLimitLayoutItem = new DevExpress.XtraLayout.LayoutControlItem();
            layoutControlItem3 = new DevExpress.XtraLayout.LayoutControlItem();
            layoutControlItem4 = new DevExpress.XtraLayout.LayoutControlItem();
            langPopup = new DevExpress.XtraBars.PopupMenu(components);
            ribbonControl1 = new DevExpress.XtraBars.Ribbon.RibbonControl();
            SkinDropDownButton = new DevExpress.XtraBars.SkinDropDownButtonItem();
            SkinPaletteRibbonGallery = new DevExpress.XtraBars.SkinPaletteRibbonGalleryBarItem();
            AccentColorsCheckItem = new DevExpress.XtraBars.BarCheckItem();
            ribbonPage1 = new DevExpress.XtraBars.Ribbon.RibbonPage();
            SkinsRibbonPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ColorsRibbonPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            accordionControlElement1 = new AccordionControlElement();
            SettingsNavigationPane = new NavigationPane();
            GeneralNavPage = new NavigationPage();
            xtraScrollableControl1 = new DevExpress.XtraEditors.XtraScrollableControl();
            LocalizationPanel = new DevExpress.XtraEditors.PanelControl();
            groupControl1 = new DevExpress.XtraEditors.GroupControl();
            AdvancedNavPage = new NavigationPage();
            xtraScrollableControl2 = new DevExpress.XtraEditors.XtraScrollableControl();
            LoggingPanel = new DevExpress.XtraEditors.PanelControl();
            groupControl2 = new DevExpress.XtraEditors.GroupControl();
            InterfaceNavPage = new NavigationPage();
            panelControl1 = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)tablePanel2).BeginInit();
            tablePanel2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)languageList).BeginInit();
            ((System.ComponentModel.ISupportInitialize)layoutControl1).BeginInit();
            layoutControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)SpinLoggingFileLimit.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)groupRollingInterval).BeginInit();
            groupRollingInterval.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)radGroupInterval.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)Root).BeginInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem1).BeginInit();
            ((System.ComponentModel.ISupportInitialize)FileLimitLayoutItem).BeginInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem3).BeginInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem4).BeginInit();
            ((System.ComponentModel.ISupportInitialize)langPopup).BeginInit();
            ((System.ComponentModel.ISupportInitialize)ribbonControl1).BeginInit();
            ((System.ComponentModel.ISupportInitialize)SettingsNavigationPane).BeginInit();
            SettingsNavigationPane.SuspendLayout();
            GeneralNavPage.SuspendLayout();
            xtraScrollableControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)LocalizationPanel).BeginInit();
            LocalizationPanel.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)groupControl1).BeginInit();
            groupControl1.SuspendLayout();
            AdvancedNavPage.SuspendLayout();
            xtraScrollableControl2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)LoggingPanel).BeginInit();
            LoggingPanel.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)groupControl2).BeginInit();
            groupControl2.SuspendLayout();
            InterfaceNavPage.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)panelControl1).BeginInit();
            SuspendLayout();
            // 
            // tablePanel2
            // 
            tablePanel2.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 60F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 95F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 181F) });
            tablePanel2.Controls.Add(lblLocalDescription);
            tablePanel2.Controls.Add(lblCurrCult);
            tablePanel2.Controls.Add(lblCurrLang);
            tablePanel2.Controls.Add(lblCurrCultLabel);
            tablePanel2.Controls.Add(lblCurrLangLabel);
            tablePanel2.Controls.Add(lblSelectLanguage);
            tablePanel2.Controls.Add(languageList);
            tablePanel2.Dock = DockStyle.Fill;
            tablePanel2.Location = new Point(2, 23);
            tablePanel2.Name = "tablePanel2";
            tablePanel2.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 35F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F) });
            tablePanel2.Size = new Size(707, 308);
            tablePanel2.TabIndex = 2;
            tablePanel2.UseSkinIndents = true;
            // 
            // lblLocalDescription
            // 
            lblLocalDescription.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblLocalDescription.Appearance.Options.UseFont = true;
            lblLocalDescription.Appearance.Options.UseTextOptions = true;
            lblLocalDescription.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            lblLocalDescription.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            lblLocalDescription.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel2.SetColumn(lblLocalDescription, 0);
            tablePanel2.SetColumnSpan(lblLocalDescription, 2);
            lblLocalDescription.Dock = DockStyle.Fill;
            lblLocalDescription.Location = new Point(14, 13);
            lblLocalDescription.Margin = new Padding(3, 3, 20, 3);
            lblLocalDescription.Name = "lblLocalDescription";
            tablePanel2.SetRow(lblLocalDescription, 0);
            tablePanel2.SetRowSpan(lblLocalDescription, 2);
            lblLocalDescription.Size = new Size(481, 161);
            lblLocalDescription.TabIndex = 2;
            lblLocalDescription.Text = resources.GetString("lblLocalDescription.Text");
            // 
            // lblCurrCult
            // 
            lblCurrCult.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblCurrCult.Appearance.Options.UseFont = true;
            lblCurrCult.AutoEllipsis = true;
            lblCurrCult.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel2.SetColumn(lblCurrCult, 1);
            lblCurrCult.Dock = DockStyle.Fill;
            lblCurrCult.Location = new Point(208, 219);
            lblCurrCult.Name = "lblCurrCult";
            tablePanel2.SetRow(lblCurrCult, 3);
            lblCurrCult.Size = new Size(305, 36);
            lblCurrCult.TabIndex = 6;
            lblCurrCult.Text = "en";
            // 
            // lblCurrLang
            // 
            lblCurrLang.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblCurrLang.Appearance.Options.UseFont = true;
            lblCurrLang.AutoEllipsis = true;
            lblCurrLang.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel2.SetColumn(lblCurrLang, 1);
            lblCurrLang.Dock = DockStyle.Fill;
            lblCurrLang.Location = new Point(208, 179);
            lblCurrLang.Name = "lblCurrLang";
            tablePanel2.SetRow(lblCurrLang, 2);
            lblCurrLang.Size = new Size(305, 36);
            lblCurrLang.TabIndex = 5;
            lblCurrLang.Text = "English";
            // 
            // lblCurrCultLabel
            // 
            lblCurrCultLabel.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            lblCurrCultLabel.Appearance.Options.UseFont = true;
            lblCurrCultLabel.AutoEllipsis = true;
            lblCurrCultLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel2.SetColumn(lblCurrCultLabel, 0);
            lblCurrCultLabel.Dock = DockStyle.Fill;
            lblCurrCultLabel.Location = new Point(13, 219);
            lblCurrCultLabel.Name = "lblCurrCultLabel";
            tablePanel2.SetRow(lblCurrCultLabel, 3);
            lblCurrCultLabel.Size = new Size(191, 36);
            lblCurrCultLabel.TabIndex = 4;
            lblCurrCultLabel.Text = "Current Language ISO:";
            // 
            // lblCurrLangLabel
            // 
            lblCurrLangLabel.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            lblCurrLangLabel.Appearance.Options.UseFont = true;
            lblCurrLangLabel.AutoEllipsis = true;
            lblCurrLangLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel2.SetColumn(lblCurrLangLabel, 0);
            lblCurrLangLabel.Dock = DockStyle.Fill;
            lblCurrLangLabel.Location = new Point(13, 179);
            lblCurrLangLabel.Name = "lblCurrLangLabel";
            tablePanel2.SetRow(lblCurrLangLabel, 2);
            lblCurrLangLabel.Size = new Size(191, 36);
            lblCurrLangLabel.TabIndex = 3;
            lblCurrLangLabel.Text = "Current Language:";
            // 
            // lblSelectLanguage
            // 
            lblSelectLanguage.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            lblSelectLanguage.Appearance.Options.UseFont = true;
            tablePanel2.SetColumn(lblSelectLanguage, 2);
            lblSelectLanguage.Dock = DockStyle.Fill;
            lblSelectLanguage.Location = new Point(517, 12);
            lblSelectLanguage.Name = "lblSelectLanguage";
            tablePanel2.SetRow(lblSelectLanguage, 0);
            lblSelectLanguage.Size = new Size(177, 31);
            lblSelectLanguage.TabIndex = 1;
            lblSelectLanguage.Text = "Select Language";
            // 
            // languageList
            // 
            tablePanel2.SetColumn(languageList, 2);
            languageList.Dock = DockStyle.Fill;
            languageList.GlyphAlignment = DevExpress.Utils.HorzAlignment.Default;
            languageList.ItemHeight = 32;
            languageList.ItemPadding = new Padding(30, 0, 0, 0);
            imageListBoxItemImageOptions1.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("imageListBoxItemImageOptions1.SvgImage");
            imageListBoxItemImageOptions1.SvgImageSize = new Size(32, 32);
            languageList.Items.AddRange(new DevExpress.XtraEditors.Controls.ImageListBoxItem[] { new DevExpress.XtraEditors.Controls.ImageListBoxItem("Language", "", imageListBoxItemImageOptions1, null) });
            languageList.Location = new Point(517, 47);
            languageList.Name = "languageList";
            tablePanel2.SetRow(languageList, 1);
            tablePanel2.SetRowSpan(languageList, 4);
            languageList.Size = new Size(177, 248);
            languageList.TabIndex = 0;
            // 
            // BtnCleanLog
            // 
            BtnCleanLog.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            BtnCleanLog.Appearance.Options.UseFont = true;
            BtnCleanLog.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("BtnCleanLog.ImageOptions.SvgImage");
            BtnCleanLog.Location = new Point(526, 126);
            BtnCleanLog.Margin = new Padding(6, 10, 6, 7);
            BtnCleanLog.Name = "BtnCleanLog";
            BtnCleanLog.Size = new Size(169, 36);
            BtnCleanLog.StyleController = layoutControl1;
            BtnCleanLog.TabIndex = 12;
            BtnCleanLog.Text = "Clean Serilog";
            BtnCleanLog.ToolTip = resources.GetString("BtnCleanLog.ToolTip");
            BtnCleanLog.ToolTipController = toolTipSettingsController;
            BtnCleanLog.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Asterisk;
            BtnCleanLog.ToolTipTitle = "Clean the Serilog Directory";
            BtnCleanLog.Click += BtnCleanLog_Click;
            // 
            // layoutControl1
            // 
            layoutControl1.Controls.Add(BtnCleanLog);
            layoutControl1.Controls.Add(BtnOpenLog);
            layoutControl1.Controls.Add(SpinLoggingFileLimit);
            layoutControl1.Controls.Add(groupRollingInterval);
            layoutControl1.Dock = DockStyle.Fill;
            layoutControl1.Location = new Point(2, 23);
            layoutControl1.Name = "layoutControl1";
            layoutControl1.Root = Root;
            layoutControl1.Size = new Size(707, 174);
            layoutControl1.TabIndex = 0;
            layoutControl1.Text = "layoutControl1";
            // 
            // BtnOpenLog
            // 
            BtnOpenLog.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            BtnOpenLog.Appearance.Options.UseFont = true;
            BtnOpenLog.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("BtnOpenLog.ImageOptions.SvgImage");
            BtnOpenLog.Location = new Point(355, 126);
            BtnOpenLog.Margin = new Padding(6, 10, 6, 4);
            BtnOpenLog.Name = "BtnOpenLog";
            BtnOpenLog.Size = new Size(167, 36);
            BtnOpenLog.StyleController = layoutControl1;
            BtnOpenLog.TabIndex = 11;
            BtnOpenLog.Text = "Open log";
            BtnOpenLog.ToolTip = "Open the Serilog logging directory.";
            BtnOpenLog.ToolTipController = toolTipSettingsController;
            BtnOpenLog.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            BtnOpenLog.ToolTipTitle = "Open Serilog Directory";
            BtnOpenLog.Click += BtnOpenLog_Click;
            // 
            // toolTipSettingsController
            // 
            toolTipSettingsController.AllowHtmlText = true;
            toolTipSettingsController.AutoPopDelay = 20000;
            toolTipSettingsController.Rounded = true;
            toolTipSettingsController.RoundRadius = 6;
            toolTipSettingsController.ShowBeak = true;
            toolTipSettingsController.ToolTipType = DevExpress.Utils.ToolTipType.SuperTip;
            // 
            // SpinLoggingFileLimit
            // 
            SpinLoggingFileLimit.EditValue = new decimal(new int[] { 0, 0, 0, 0 });
            SpinLoggingFileLimit.Location = new Point(64, 133);
            SpinLoggingFileLimit.Margin = new Padding(5);
            SpinLoggingFileLimit.Name = "SpinLoggingFileLimit";
            SpinLoggingFileLimit.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            SpinLoggingFileLimit.Properties.Appearance.Options.UseFont = true;
            SpinLoggingFileLimit.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            SpinLoggingFileLimit.Properties.EditFormat.FormatType = DevExpress.Utils.FormatType.Numeric;
            SpinLoggingFileLimit.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Default;
            SpinLoggingFileLimit.Properties.IsFloatValue = false;
            SpinLoggingFileLimit.Properties.MaskSettings.Set("mask", "N00");
            SpinLoggingFileLimit.Size = new Size(269, 22);
            SpinLoggingFileLimit.StyleController = layoutControl1;
            SpinLoggingFileLimit.TabIndex = 13;
            SpinLoggingFileLimit.ToolTip = "Sets a limit on how many log files can stick around in the logging system. It helps keep things shipshape and prevents an avalanche of log files from burying us alive.";
            SpinLoggingFileLimit.ToolTipController = toolTipSettingsController;
            SpinLoggingFileLimit.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            SpinLoggingFileLimit.ToolTipTitle = "Log File Limit";
            SpinLoggingFileLimit.ValueChanged += SpinLoggingFileLimit_ValueChanged;
            // 
            // groupRollingInterval
            // 
            groupRollingInterval.AppearanceCaption.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            groupRollingInterval.AppearanceCaption.Options.UseFont = true;
            groupRollingInterval.Controls.Add(radGroupInterval);
            groupRollingInterval.Location = new Point(12, 12);
            groupRollingInterval.Margin = new Padding(3, 4, 3, 10);
            groupRollingInterval.Name = "groupRollingInterval";
            groupRollingInterval.Size = new Size(683, 110);
            groupRollingInterval.TabIndex = 8;
            groupRollingInterval.Text = "Rolling Interval";
            // 
            // radGroupInterval
            // 
            radGroupInterval.Dock = DockStyle.Fill;
            radGroupInterval.Location = new Point(2, 23);
            radGroupInterval.Margin = new Padding(3, 4, 3, 4);
            radGroupInterval.Name = "radGroupInterval";
            radGroupInterval.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            radGroupInterval.Properties.Appearance.Options.UseFont = true;
            radGroupInterval.Properties.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            radGroupInterval.Properties.Items.AddRange(new DevExpress.XtraEditors.Controls.RadioGroupItem[] { new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Minute"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Hour"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Day"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Month"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Infinite") });
            radGroupInterval.Properties.Padding = new Padding(10, 4, 4, 4);
            radGroupInterval.Size = new Size(679, 85);
            radGroupInterval.TabIndex = 0;
            radGroupInterval.ToolTipController = toolTipSettingsController;
            radGroupInterval.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            radGroupInterval.ToolTipTitle = "Log rolling interval";
            radGroupInterval.SelectedIndexChanged += RadGroupInterval_SelectedIndexChanged;
            // 
            // Root
            // 
            Root.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True;
            Root.GroupBordersVisible = false;
            Root.Items.AddRange(new DevExpress.XtraLayout.BaseLayoutItem[] { layoutControlItem1, FileLimitLayoutItem, layoutControlItem3, layoutControlItem4 });
            Root.Name = "Root";
            Root.Size = new Size(707, 174);
            Root.TextVisible = false;
            // 
            // layoutControlItem1
            // 
            layoutControlItem1.Control = groupRollingInterval;
            layoutControlItem1.Location = new Point(0, 0);
            layoutControlItem1.Name = "layoutControlItem1";
            layoutControlItem1.Size = new Size(687, 114);
            layoutControlItem1.TextSize = new Size(0, 0);
            layoutControlItem1.TextVisible = false;
            // 
            // FileLimitLayoutItem
            // 
            FileLimitLayoutItem.ContentVertAlignment = DevExpress.Utils.VertAlignment.Center;
            FileLimitLayoutItem.Control = SpinLoggingFileLimit;
            FileLimitLayoutItem.Location = new Point(0, 114);
            FileLimitLayoutItem.Name = "FileLimitLayoutItem";
            FileLimitLayoutItem.Padding = new DevExpress.XtraLayout.Utils.Padding(2, 20, 2, 2);
            FileLimitLayoutItem.Size = new Size(343, 40);
            FileLimitLayoutItem.Text = "File Limit";
            FileLimitLayoutItem.TextSize = new Size(40, 13);
            // 
            // layoutControlItem3
            // 
            layoutControlItem3.Control = BtnOpenLog;
            layoutControlItem3.Location = new Point(343, 114);
            layoutControlItem3.Name = "layoutControlItem3";
            layoutControlItem3.Size = new Size(171, 40);
            layoutControlItem3.TextSize = new Size(0, 0);
            layoutControlItem3.TextVisible = false;
            // 
            // layoutControlItem4
            // 
            layoutControlItem4.Control = BtnCleanLog;
            layoutControlItem4.Location = new Point(514, 114);
            layoutControlItem4.Name = "layoutControlItem4";
            layoutControlItem4.Size = new Size(173, 40);
            layoutControlItem4.TextSize = new Size(0, 0);
            layoutControlItem4.TextVisible = false;
            // 
            // langPopup
            // 
            langPopup.Name = "langPopup";
            langPopup.Ribbon = ribbonControl1;
            // 
            // ribbonControl1
            // 
            ribbonControl1.ExpandCollapseItem.Id = 0;
            ribbonControl1.Items.AddRange(new DevExpress.XtraBars.BarItem[] { ribbonControl1.ExpandCollapseItem, SkinDropDownButton, SkinPaletteRibbonGallery, AccentColorsCheckItem });
            ribbonControl1.Location = new Point(0, 0);
            ribbonControl1.MaxItemId = 6;
            ribbonControl1.Name = "ribbonControl1";
            ribbonControl1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { ribbonPage1 });
            ribbonControl1.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            ribbonControl1.Size = new Size(798, 158);
            // 
            // SkinDropDownButton
            // 
            SkinDropDownButton.ActAsDropDown = true;
            SkinDropDownButton.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            SkinDropDownButton.Id = 1;
            SkinDropDownButton.Name = "SkinDropDownButton";
            // 
            // SkinPaletteRibbonGallery
            // 
            SkinPaletteRibbonGallery.Caption = "skinPaletteRibbonGalleryBarItem1";
            SkinPaletteRibbonGallery.Id = 2;
            SkinPaletteRibbonGallery.Name = "SkinPaletteRibbonGallery";
            // 
            // AccentColorsCheckItem
            // 
            AccentColorsCheckItem.Caption = "System Accent Color";
            AccentColorsCheckItem.Id = 5;
            AccentColorsCheckItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("AccentColorsCheckItem.ImageOptions.SvgImage");
            AccentColorsCheckItem.Name = "AccentColorsCheckItem";
            AccentColorsCheckItem.CheckedChanged += AccentColorsCheckItem_CheckedChanged;
            // 
            // ribbonPage1
            // 
            ribbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { SkinsRibbonPageGroup, ColorsRibbonPageGroup });
            ribbonPage1.Name = "ribbonPage1";
            ribbonPage1.Text = "Home";
            // 
            // SkinsRibbonPageGroup
            // 
            SkinsRibbonPageGroup.ItemLinks.Add(SkinDropDownButton);
            SkinsRibbonPageGroup.ItemLinks.Add(SkinPaletteRibbonGallery);
            SkinsRibbonPageGroup.Name = "SkinsRibbonPageGroup";
            SkinsRibbonPageGroup.Text = "Skins";
            // 
            // ColorsRibbonPageGroup
            // 
            ColorsRibbonPageGroup.ItemLinks.Add(AccentColorsCheckItem);
            ColorsRibbonPageGroup.Name = "ColorsRibbonPageGroup";
            ColorsRibbonPageGroup.Text = "Colors";
            // 
            // accordionControlElement1
            // 
            accordionControlElement1.Appearance.Default.Font = new Font("Segoe UI", 11F, FontStyle.Regular, GraphicsUnit.Point);
            accordionControlElement1.Appearance.Default.Options.UseFont = true;
            accordionControlElement1.Expanded = true;
            accordionControlElement1.HeaderTemplate.AddRange(new HeaderElementInfo[] { new HeaderElementInfo(HeaderElementType.Text), new HeaderElementInfo(HeaderElementType.Image, HeaderElementAlignment.Right), new HeaderElementInfo(HeaderElementType.HeaderControl), new HeaderElementInfo(HeaderElementType.ContextButtons) });
            accordionControlElement1.Name = "accordionControlElement1";
            accordionControlElement1.Style = ElementStyle.Item;
            accordionControlElement1.Text = "Localization";
            // 
            // SettingsNavigationPane
            // 
            SettingsNavigationPane.AllowTransitionAnimation = DevExpress.Utils.DefaultBoolean.True;
            SettingsNavigationPane.Controls.Add(GeneralNavPage);
            SettingsNavigationPane.Controls.Add(AdvancedNavPage);
            SettingsNavigationPane.Controls.Add(InterfaceNavPage);
            SettingsNavigationPane.Dock = DockStyle.Fill;
            SettingsNavigationPane.Location = new Point(0, 158);
            SettingsNavigationPane.Name = "SettingsNavigationPane";
            SettingsNavigationPane.PageProperties.ShowCollapseButton = false;
            SettingsNavigationPane.PageProperties.ShowExpandButton = false;
            SettingsNavigationPane.Pages.AddRange(new NavigationPageBase[] { GeneralNavPage, InterfaceNavPage, AdvancedNavPage });
            SettingsNavigationPane.RegularSize = new Size(798, 521);
            SettingsNavigationPane.SelectedPage = GeneralNavPage;
            SettingsNavigationPane.Size = new Size(798, 521);
            SettingsNavigationPane.TabIndex = 2;
            SettingsNavigationPane.Text = "navigationPane1";
            SettingsNavigationPane.TransitionType = DevExpress.Utils.Animation.Transitions.Push;
            // 
            // GeneralNavPage
            // 
            GeneralNavPage.Caption = "General";
            GeneralNavPage.Controls.Add(xtraScrollableControl1);
            GeneralNavPage.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("GeneralNavPage.ImageOptions.SvgImage");
            GeneralNavPage.Name = "GeneralNavPage";
            GeneralNavPage.Size = new Size(711, 457);
            // 
            // xtraScrollableControl1
            // 
            xtraScrollableControl1.Controls.Add(LocalizationPanel);
            xtraScrollableControl1.Dock = DockStyle.Fill;
            xtraScrollableControl1.Location = new Point(0, 0);
            xtraScrollableControl1.Name = "xtraScrollableControl1";
            xtraScrollableControl1.Size = new Size(711, 457);
            xtraScrollableControl1.TabIndex = 0;
            // 
            // LocalizationPanel
            // 
            LocalizationPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            LocalizationPanel.Controls.Add(groupControl1);
            LocalizationPanel.Dock = DockStyle.Top;
            LocalizationPanel.Location = new Point(0, 0);
            LocalizationPanel.Name = "LocalizationPanel";
            LocalizationPanel.Padding = new Padding(0, 0, 0, 10);
            LocalizationPanel.Size = new Size(711, 343);
            LocalizationPanel.TabIndex = 1;
            // 
            // groupControl1
            // 
            groupControl1.Controls.Add(tablePanel2);
            groupControl1.Dock = DockStyle.Fill;
            groupControl1.Location = new Point(0, 0);
            groupControl1.Name = "groupControl1";
            groupControl1.Size = new Size(711, 333);
            groupControl1.TabIndex = 0;
            groupControl1.Text = "Localization";
            // 
            // AdvancedNavPage
            // 
            AdvancedNavPage.Caption = "Advanced";
            AdvancedNavPage.Controls.Add(xtraScrollableControl2);
            AdvancedNavPage.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("AdvancedNavPage.ImageOptions.SvgImage");
            AdvancedNavPage.Name = "AdvancedNavPage";
            AdvancedNavPage.Size = new Size(711, 457);
            // 
            // xtraScrollableControl2
            // 
            xtraScrollableControl2.Controls.Add(LoggingPanel);
            xtraScrollableControl2.Dock = DockStyle.Fill;
            xtraScrollableControl2.Location = new Point(0, 0);
            xtraScrollableControl2.Name = "xtraScrollableControl2";
            xtraScrollableControl2.Size = new Size(711, 457);
            xtraScrollableControl2.TabIndex = 0;
            // 
            // LoggingPanel
            // 
            LoggingPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            LoggingPanel.Controls.Add(groupControl2);
            LoggingPanel.Dock = DockStyle.Top;
            LoggingPanel.Location = new Point(0, 0);
            LoggingPanel.Name = "LoggingPanel";
            LoggingPanel.Padding = new Padding(0, 0, 0, 10);
            LoggingPanel.Size = new Size(711, 209);
            LoggingPanel.TabIndex = 2;
            // 
            // groupControl2
            // 
            groupControl2.Controls.Add(layoutControl1);
            groupControl2.Dock = DockStyle.Fill;
            groupControl2.Location = new Point(0, 0);
            groupControl2.Name = "groupControl2";
            groupControl2.Size = new Size(711, 199);
            groupControl2.TabIndex = 0;
            groupControl2.Text = "Logging";
            // 
            // InterfaceNavPage
            // 
            InterfaceNavPage.Caption = "Interface";
            InterfaceNavPage.Controls.Add(panelControl1);
            InterfaceNavPage.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("InterfaceNavPage.ImageOptions.SvgImage");
            InterfaceNavPage.Name = "InterfaceNavPage";
            InterfaceNavPage.Size = new Size(711, 457);
            // 
            // panelControl1
            // 
            panelControl1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl1.Dock = DockStyle.Top;
            panelControl1.Location = new Point(0, 0);
            panelControl1.Name = "panelControl1";
            panelControl1.Padding = new Padding(0, 0, 0, 10);
            panelControl1.Size = new Size(711, 100);
            panelControl1.TabIndex = 0;
            // 
            // SettingsForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(798, 679);
            Controls.Add(SettingsNavigationPane);
            Controls.Add(ribbonControl1);
            Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("SettingsForm.IconOptions.SvgImage");
            Margin = new Padding(3, 4, 3, 4);
            MinimizeBox = false;
            Name = "SettingsForm";
            Ribbon = ribbonControl1;
            Text = "Settings";
            FormClosing += SettingsForm_FormClosingAsync;
            ((System.ComponentModel.ISupportInitialize)tablePanel2).EndInit();
            tablePanel2.ResumeLayout(false);
            tablePanel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)languageList).EndInit();
            ((System.ComponentModel.ISupportInitialize)layoutControl1).EndInit();
            layoutControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)SpinLoggingFileLimit.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)groupRollingInterval).EndInit();
            groupRollingInterval.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)radGroupInterval.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)Root).EndInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem1).EndInit();
            ((System.ComponentModel.ISupportInitialize)FileLimitLayoutItem).EndInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem3).EndInit();
            ((System.ComponentModel.ISupportInitialize)layoutControlItem4).EndInit();
            ((System.ComponentModel.ISupportInitialize)langPopup).EndInit();
            ((System.ComponentModel.ISupportInitialize)ribbonControl1).EndInit();
            ((System.ComponentModel.ISupportInitialize)SettingsNavigationPane).EndInit();
            SettingsNavigationPane.ResumeLayout(false);
            GeneralNavPage.ResumeLayout(false);
            xtraScrollableControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)LocalizationPanel).EndInit();
            LocalizationPanel.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)groupControl1).EndInit();
            groupControl1.ResumeLayout(false);
            AdvancedNavPage.ResumeLayout(false);
            xtraScrollableControl2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)LoggingPanel).EndInit();
            LoggingPanel.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)groupControl2).EndInit();
            groupControl2.ResumeLayout(false);
            InterfaceNavPage.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)panelControl1).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion
        private DevExpress.XtraEditors.SimpleButton BtnCleanLog;
        private DevExpress.XtraEditors.SimpleButton BtnOpenLog;
        private DevExpress.XtraEditors.GroupControl groupRollingInterval;
        private DevExpress.XtraEditors.RadioGroup radGroupInterval;
        private DevExpress.XtraEditors.SpinEdit SpinLoggingFileLimit;
        private DevExpress.Utils.ToolTipController toolTipSettingsController;
        private DevExpress.XtraBars.PopupMenu langPopup;
        private AccordionControlElement accordionControlElement1;
        private DevExpress.Utils.Layout.TablePanel tablePanel2;
        private DevExpress.XtraEditors.LabelControl lblLocalDescription;
        private DevExpress.XtraEditors.LabelControl lblCurrCult;
        private DevExpress.XtraEditors.LabelControl lblCurrLang;
        private DevExpress.XtraEditors.LabelControl lblCurrCultLabel;
        private DevExpress.XtraEditors.LabelControl lblCurrLangLabel;
        private DevExpress.XtraEditors.LabelControl lblSelectLanguage;
        private DevExpress.XtraEditors.ImageListBoxControl languageList;
        private NavigationPane SettingsNavigationPane;
        private NavigationPage GeneralNavPage;
        private DevExpress.XtraEditors.XtraScrollableControl xtraScrollableControl1;
        private DevExpress.XtraEditors.PanelControl LocalizationPanel;
        private DevExpress.XtraEditors.GroupControl groupControl1;
        private NavigationPage AdvancedNavPage;
        private DevExpress.XtraEditors.XtraScrollableControl xtraScrollableControl2;
        private DevExpress.XtraEditors.PanelControl LoggingPanel;
        private DevExpress.XtraLayout.LayoutControl layoutControl1;
        private DevExpress.XtraLayout.LayoutControlGroup Root;
        private DevExpress.XtraLayout.LayoutControlItem layoutControlItem1;
        private DevExpress.XtraLayout.LayoutControlItem FileLimitLayoutItem;
        private DevExpress.XtraLayout.LayoutControlItem layoutControlItem3;
        private DevExpress.XtraLayout.LayoutControlItem layoutControlItem4;
        private DevExpress.XtraEditors.GroupControl groupControl2;
        private DevExpress.XtraBars.Ribbon.RibbonControl ribbonControl1;
        private DevExpress.XtraBars.Ribbon.RibbonPage ribbonPage1;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup SkinsRibbonPageGroup;
        private DevExpress.XtraBars.SkinDropDownButtonItem SkinDropDownButton;
        private DevExpress.XtraBars.SkinPaletteRibbonGalleryBarItem SkinPaletteRibbonGallery;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ColorsRibbonPageGroup;
        private NavigationPage InterfaceNavPage;
        private DevExpress.XtraEditors.PanelControl panelControl1;
        private DevExpress.XtraBars.BarCheckItem AccentColorsCheckItem;
    }
}