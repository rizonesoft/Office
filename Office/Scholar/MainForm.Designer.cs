namespace Rizonesoft.Office.Scholar
{
    sealed partial class MainForm
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
            ribbonMain = new DevExpress.XtraBars.Ribbon.RibbonControl();
            OpenBarItem = new DevExpress.XtraBars.BarButtonItem();
            mruPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            CompressBarButton = new DevExpress.XtraBars.BarButtonItem();
            HomeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            FileRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonPage1 = new DevExpress.XtraBars.Ribbon.RibbonPage();
            ToolsRibPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            mainMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            panelControl1 = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)ribbonMain).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mainMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)panelControl1).BeginInit();
            SuspendLayout();
            // 
            // ribbonMain
            // 
            ribbonMain.AllowCustomization = true;
            ribbonMain.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(45, 49, 45, 49);
            ribbonMain.ExpandCollapseItem.Id = 0;
            ribbonMain.Items.AddRange(new DevExpress.XtraBars.BarItem[] { ribbonMain.ExpandCollapseItem, OpenBarItem, CompressBarButton });
            ribbonMain.Location = new System.Drawing.Point(0, 0);
            ribbonMain.Margin = new System.Windows.Forms.Padding(4);
            ribbonMain.MaxItemId = 8;
            ribbonMain.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            ribbonMain.Name = "ribbonMain";
            ribbonMain.OptionsMenuMinWidth = 495;
            ribbonMain.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { HomeRibbonPage, ribbonPage1 });
            ribbonMain.QuickToolbarItemLinks.Add(OpenBarItem);
            ribbonMain.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office365;
            ribbonMain.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            ribbonMain.Size = new System.Drawing.Size(981, 201);
            // 
            // OpenBarItem
            // 
            OpenBarItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            OpenBarItem.Caption = "Open";
            OpenBarItem.DropDownControl = mruPopupMenu;
            OpenBarItem.Id = 5;
            OpenBarItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("OpenBarItem.ImageOptions.SvgImage");
            OpenBarItem.Name = "OpenBarItem";
            OpenBarItem.ItemClick += OpenBarItem_ItemClick;
            // 
            // mruPopupMenu
            // 
            mruPopupMenu.Name = "mruPopupMenu";
            mruPopupMenu.Ribbon = ribbonMain;
            // 
            // CompressBarButton
            // 
            CompressBarButton.Caption = "Compress";
            CompressBarButton.Id = 7;
            CompressBarButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CompressBarButton.ImageOptions.SvgImage");
            CompressBarButton.Name = "CompressBarButton";
            CompressBarButton.ItemClick += CompressBarButton_ItemClick;
            // 
            // HomeRibbonPage
            // 
            HomeRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { FileRibbonGroup, OptionsRibbonGroup });
            HomeRibbonPage.MergeOrder = 1;
            HomeRibbonPage.Name = "HomeRibbonPage";
            HomeRibbonPage.Text = "Home";
            // 
            // FileRibbonGroup
            // 
            FileRibbonGroup.ItemLinks.Add(OpenBarItem);
            FileRibbonGroup.MergeOrder = 0;
            FileRibbonGroup.Name = "FileRibbonGroup";
            FileRibbonGroup.Text = "File";
            // 
            // OptionsRibbonGroup
            // 
            OptionsRibbonGroup.MergeOrder = 99;
            OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            OptionsRibbonGroup.Text = "Options";
            // 
            // ribbonPage1
            // 
            ribbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { ToolsRibPageGroup });
            ribbonPage1.Name = "ribbonPage1";
            ribbonPage1.Text = "Tools";
            // 
            // ToolsRibPageGroup
            // 
            ToolsRibPageGroup.ItemLinks.Add(CompressBarButton);
            ToolsRibPageGroup.Name = "ToolsRibPageGroup";
            ToolsRibPageGroup.Text = "Tools";
            // 
            // mainMdiManager
            // 
            mainMdiManager.MdiParent = null;
            // 
            // panelControl1
            // 
            panelControl1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            panelControl1.Location = new System.Drawing.Point(0, 201);
            panelControl1.Name = "panelControl1";
            panelControl1.Size = new System.Drawing.Size(981, 11);
            panelControl1.TabIndex = 2;
            // 
            // MainForm
            // 
            AllowDrop = true;
            AllowFormGlass = DevExpress.Utils.DefaultBoolean.True;
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(981, 1071);
            Controls.Add(panelControl1);
            Controls.Add(ribbonMain);
            Font = new System.Drawing.Font("Segoe UI", 8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            IconOptions.ShowIcon = false;
            IsMdiContainer = true;
            Margin = new System.Windows.Forms.Padding(4);
            Name = "MainForm";
            Ribbon = ribbonMain;
            Load += MainForm_Load;
            Shown += MainForm_Shown;
            ((System.ComponentModel.ISupportInitialize)ribbonMain).EndInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)mainMdiManager).EndInit();
            ((System.ComponentModel.ISupportInitialize)panelControl1).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl ribbonMain;
        private DevExpress.XtraBars.Ribbon.RibbonPage HomeRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup OptionsRibbonGroup;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager mainMdiManager;
        private DevExpress.XtraEditors.PanelControl panelControl1;
        private DevExpress.XtraBars.BarButtonItem OpenBarItem;
        private DevExpress.XtraBars.PopupMenu mruPopupMenu;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup FileRibbonGroup;
        private DevExpress.XtraBars.BarButtonItem CompressBarButton;
        private DevExpress.XtraBars.Ribbon.RibbonPage ribbonPage1;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ToolsRibPageGroup;
    }
}

