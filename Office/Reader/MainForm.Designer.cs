namespace Rizonesoft.Office.Reader
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
            this.viewerRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.ribbonStatusBar1 = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.bottomSpacerPannel = new DevExpress.XtraEditors.PanelControl();
            this.rightSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            this.leftSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            this.topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            this.pdfToolsPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.bottomSpacerPannel)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.rightSpacerPanel)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.leftSpacerPanel)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.topSpacerPanel)).BeginInit();
            this.SuspendLayout();
            // 
            // mainRibbonControl
            // 
            this.mainRibbonControl.AllowContentChangeAnimation = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.AutoUpdateMergedRibbons = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ExpandCollapseItem.Id = 0;
            this.mainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.mainRibbonControl.ExpandCollapseItem,
            this.mainRibbonControl.SearchEditItem});
            this.mainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.mainRibbonControl.MaxItemId = 1;
            this.mainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.mainRibbonControl.Name = "mainRibbonControl";
            this.mainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.viewerRibbonPage});
            this.mainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.mainRibbonControl.ShowDisplayOptionsMenuButton = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowExpandCollapseButton = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowItemCaptionsInCaptionBar = true;
            this.mainRibbonControl.ShowItemCaptionsInPageHeader = true;
            this.mainRibbonControl.ShowItemCaptionsInQAT = true;
            this.mainRibbonControl.ShowMoreCommandsButton = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowPageHeadersInFormCaption = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ShowSearchItem = true;
            this.mainRibbonControl.Size = new System.Drawing.Size(993, 158);
            this.mainRibbonControl.StatusBar = this.ribbonStatusBar1;
            this.mainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.MainRibbonControl_Merge);
            // 
            // viewerRibbonPage
            // 
            this.viewerRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.pdfToolsPageGroup});
            this.viewerRibbonPage.Name = "viewerRibbonPage";
            this.viewerRibbonPage.Text = "PDF Viewer";
            // 
            // ribbonStatusBar1
            // 
            this.ribbonStatusBar1.Location = new System.Drawing.Point(0, 588);
            this.ribbonStatusBar1.Name = "ribbonStatusBar1";
            this.ribbonStatusBar1.Ribbon = this.mainRibbonControl;
            this.ribbonStatusBar1.Size = new System.Drawing.Size(993, 24);
            // 
            // mainTabbedMdiManager
            // 
            this.mainTabbedMdiManager.AppearancePage.Header.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.mainTabbedMdiManager.AppearancePage.Header.Options.UseFont = true;
            this.mainTabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.Preview;
            this.mainTabbedMdiManager.HeaderButtons = ((DevExpress.XtraTab.TabButtons)((((DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next) 
            | DevExpress.XtraTab.TabButtons.Close) 
            | DevExpress.XtraTab.TabButtons.Default)));
            this.mainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.Always;
            this.mainTabbedMdiManager.MdiParent = this;
            this.mainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InActiveTabPageHeaderAndOnMouseHover;
            this.mainTabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            // 
            // bottomSpacerPannel
            // 
            this.bottomSpacerPannel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.bottomSpacerPannel.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.bottomSpacerPannel.Location = new System.Drawing.Point(5, 583);
            this.bottomSpacerPannel.Name = "bottomSpacerPannel";
            this.bottomSpacerPannel.Size = new System.Drawing.Size(983, 5);
            this.bottomSpacerPannel.TabIndex = 14;
            // 
            // rightSpacerPanel
            // 
            this.rightSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.rightSpacerPanel.Dock = System.Windows.Forms.DockStyle.Right;
            this.rightSpacerPanel.Location = new System.Drawing.Point(988, 163);
            this.rightSpacerPanel.Name = "rightSpacerPanel";
            this.rightSpacerPanel.Size = new System.Drawing.Size(5, 425);
            this.rightSpacerPanel.TabIndex = 13;
            // 
            // leftSpacerPanel
            // 
            this.leftSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.leftSpacerPanel.Dock = System.Windows.Forms.DockStyle.Left;
            this.leftSpacerPanel.Location = new System.Drawing.Point(0, 163);
            this.leftSpacerPanel.Name = "leftSpacerPanel";
            this.leftSpacerPanel.Size = new System.Drawing.Size(5, 425);
            this.leftSpacerPanel.TabIndex = 12;
            // 
            // topSpacerPanel
            // 
            this.topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            this.topSpacerPanel.Location = new System.Drawing.Point(0, 158);
            this.topSpacerPanel.Name = "topSpacerPanel";
            this.topSpacerPanel.Size = new System.Drawing.Size(993, 5);
            this.topSpacerPanel.TabIndex = 11;
            // 
            // pdfToolsPageGroup
            // 
            this.pdfToolsPageGroup.Name = "pdfToolsPageGroup";
            this.pdfToolsPageGroup.Text = "PDF Tools";
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(993, 612);
            this.Controls.Add(this.bottomSpacerPannel);
            this.Controls.Add(this.rightSpacerPanel);
            this.Controls.Add(this.leftSpacerPanel);
            this.Controls.Add(this.topSpacerPanel);
            this.Controls.Add(this.ribbonStatusBar1);
            this.Controls.Add(this.mainRibbonControl);
            this.IconOptions.ShowIcon = false;
            this.IconOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("MainForm.IconOptions.SvgImage")));
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.mainRibbonControl;
            this.StatusBar = this.ribbonStatusBar1;
            this.Text = "Rizonesoft Reader";
            this.Load += new System.EventHandler(this.MainForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.bottomSpacerPannel)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.rightSpacerPanel)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.leftSpacerPanel)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.topSpacerPanel)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage viewerRibbonPage;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraEditors.PanelControl bottomSpacerPannel;
        private DevExpress.XtraEditors.PanelControl rightSpacerPanel;
        private DevExpress.XtraEditors.PanelControl leftSpacerPanel;
        private DevExpress.XtraEditors.PanelControl topSpacerPanel;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar1;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup pdfToolsPageGroup;
    }
}

