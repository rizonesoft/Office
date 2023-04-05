namespace Rizonesoft.Office.Reader
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
            mainRibbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            barOpenItem = new DevExpress.XtraBars.BarButtonItem();
            mruPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            viewerRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            filePageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonStatusBar1 = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)mainRibbonControl).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mainTabbedMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).BeginInit();
            SuspendLayout();
            // 
            // mainRibbonControl
            // 
            mainRibbonControl.AllowContentChangeAnimation = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.AutoUpdateMergedRibbons = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(45, 49, 45, 49);
            mainRibbonControl.ExpandCollapseItem.Id = 0;
            mainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] { mainRibbonControl.ExpandCollapseItem, mainRibbonControl.SearchEditItem, barOpenItem });
            mainRibbonControl.Location = new System.Drawing.Point(0, 0);
            mainRibbonControl.Margin = new System.Windows.Forms.Padding(4);
            mainRibbonControl.MaxItemId = 2;
            mainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            mainRibbonControl.Name = "mainRibbonControl";
            mainRibbonControl.OptionsMenuMinWidth = 495;
            mainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { viewerRibbonPage });
            mainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            mainRibbonControl.ShowDisplayOptionsMenuButton = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.ShowExpandCollapseButton = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.ShowItemCaptionsInCaptionBar = true;
            mainRibbonControl.ShowItemCaptionsInPageHeader = true;
            mainRibbonControl.ShowItemCaptionsInQAT = true;
            mainRibbonControl.ShowMoreCommandsButton = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.ShowPageHeadersInFormCaption = DevExpress.Utils.DefaultBoolean.True;
            mainRibbonControl.ShowSearchItem = true;
            mainRibbonControl.Size = new System.Drawing.Size(1490, 292);
            mainRibbonControl.StatusBar = ribbonStatusBar1;
            mainRibbonControl.Merge += MainRibbonControl_Merge;
            // 
            // barOpenItem
            // 
            barOpenItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            barOpenItem.Caption = "Open";
            barOpenItem.DropDownControl = mruPopupMenu;
            barOpenItem.Id = 1;
            barOpenItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("barOpenItem.ImageOptions.SvgImage");
            barOpenItem.Name = "barOpenItem";
            barOpenItem.ItemClick += barOpenItem_ItemClick;
            // 
            // mruPopupMenu
            // 
            mruPopupMenu.Name = "mruPopupMenu";
            mruPopupMenu.Ribbon = mainRibbonControl;
            // 
            // viewerRibbonPage
            // 
            viewerRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { filePageGroup });
            viewerRibbonPage.Name = "viewerRibbonPage";
            viewerRibbonPage.Text = "PDF Viewer";
            // 
            // filePageGroup
            // 
            filePageGroup.ItemLinks.Add(barOpenItem);
            filePageGroup.Name = "filePageGroup";
            filePageGroup.Text = "File";
            // 
            // ribbonStatusBar1
            // 
            ribbonStatusBar1.Location = new System.Drawing.Point(0, 933);
            ribbonStatusBar1.Margin = new System.Windows.Forms.Padding(4);
            ribbonStatusBar1.Name = "ribbonStatusBar1";
            ribbonStatusBar1.Ribbon = mainRibbonControl;
            ribbonStatusBar1.Size = new System.Drawing.Size(1490, 55);
            // 
            // mainTabbedMdiManager
            // 
            mainTabbedMdiManager.AppearancePage.Header.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            mainTabbedMdiManager.AppearancePage.Header.Options.UseFont = true;
            mainTabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.Preview;
            mainTabbedMdiManager.HeaderButtons = DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next | DevExpress.XtraTab.TabButtons.Close | DevExpress.XtraTab.TabButtons.Default;
            mainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            mainTabbedMdiManager.MdiParent = this;
            mainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InActiveTabPageHeaderAndOnMouseHover;
            mainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            mainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            // 
            // topSpacerPanel
            // 
            topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            topSpacerPanel.Location = new System.Drawing.Point(0, 292);
            topSpacerPanel.Margin = new System.Windows.Forms.Padding(4);
            topSpacerPanel.Name = "topSpacerPanel";
            topSpacerPanel.Size = new System.Drawing.Size(1490, 8);
            topSpacerPanel.TabIndex = 11;
            // 
            // MainForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(9F, 21F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(1490, 988);
            Controls.Add(topSpacerPanel);
            Controls.Add(ribbonStatusBar1);
            Controls.Add(mainRibbonControl);
            Font = new System.Drawing.Font("Segoe UI", 8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            IconOptions.ShowIcon = false;
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("MainForm.IconOptions.SvgImage");
            IsMdiContainer = true;
            Margin = new System.Windows.Forms.Padding(4);
            Name = "MainForm";
            Ribbon = mainRibbonControl;
            StatusBar = ribbonStatusBar1;
            Text = "Rizonesoft Reader";
            Load += MainForm_Load;
            ((System.ComponentModel.ISupportInitialize)mainRibbonControl).EndInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)mainTabbedMdiManager).EndInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage viewerRibbonPage;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraEditors.PanelControl topSpacerPanel;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar1;
        private DevExpress.XtraBars.BarButtonItem barOpenItem;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup filePageGroup;
        private DevExpress.XtraBars.PopupMenu mruPopupMenu;
    }
}

