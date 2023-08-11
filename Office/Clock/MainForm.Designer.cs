namespace Rizonesoft.Office.Clock
{
    partial class MainForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            ribbon = new DevExpress.XtraBars.Ribbon.RibbonControl();
            ClockButton = new DevExpress.XtraBars.BarButtonItem();
            TimerButton = new DevExpress.XtraBars.BarButtonItem();
            StopwatchButton = new DevExpress.XtraBars.BarButtonItem();
            AlarmButton = new DevExpress.XtraBars.BarButtonItem();
            FocusButton = new DevExpress.XtraBars.BarButtonItem();
            DateStatusItem = new DevExpress.XtraBars.BarStaticItem();
            TimeStatusItem = new DevExpress.XtraBars.BarStaticItem();
            HomeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            ComminRibPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            MainNavigationFrame = new DevExpress.XtraBars.Navigation.NavigationFrame();
            ClockPage = new DevExpress.XtraBars.Navigation.NavigationPage();
            tablePanel1 = new DevExpress.Utils.Layout.TablePanel();
            ClockLabel = new DevExpress.XtraEditors.LabelControl();
            TimerPage = new DevExpress.XtraBars.Navigation.NavigationPage();
            tablePanel2 = new DevExpress.Utils.Layout.TablePanel();
            progressBarControl1 = new DevExpress.XtraEditors.ProgressBarControl();
            labelControl1 = new DevExpress.XtraEditors.LabelControl();
            simpleButton3 = new DevExpress.XtraEditors.SimpleButton();
            simpleButton2 = new DevExpress.XtraEditors.SimpleButton();
            simpleButton1 = new DevExpress.XtraEditors.SimpleButton();
            MinutesSpinEdit = new DevExpress.XtraEditors.SpinEdit();
            TimerLabel = new DevExpress.XtraEditors.LabelControl();
            StopwatchPage = new DevExpress.XtraBars.Navigation.NavigationPage();
            AlarmPage = new DevExpress.XtraBars.Navigation.NavigationPage();
            FocusPage = new DevExpress.XtraBars.Navigation.NavigationPage();
            ClockTimer = new System.Windows.Forms.Timer(components);
            ((System.ComponentModel.ISupportInitialize)ribbon).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MainNavigationFrame).BeginInit();
            MainNavigationFrame.SuspendLayout();
            ClockPage.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)tablePanel1).BeginInit();
            tablePanel1.SuspendLayout();
            TimerPage.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)tablePanel2).BeginInit();
            tablePanel2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)progressBarControl1.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MinutesSpinEdit.Properties).BeginInit();
            SuspendLayout();
            // 
            // ribbon
            // 
            ribbon.ExpandCollapseItem.Id = 0;
            ribbon.Items.AddRange(new DevExpress.XtraBars.BarItem[] { ribbon.ExpandCollapseItem, ClockButton, TimerButton, StopwatchButton, AlarmButton, FocusButton, DateStatusItem, TimeStatusItem });
            ribbon.Location = new System.Drawing.Point(0, 0);
            ribbon.MaxItemId = 8;
            ribbon.Name = "ribbon";
            ribbon.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { HomeRibbonPage });
            ribbon.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office365;
            ribbon.SearchItemPosition = DevExpress.XtraBars.Ribbon.SearchItemPosition.None;
            ribbon.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            ribbon.Size = new System.Drawing.Size(498, 201);
            ribbon.StatusBar = ribbonStatusBar;
            // 
            // ClockButton
            // 
            ClockButton.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.Check;
            ClockButton.Caption = "Clock";
            ClockButton.Id = 1;
            ClockButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ClockButton.ImageOptions.SvgImage");
            ClockButton.Name = "ClockButton";
            ClockButton.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large;
            ClockButton.DownChanged += RibbonButton_DownChanged;
            // 
            // TimerButton
            // 
            TimerButton.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.Check;
            TimerButton.Caption = "Timer";
            TimerButton.Id = 2;
            TimerButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("TimerButton.ImageOptions.SvgImage");
            TimerButton.Name = "TimerButton";
            TimerButton.DownChanged += RibbonButton_DownChanged;
            // 
            // StopwatchButton
            // 
            StopwatchButton.Caption = "Stopwatch";
            StopwatchButton.Enabled = false;
            StopwatchButton.Id = 3;
            StopwatchButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("StopwatchButton.ImageOptions.SvgImage");
            StopwatchButton.Name = "StopwatchButton";
            StopwatchButton.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large;
            // 
            // AlarmButton
            // 
            AlarmButton.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.Check;
            AlarmButton.Caption = "Alarm";
            AlarmButton.Enabled = false;
            AlarmButton.Id = 4;
            AlarmButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("AlarmButton.ImageOptions.SvgImage");
            AlarmButton.Name = "AlarmButton";
            AlarmButton.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large;
            // 
            // FocusButton
            // 
            FocusButton.Caption = "Focus";
            FocusButton.Enabled = false;
            FocusButton.Id = 5;
            FocusButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("FocusButton.ImageOptions.SvgImage");
            FocusButton.Name = "FocusButton";
            // 
            // DateStatusItem
            // 
            DateStatusItem.Caption = "Monday, 01 January 2000";
            DateStatusItem.Id = 6;
            DateStatusItem.Name = "DateStatusItem";
            // 
            // TimeStatusItem
            // 
            TimeStatusItem.Alignment = DevExpress.XtraBars.BarItemLinkAlignment.Right;
            TimeStatusItem.Caption = "00:00:00";
            TimeStatusItem.Id = 7;
            TimeStatusItem.Name = "TimeStatusItem";
            // 
            // HomeRibbonPage
            // 
            HomeRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { ComminRibPageGroup });
            HomeRibbonPage.Name = "HomeRibbonPage";
            HomeRibbonPage.Text = "Home";
            // 
            // ComminRibPageGroup
            // 
            ComminRibPageGroup.ItemLinks.Add(ClockButton);
            ComminRibPageGroup.ItemLinks.Add(TimerButton);
            ComminRibPageGroup.ItemLinks.Add(StopwatchButton);
            ComminRibPageGroup.ItemLinks.Add(AlarmButton);
            ComminRibPageGroup.ItemLinks.Add(FocusButton);
            ComminRibPageGroup.Name = "ComminRibPageGroup";
            ComminRibPageGroup.Text = "Common";
            // 
            // ribbonStatusBar
            // 
            ribbonStatusBar.ItemLinks.Add(DateStatusItem);
            ribbonStatusBar.ItemLinks.Add(TimeStatusItem);
            ribbonStatusBar.Location = new System.Drawing.Point(0, 507);
            ribbonStatusBar.Name = "ribbonStatusBar";
            ribbonStatusBar.Ribbon = ribbon;
            ribbonStatusBar.Size = new System.Drawing.Size(498, 37);
            // 
            // MainNavigationFrame
            // 
            MainNavigationFrame.Controls.Add(ClockPage);
            MainNavigationFrame.Controls.Add(TimerPage);
            MainNavigationFrame.Controls.Add(StopwatchPage);
            MainNavigationFrame.Controls.Add(AlarmPage);
            MainNavigationFrame.Controls.Add(FocusPage);
            MainNavigationFrame.Dock = System.Windows.Forms.DockStyle.Fill;
            MainNavigationFrame.Location = new System.Drawing.Point(0, 201);
            MainNavigationFrame.Name = "MainNavigationFrame";
            MainNavigationFrame.Padding = new System.Windows.Forms.Padding(10);
            MainNavigationFrame.Pages.AddRange(new DevExpress.XtraBars.Navigation.NavigationPageBase[] { ClockPage, TimerPage, StopwatchPage, AlarmPage, FocusPage });
            MainNavigationFrame.SelectedPage = ClockPage;
            MainNavigationFrame.Size = new System.Drawing.Size(498, 306);
            MainNavigationFrame.TabIndex = 2;
            // 
            // ClockPage
            // 
            ClockPage.Caption = "ClockPage";
            ClockPage.Controls.Add(tablePanel1);
            ClockPage.Name = "ClockPage";
            ClockPage.Padding = new System.Windows.Forms.Padding(5);
            ClockPage.Size = new System.Drawing.Size(498, 306);
            // 
            // tablePanel1
            // 
            tablePanel1.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 350F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F) });
            tablePanel1.Controls.Add(ClockLabel);
            tablePanel1.Dock = System.Windows.Forms.DockStyle.Fill;
            tablePanel1.Location = new System.Drawing.Point(5, 5);
            tablePanel1.Margin = new System.Windows.Forms.Padding(10);
            tablePanel1.Name = "tablePanel1";
            tablePanel1.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 118F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 26F) });
            tablePanel1.Size = new System.Drawing.Size(488, 296);
            tablePanel1.TabIndex = 0;
            tablePanel1.UseSkinIndents = true;
            // 
            // ClockLabel
            // 
            ClockLabel.Appearance.Font = new System.Drawing.Font("Segoe UI Semibold", 60F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
            ClockLabel.Appearance.Options.UseFont = true;
            ClockLabel.Appearance.Options.UseTextOptions = true;
            ClockLabel.Appearance.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Near;
            tablePanel1.SetColumn(ClockLabel, 1);
            tablePanel1.SetColumnSpan(ClockLabel, 2);
            ClockLabel.Location = new System.Drawing.Point(72, 16);
            ClockLabel.Name = "ClockLabel";
            ClockLabel.Padding = new System.Windows.Forms.Padding(10);
            tablePanel1.SetRow(ClockLabel, 0);
            ClockLabel.Size = new System.Drawing.Size(322, 112);
            ClockLabel.TabIndex = 0;
            ClockLabel.Text = "00:00:00";
            // 
            // TimerPage
            // 
            TimerPage.AutoScroll = true;
            TimerPage.AutoScrollMargin = new System.Drawing.Size(500, 450);
            TimerPage.Caption = "TimerPage";
            TimerPage.Controls.Add(tablePanel2);
            TimerPage.Name = "TimerPage";
            TimerPage.Padding = new System.Windows.Forms.Padding(5);
            TimerPage.Size = new System.Drawing.Size(498, 306);
            // 
            // tablePanel2
            // 
            tablePanel2.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 5F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 120F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 80F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 60F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 60F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 60F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 5F) });
            tablePanel2.Controls.Add(progressBarControl1);
            tablePanel2.Controls.Add(labelControl1);
            tablePanel2.Controls.Add(simpleButton3);
            tablePanel2.Controls.Add(simpleButton2);
            tablePanel2.Controls.Add(simpleButton1);
            tablePanel2.Controls.Add(MinutesSpinEdit);
            tablePanel2.Controls.Add(TimerLabel);
            tablePanel2.Dock = System.Windows.Forms.DockStyle.Fill;
            tablePanel2.Location = new System.Drawing.Point(5, 5);
            tablePanel2.Margin = new System.Windows.Forms.Padding(10);
            tablePanel2.MinimumSize = new System.Drawing.Size(400, 300);
            tablePanel2.Name = "tablePanel2";
            tablePanel2.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 20F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 120F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 26F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 60F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 30F) });
            tablePanel2.Size = new System.Drawing.Size(488, 300);
            tablePanel2.TabIndex = 1;
            tablePanel2.UseSkinIndents = true;
            // 
            // progressBarControl1
            // 
            tablePanel2.SetColumn(progressBarControl1, 1);
            tablePanel2.SetColumnSpan(progressBarControl1, 5);
            progressBarControl1.Location = new System.Drawing.Point(57, 18);
            progressBarControl1.MenuManager = ribbon;
            progressBarControl1.Name = "progressBarControl1";
            tablePanel2.SetRow(progressBarControl1, 0);
            progressBarControl1.Size = new System.Drawing.Size(374, 10);
            progressBarControl1.TabIndex = 6;
            // 
            // labelControl1
            // 
            labelControl1.Appearance.Font = new System.Drawing.Font("Segoe UI", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            labelControl1.Appearance.Options.UseFont = true;
            tablePanel2.SetColumn(labelControl1, 1);
            labelControl1.Location = new System.Drawing.Point(57, 156);
            labelControl1.Name = "labelControl1";
            tablePanel2.SetRow(labelControl1, 2);
            labelControl1.Size = new System.Drawing.Size(55, 20);
            labelControl1.TabIndex = 5;
            labelControl1.Text = "Minutes:";
            // 
            // simpleButton3
            // 
            tablePanel2.SetColumn(simpleButton3, 5);
            simpleButton3.Dock = System.Windows.Forms.DockStyle.Fill;
            simpleButton3.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            simpleButton3.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("simpleButton3.ImageOptions.SvgImage");
            simpleButton3.Location = new System.Drawing.Point(377, 182);
            simpleButton3.Name = "simpleButton3";
            tablePanel2.SetRow(simpleButton3, 3);
            simpleButton3.Size = new System.Drawing.Size(54, 54);
            simpleButton3.TabIndex = 4;
            // 
            // simpleButton2
            // 
            tablePanel2.SetColumn(simpleButton2, 4);
            simpleButton2.Dock = System.Windows.Forms.DockStyle.Fill;
            simpleButton2.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            simpleButton2.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("simpleButton2.ImageOptions.SvgImage");
            simpleButton2.Location = new System.Drawing.Point(317, 182);
            simpleButton2.Name = "simpleButton2";
            tablePanel2.SetRow(simpleButton2, 3);
            simpleButton2.Size = new System.Drawing.Size(54, 54);
            simpleButton2.TabIndex = 3;
            // 
            // simpleButton1
            // 
            tablePanel2.SetColumn(simpleButton1, 3);
            simpleButton1.Dock = System.Windows.Forms.DockStyle.Fill;
            simpleButton1.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            simpleButton1.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("simpleButton1.ImageOptions.SvgImage");
            simpleButton1.Location = new System.Drawing.Point(257, 182);
            simpleButton1.Name = "simpleButton1";
            tablePanel2.SetRow(simpleButton1, 3);
            simpleButton1.Size = new System.Drawing.Size(54, 54);
            simpleButton1.TabIndex = 2;
            // 
            // MinutesSpinEdit
            // 
            tablePanel2.SetColumn(MinutesSpinEdit, 1);
            MinutesSpinEdit.EditValue = new decimal(new int[] { 10, 0, 0, 0 });
            MinutesSpinEdit.Location = new System.Drawing.Point(57, 187);
            MinutesSpinEdit.MenuManager = ribbon;
            MinutesSpinEdit.Name = "MinutesSpinEdit";
            MinutesSpinEdit.Properties.AllowNullInput = DevExpress.Utils.DefaultBoolean.False;
            MinutesSpinEdit.Properties.Appearance.Font = new System.Drawing.Font("Segoe UI", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            MinutesSpinEdit.Properties.Appearance.Options.UseFont = true;
            MinutesSpinEdit.Properties.BeepOnError = true;
            MinutesSpinEdit.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            MinutesSpinEdit.Properties.IsFloatValue = false;
            MinutesSpinEdit.Properties.MaskSettings.Set("mask", "N00");
            tablePanel2.SetRow(MinutesSpinEdit, 3);
            MinutesSpinEdit.Size = new System.Drawing.Size(114, 44);
            MinutesSpinEdit.TabIndex = 1;
            MinutesSpinEdit.ValueChanged += MinutesSpinEdit_ValueChanged;
            // 
            // TimerLabel
            // 
            TimerLabel.Appearance.Font = new System.Drawing.Font("Segoe UI Semibold", 60F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
            TimerLabel.Appearance.Options.UseFont = true;
            TimerLabel.Appearance.Options.UseTextOptions = true;
            TimerLabel.Appearance.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Near;
            tablePanel2.SetColumn(TimerLabel, 1);
            tablePanel2.SetColumnSpan(TimerLabel, 5);
            TimerLabel.Dock = System.Windows.Forms.DockStyle.Fill;
            TimerLabel.Location = new System.Drawing.Point(57, 36);
            TimerLabel.Name = "TimerLabel";
            tablePanel2.SetRow(TimerLabel, 1);
            TimerLabel.Size = new System.Drawing.Size(374, 114);
            TimerLabel.TabIndex = 0;
            TimerLabel.Text = "00:00:00";
            // 
            // StopwatchPage
            // 
            StopwatchPage.Caption = "StopwatchPage";
            StopwatchPage.Name = "StopwatchPage";
            StopwatchPage.Size = new System.Drawing.Size(498, 306);
            // 
            // AlarmPage
            // 
            AlarmPage.Caption = "AlarmPage";
            AlarmPage.Name = "AlarmPage";
            AlarmPage.Size = new System.Drawing.Size(498, 306);
            // 
            // FocusPage
            // 
            FocusPage.Caption = "FocusPage";
            FocusPage.Name = "FocusPage";
            FocusPage.Size = new System.Drawing.Size(498, 306);
            // 
            // ClockTimer
            // 
            ClockTimer.Enabled = true;
            ClockTimer.Interval = 1000;
            ClockTimer.Tick += ClockTimer_Tick;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(498, 544);
            Controls.Add(MainNavigationFrame);
            Controls.Add(ribbonStatusBar);
            Controls.Add(ribbon);
            IconOptions.ShowIcon = false;
            Name = "MainForm";
            Ribbon = ribbon;
            StatusBar = ribbonStatusBar;
            Text = "MainForm";
            ((System.ComponentModel.ISupportInitialize)ribbon).EndInit();
            ((System.ComponentModel.ISupportInitialize)MainNavigationFrame).EndInit();
            MainNavigationFrame.ResumeLayout(false);
            ClockPage.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)tablePanel1).EndInit();
            tablePanel1.ResumeLayout(false);
            tablePanel1.PerformLayout();
            TimerPage.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)tablePanel2).EndInit();
            tablePanel2.ResumeLayout(false);
            tablePanel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)progressBarControl1.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)MinutesSpinEdit.Properties).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl ribbon;
        private DevExpress.XtraBars.Ribbon.RibbonPage HomeRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ComminRibPageGroup;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar;
        private DevExpress.XtraBars.Navigation.NavigationFrame MainNavigationFrame;
        private DevExpress.XtraBars.Navigation.NavigationPage ClockPage;
        private DevExpress.XtraBars.Navigation.NavigationPage TimerPage;
        private DevExpress.XtraBars.BarButtonItem ClockButton;
        private DevExpress.XtraBars.BarButtonItem TimerButton;
        private DevExpress.XtraBars.BarButtonItem StopwatchButton;
        private DevExpress.XtraBars.BarButtonItem AlarmButton;
        private DevExpress.XtraBars.BarButtonItem FocusButton;
        private DevExpress.XtraBars.BarStaticItem DateStatusItem;
        private DevExpress.XtraBars.BarStaticItem TimeStatusItem;
        private DevExpress.Utils.Layout.TablePanel tablePanel1;
        private DevExpress.XtraEditors.LabelControl ClockLabel;
        private DevExpress.Utils.Layout.TablePanel tablePanel2;
        private DevExpress.XtraEditors.LabelControl TimerLabel;
        private System.Windows.Forms.Timer ClockTimer;
        private DevExpress.XtraEditors.SpinEdit MinutesSpinEdit;
        private DevExpress.XtraEditors.SimpleButton simpleButton3;
        private DevExpress.XtraEditors.SimpleButton simpleButton2;
        private DevExpress.XtraEditors.SimpleButton simpleButton1;
        private DevExpress.XtraBars.Navigation.NavigationPage StopwatchPage;
        private DevExpress.XtraBars.Navigation.NavigationPage AlarmPage;
        private DevExpress.XtraBars.Navigation.NavigationPage FocusPage;
        private DevExpress.XtraEditors.LabelControl labelControl1;
        private DevExpress.XtraEditors.ProgressBarControl progressBarControl1;
    }
}