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
            tabPaneMain = new TabPane();
            tabNavGeneral = new TabNavigationPage();
            accordionControl1 = new AccordionControl();
            accordionContentContainer1 = new AccordionContentContainer();
            tablePanel2 = new DevExpress.Utils.Layout.TablePanel();
            lblCurrCult = new DevExpress.XtraEditors.LabelControl();
            lblCurrLang = new DevExpress.XtraEditors.LabelControl();
            lblCurrCultLabel = new DevExpress.XtraEditors.LabelControl();
            lblCurrLangLabel = new DevExpress.XtraEditors.LabelControl();
            lblLocalDescription = new DevExpress.XtraEditors.LabelControl();
            lblSelectLanguage = new DevExpress.XtraEditors.LabelControl();
            languageList = new DevExpress.XtraEditors.ImageListBoxControl();
            accElementLanguage = new AccordionControlElement();
            accordionControlSeparator1 = new AccordionControlSeparator();
            tabNavAdvanced = new TabNavigationPage();
            accordAdvanced = new AccordionControl();
            accContentLogging = new AccordionContentContainer();
            tablePanel1 = new DevExpress.Utils.Layout.TablePanel();
            BtnCleanLog = new DevExpress.XtraEditors.SimpleButton();
            toolTipSettingsController = new DevExpress.Utils.ToolTipController(components);
            BtnOpenLog = new DevExpress.XtraEditors.SimpleButton();
            lblLoggingFileLimit = new DevExpress.XtraEditors.LabelControl();
            groupRollingInterval = new DevExpress.XtraEditors.GroupControl();
            radGroupInterval = new DevExpress.XtraEditors.RadioGroup();
            SpinLoggingFileLimit = new DevExpress.XtraEditors.SpinEdit();
            accElementLogging = new AccordionControlElement();
            accordionControlSeparator2 = new AccordionControlSeparator();
            langPopup = new DevExpress.XtraBars.PopupMenu(components);
            ((System.ComponentModel.ISupportInitialize)tabPaneMain).BeginInit();
            tabPaneMain.SuspendLayout();
            tabNavGeneral.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)accordionControl1).BeginInit();
            accordionControl1.SuspendLayout();
            accordionContentContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)tablePanel2).BeginInit();
            tablePanel2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)languageList).BeginInit();
            tabNavAdvanced.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)accordAdvanced).BeginInit();
            accordAdvanced.SuspendLayout();
            accContentLogging.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)tablePanel1).BeginInit();
            tablePanel1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)groupRollingInterval).BeginInit();
            groupRollingInterval.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)radGroupInterval.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)SpinLoggingFileLimit.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)langPopup).BeginInit();
            SuspendLayout();
            // 
            // tabPaneMain
            // 
            tabPaneMain.AllowTransitionAnimation = DevExpress.Utils.DefaultBoolean.True;
            tabPaneMain.Controls.Add(tabNavGeneral);
            tabPaneMain.Controls.Add(tabNavAdvanced);
            tabPaneMain.Dock = DockStyle.Fill;
            tabPaneMain.Location = new Point(11, 13);
            tabPaneMain.Name = "tabPaneMain";
            tabPaneMain.Pages.AddRange(new NavigationPageBase[] { tabNavGeneral, tabNavAdvanced });
            tabPaneMain.RegularSize = new Size(1287, 962);
            tabPaneMain.SelectedPage = tabNavGeneral;
            tabPaneMain.Size = new Size(1287, 962);
            tabPaneMain.TabIndex = 1;
            tabPaneMain.Text = "tabPane1";
            tabPaneMain.TransitionType = DevExpress.Utils.Animation.Transitions.Push;
            // 
            // tabNavGeneral
            // 
            tabNavGeneral.Caption = "General";
            tabNavGeneral.Controls.Add(accordionControl1);
            tabNavGeneral.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("tabNavGeneral.ImageOptions.SvgImage");
            tabNavGeneral.ImageOptions.SvgImageSize = new Size(24, 24);
            tabNavGeneral.ItemShowMode = ItemShowMode.ImageAndText;
            tabNavGeneral.Name = "tabNavGeneral";
            tabNavGeneral.Properties.ShowMode = ItemShowMode.ImageAndText;
            tabNavGeneral.Size = new Size(1287, 910);
            // 
            // accordionControl1
            // 
            accordionControl1.Controls.Add(accordionContentContainer1);
            accordionControl1.Dock = DockStyle.Fill;
            accordionControl1.Elements.AddRange(new AccordionControlElement[] { accElementLanguage, accordionControlSeparator1 });
            accordionControl1.ExpandElementMode = ExpandElementMode.Multiple;
            accordionControl1.Location = new Point(0, 0);
            accordionControl1.Margin = new Padding(3, 4, 3, 4);
            accordionControl1.Name = "accordionControl1";
            accordionControl1.OptionsMinimizing.AllowMinimizeMode = DevExpress.Utils.DefaultBoolean.False;
            accordionControl1.ScrollBarMode = ScrollBarMode.Auto;
            accordionControl1.ShowFilterControl = ShowFilterControl.Always;
            accordionControl1.Size = new Size(1287, 910);
            accordionControl1.TabIndex = 3;
            // 
            // accordionContentContainer1
            // 
            accordionContentContainer1.Controls.Add(tablePanel2);
            accordionContentContainer1.Margin = new Padding(3, 4, 3, 4);
            accordionContentContainer1.Name = "accordionContentContainer1";
            accordionContentContainer1.Size = new Size(1259, 340);
            accordionContentContainer1.TabIndex = 2;
            // 
            // tablePanel2
            // 
            tablePanel2.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 60F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 95F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 350F) });
            tablePanel2.Controls.Add(lblCurrCult);
            tablePanel2.Controls.Add(lblCurrLang);
            tablePanel2.Controls.Add(lblCurrCultLabel);
            tablePanel2.Controls.Add(lblCurrLangLabel);
            tablePanel2.Controls.Add(lblLocalDescription);
            tablePanel2.Controls.Add(lblSelectLanguage);
            tablePanel2.Controls.Add(languageList);
            tablePanel2.Dock = DockStyle.Fill;
            tablePanel2.Location = new Point(0, 0);
            tablePanel2.Name = "tablePanel2";
            tablePanel2.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 35F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 40F) });
            tablePanel2.Size = new Size(1259, 340);
            tablePanel2.TabIndex = 0;
            tablePanel2.UseSkinIndents = true;
            // 
            // lblCurrCult
            // 
            lblCurrCult.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblCurrCult.Appearance.Options.UseFont = true;
            lblCurrCult.AutoEllipsis = true;
            lblCurrCult.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel2.SetColumn(lblCurrCult, 1);
            lblCurrCult.Dock = DockStyle.Fill;
            lblCurrCult.Location = new Point(358, 247);
            lblCurrCult.Name = "lblCurrCult";
            tablePanel2.SetRow(lblCurrCult, 3);
            lblCurrCult.Size = new Size(532, 34);
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
            lblCurrLang.Location = new Point(358, 207);
            lblCurrLang.Name = "lblCurrLang";
            tablePanel2.SetRow(lblCurrLang, 2);
            lblCurrLang.Size = new Size(532, 34);
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
            lblCurrCultLabel.Location = new Point(19, 247);
            lblCurrCultLabel.Name = "lblCurrCultLabel";
            tablePanel2.SetRow(lblCurrCultLabel, 3);
            lblCurrCultLabel.Size = new Size(333, 34);
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
            lblCurrLangLabel.Location = new Point(19, 207);
            lblCurrLangLabel.Name = "lblCurrLangLabel";
            tablePanel2.SetRow(lblCurrLangLabel, 2);
            lblCurrLangLabel.Size = new Size(333, 34);
            lblCurrLangLabel.TabIndex = 3;
            lblCurrLangLabel.Text = "Current Language:";
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
            lblLocalDescription.Location = new Point(19, 18);
            lblLocalDescription.Margin = new Padding(3, 3, 20, 3);
            lblLocalDescription.Name = "lblLocalDescription";
            tablePanel2.SetRow(lblLocalDescription, 0);
            tablePanel2.SetRowSpan(lblLocalDescription, 2);
            lblLocalDescription.Size = new Size(854, 183);
            lblLocalDescription.TabIndex = 2;
            lblLocalDescription.Text = resources.GetString("lblLocalDescription.Text");
            // 
            // lblSelectLanguage
            // 
            lblSelectLanguage.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            lblSelectLanguage.Appearance.Options.UseFont = true;
            tablePanel2.SetColumn(lblSelectLanguage, 2);
            lblSelectLanguage.Dock = DockStyle.Fill;
            lblSelectLanguage.Location = new Point(896, 18);
            lblSelectLanguage.Name = "lblSelectLanguage";
            tablePanel2.SetRow(lblSelectLanguage, 0);
            lblSelectLanguage.Size = new Size(344, 29);
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
            languageList.Location = new Point(896, 53);
            languageList.Name = "languageList";
            tablePanel2.SetRow(languageList, 1);
            tablePanel2.SetRowSpan(languageList, 4);
            languageList.Size = new Size(344, 268);
            languageList.TabIndex = 0;
            // 
            // accElementLanguage
            // 
            accElementLanguage.Appearance.Default.Font = new Font("Segoe UI", 11F, FontStyle.Regular, GraphicsUnit.Point);
            accElementLanguage.Appearance.Default.Options.UseFont = true;
            accElementLanguage.ContentContainer = accordionContentContainer1;
            accElementLanguage.Expanded = true;
            accElementLanguage.HeaderTemplate.AddRange(new HeaderElementInfo[] { new HeaderElementInfo(HeaderElementType.Text), new HeaderElementInfo(HeaderElementType.Image, HeaderElementAlignment.Right), new HeaderElementInfo(HeaderElementType.HeaderControl), new HeaderElementInfo(HeaderElementType.ContextButtons) });
            accElementLanguage.Name = "accElementLanguage";
            accElementLanguage.Style = ElementStyle.Item;
            accElementLanguage.Text = "Localization";
            // 
            // accordionControlSeparator1
            // 
            accordionControlSeparator1.Name = "accordionControlSeparator1";
            // 
            // tabNavAdvanced
            // 
            tabNavAdvanced.Caption = "Advanced";
            tabNavAdvanced.Controls.Add(accordAdvanced);
            tabNavAdvanced.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("tabNavAdvanced.ImageOptions.SvgImage");
            tabNavAdvanced.ImageOptions.SvgImageSize = new Size(24, 24);
            tabNavAdvanced.ItemShowMode = ItemShowMode.ImageAndText;
            tabNavAdvanced.Name = "tabNavAdvanced";
            tabNavAdvanced.Properties.ShowMode = ItemShowMode.ImageAndText;
            tabNavAdvanced.Size = new Size(1287, 910);
            // 
            // accordAdvanced
            // 
            accordAdvanced.Controls.Add(accContentLogging);
            accordAdvanced.Dock = DockStyle.Fill;
            accordAdvanced.Elements.AddRange(new AccordionControlElement[] { accElementLogging, accordionControlSeparator2 });
            accordAdvanced.ExpandElementMode = ExpandElementMode.Multiple;
            accordAdvanced.Location = new Point(0, 0);
            accordAdvanced.Margin = new Padding(3, 4, 3, 4);
            accordAdvanced.Name = "accordAdvanced";
            accordAdvanced.OptionsMinimizing.AllowMinimizeMode = DevExpress.Utils.DefaultBoolean.False;
            accordAdvanced.ScrollBarMode = ScrollBarMode.Auto;
            accordAdvanced.ShowFilterControl = ShowFilterControl.Always;
            accordAdvanced.Size = new Size(1287, 910);
            accordAdvanced.TabIndex = 2;
            // 
            // accContentLogging
            // 
            accContentLogging.Controls.Add(tablePanel1);
            accContentLogging.Margin = new Padding(3, 4, 3, 4);
            accContentLogging.Name = "accContentLogging";
            accContentLogging.Size = new Size(1259, 279);
            accContentLogging.TabIndex = 2;
            // 
            // tablePanel1
            // 
            tablePanel1.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 220F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 24.3F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 300F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 300F) });
            tablePanel1.Controls.Add(BtnCleanLog);
            tablePanel1.Controls.Add(BtnOpenLog);
            tablePanel1.Controls.Add(lblLoggingFileLimit);
            tablePanel1.Controls.Add(groupRollingInterval);
            tablePanel1.Controls.Add(SpinLoggingFileLimit);
            tablePanel1.Dock = DockStyle.Fill;
            tablePanel1.Location = new Point(0, 0);
            tablePanel1.Margin = new Padding(3, 4, 3, 4);
            tablePanel1.Name = "tablePanel1";
            tablePanel1.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F) });
            tablePanel1.Size = new Size(1259, 279);
            tablePanel1.TabIndex = 1;
            tablePanel1.UseSkinIndents = true;
            // 
            // BtnCleanLog
            // 
            BtnCleanLog.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            BtnCleanLog.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(BtnCleanLog, 4);
            BtnCleanLog.Dock = DockStyle.Top;
            BtnCleanLog.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("BtnCleanLog.ImageOptions.SvgImage");
            BtnCleanLog.Location = new Point(949, 149);
            BtnCleanLog.Margin = new Padding(6, 10, 6, 7);
            BtnCleanLog.Name = "BtnCleanLog";
            tablePanel1.SetRow(BtnCleanLog, 1);
            BtnCleanLog.Size = new Size(288, 73);
            BtnCleanLog.TabIndex = 12;
            BtnCleanLog.Text = "Clean Serilog";
            BtnCleanLog.ToolTip = resources.GetString("BtnCleanLog.ToolTip");
            BtnCleanLog.ToolTipController = toolTipSettingsController;
            BtnCleanLog.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Asterisk;
            BtnCleanLog.ToolTipTitle = "Clean the Serilog Directory";
            BtnCleanLog.Click += BtnCleanLog_Click;
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
            // BtnOpenLog
            // 
            BtnOpenLog.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            BtnOpenLog.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(BtnOpenLog, 3);
            BtnOpenLog.Dock = DockStyle.Top;
            BtnOpenLog.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("BtnOpenLog.ImageOptions.SvgImage");
            BtnOpenLog.Location = new Point(649, 149);
            BtnOpenLog.Margin = new Padding(6, 10, 6, 4);
            BtnOpenLog.Name = "BtnOpenLog";
            tablePanel1.SetRow(BtnOpenLog, 1);
            BtnOpenLog.Size = new Size(288, 73);
            BtnOpenLog.TabIndex = 11;
            BtnOpenLog.Text = "Open log";
            BtnOpenLog.ToolTip = "Open the Serilog logging directory.";
            BtnOpenLog.ToolTipController = toolTipSettingsController;
            BtnOpenLog.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            BtnOpenLog.ToolTipTitle = "Open Serilog Directory";
            BtnOpenLog.Click += BtnOpenLog_Click;
            // 
            // lblLoggingFileLimit
            // 
            lblLoggingFileLimit.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblLoggingFileLimit.Appearance.Options.UseFont = true;
            lblLoggingFileLimit.Appearance.Options.UseTextOptions = true;
            lblLoggingFileLimit.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            tablePanel1.SetColumn(lblLoggingFileLimit, 0);
            lblLoggingFileLimit.Dock = DockStyle.Fill;
            lblLoggingFileLimit.Location = new Point(19, 149);
            lblLoggingFileLimit.Margin = new Padding(3, 10, 3, 4);
            lblLoggingFileLimit.Name = "lblLoggingFileLimit";
            tablePanel1.SetRow(lblLoggingFileLimit, 1);
            lblLoggingFileLimit.Size = new Size(214, 110);
            lblLoggingFileLimit.TabIndex = 9;
            lblLoggingFileLimit.Text = "File Limit";
            // 
            // groupRollingInterval
            // 
            groupRollingInterval.AppearanceCaption.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            groupRollingInterval.AppearanceCaption.Options.UseFont = true;
            tablePanel1.SetColumn(groupRollingInterval, 0);
            tablePanel1.SetColumnSpan(groupRollingInterval, 5);
            groupRollingInterval.Controls.Add(radGroupInterval);
            groupRollingInterval.Dock = DockStyle.Fill;
            groupRollingInterval.Location = new Point(19, 19);
            groupRollingInterval.Margin = new Padding(3, 4, 3, 10);
            groupRollingInterval.Name = "groupRollingInterval";
            tablePanel1.SetRow(groupRollingInterval, 0);
            groupRollingInterval.Size = new Size(1221, 110);
            groupRollingInterval.TabIndex = 8;
            groupRollingInterval.Text = "Rolling Interval";
            // 
            // radGroupInterval
            // 
            radGroupInterval.Dock = DockStyle.Fill;
            radGroupInterval.Location = new Point(2, 34);
            radGroupInterval.Margin = new Padding(3, 4, 3, 4);
            radGroupInterval.Name = "radGroupInterval";
            radGroupInterval.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            radGroupInterval.Properties.Appearance.Options.UseFont = true;
            radGroupInterval.Properties.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            radGroupInterval.Properties.Items.AddRange(new DevExpress.XtraEditors.Controls.RadioGroupItem[] { new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Minute"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Hour"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Day"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Month"), new DevExpress.XtraEditors.Controls.RadioGroupItem(null, "Infinite") });
            radGroupInterval.Properties.Padding = new Padding(10, 4, 4, 4);
            radGroupInterval.Size = new Size(1217, 74);
            radGroupInterval.TabIndex = 0;
            radGroupInterval.ToolTip = resources.GetString("radGroupInterval.ToolTip");
            radGroupInterval.ToolTipController = toolTipSettingsController;
            radGroupInterval.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            radGroupInterval.ToolTipTitle = "Log rolling interval";
            radGroupInterval.SelectedIndexChanged += RadGroupInterval_SelectedIndexChanged;
            // 
            // SpinLoggingFileLimit
            // 
            tablePanel1.SetColumn(SpinLoggingFileLimit, 1);
            SpinLoggingFileLimit.Dock = DockStyle.Left;
            SpinLoggingFileLimit.EditValue = new decimal(new int[] { 0, 0, 0, 0 });
            SpinLoggingFileLimit.Location = new Point(239, 149);
            SpinLoggingFileLimit.Margin = new Padding(3, 10, 22, 4);
            SpinLoggingFileLimit.Name = "SpinLoggingFileLimit";
            SpinLoggingFileLimit.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            SpinLoggingFileLimit.Properties.Appearance.Options.UseFont = true;
            SpinLoggingFileLimit.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            SpinLoggingFileLimit.Properties.EditFormat.FormatType = DevExpress.Utils.FormatType.Numeric;
            SpinLoggingFileLimit.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Default;
            SpinLoggingFileLimit.Properties.IsFloatValue = false;
            SpinLoggingFileLimit.Properties.MaskSettings.Set("mask", "N00");
            tablePanel1.SetRow(SpinLoggingFileLimit, 1);
            SpinLoggingFileLimit.Size = new Size(91, 32);
            SpinLoggingFileLimit.TabIndex = 13;
            SpinLoggingFileLimit.ToolTip = "Sets a limit on how many log files can stick around in the logging system. It helps keep things shipshape and prevents an avalanche of log files from burying us alive.";
            SpinLoggingFileLimit.ToolTipController = toolTipSettingsController;
            SpinLoggingFileLimit.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            SpinLoggingFileLimit.ToolTipTitle = "Log File Limit";
            SpinLoggingFileLimit.ValueChanged += SpinLoggingFileLimit_ValueChanged;
            // 
            // accElementLogging
            // 
            accElementLogging.Appearance.Default.Font = new Font("Segoe UI", 11F, FontStyle.Regular, GraphicsUnit.Point);
            accElementLogging.Appearance.Default.Options.UseFont = true;
            accElementLogging.ContentContainer = accContentLogging;
            accElementLogging.Expanded = true;
            accElementLogging.HeaderTemplate.AddRange(new HeaderElementInfo[] { new HeaderElementInfo(HeaderElementType.Text), new HeaderElementInfo(HeaderElementType.Image, HeaderElementAlignment.Right), new HeaderElementInfo(HeaderElementType.HeaderControl), new HeaderElementInfo(HeaderElementType.ContextButtons) });
            accElementLogging.Name = "accElementLogging";
            accElementLogging.Style = ElementStyle.Item;
            accElementLogging.Text = "Logging";
            // 
            // accordionControlSeparator2
            // 
            accordionControlSeparator2.Name = "accordionControlSeparator2";
            // 
            // langPopup
            // 
            langPopup.Name = "langPopup";
            // 
            // SettingsForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new SizeF(10F, 25F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(1309, 988);
            Controls.Add(tabPaneMain);
            Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("SettingsForm.IconOptions.SvgImage");
            Margin = new Padding(3, 4, 3, 4);
            MinimizeBox = false;
            Name = "SettingsForm";
            Padding = new Padding(11, 13, 11, 13);
            Text = "Settings";
            FormClosing += SettingsForm_FormClosingAsync;
            ((System.ComponentModel.ISupportInitialize)tabPaneMain).EndInit();
            tabPaneMain.ResumeLayout(false);
            tabNavGeneral.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)accordionControl1).EndInit();
            accordionControl1.ResumeLayout(false);
            accordionContentContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)tablePanel2).EndInit();
            tablePanel2.ResumeLayout(false);
            tablePanel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)languageList).EndInit();
            tabNavAdvanced.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)accordAdvanced).EndInit();
            accordAdvanced.ResumeLayout(false);
            accContentLogging.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)tablePanel1).EndInit();
            tablePanel1.ResumeLayout(false);
            tablePanel1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)groupRollingInterval).EndInit();
            groupRollingInterval.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)radGroupInterval.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)SpinLoggingFileLimit.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)langPopup).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraBars.Navigation.TabPane tabPaneMain;
        private DevExpress.XtraBars.Navigation.TabNavigationPage tabNavGeneral;
        private DevExpress.XtraBars.Navigation.TabNavigationPage tabNavAdvanced;
        private DevExpress.XtraBars.Navigation.AccordionControl accordAdvanced;
        private DevExpress.XtraBars.Navigation.AccordionContentContainer accContentLogging;
        private DevExpress.Utils.Layout.TablePanel tablePanel1;
        private DevExpress.XtraEditors.SimpleButton BtnCleanLog;
        private DevExpress.XtraEditors.SimpleButton BtnOpenLog;
        private DevExpress.XtraEditors.LabelControl lblLoggingFileLimit;
        private DevExpress.XtraEditors.GroupControl groupRollingInterval;
        private DevExpress.XtraEditors.RadioGroup radGroupInterval;
        private DevExpress.XtraBars.Navigation.AccordionControlElement accElementLogging;
        private DevExpress.XtraBars.Navigation.AccordionControlSeparator accordionControlSeparator2;
        private DevExpress.XtraEditors.SpinEdit SpinLoggingFileLimit;
        private DevExpress.Utils.ToolTipController toolTipSettingsController;
        private AccordionControl accordionControl1;
        private AccordionContentContainer accordionContentContainer1;
        private DevExpress.Utils.Layout.TablePanel tablePanel2;
        private AccordionControlElement accElementLanguage;
        private AccordionControlSeparator accordionControlSeparator1;
        private DevExpress.XtraBars.PopupMenu langPopup;
        private DevExpress.XtraEditors.ImageListBoxControl languageList;
        private DevExpress.XtraEditors.LabelControl lblCurrCultLabel;
        private DevExpress.XtraEditors.LabelControl lblCurrLangLabel;
        private DevExpress.XtraEditors.LabelControl lblLocalDescription;
        private DevExpress.XtraEditors.LabelControl lblSelectLanguage;
        private DevExpress.XtraEditors.LabelControl lblCurrCult;
        private DevExpress.XtraEditors.LabelControl lblCurrLang;
    }
}