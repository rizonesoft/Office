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
            DevExpress.XtraSplashScreen.SplashScreenManager mainSplashScreenManager = new DevExpress.XtraSplashScreen.SplashScreenManager(this, typeof(global::Rizonesoft.Office.Verbum.SplashScreenForm), true, true);
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.MainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
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
            this.fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.optionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.licenseRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.debugRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.homeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.MainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.mainSharedDictionaryStorage = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.MainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainSplashScreenManager
            // 
            mainSplashScreenManager.ClosingDelay = 300;
            // 
            // MainRibbonControl
            // 
            this.MainRibbonControl.ExpandCollapseItem.Id = 0;
            this.MainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.MainRibbonControl.ExpandCollapseItem,
            this.MainRibbonControl.SearchEditItem,
            this.mainBarMdiChildrenListItem,
            this.barNewItem,
            this.barOpenItem,
            this.barCloseItem,
            this.skinDropDownItem,
            this.skinPaletteDropDownItem,
            this.barOptionsItem,
            this.barRegisterItem,
            this.barBuyNowItem,
            this.exceptionButtonItem});
            this.MainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.MainRibbonControl.Margin = new System.Windows.Forms.Padding(10);
            this.MainRibbonControl.MaxItemId = 12;
            this.MainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.MainRibbonControl.Name = "MainRibbonControl";
            this.MainRibbonControl.PageHeaderItemLinks.Add(this.mainBarMdiChildrenListItem);
            this.MainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage,
            this.homeRibbonPage});
            this.MainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.MainRibbonControl.ShowDisplayOptionsMenuButton = DevExpress.Utils.DefaultBoolean.True;
            this.MainRibbonControl.ShowSearchItem = true;
            this.MainRibbonControl.Size = new System.Drawing.Size(898, 158);
            this.MainRibbonControl.StatusBar = this.MainRibbonStatusBar;
            this.MainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.mainRibbonControl_Merge);
            // 
            // mainBarMdiChildrenListItem
            // 
            this.mainBarMdiChildrenListItem.Caption = "Documents";
            this.mainBarMdiChildrenListItem.Id = 1;
            this.mainBarMdiChildrenListItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("mainBarMdiChildrenListItem.ImageOptions.SvgImage")));
            this.mainBarMdiChildrenListItem.Name = "mainBarMdiChildrenListItem";
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
            this.mruPopupMenu.Ribbon = this.MainRibbonControl;
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
            this.barRegisterItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barRegisterItem_ItemClick);
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
            // fileRibbonPage
            // 
            this.fileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.commonRibbonGroup,
            this.optionsRibbonGroup,
            this.licenseRibbonGroup,
            this.debugRibbonGroup});
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
            // optionsRibbonGroup
            // 
            this.optionsRibbonGroup.ItemLinks.Add(this.skinDropDownItem);
            this.optionsRibbonGroup.ItemLinks.Add(this.skinPaletteDropDownItem);
            this.optionsRibbonGroup.ItemLinks.Add(this.barOptionsItem, true);
            this.optionsRibbonGroup.Name = "optionsRibbonGroup";
            this.optionsRibbonGroup.Text = "Options";
            // 
            // licenseRibbonGroup
            // 
            this.licenseRibbonGroup.ItemLinks.Add(this.barRegisterItem);
            this.licenseRibbonGroup.ItemLinks.Add(this.barBuyNowItem);
            this.licenseRibbonGroup.Name = "licenseRibbonGroup";
            this.licenseRibbonGroup.Text = "Registration";
            // 
            // debugRibbonGroup
            // 
            this.debugRibbonGroup.ItemLinks.Add(this.exceptionButtonItem);
            this.debugRibbonGroup.Name = "debugRibbonGroup";
            this.debugRibbonGroup.Text = "Debug";
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
            this.MainRibbonStatusBar.Ribbon = this.MainRibbonControl;
            this.MainRibbonStatusBar.Size = new System.Drawing.Size(898, 24);
            // 
            // mainTabbedMdiManager
            // 
            this.mainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InAllTabPageHeaders;
            this.mainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
            this.mainTabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.Preview;
            this.mainTabbedMdiManager.HeaderButtons = ((DevExpress.XtraTab.TabButtons)((((DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next) 
            | DevExpress.XtraTab.TabButtons.Close) 
            | DevExpress.XtraTab.TabButtons.Default)));
            this.mainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            this.mainTabbedMdiManager.MdiParent = this;
            this.mainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InAllTabPageHeaders;
            this.mainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.PageAdded += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.mainTabbedMdiManager_PageAdded);
            this.mainTabbedMdiManager.PageRemoved += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.mainTabbedMdiManager_PageRemoved);
            // 
            // MainForm
            // 
            this.AllowMdiBar = true;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(898, 649);
            this.Controls.Add(this.MainRibbonStatusBar);
            this.Controls.Add(this.MainRibbonControl);
            this.IconOptions.ShowIcon = false;
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.MainRibbonControl;
            this.StatusBar = this.MainRibbonStatusBar;
            this.Text = "Rizonesoft Verbum";
            this.Load += new System.EventHandler(this.MainForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.MainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl MainRibbonControl;
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
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraSpellChecker.SharedDictionaryStorage mainSharedDictionaryStorage;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar MainRibbonStatusBar;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup licenseRibbonGroup;
        private DevExpress.XtraBars.BarButtonItem barRegisterItem;
        private DevExpress.XtraBars.BarButtonItem barBuyNowItem;
        private DevExpress.XtraBars.BarButtonItem exceptionButtonItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup debugRibbonGroup;
    }
}

