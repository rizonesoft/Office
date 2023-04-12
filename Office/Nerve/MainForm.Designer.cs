namespace Rizonesoft.Office.Nerve
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
            ribbonControl1 = new DevExpress.XtraBars.Ribbon.RibbonControl();
            messageStatusItem = new DevExpress.XtraBars.BarStaticItem();
            loadingEditItem = new DevExpress.XtraBars.BarEditItem();
            loadingItemMarqueeProgressBar = new DevExpress.XtraEditors.Repository.RepositoryItemMarqueeProgressBar();
            copyButtonItem = new DevExpress.XtraBars.BarButtonItem();
            modeToggleButton = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem1 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem2 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem3 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem4 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem5 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem6 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem7 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem8 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem9 = new DevExpress.XtraBars.BarButtonItem();
            barButtonItem10 = new DevExpress.XtraBars.BarButtonItem();
            ribbonPage1 = new DevExpress.XtraBars.Ribbon.RibbonPage();
            ribbonPageGroup3 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPageGroup1 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPageGroup2 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPageGroup4 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            loadingProgressRepositoryItem = new DevExpress.XtraEditors.Repository.RepositoryItemProgressBar();
            repositoryItemButtonEdit1 = new DevExpress.XtraEditors.Repository.RepositoryItemButtonEdit();
            ribbonStatusBar1 = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            chromiumWebBrowser1 = new CefSharp.WinForms.ChromiumWebBrowser();
            BrowserSvgImageCollection = new DevExpress.Utils.SvgImageCollection(components);
            panelControl1 = new DevExpress.XtraEditors.PanelControl();
            panelControl4 = new DevExpress.XtraEditors.PanelControl();
            comboBoxEdit2 = new DevExpress.XtraEditors.ComboBoxEdit();
            panelControl3 = new DevExpress.XtraEditors.PanelControl();
            comboBoxEdit1 = new DevExpress.XtraEditors.ComboBoxEdit();
            labelControl1 = new DevExpress.XtraEditors.LabelControl();
            panelControl2 = new DevExpress.XtraEditors.PanelControl();
            simpleButton2 = new DevExpress.XtraEditors.SimpleButton();
            simpleButton1 = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)ribbonControl1).BeginInit();
            ((System.ComponentModel.ISupportInitialize)loadingItemMarqueeProgressBar).BeginInit();
            ((System.ComponentModel.ISupportInitialize)loadingProgressRepositoryItem).BeginInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemButtonEdit1).BeginInit();
            ((System.ComponentModel.ISupportInitialize)BrowserSvgImageCollection).BeginInit();
            ((System.ComponentModel.ISupportInitialize)panelControl1).BeginInit();
            panelControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)panelControl4).BeginInit();
            panelControl4.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)comboBoxEdit2.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)panelControl3).BeginInit();
            panelControl3.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)comboBoxEdit1.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)panelControl2).BeginInit();
            panelControl2.SuspendLayout();
            SuspendLayout();
            // 
            // ribbonControl1
            // 
            ribbonControl1.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(45, 49, 45, 49);
            ribbonControl1.ExpandCollapseItem.Id = 0;
            ribbonControl1.Items.AddRange(new DevExpress.XtraBars.BarItem[] { ribbonControl1.ExpandCollapseItem, ribbonControl1.SearchEditItem, messageStatusItem, loadingEditItem, copyButtonItem, modeToggleButton, barButtonItem1, barButtonItem2, barButtonItem3, barButtonItem4, barButtonItem5, barButtonItem6, barButtonItem7, barButtonItem8, barButtonItem9, barButtonItem10 });
            ribbonControl1.Location = new System.Drawing.Point(0, 0);
            ribbonControl1.Margin = new System.Windows.Forms.Padding(4);
            ribbonControl1.MaxItemId = 19;
            ribbonControl1.Name = "ribbonControl1";
            ribbonControl1.OptionsMenuMinWidth = 495;
            ribbonControl1.PageHeaderItemLinks.Add(barButtonItem9);
            ribbonControl1.PageHeaderItemLinks.Add(barButtonItem10);
            ribbonControl1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { ribbonPage1 });
            ribbonControl1.RepositoryItems.AddRange(new DevExpress.XtraEditors.Repository.RepositoryItem[] { loadingProgressRepositoryItem, loadingItemMarqueeProgressBar, repositoryItemButtonEdit1 });
            ribbonControl1.Size = new System.Drawing.Size(1547, 296);
            ribbonControl1.StatusBar = ribbonStatusBar1;
            // 
            // messageStatusItem
            // 
            messageStatusItem.Id = 1;
            messageStatusItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("messageStatusItem.ImageOptions.SvgImage");
            messageStatusItem.Name = "messageStatusItem";
            messageStatusItem.PaintStyle = DevExpress.XtraBars.BarItemPaintStyle.CaptionGlyph;
            // 
            // loadingEditItem
            // 
            loadingEditItem.Alignment = DevExpress.XtraBars.BarItemLinkAlignment.Right;
            loadingEditItem.Edit = loadingItemMarqueeProgressBar;
            loadingEditItem.EditWidth = 100;
            loadingEditItem.Id = 3;
            loadingEditItem.Name = "loadingEditItem";
            // 
            // loadingItemMarqueeProgressBar
            // 
            loadingItemMarqueeProgressBar.Name = "loadingItemMarqueeProgressBar";
            // 
            // copyButtonItem
            // 
            copyButtonItem.Caption = "Copy";
            copyButtonItem.Id = 4;
            copyButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("copyButtonItem.ImageOptions.SvgImage");
            copyButtonItem.Name = "copyButtonItem";
            copyButtonItem.ItemClick += CopyButtonItem_ItemClick;
            // 
            // modeToggleButton
            // 
            modeToggleButton.Caption = "Toggle mode";
            modeToggleButton.Id = 5;
            modeToggleButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("modeToggleButton.ImageOptions.SvgImage");
            modeToggleButton.Name = "modeToggleButton";
            modeToggleButton.ItemClick += modeToggleButton_Click;
            // 
            // barButtonItem1
            // 
            barButtonItem1.Caption = "Paste";
            barButtonItem1.Id = 8;
            barButtonItem1.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem1.ImageOptions.SvgImage");
            barButtonItem1.Name = "barButtonItem1";
            // 
            // barButtonItem2
            // 
            barButtonItem2.Caption = "ChatGPT";
            barButtonItem2.Id = 9;
            barButtonItem2.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem2.ImageOptions.SvgImage");
            barButtonItem2.Name = "barButtonItem2";
            // 
            // barButtonItem3
            // 
            barButtonItem3.Caption = "Settings";
            barButtonItem3.Id = 11;
            barButtonItem3.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem3.ImageOptions.SvgImage");
            barButtonItem3.Name = "barButtonItem3";
            // 
            // barButtonItem4
            // 
            barButtonItem4.Caption = "Back";
            barButtonItem4.Id = 12;
            barButtonItem4.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem4.ImageOptions.SvgImage");
            barButtonItem4.Name = "barButtonItem4";
            // 
            // barButtonItem5
            // 
            barButtonItem5.Caption = "Forward";
            barButtonItem5.Id = 13;
            barButtonItem5.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem5.ImageOptions.SvgImage");
            barButtonItem5.Name = "barButtonItem5";
            // 
            // barButtonItem6
            // 
            barButtonItem6.Caption = "Relaod";
            barButtonItem6.Id = 14;
            barButtonItem6.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem6.ImageOptions.SvgImage");
            barButtonItem6.Name = "barButtonItem6";
            // 
            // barButtonItem7
            // 
            barButtonItem7.Caption = "Signup";
            barButtonItem7.Id = 15;
            barButtonItem7.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem7.ImageOptions.SvgImage");
            barButtonItem7.Name = "barButtonItem7";
            // 
            // barButtonItem8
            // 
            barButtonItem8.Caption = "Log in";
            barButtonItem8.Id = 16;
            barButtonItem8.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem8.ImageOptions.SvgImage");
            barButtonItem8.Name = "barButtonItem8";
            // 
            // barButtonItem9
            // 
            barButtonItem9.Caption = "On-Top";
            barButtonItem9.Id = 17;
            barButtonItem9.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem9.ImageOptions.SvgImage");
            barButtonItem9.Name = "barButtonItem9";
            // 
            // barButtonItem10
            // 
            barButtonItem10.Caption = "barButtonItem10";
            barButtonItem10.Id = 18;
            barButtonItem10.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barButtonItem10.ImageOptions.SvgImage");
            barButtonItem10.Name = "barButtonItem10";
            // 
            // ribbonPage1
            // 
            ribbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { ribbonPageGroup3, ribbonPageGroup1, ribbonPageGroup2, ribbonPageGroup4 });
            ribbonPage1.Name = "ribbonPage1";
            ribbonPage1.Text = "Nerve";
            // 
            // ribbonPageGroup3
            // 
            ribbonPageGroup3.ItemLinks.Add(barButtonItem2);
            ribbonPageGroup3.ItemLinks.Add(barButtonItem4);
            ribbonPageGroup3.ItemLinks.Add(barButtonItem5);
            ribbonPageGroup3.ItemLinks.Add(barButtonItem6);
            ribbonPageGroup3.Name = "ribbonPageGroup3";
            ribbonPageGroup3.Text = "Navigation";
            // 
            // ribbonPageGroup1
            // 
            ribbonPageGroup1.ItemLinks.Add(copyButtonItem);
            ribbonPageGroup1.ItemLinks.Add(barButtonItem1);
            ribbonPageGroup1.Name = "ribbonPageGroup1";
            ribbonPageGroup1.Text = "Clipboard";
            // 
            // ribbonPageGroup2
            // 
            ribbonPageGroup2.ItemLinks.Add(modeToggleButton);
            ribbonPageGroup2.ItemLinks.Add(barButtonItem3);
            ribbonPageGroup2.Name = "ribbonPageGroup2";
            ribbonPageGroup2.Text = "Options";
            // 
            // ribbonPageGroup4
            // 
            ribbonPageGroup4.ItemLinks.Add(barButtonItem7);
            ribbonPageGroup4.ItemLinks.Add(barButtonItem8);
            ribbonPageGroup4.Name = "ribbonPageGroup4";
            ribbonPageGroup4.Text = "Account";
            // 
            // loadingProgressRepositoryItem
            // 
            loadingProgressRepositoryItem.Name = "loadingProgressRepositoryItem";
            // 
            // repositoryItemButtonEdit1
            // 
            repositoryItemButtonEdit1.AutoHeight = false;
            repositoryItemButtonEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton() });
            repositoryItemButtonEdit1.Name = "repositoryItemButtonEdit1";
            // 
            // ribbonStatusBar1
            // 
            ribbonStatusBar1.ItemLinks.Add(messageStatusItem);
            ribbonStatusBar1.ItemLinks.Add(loadingEditItem);
            ribbonStatusBar1.Location = new System.Drawing.Point(0, 1190);
            ribbonStatusBar1.Name = "ribbonStatusBar1";
            ribbonStatusBar1.Ribbon = ribbonControl1;
            ribbonStatusBar1.Size = new System.Drawing.Size(1547, 55);
            // 
            // chromiumWebBrowser1
            // 
            chromiumWebBrowser1.ActivateBrowserOnCreation = false;
            chromiumWebBrowser1.Dock = System.Windows.Forms.DockStyle.Fill;
            chromiumWebBrowser1.Location = new System.Drawing.Point(0, 367);
            chromiumWebBrowser1.Name = "chromiumWebBrowser1";
            chromiumWebBrowser1.Padding = new System.Windows.Forms.Padding(0, 10, 0, 0);
            chromiumWebBrowser1.Size = new System.Drawing.Size(1547, 823);
            chromiumWebBrowser1.TabIndex = 1;
            chromiumWebBrowser1.Text = "chromiumWebBrowser1";
            // 
            // BrowserSvgImageCollection
            // 
            BrowserSvgImageCollection.Add("weather_sunny", "image://svgimages/icon builder/weather_sunny.svg");
            BrowserSvgImageCollection.Add("weather_moon", "image://svgimages/icon builder/weather_moon.svg");
            // 
            // panelControl1
            // 
            panelControl1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl1.Controls.Add(panelControl4);
            panelControl1.Controls.Add(panelControl3);
            panelControl1.Controls.Add(panelControl2);
            panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            panelControl1.Location = new System.Drawing.Point(0, 296);
            panelControl1.Name = "panelControl1";
            panelControl1.Padding = new System.Windows.Forms.Padding(13);
            panelControl1.Size = new System.Drawing.Size(1547, 71);
            panelControl1.TabIndex = 11;
            // 
            // panelControl4
            // 
            panelControl4.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl4.Controls.Add(comboBoxEdit2);
            panelControl4.Dock = System.Windows.Forms.DockStyle.Fill;
            panelControl4.Location = new System.Drawing.Point(583, 13);
            panelControl4.Name = "panelControl4";
            panelControl4.Padding = new System.Windows.Forms.Padding(13, 0, 13, 0);
            panelControl4.Size = new System.Drawing.Size(771, 45);
            panelControl4.TabIndex = 2;
            // 
            // comboBoxEdit2
            // 
            comboBoxEdit2.Dock = System.Windows.Forms.DockStyle.Fill;
            comboBoxEdit2.Location = new System.Drawing.Point(13, 0);
            comboBoxEdit2.MenuManager = ribbonControl1;
            comboBoxEdit2.Name = "comboBoxEdit2";
            comboBoxEdit2.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            comboBoxEdit2.Size = new System.Drawing.Size(745, 42);
            comboBoxEdit2.TabIndex = 2;
            // 
            // panelControl3
            // 
            panelControl3.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl3.Controls.Add(comboBoxEdit1);
            panelControl3.Controls.Add(labelControl1);
            panelControl3.Dock = System.Windows.Forms.DockStyle.Left;
            panelControl3.Location = new System.Drawing.Point(13, 13);
            panelControl3.Name = "panelControl3";
            panelControl3.Size = new System.Drawing.Size(570, 45);
            panelControl3.TabIndex = 1;
            // 
            // comboBoxEdit1
            // 
            comboBoxEdit1.Dock = System.Windows.Forms.DockStyle.Fill;
            comboBoxEdit1.Location = new System.Drawing.Point(150, 0);
            comboBoxEdit1.MenuManager = ribbonControl1;
            comboBoxEdit1.Name = "comboBoxEdit1";
            comboBoxEdit1.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            comboBoxEdit1.Size = new System.Drawing.Size(420, 42);
            comboBoxEdit1.TabIndex = 1;
            // 
            // labelControl1
            // 
            labelControl1.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            labelControl1.Dock = System.Windows.Forms.DockStyle.Left;
            labelControl1.Location = new System.Drawing.Point(0, 0);
            labelControl1.Name = "labelControl1";
            labelControl1.Size = new System.Drawing.Size(150, 45);
            labelControl1.TabIndex = 0;
            labelControl1.Text = "labelControl1";
            // 
            // panelControl2
            // 
            panelControl2.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl2.Controls.Add(simpleButton2);
            panelControl2.Controls.Add(simpleButton1);
            panelControl2.Dock = System.Windows.Forms.DockStyle.Right;
            panelControl2.Location = new System.Drawing.Point(1354, 13);
            panelControl2.Name = "panelControl2";
            panelControl2.Size = new System.Drawing.Size(180, 45);
            panelControl2.TabIndex = 0;
            // 
            // simpleButton2
            // 
            simpleButton2.Dock = System.Windows.Forms.DockStyle.Left;
            simpleButton2.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            simpleButton2.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("simpleButton2.ImageOptions.SvgImage");
            simpleButton2.Location = new System.Drawing.Point(0, 0);
            simpleButton2.Name = "simpleButton2";
            simpleButton2.Size = new System.Drawing.Size(85, 45);
            simpleButton2.TabIndex = 1;
            simpleButton2.ToolTip = "Insert Prompt";
            // 
            // simpleButton1
            // 
            simpleButton1.Dock = System.Windows.Forms.DockStyle.Right;
            simpleButton1.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            simpleButton1.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("simpleButton1.ImageOptions.SvgImage");
            simpleButton1.Location = new System.Drawing.Point(95, 0);
            simpleButton1.Name = "simpleButton1";
            simpleButton1.Size = new System.Drawing.Size(85, 45);
            simpleButton1.TabIndex = 0;
            // 
            // MainForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(9F, 21F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(1547, 1245);
            Controls.Add(chromiumWebBrowser1);
            Controls.Add(panelControl1);
            Controls.Add(ribbonStatusBar1);
            Controls.Add(ribbonControl1);
            Font = new System.Drawing.Font("Segoe UI", 8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            Margin = new System.Windows.Forms.Padding(4);
            Name = "MainForm";
            Ribbon = ribbonControl1;
            StatusBar = ribbonStatusBar1;
            Text = "Form1";
            FormClosing += Form1_FormClosing;
            Load += Form1_Load;
            ((System.ComponentModel.ISupportInitialize)ribbonControl1).EndInit();
            ((System.ComponentModel.ISupportInitialize)loadingItemMarqueeProgressBar).EndInit();
            ((System.ComponentModel.ISupportInitialize)loadingProgressRepositoryItem).EndInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemButtonEdit1).EndInit();
            ((System.ComponentModel.ISupportInitialize)BrowserSvgImageCollection).EndInit();
            ((System.ComponentModel.ISupportInitialize)panelControl1).EndInit();
            panelControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)panelControl4).EndInit();
            panelControl4.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)comboBoxEdit2.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)panelControl3).EndInit();
            panelControl3.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)comboBoxEdit1.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)panelControl2).EndInit();
            panelControl2.ResumeLayout(false);
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl ribbonControl1;
        private DevExpress.XtraBars.Ribbon.RibbonPage ribbonPage1;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup1;
        private CefSharp.WinForms.ChromiumWebBrowser chromiumWebBrowser1;
        private DevExpress.XtraBars.BarStaticItem messageStatusItem;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar1;
        private DevExpress.XtraEditors.Repository.RepositoryItemProgressBar loadingProgressRepositoryItem;
        private DevExpress.XtraBars.BarEditItem loadingEditItem;
        private DevExpress.XtraEditors.Repository.RepositoryItemMarqueeProgressBar loadingItemMarqueeProgressBar;
        private DevExpress.XtraBars.BarButtonItem copyButtonItem;
        private DevExpress.XtraBars.BarButtonItem modeToggleButton;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup2;
        private DevExpress.XtraEditors.Repository.RepositoryItemButtonEdit repositoryItemButtonEdit1;
        private DevExpress.Utils.SvgImageCollection BrowserSvgImageCollection;
        private DevExpress.XtraBars.BarButtonItem barButtonItem1;
        private DevExpress.XtraBars.BarButtonItem barButtonItem2;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup3;
        private DevExpress.XtraEditors.PanelControl panelControl1;
        private DevExpress.XtraEditors.PanelControl panelControl4;
        private DevExpress.XtraEditors.ComboBoxEdit comboBoxEdit2;
        private DevExpress.XtraEditors.PanelControl panelControl3;
        private DevExpress.XtraEditors.ComboBoxEdit comboBoxEdit1;
        private DevExpress.XtraEditors.LabelControl labelControl1;
        private DevExpress.XtraEditors.PanelControl panelControl2;
        private DevExpress.XtraEditors.SimpleButton simpleButton2;
        private DevExpress.XtraEditors.SimpleButton simpleButton1;
        private DevExpress.XtraBars.BarButtonItem barButtonItem3;
        private DevExpress.XtraBars.BarButtonItem barButtonItem4;
        private DevExpress.XtraBars.BarButtonItem barButtonItem5;
        private DevExpress.XtraBars.BarButtonItem barButtonItem6;
        private DevExpress.XtraBars.BarButtonItem barButtonItem7;
        private DevExpress.XtraBars.BarButtonItem barButtonItem8;
        private DevExpress.XtraBars.BarButtonItem barButtonItem9;
        private DevExpress.XtraBars.BarButtonItem barButtonItem10;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup4;
    }
}

