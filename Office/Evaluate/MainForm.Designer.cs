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
            mainRibbon = new DevExpress.XtraBars.Ribbon.RibbonControl();
            OpenDropdownBtn = new DevExpress.XtraBars.BarButtonItem();
            MruPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            NewBarBtn = new DevExpress.XtraBars.BarButtonItem();
            FileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            CommonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            CoreMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            ((System.ComponentModel.ISupportInitialize)mainRibbon).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).BeginInit();
            ((System.ComponentModel.ISupportInitialize)CoreMdiManager).BeginInit();
            SuspendLayout();
            // 
            // mainRibbon
            // 
            mainRibbon.AllowCustomization = true;
            mainRibbon.ExpandCollapseItem.Id = 0;
            mainRibbon.Items.AddRange(new DevExpress.XtraBars.BarItem[] { mainRibbon.ExpandCollapseItem, OpenDropdownBtn, NewBarBtn });
            mainRibbon.Location = new System.Drawing.Point(0, 0);
            mainRibbon.MaxItemId = 3;
            mainRibbon.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            mainRibbon.Name = "mainRibbon";
            mainRibbon.OptionsMenuMinWidth = 220;
            mainRibbon.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { FileRibbonPage });
            mainRibbon.QuickToolbarItemLinks.Add(NewBarBtn);
            mainRibbon.QuickToolbarItemLinks.Add(OpenDropdownBtn);
            mainRibbon.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office2019;
            mainRibbon.SearchItemPosition = DevExpress.XtraBars.Ribbon.SearchItemPosition.Caption;
            mainRibbon.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            mainRibbon.Size = new System.Drawing.Size(1164, 203);
            // 
            // OpenDropdownBtn
            // 
            OpenDropdownBtn.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            OpenDropdownBtn.Caption = "Open";
            OpenDropdownBtn.DropDownControl = MruPopupMenu;
            OpenDropdownBtn.Id = 1;
            OpenDropdownBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("OpenDropdownBtn.ImageOptions.SvgImage");
            OpenDropdownBtn.Name = "OpenDropdownBtn";
            OpenDropdownBtn.ItemClick += OpenDropdownBtn_ItemClick;
            // 
            // MruPopupMenu
            // 
            MruPopupMenu.Name = "MruPopupMenu";
            MruPopupMenu.Ribbon = mainRibbon;
            // 
            // NewBarBtn
            // 
            NewBarBtn.Caption = "New";
            NewBarBtn.Id = 2;
            NewBarBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("NewBarBtn.ImageOptions.SvgImage");
            NewBarBtn.Name = "NewBarBtn";
            NewBarBtn.ItemClick += NewBarBtn_ItemClick;
            // 
            // FileRibbonPage
            // 
            FileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { CommonRibbonGroup, OptionsRibbonGroup });
            FileRibbonPage.MergeOrder = 0;
            FileRibbonPage.Name = "FileRibbonPage";
            FileRibbonPage.Text = "File";
            // 
            // CommonRibbonGroup
            // 
            CommonRibbonGroup.ItemLinks.Add(NewBarBtn);
            CommonRibbonGroup.ItemLinks.Add(OpenDropdownBtn);
            CommonRibbonGroup.MergeOrder = 0;
            CommonRibbonGroup.Name = "CommonRibbonGroup";
            CommonRibbonGroup.Text = "Common";
            // 
            // OptionsRibbonGroup
            // 
            OptionsRibbonGroup.MergeOrder = 2;
            OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            OptionsRibbonGroup.Text = "Options";
            // 
            // topSpacerPanel
            // 
            topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            topSpacerPanel.Location = new System.Drawing.Point(0, 203);
            topSpacerPanel.Name = "topSpacerPanel";
            topSpacerPanel.Size = new System.Drawing.Size(1164, 10);
            topSpacerPanel.TabIndex = 5;
            // 
            // CoreMdiManager
            // 
            CoreMdiManager.MdiParent = this;
            CoreMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            CoreMdiManager.PageAdded += CoreMdiManager_PageAdded;
            // 
            // MainForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(1164, 674);
            Controls.Add(topSpacerPanel);
            Controls.Add(mainRibbon);
            IconOptions.ShowIcon = false;
            IsMdiContainer = true;
            Name = "MainForm";
            Ribbon = mainRibbon;
            Text = "Evaluate";
            Load += MainForm_Load;
            Shown += MainForm_Shown;
            ((System.ComponentModel.ISupportInitialize)mainRibbon).EndInit();
            ((System.ComponentModel.ISupportInitialize)MruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).EndInit();
            ((System.ComponentModel.ISupportInitialize)CoreMdiManager).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl mainRibbon;
        private DevExpress.XtraBars.Ribbon.RibbonPage FileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup CommonRibbonGroup;
        private DevExpress.XtraEditors.PanelControl topSpacerPanel;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup OptionsRibbonGroup;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager CoreMdiManager;
        private DevExpress.XtraBars.BarButtonItem OpenDropdownBtn;
        private DevExpress.XtraBars.PopupMenu MruPopupMenu;
        private DevExpress.XtraBars.BarButtonItem NewBarBtn;
    }
}

