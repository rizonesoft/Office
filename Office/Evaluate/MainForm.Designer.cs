namespace Rizonesoft.Office.Evaluate
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
            fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPageGroup1 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            LicenseRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            DonateRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            HomeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            MainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            MainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            ribbonSVGImageCollection = new DevExpress.Utils.SvgImageCollection(components);
            ((System.ComponentModel.ISupportInitialize)MainRibbonControl).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MainTabbedMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).BeginInit();
            ((System.ComponentModel.ISupportInitialize)ribbonSVGImageCollection).BeginInit();
            SuspendLayout();
            // 
            // MainRibbonControl
            // 
            MainRibbonControl.ExpandCollapseItem.Id = 0;
            MainRibbonControl.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            MainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] { MainRibbonControl.ExpandCollapseItem, MainRibbonControl.SearchEditItem, NewBarButtonItem, OpenBarButtonItem, CloseBarButtonItem, SkinDropDownButtonItem, PaletteDropDownButtonItem, LicenseButtonItem, GetLicenseButtonItem, DonateButtonItem });
            MainRibbonControl.Location = new System.Drawing.Point(0, 0);
            MainRibbonControl.MaxItemId = 10;
            MainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            MainRibbonControl.Name = "MainRibbonControl";
            MainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { fileRibbonPage, HomeRibbonPage });
            MainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            MainRibbonControl.Size = new System.Drawing.Size(898, 201);
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
            OptionsRibbonGroup.ItemLinks.Add(SkinDropDownButtonItem);
            OptionsRibbonGroup.ItemLinks.Add(PaletteDropDownButtonItem);
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
            // MainRibbonStatusBar
            // 
            MainRibbonStatusBar.AutoUpdateMergedBars = DevExpress.Utils.DefaultBoolean.True;
            MainRibbonStatusBar.Location = new System.Drawing.Point(0, 612);
            MainRibbonStatusBar.Name = "MainRibbonStatusBar";
            MainRibbonStatusBar.Ribbon = MainRibbonControl;
            MainRibbonStatusBar.Size = new System.Drawing.Size(898, 37);
            // 
            // MainTabbedMdiManager
            // 
            MainTabbedMdiManager.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            MainTabbedMdiManager.Appearance.Options.UseFont = true;
            MainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InActiveTabPageHeader;
            MainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
            MainTabbedMdiManager.HeaderButtons = DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next | DevExpress.XtraTab.TabButtons.Close | DevExpress.XtraTab.TabButtons.Default;
            MainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            MainTabbedMdiManager.MdiParent = this;
            MainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InAllTabPageHeaders;
            MainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            MainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            MainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            MainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            MainTabbedMdiManager.PageAdded += MainTabbedMdiManager_PageAdded;
            MainTabbedMdiManager.PageRemoved += MainTabbedMdiManager_PageRemoved;
            // 
            // topSpacerPanel
            // 
            topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            topSpacerPanel.Location = new System.Drawing.Point(0, 201);
            topSpacerPanel.Name = "topSpacerPanel";
            topSpacerPanel.Size = new System.Drawing.Size(898, 5);
            topSpacerPanel.TabIndex = 11;
            // 
            // ribbonSVGImageCollection
            // 
            ribbonSVGImageCollection.Add("security_key", "image://svgimages/icon builder/security_key.svg");
            ribbonSVGImageCollection.Add("security_security", "image://svgimages/icon builder/security_security.svg");
            // 
            // MainForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(898, 649);
            Controls.Add(topSpacerPanel);
            Controls.Add(MainRibbonStatusBar);
            Controls.Add(MainRibbonControl);
            IconOptions.ShowIcon = false;
            IsMdiContainer = true;
            Name = "MainForm";
            Ribbon = MainRibbonControl;
            StatusBar = MainRibbonStatusBar;
            Text = "Rizonesoft ";
            Load += MainForm_Load;
            ((System.ComponentModel.ISupportInitialize)MainRibbonControl).EndInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)MainTabbedMdiManager).EndInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).EndInit();
            ((System.ComponentModel.ISupportInitialize)ribbonSVGImageCollection).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl MainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage fileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup commonRibbonGroup;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager MainTabbedMdiManager;
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
    }
}

