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
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.panelControl1 = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).BeginInit();
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
            // 
            // viewerRibbonPage
            // 
            this.viewerRibbonPage.Name = "viewerRibbonPage";
            this.viewerRibbonPage.Text = "PDF Viewer";
            // 
            // mainTabbedMdiManager
            // 
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
            // panelControl1
            // 
            this.panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelControl1.Location = new System.Drawing.Point(0, 158);
            this.panelControl1.Name = "panelControl1";
            this.panelControl1.Size = new System.Drawing.Size(993, 13);
            this.panelControl1.TabIndex = 2;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(993, 612);
            this.Controls.Add(this.panelControl1);
            this.Controls.Add(this.mainRibbonControl);
            this.IconOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("MainForm.IconOptions.SvgImage")));
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.mainRibbonControl;
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage viewerRibbonPage;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraEditors.PanelControl panelControl1;
    }
}

