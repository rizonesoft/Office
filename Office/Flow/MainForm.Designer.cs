namespace Rizonesoft.Office.Flow
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
            this.barButtonItem1 = new DevExpress.XtraBars.BarButtonItem();
            this.barButtonItem2 = new DevExpress.XtraBars.BarButtonItem();
            this.barSubItem1 = new DevExpress.XtraBars.BarSubItem();
            this.ribbonPage1 = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.homeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.insertRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.designRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.viewRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.mainRibbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.mainTabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainRibbonControl
            // 
            this.mainRibbonControl.AutoUpdateMergedRibbons = DevExpress.Utils.DefaultBoolean.True;
            this.mainRibbonControl.ExpandCollapseItem.Id = 0;
            this.mainRibbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.mainRibbonControl.ExpandCollapseItem,
            this.mainRibbonControl.SearchEditItem,
            this.barButtonItem1,
            this.barButtonItem2,
            this.barSubItem1});
            this.mainRibbonControl.Location = new System.Drawing.Point(0, 0);
            this.mainRibbonControl.MaxItemId = 4;
            this.mainRibbonControl.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            this.mainRibbonControl.Name = "mainRibbonControl";
            this.mainRibbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.ribbonPage1,
            this.homeRibbonPage,
            this.insertRibbonPage,
            this.designRibbonPage,
            this.viewRibbonPage});
            this.mainRibbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            this.mainRibbonControl.Size = new System.Drawing.Size(955, 158);
            this.mainRibbonControl.StatusBar = this.mainRibbonStatusBar;
            this.mainRibbonControl.Merge += new DevExpress.XtraBars.Ribbon.RibbonMergeEventHandler(this.mainRibbonControl_Merge);
            // 
            // barButtonItem1
            // 
            this.barButtonItem1.Caption = "New";
            this.barButtonItem1.Id = 1;
            this.barButtonItem1.MergeType = DevExpress.XtraBars.BarMenuMerge.Replace;
            this.barButtonItem1.Name = "barButtonItem1";
            // 
            // barButtonItem2
            // 
            this.barButtonItem2.Caption = "New";
            this.barButtonItem2.Id = 2;
            this.barButtonItem2.Name = "barButtonItem2";
            // 
            // barSubItem1
            // 
            this.barSubItem1.Caption = "barSubItem1";
            this.barSubItem1.Id = 3;
            this.barSubItem1.MenuCaption = "New";
            this.barSubItem1.Name = "barSubItem1";
            // 
            // ribbonPage1
            // 
            this.ribbonPage1.Name = "ribbonPage1";
            this.ribbonPage1.Text = "File";
            // 
            // homeRibbonPage
            // 
            this.homeRibbonPage.Name = "homeRibbonPage";
            this.homeRibbonPage.Text = "Home";
            // 
            // insertRibbonPage
            // 
            this.insertRibbonPage.Name = "insertRibbonPage";
            this.insertRibbonPage.Text = "Insert";
            // 
            // designRibbonPage
            // 
            this.designRibbonPage.Name = "designRibbonPage";
            this.designRibbonPage.Text = "Design";
            // 
            // viewRibbonPage
            // 
            this.viewRibbonPage.Name = "viewRibbonPage";
            this.viewRibbonPage.Text = "View";
            // 
            // mainRibbonStatusBar
            // 
            this.mainRibbonStatusBar.AutoUpdateMergedBars = DevExpress.Utils.DefaultBoolean.False;
            this.mainRibbonStatusBar.Location = new System.Drawing.Point(0, 616);
            this.mainRibbonStatusBar.Name = "mainRibbonStatusBar";
            this.mainRibbonStatusBar.Ribbon = this.mainRibbonControl;
            this.mainRibbonStatusBar.Size = new System.Drawing.Size(955, 24);
            // 
            // mainTabbedMdiManager
            // 
            this.mainTabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InAllTabPagesAndTabControlHeader;
            this.mainTabbedMdiManager.CloseTabOnMiddleClick = DevExpress.XtraTabbedMdi.CloseTabOnMiddleClick.Never;
            this.mainTabbedMdiManager.HeaderButtons = ((DevExpress.XtraTab.TabButtons)((((DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next) 
            | DevExpress.XtraTab.TabButtons.Close) 
            | DevExpress.XtraTab.TabButtons.Default)));
            this.mainTabbedMdiManager.HeaderButtonsShowMode = DevExpress.XtraTab.TabButtonShowMode.WhenNeeded;
            this.mainTabbedMdiManager.HeaderOrientation = DevExpress.XtraTab.TabOrientation.Horizontal;
            this.mainTabbedMdiManager.MdiParent = this;
            this.mainTabbedMdiManager.PinPageButtonShowMode = DevExpress.XtraTab.PinPageButtonShowMode.InActiveTabPageHeaderAndOnMouseHover;
            this.mainTabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            this.mainTabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(955, 640);
            this.Controls.Add(this.mainRibbonStatusBar);
            this.Controls.Add(this.mainRibbonControl);
            this.IconOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("MainForm.IconOptions.SvgImage")));
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Ribbon = this.mainRibbonControl;
            this.StatusBar = this.mainRibbonStatusBar;
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.mainRibbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.mainTabbedMdiManager)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbonControl;
        private DevExpress.XtraBars.Ribbon.RibbonPage ribbonPage1;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainTabbedMdiManager;
        private DevExpress.XtraBars.BarButtonItem barButtonItem1;
        private DevExpress.XtraBars.BarButtonItem barButtonItem2;
        private DevExpress.XtraBars.BarSubItem barSubItem1;
        private DevExpress.XtraBars.Ribbon.RibbonPage homeRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPage insertRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPage designRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPage viewRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar mainRibbonStatusBar;
    }
}

