namespace Rizonesoft.Office.Verbum
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
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.mainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            this.mainBarMdiChildrenListItem = new DevExpress.XtraBars.BarMdiChildrenListItem();
            this.barNewItem = new DevExpress.XtraBars.BarButtonItem();
            this.barOpenItem = new DevExpress.XtraBars.BarButtonItem();
            this.mruPopupMenu = new DevExpress.XtraBars.PopupMenu(this.components);
            this.barCloseItem = new DevExpress.XtraBars.BarButtonItem();
            this.skinDropDownItem = new DevExpress.XtraBars.SkinDropDownButtonItem();
            this.skinPaletteDropDownItem = new DevExpress.XtraBars.SkinPaletteDropDownButtonItem();
            this.barOptionsItem = new DevExpress.XtraBars.BarButtonItem();
            this.barRegisterItem = new DevExpress.XtraBars.BarButtonItem();
            this.barBuyNowItem = new DevExpress.XtraBars.BarButtonItem();
            this.exceptionButtonItem = new DevExpress.XtraBars.BarButtonItem();
            this.evaluatePopupMenuItem = new DevExpress.XtraBars.BarButtonItem();
            this.barButtonItem2 = new DevExpress.XtraBars.BarButtonItem();
            this.officePopupMenu = new DevExpress.XtraBars.PopupMenu(this.components);
            this.fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.exportRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.infoRibbonPageGroup1 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.optionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.debugRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.licenseRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.homeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.MainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.MainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.mainSharedDictionaryStorage = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.officePopupMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.MainTabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainRibbonControl
            // 
            this.mainRibbonControl.AllowCustomization = true;
            this.mainRibbonControl.AutoSaveLayoutToXmlPath = "";
            this.mainRibbonControl.ExpandCollapseItem.Id = 0;
            this.mainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.mainRibbonControl.ExpandCollapseItem,
            this.mainRibbonControl.SearchEditItem,
            this.mainBarMdiChildrenListItem,
            this.barNewItem,
            this.barOpenItem,
            this.barCloseItem,
            this.skinDropDownItem,
            this.skinPaletteDropDownItem,
            this.barOptionsItem,
            this.barRegisterItem,
            this.barBuyNowItem,
            this.exceptionButtonItem,
            this.evaluatePopupMenuItem,
            this.barButtonItem2});
            this.mainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.mainRibbonControl.Margin = new System.Windows.Forms.Padding(10);
            this.mainRibbonControl.MaxItemId = 20;
            this.mainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.mainRibbonControl.Name = "mainRibbonControl";
            this.mainRibbonControl.OptionsTouch.ShowTouchUISelectorInQAT = true;
            this.mainRibbonControl.OptionsTouch.ShowTouchUISelectorVisibilityItemInQATMenu = true;
            this.mainRibbonControl.PageHeaderItemLinks.Add(this.mainBarMdiChildrenListItem);
            this.mainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage,
            this.homeRibbonPage});
            this.mainRibbonControl.QuickToolbarItemLinks.Add(this.barNewItem);
            this.mainRibbonControl.QuickToolbarItemLinks.Add(this.barOpenItem);
            this.mainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.mainRibbonControl.ShowDisplayOptionsMenuButton = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowPageHeadersInFormCaption = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowPageHeadersMode = DevExpress.XtraBars.Ribbon.ShowPageHeadersMode.Show;
            this.mainRibbonControl.ShowSearchItem = true;
            this.mainRibbonControl.Size = new System.Drawing.Size(1005, 158);
            this.mainRibbonControl.StatusBar = this.MainRibbonStatusBar;
            this.mainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.mainRibbonControl_Merge);
            this.mainRibbonControl.Click += new System.EventHandler(this.MainRibbonControl_Click);
            // 
            // mainBarMdiChildrenListItem
            // 
            this.mainBarMdiChildrenListItem.Caption = "Documents";
            this.mainBarMdiChildrenListItem.Id = 1;
            this.mainBarMdiChildrenListItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("mainBarMdiChildrenListItem.ImageOptions.SvgImage")));
            this.mainBarMdiChildrenListItem.Name = "mainBarMdiChildrenListItem";
            this.mainBarMdiChildrenListItem.ShowMenuCaption = true;
            // 
            // barNewItem
            // 
            this.barNewItem.Caption = "New";
            this.barNewItem.Id = 2;
            this.barNewItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barNewItem.ImageOptions.SvgImage")));
            this.barNewItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.N));
            this.barNewItem.Name = "barNewItem";
            this.barNewItem.ShowItemShortcut = DevExpress.Utils.DefaultBoolean.True;
            this.barNewItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barNewItem_ItemClick);
            // 
            // barOpenItem
            // 
            this.barOpenItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.barOpenItem.Caption = "Open";
            this.barOpenItem.DropDownControl = this.mruPopupMenu;
            this.barOpenItem.Id = 3;
            this.barOpenItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barOpenItem.ImageOptions.SvgImage")));
            this.barOpenItem.Name = "barOpenItem";
            this.barOpenItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barOpenItem_ItemClick);
            // 
            // mruPopupMenu
            // 
            this.mruPopupMenu.Name = "mruPopupMenu";
            this.mruPopupMenu.Ribbon = this.mainRibbonControl;
            // 
            // barCloseItem
            // 
            this.barCloseItem.Caption = "Close";
            this.barCloseItem.Id = 4;
            this.barCloseItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barCloseItem.ImageOptions.SvgImage")));
            this.barCloseItem.Name = "barCloseItem";
            this.barCloseItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barCloseItem_ItemClick);
            // 
            // skinDropDownItem
            // 
            this.skinDropDownItem.ActAsDropDown = true;
            this.skinDropDownItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.skinDropDownItem.Id = 5;
            this.skinDropDownItem.MergeOrder = 90;
            this.skinDropDownItem.Name = "skinDropDownItem";
            // 
            // skinPaletteDropDownItem
            // 
            this.skinPaletteDropDownItem.ActAsDropDown = true;
            this.skinPaletteDropDownItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.skinPaletteDropDownItem.Id = 6;
            this.skinPaletteDropDownItem.MergeOrder = 91;
            this.skinPaletteDropDownItem.Name = "skinPaletteDropDownItem";
            // 
            // barOptionsItem
            // 
            this.barOptionsItem.Caption = "Options";
            this.barOptionsItem.Id = 7;
            this.barOptionsItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barOptionsItem.ImageOptions.SvgImage")));
            this.barOptionsItem.MergeOrder = 93;
            this.barOptionsItem.Name = "barOptionsItem";
            this.barOptionsItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barOptionsItem_ItemClick);
            // 
            // barRegisterItem
            // 
            this.barRegisterItem.Caption = "Register!";
            this.barRegisterItem.Id = 9;
            this.barRegisterItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barRegisterItem.ImageOptions.SvgImage")));
            this.barRegisterItem.Name = "barRegisterItem";
            this.barRegisterItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.BarRegisterItem_ItemClick);
            // 
            // barBuyNowItem
            // 
            this.barBuyNowItem.Caption = "Buy Now!";
            this.barBuyNowItem.Id = 10;
            this.barBuyNowItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barBuyNowItem.ImageOptions.SvgImage")));
            this.barBuyNowItem.Name = "barBuyNowItem";
            // 
            // exceptionButtonItem
            // 
            this.exceptionButtonItem.Caption = "Exception";
            this.exceptionButtonItem.Id = 11;
            this.exceptionButtonItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("exceptionButtonItem.ImageOptions.SvgImage")));
            this.exceptionButtonItem.Name = "exceptionButtonItem";
            this.exceptionButtonItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.exceptionButtonItem_ItemClick);
            // 
            // evaluatePopupMenuItem
            // 
            this.evaluatePopupMenuItem.Caption = "Evaluate";
            this.evaluatePopupMenuItem.Description = "Spreadsheets";
            this.evaluatePopupMenuItem.Id = 12;
            this.evaluatePopupMenuItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("evaluatePopupMenuItem.ImageOptions.SvgImage")));
            this.evaluatePopupMenuItem.Name = "evaluatePopupMenuItem";
            // 
            // barButtonItem2
            // 
            this.barButtonItem2.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.barButtonItem2.Caption = "barButtonItem2";
            this.barButtonItem2.DropDownControl = this.officePopupMenu;
            this.barButtonItem2.Id = 13;
            this.barButtonItem2.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barButtonItem2.ImageOptions.SvgImage")));
            this.barButtonItem2.Name = "barButtonItem2";
            // 
            // officePopupMenu
            // 
            this.officePopupMenu.MenuDrawMode = DevExpress.XtraBars.MenuDrawMode.LargeImagesTextDescription;
            this.officePopupMenu.Name = "officePopupMenu";
            this.officePopupMenu.Ribbon = this.mainRibbonControl;
            // 
            // fileRibbonPage
            // 
            this.fileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.commonRibbonGroup,
            this.exportRibbonGroup,
            this.infoRibbonPageGroup1,
            this.optionsRibbonGroup,
            this.debugRibbonGroup,
            this.licenseRibbonGroup});
            this.fileRibbonPage.Name = "fileRibbonPage";
            this.fileRibbonPage.Text = "File";
            // 
            // commonRibbonGroup
            // 
            this.commonRibbonGroup.ItemLinks.Add(this.barNewItem);
            this.commonRibbonGroup.ItemLinks.Add(this.barOpenItem);
            this.commonRibbonGroup.ItemLinks.Add(this.barCloseItem);
            this.commonRibbonGroup.MergeOrder = 0;
            this.commonRibbonGroup.Name = "commonRibbonGroup";
            this.commonRibbonGroup.Text = "Common";
            // 
            // exportRibbonGroup
            // 
            this.exportRibbonGroup.Name = "exportRibbonGroup";
            this.exportRibbonGroup.Text = "Export to";
            // 
            // infoRibbonPageGroup1
            // 
            this.infoRibbonPageGroup1.Name = "infoRibbonPageGroup1";
            this.infoRibbonPageGroup1.Text = "Info";
            // 
            // optionsRibbonGroup
            // 
            this.optionsRibbonGroup.ItemLinks.Add(this.skinDropDownItem);
            this.optionsRibbonGroup.ItemLinks.Add(this.skinPaletteDropDownItem);
            this.optionsRibbonGroup.ItemLinks.Add(this.barOptionsItem, true);
            this.optionsRibbonGroup.Name = "optionsRibbonGroup";
            this.optionsRibbonGroup.Text = "Options";
            // 
            // debugRibbonGroup
            // 
            this.debugRibbonGroup.ItemLinks.Add(this.exceptionButtonItem);
            this.debugRibbonGroup.Name = "debugRibbonGroup";
            this.debugRibbonGroup.Text = "Debug";
            // 
            // licenseRibbonGroup
            // 
            this.licenseRibbonGroup.ItemLinks.Add(this.barRegisterItem);
            this.licenseRibbonGroup.ItemLinks.Add(this.barBuyNowItem);
            this.licenseRibbonGroup.Name = "licenseRibbonGroup";
            this.licenseRibbonGroup.Text = "Registration";
            // 
            // homeRibbonPage
            // 
            this.homeRibbonPage.Name = "homeRibbonPage";
            this.homeRibbonPage.Text = "Home";
            // 
            // MainRibbonStatusBar
            // 
            this.MainRibbonStatusBar.AutoUpdateMergedBars = DevExpress.Utils.DefaultBoolean.True;
            this.MainRibbonStatusBar.Location = new System.Drawing.Point(0, 625);
            this.MainRibbonStatusBar.Name = "MainRibbonStatusBar";
            this.MainRibbonStatusBar.Ribbon = this.mainRibbonControl;
            this.MainRibbonStatusBar.Size = new System.Drawing.Size(1005, 24);
            // 
            // MainTabbedMdiManager
            // 
            this.MainTabbedMdiManager.AppearancePage.Header.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.MainTabbedMdiManager.AppearancePage.Header.Options.UseFont = true;
            this.MainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InAllTabPageHeaders;
            this.MainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
            this.MainTabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.Preview;
            this.MainTabbedMdiManager.HeaderButtons = ((DevExpress.XtraTab.TabButtons)((((DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next) 
            | DevExpress.XtraTab.TabButtons.Close) 
            | DevExpress.XtraTab.TabButtons.Default)));
            this.MainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            this.MainTabbedMdiManager.MdiParent = this;
            this.MainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InAllTabPageHeaders;
            this.MainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            this.MainTabbedMdiManager.PageAdded += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.mainTabbedMdiManager_PageAdded);
            this.MainTabbedMdiManager.PageRemoved += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.mainTabbedMdiManager_PageRemoved);
            // 
            // MainForm
            // 
            this.AllowMdiBar = true;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1005, 649);
            this.Controls.Add(this.MainRibbonStatusBar);
            this.Controls.Add(this.mainRibbonControl);
            this.IconOptions.ShowIcon = false;
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.mainRibbonControl;
            this.StatusBar = this.MainRibbonStatusBar;
            this.Text = "Verbum";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.MainForm_FormClosing);
            this.Load += new System.EventHandler(this.MainForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.officePopupMenu)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.MainTabbedMdiManager)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage fileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup commonRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPage homeRibbonPage;
        private DevExpress.XtraBars.BarMdiChildrenListItem mainBarMdiChildrenListItem;
        private DevExpress.XtraBars.BarButtonItem barNewItem;
        private DevExpress.XtraBars.BarButtonItem barOpenItem;
        private DevExpress.XtraBars.PopupMenu mruPopupMenu;
        private DevExpress.XtraBars.BarButtonItem barCloseItem;
        private DevExpress.XtraBars.SkinDropDownButtonItem skinDropDownItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup optionsRibbonGroup;
        private DevExpress.XtraBars.SkinPaletteDropDownButtonItem skinPaletteDropDownItem;
        private DevExpress.XtraBars.BarButtonItem barOptionsItem;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager MainTabbedMdiManager;
        private DevExpress.XtraSpellChecker.SharedDictionaryStorage mainSharedDictionaryStorage;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar MainRibbonStatusBar;
        private DevExpress.XtraBars.BarButtonItem barRegisterItem;
        private DevExpress.XtraBars.BarButtonItem barBuyNowItem;
        private DevExpress.XtraBars.BarButtonItem exceptionButtonItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup debugRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup exportRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup infoRibbonPageGroup1;
        private DevExpress.XtraBars.BarButtonItem evaluatePopupMenuItem;
        private DevExpress.XtraBars.BarButtonItem barButtonItem2;
        private DevExpress.XtraBars.PopupMenu officePopupMenu;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup licenseRibbonGroup;
    }
}

