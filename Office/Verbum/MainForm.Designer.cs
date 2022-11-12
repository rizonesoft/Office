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
            this.mainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            this.mainBarMdiChildrenListItem = new DevExpress.XtraBars.BarMdiChildrenListItem();
            this.barNewItem = new DevExpress.XtraBars.BarButtonItem();
            this.barOpenItem = new DevExpress.XtraBars.BarButtonItem();
            this.mruPopupMenu = new DevExpress.XtraBars.PopupMenu(this.components);
            this.barCloseItem = new DevExpress.XtraBars.BarButtonItem();
            this.skinDropDownItem = new DevExpress.XtraBars.SkinDropDownButtonItem();
            this.skinPaletteDropDownItem = new DevExpress.XtraBars.SkinPaletteDropDownButtonItem();
            this.barOptionsItem = new DevExpress.XtraBars.BarButtonItem();
            this.fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.optionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.homeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.ribbonPageGroup2 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.ribbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.mainSharedDictionaryStorage = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainSplashScreenManager
            // 
            mainSplashScreenManager.ClosingDelay = 300;
            // 
            // mainRibbonControl
            // 
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
            this.barOptionsItem});
            this.mainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.mainRibbonControl.MaxItemId = 8;
            this.mainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.mainRibbonControl.Name = "mainRibbonControl";
            this.mainRibbonControl.PageHeaderItemLinks.Add(this.mainBarMdiChildrenListItem);
            this.mainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage,
            this.homeRibbonPage});
            this.mainRibbonControl.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office2019;
            this.mainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.mainRibbonControl.ShowDisplayOptionsMenuButton = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowSearchItem = true;
            this.mainRibbonControl.Size = new System.Drawing.Size(898, 158);
            this.mainRibbonControl.StatusBar = this.ribbonStatusBar;
            this.mainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.mainRibbonControl_Merge);
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
            this.barNewItem.MergeType = DevExpress.XtraBars.BarMenuMerge.Replace;
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
            this.skinDropDownItem.Name = "skinDropDownItem";
            // 
            // skinPaletteDropDownItem
            // 
            this.skinPaletteDropDownItem.ActAsDropDown = true;
            this.skinPaletteDropDownItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.skinPaletteDropDownItem.Id = 6;
            this.skinPaletteDropDownItem.Name = "skinPaletteDropDownItem";
            // 
            // barOptionsItem
            // 
            this.barOptionsItem.Caption = "Options";
            this.barOptionsItem.Id = 7;
            this.barOptionsItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("barOptionsItem.ImageOptions.SvgImage")));
            this.barOptionsItem.Name = "barOptionsItem";
            // 
            // fileRibbonPage
            // 
            this.fileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.commonRibbonGroup,
            this.optionsRibbonGroup});
            this.fileRibbonPage.Name = "fileRibbonPage";
            this.fileRibbonPage.Text = "File";
            // 
            // commonRibbonGroup
            // 
            this.commonRibbonGroup.ItemLinks.Add(this.barNewItem);
            this.commonRibbonGroup.ItemLinks.Add(this.barOpenItem);
            this.commonRibbonGroup.ItemLinks.Add(this.barCloseItem);
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
            // homeRibbonPage
            // 
            this.homeRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.ribbonPageGroup2});
            this.homeRibbonPage.Name = "homeRibbonPage";
            this.homeRibbonPage.Text = "Home";
            // 
            // ribbonPageGroup2
            // 
            this.ribbonPageGroup2.Name = "ribbonPageGroup2";
            this.ribbonPageGroup2.Text = "ribbonPageGroup2";
            // 
            // ribbonStatusBar
            // 
            this.ribbonStatusBar.AutoUpdateMergedBars = DevExpress.Utils.DefaultBoolean.True;
            this.ribbonStatusBar.Location = new System.Drawing.Point(0, 625);
            this.ribbonStatusBar.Name = "ribbonStatusBar";
            this.ribbonStatusBar.Ribbon = this.mainRibbonControl;
            this.ribbonStatusBar.Size = new System.Drawing.Size(898, 24);
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
            this.Controls.Add(this.ribbonStatusBar);
            this.Controls.Add(this.mainRibbonControl);
            this.IconOptions.ShowIcon = false;
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.mainRibbonControl;
            this.StatusBar = this.ribbonStatusBar;
            this.Text = "Rizonesoft Verbum";
            this.Load += new System.EventHandler(this.MainForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage fileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup commonRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPage homeRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ribbonPageGroup2;
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
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar;
    }
}

