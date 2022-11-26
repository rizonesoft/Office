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
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.MainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            this.NewBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            this.OpenBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            this.mruPopupMenu = new DevExpress.XtraBars.PopupMenu(this.components);
            this.CloseBarButtonItem = new DevExpress.XtraBars.BarButtonItem();
            this.SkinDropDownButtonItem = new DevExpress.XtraBars.SkinDropDownButtonItem();
            this.PaletteDropDownButtonItem = new DevExpress.XtraBars.SkinPaletteDropDownButtonItem();
            this.fileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.commonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.ribbonPageGroup1 = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.LicenseRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.MainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.MainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mruPopupMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // MainRibbonControl
            // 
            this.MainRibbonControl.ExpandCollapseItem.Id = 0;
            this.MainRibbonControl.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.MainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.MainRibbonControl.ExpandCollapseItem,
            this.MainRibbonControl.SearchEditItem,
            this.NewBarButtonItem,
            this.OpenBarButtonItem,
            this.CloseBarButtonItem,
            this.SkinDropDownButtonItem,
            this.PaletteDropDownButtonItem});
            this.MainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.MainRibbonControl.MaxItemId = 7;
            this.MainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.MainRibbonControl.Name = "MainRibbonControl";
            this.MainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage});
            this.MainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.MainRibbonControl.Size = new System.Drawing.Size(898, 160);
            this.MainRibbonControl.StatusBar = this.MainRibbonStatusBar;
            this.MainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.MainRibbonControl_Merge);
            // 
            // NewBarButtonItem
            // 
            this.NewBarButtonItem.Caption = "New";
            this.NewBarButtonItem.Id = 1;
            this.NewBarButtonItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("NewBarButtonItem.ImageOptions.SvgImage")));
            this.NewBarButtonItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.N));
            this.NewBarButtonItem.Name = "NewBarButtonItem";
            this.NewBarButtonItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.NewBarButtonItem_ItemClick);
            // 
            // OpenBarButtonItem
            // 
            this.OpenBarButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.OpenBarButtonItem.Caption = "Open";
            this.OpenBarButtonItem.DropDownControl = this.mruPopupMenu;
            this.OpenBarButtonItem.Id = 2;
            this.OpenBarButtonItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("OpenBarButtonItem.ImageOptions.SvgImage")));
            this.OpenBarButtonItem.Name = "OpenBarButtonItem";
            this.OpenBarButtonItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.OpenBarButtonItem_ItemClick);
            // 
            // mruPopupMenu
            // 
            this.mruPopupMenu.Name = "mruPopupMenu";
            this.mruPopupMenu.Ribbon = this.MainRibbonControl;
            // 
            // CloseBarButtonItem
            // 
            this.CloseBarButtonItem.Caption = "Close";
            this.CloseBarButtonItem.Id = 3;
            this.CloseBarButtonItem.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("CloseBarButtonItem.ImageOptions.SvgImage")));
            this.CloseBarButtonItem.Name = "CloseBarButtonItem";
            // 
            // SkinDropDownButtonItem
            // 
            this.SkinDropDownButtonItem.ActAsDropDown = true;
            this.SkinDropDownButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.SkinDropDownButtonItem.Id = 4;
            this.SkinDropDownButtonItem.Name = "SkinDropDownButtonItem";
            // 
            // PaletteDropDownButtonItem
            // 
            this.PaletteDropDownButtonItem.ActAsDropDown = true;
            this.PaletteDropDownButtonItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            this.PaletteDropDownButtonItem.Id = 5;
            this.PaletteDropDownButtonItem.Name = "PaletteDropDownButtonItem";
            // 
            // fileRibbonPage
            // 
            this.fileRibbonPage.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.fileRibbonPage.Appearance.Options.UseFont = true;
            this.fileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.commonRibbonGroup,
            this.ribbonPageGroup1,
            this.OptionsRibbonGroup,
            this.LicenseRibbonGroup});
            this.fileRibbonPage.Name = "fileRibbonPage";
            this.fileRibbonPage.Text = "File";
            // 
            // commonRibbonGroup
            // 
            this.commonRibbonGroup.ItemLinks.Add(this.NewBarButtonItem);
            this.commonRibbonGroup.ItemLinks.Add(this.OpenBarButtonItem);
            this.commonRibbonGroup.ItemLinks.Add(this.CloseBarButtonItem);
            this.commonRibbonGroup.Name = "commonRibbonGroup";
            this.commonRibbonGroup.Text = "Common";
            // 
            // ribbonPageGroup1
            // 
            this.ribbonPageGroup1.Name = "ribbonPageGroup1";
            this.ribbonPageGroup1.Text = "Info";
            // 
            // OptionsRibbonGroup
            // 
            this.OptionsRibbonGroup.ItemLinks.Add(this.SkinDropDownButtonItem);
            this.OptionsRibbonGroup.ItemLinks.Add(this.PaletteDropDownButtonItem);
            this.OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            this.OptionsRibbonGroup.Text = "Options";
            // 
            // LicenseRibbonGroup
            // 
            this.LicenseRibbonGroup.Name = "LicenseRibbonGroup";
            this.LicenseRibbonGroup.Text = "Registration";
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
            this.mainTabbedMdiManager.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.mainTabbedMdiManager.Appearance.Options.UseFont = true;
            this.mainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InActiveTabPageHeader;
            this.mainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
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
            // 
            // MainForm
            // 
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
            this.Text = "Rizonesoft ";
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
    }
}

