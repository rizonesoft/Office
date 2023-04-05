namespace Rizonesoft.Office.Evaluate
{
    internal sealed partial class MainForm
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
            MainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            NewBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            OpenBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            mruPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            CloseBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            SkinDropDownButtonItem = new DevExpress.XtraBars.SkinDropDownButtonItem();
            PaletteDropDownButtonItem = new DevExpress.XtraBars.SkinPaletteDropDownButtonItem();
            LicenseButtonItem = new DevExpress.XtraBars.BarButtonItem();
            GetLicenseButtonItem = new DevExpress.XtraBars.BarButtonItem();
            DonateButtonItem = new DevExpress.XtraBars.BarButtonItem();
            OptionsBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            TimeStatusButton = new DevExpress.XtraBars.BarButtonItem();
            fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPageGroup1 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            LicenseRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            DonateRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            HomeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            ViewRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            InterfacePageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            repositoryItemCalcEdit1 = new DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit();
            repositoryItemCalcEdit2 = new DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit();
            repositoryItemCalcEdit3 = new DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit();
            MainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            ribbonSVGImageCollection = new DevExpress.Utils.SvgImageCollection(components);
            LicenseTimer = new System.Windows.Forms.Timer(components);
            ((System.ComponentModel.ISupportInitialize)MainRibbonControl).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit1).BeginInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit2).BeginInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit3).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mainTabbedMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).BeginInit();
            ((System.ComponentModel.ISupportInitialize)ribbonSVGImageCollection).BeginInit();
            SuspendLayout();
            // 
            // MainRibbonControl
            // 
            MainRibbonControl.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(45, 49, 45, 49);
            MainRibbonControl.ExpandCollapseItem.Id = 0;
            MainRibbonControl.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            MainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] { MainRibbonControl.ExpandCollapseItem, MainRibbonControl.SearchEditItem, NewBarButtonItem, OpenBarButtonItem, CloseBarButtonItem, SkinDropDownButtonItem, PaletteDropDownButtonItem, LicenseButtonItem, GetLicenseButtonItem, DonateButtonItem, OptionsBarButtonItem, TimeStatusButton });
            MainRibbonControl.Location = new System.Drawing.Point(0, 0);
            MainRibbonControl.Margin = new System.Windows.Forms.Padding(4);
            MainRibbonControl.MaxItemId = 16;
            MainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            MainRibbonControl.Name = "MainRibbonControl";
            MainRibbonControl.OptionsMenuMinWidth = 495;
            MainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { fileRibbonPage, HomeRibbonPage, ViewRibbonPage });
            MainRibbonControl.QuickToolbarItemLinks.Add(NewBarButtonItem);
            MainRibbonControl.QuickToolbarItemLinks.Add(OpenBarButtonItem);
            MainRibbonControl.RepositoryItems.AddRange(new DevExpress.XtraEditors.Repository.RepositoryItem[] { repositoryItemCalcEdit1, repositoryItemCalcEdit2, repositoryItemCalcEdit3 });
            MainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            MainRibbonControl.Size = new System.Drawing.Size(1347, 296);
            MainRibbonControl.StatusBar = MainRibbonStatusBar;
            MainRibbonControl.Merge += MainRibbonControl_Merge;
            // 
            // NewBarButtonItem
            // 
            NewBarButtonItem.Caption = "New";
            NewBarButtonItem.Id = 1;
            NewBarButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("NewBarButtonItem.ImageOptions.SvgImage");
            NewBarButtonItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut(System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.N);
            NewBarButtonItem.Name = "NewBarButtonItem";
            NewBarButtonItem.ItemClick += NewBarButtonItem_ItemClick;
            // 
            // OpenBarButtonItem
            // 
            OpenBarButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            OpenBarButtonItem.Caption = "Open";
            OpenBarButtonItem.DropDownControl = mruPopupMenu;
            OpenBarButtonItem.Id = 2;
            OpenBarButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("OpenBarButtonItem.ImageOptions.SvgImage");
            OpenBarButtonItem.Name = "OpenBarButtonItem";
            OpenBarButtonItem.ItemClick += OpenBarButtonItem_ItemClick;
            // 
            // mruPopupMenu
            // 
            mruPopupMenu.Name = "mruPopupMenu";
            mruPopupMenu.Ribbon = MainRibbonControl;
            // 
            // CloseBarButtonItem
            // 
            CloseBarButtonItem.Caption = "Close";
            CloseBarButtonItem.Id = 3;
            CloseBarButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseBarButtonItem.ImageOptions.SvgImage");
            CloseBarButtonItem.Name = "CloseBarButtonItem";
            CloseBarButtonItem.ItemClick += CloseBarButtonItem_ItemClick;
            // 
            // SkinDropDownButtonItem
            // 
            SkinDropDownButtonItem.ActAsDropDown = true;
            SkinDropDownButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            SkinDropDownButtonItem.Id = 4;
            SkinDropDownButtonItem.Name = "SkinDropDownButtonItem";
            // 
            // PaletteDropDownButtonItem
            // 
            PaletteDropDownButtonItem.ActAsDropDown = true;
            PaletteDropDownButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            PaletteDropDownButtonItem.Id = 5;
            PaletteDropDownButtonItem.Name = "PaletteDropDownButtonItem";
            // 
            // LicenseButtonItem
            // 
            LicenseButtonItem.Caption = "License";
            LicenseButtonItem.Id = 7;
            LicenseButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("LicenseButtonItem.ImageOptions.SvgImage");
            LicenseButtonItem.Name = "LicenseButtonItem";
            LicenseButtonItem.ItemClick += LicenseButtonItem_ItemClick;
            // 
            // GetLicenseButtonItem
            // 
            GetLicenseButtonItem.Caption = "Get License";
            GetLicenseButtonItem.Id = 8;
            GetLicenseButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("GetLicenseButtonItem.ImageOptions.SvgImage");
            GetLicenseButtonItem.Name = "GetLicenseButtonItem";
            // 
            // DonateButtonItem
            // 
            DonateButtonItem.Caption = "Donate";
            DonateButtonItem.Id = 9;
            DonateButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("DonateButtonItem.ImageOptions.SvgImage");
            DonateButtonItem.Name = "DonateButtonItem";
            // 
            // OptionsBarButtonItem
            // 
            OptionsBarButtonItem.Caption = "Options";
            OptionsBarButtonItem.Id = 10;
            OptionsBarButtonItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("OptionsBarButtonItem.ImageOptions.SvgImage");
            OptionsBarButtonItem.Name = "OptionsBarButtonItem";
            // 
            // TimeStatusButton
            // 
            TimeStatusButton.Alignment = DevExpress.XtraBars.BarItemLinkAlignment.Right;
            TimeStatusButton.Caption = "00:00 AM";
            TimeStatusButton.Id = 11;
            TimeStatusButton.MergeOrder = 10;
            TimeStatusButton.Name = "TimeStatusButton";
            TimeStatusButton.ItemClick += TimeStatusButton_ItemClick;
            // 
            // fileRibbonPage
            // 
            fileRibbonPage.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            fileRibbonPage.Appearance.Options.UseFont = true;
            fileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { commonRibbonGroup, ribbonPageGroup1, OptionsRibbonGroup, LicenseRibbonGroup, DonateRibbonGroup });
            fileRibbonPage.Name = "fileRibbonPage";
            fileRibbonPage.Text = "File";
            // 
            // commonRibbonGroup
            // 
            commonRibbonGroup.ItemLinks.Add(NewBarButtonItem);
            commonRibbonGroup.ItemLinks.Add(OpenBarButtonItem);
            commonRibbonGroup.ItemLinks.Add(CloseBarButtonItem);
            commonRibbonGroup.Name = "commonRibbonGroup";
            commonRibbonGroup.Text = "Common";
            // 
            // ribbonPageGroup1
            // 
            ribbonPageGroup1.Name = "ribbonPageGroup1";
            ribbonPageGroup1.Text = "Info";
            // 
            // OptionsRibbonGroup
            // 
            OptionsRibbonGroup.ItemLinks.Add(OptionsBarButtonItem);
            OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            OptionsRibbonGroup.Text = "Options";
            // 
            // LicenseRibbonGroup
            // 
            LicenseRibbonGroup.ItemLinks.Add(LicenseButtonItem);
            LicenseRibbonGroup.ItemLinks.Add(GetLicenseButtonItem);
            LicenseRibbonGroup.Name = "LicenseRibbonGroup";
            LicenseRibbonGroup.Text = "Registration";
            // 
            // DonateRibbonGroup
            // 
            DonateRibbonGroup.ItemLinks.Add(DonateButtonItem);
            DonateRibbonGroup.Name = "DonateRibbonGroup";
            DonateRibbonGroup.Text = "Contribute";
            // 
            // HomeRibbonPage
            // 
            HomeRibbonPage.Name = "HomeRibbonPage";
            HomeRibbonPage.Text = "Home";
            // 
            // ViewRibbonPage
            // 
            ViewRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { InterfacePageGroup });
            ViewRibbonPage.Name = "ViewRibbonPage";
            ViewRibbonPage.Text = "View";
            // 
            // InterfacePageGroup
            // 
            InterfacePageGroup.ItemLinks.Add(SkinDropDownButtonItem);
            InterfacePageGroup.ItemLinks.Add(PaletteDropDownButtonItem);
            InterfacePageGroup.Name = "InterfacePageGroup";
            InterfacePageGroup.Text = "Theme";
            // 
            // repositoryItemCalcEdit1
            // 
            repositoryItemCalcEdit1.AutoHeight = false;
            repositoryItemCalcEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            repositoryItemCalcEdit1.Name = "repositoryItemCalcEdit1";
            // 
            // repositoryItemCalcEdit2
            // 
            repositoryItemCalcEdit2.AutoHeight = false;
            repositoryItemCalcEdit2.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            repositoryItemCalcEdit2.Name = "repositoryItemCalcEdit2";
            // 
            // repositoryItemCalcEdit3
            // 
            repositoryItemCalcEdit3.AutoHeight = false;
            repositoryItemCalcEdit3.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo) });
            repositoryItemCalcEdit3.Name = "repositoryItemCalcEdit3";
            // 
            // MainRibbonStatusBar
            // 
            MainRibbonStatusBar.AutoUpdateMergedBars = DevExpress.Utils.DefaultBoolean.True;
            MainRibbonStatusBar.ItemLinks.Add(TimeStatusButton, true);
            MainRibbonStatusBar.Location = new System.Drawing.Point(0, 994);
            MainRibbonStatusBar.Margin = new System.Windows.Forms.Padding(4);
            MainRibbonStatusBar.Name = "MainRibbonStatusBar";
            MainRibbonStatusBar.Ribbon = MainRibbonControl;
            MainRibbonStatusBar.Size = new System.Drawing.Size(1347, 55);
            MainRibbonStatusBar.Click += MainRibbonStatusBar_Click;
            // 
            // mainTabbedMdiManager
            // 
            mainTabbedMdiManager.AllowDragDrop = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.AllowGlyphSkinning = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            mainTabbedMdiManager.Appearance.Options.UseFont = true;
            mainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InActiveTabPageHeader;
            mainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
            mainTabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.FullWindow;
            mainTabbedMdiManager.HeaderButtons = DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next | DevExpress.XtraTab.TabButtons.Close | DevExpress.XtraTab.TabButtons.Default;
            mainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            mainTabbedMdiManager.MdiParent = this;
            mainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InAllTabPageHeaders;
            mainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.PageAdded += MainTabbedMdiManager_PageAdded;
            mainTabbedMdiManager.PageRemoved += MainTabbedMdiManager_PageRemoved;
            // 
            // topSpacerPanel
            // 
            topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            topSpacerPanel.Location = new System.Drawing.Point(0, 296);
            topSpacerPanel.Margin = new System.Windows.Forms.Padding(4);
            topSpacerPanel.Name = "topSpacerPanel";
            topSpacerPanel.Size = new System.Drawing.Size(1347, 8);
            topSpacerPanel.TabIndex = 11;
            // 
            // ribbonSVGImageCollection
            // 
            ribbonSVGImageCollection.Add("security_key", "image://svgimages/icon builder/security_key.svg");
            ribbonSVGImageCollection.Add("security_security", "image://svgimages/icon builder/security_security.svg");
            // 
            // LicenseTimer
            // 
            LicenseTimer.Enabled = true;
            LicenseTimer.Interval = 1000;
            LicenseTimer.Tick += LicenseTimer_Tick;
            // 
            // MainForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(9F, 21F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(1347, 1049);
            Controls.Add(topSpacerPanel);
            Controls.Add(MainRibbonStatusBar);
            Controls.Add(MainRibbonControl);
            DoubleBuffered = false;
            IsMdiContainer = true;
            Margin = new System.Windows.Forms.Padding(4);
            Name = "MainForm";
            Ribbon = MainRibbonControl;
            StatusBar = MainRibbonStatusBar;
            Text = "Rizonesoft ";
            Load += MainForm_Load;
            DragDrop += MainForm_DragDrop;
            ((System.ComponentModel.ISupportInitialize)MainRibbonControl).EndInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit1).EndInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit2).EndInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemCalcEdit3).EndInit();
            ((System.ComponentModel.ISupportInitialize)mainTabbedMdiManager).EndInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).EndInit();
            ((System.ComponentModel.ISupportInitialize)ribbonSVGImageCollection).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl MainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage fileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup commonRibbonGroup;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar MainRibbonStatusBar;
        private DevExpress.XtraBars.PopupMenu mruPopupMenu;
        private DevExpress.XtraBars.BarButtonItem NewBarButtonItem;
        private DevExpress.XtraBars.BarButtonItem OpenBarButtonItem;
        private DevExpress.XtraBars.BarButtonItem CloseBarButtonItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup OptionsRibbonGroup;
        private DevExpress.XtraBars.SkinDropDownButtonItem SkinDropDownButtonItem;
        private DevExpress.XtraBars.SkinPaletteDropDownButtonItem PaletteDropDownButtonItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup LicenseRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup1;
        private DevExpress.XtraEditors.PanelControl topSpacerPanel;
        private DevExpress.XtraBars.BarButtonItem LicenseButtonItem;
        private DevExpress.XtraBars.BarButtonItem GetLicenseButtonItem;
        private DevExpress.XtraBars.BarButtonItem DonateButtonItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup DonateRibbonGroup;
        private DevExpress.Utils.SvgImageCollection ribbonSVGImageCollection;
        private DevExpress.XtraBars.Ribbon.RibbonPage HomeRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPage ViewRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup InterfacePageGroup;
        private DevExpress.XtraBars.BarButtonItem OptionsBarButtonItem;
        private System.Windows.Forms.Timer LicenseTimer;
        private DevExpress.XtraBars.BarButtonItem TimeStatusButton;
        private DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit repositoryItemCalcEdit1;
        private DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit repositoryItemCalcEdit2;
        private DevExpress.XtraEditors.Repository.RepositoryItemCalcEdit repositoryItemCalcEdit3;
    }
}

