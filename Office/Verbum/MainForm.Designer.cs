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
            components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            DevExpress.XtraEditors.Controls.EditorButtonImageOptions editorButtonImageOptions1 = new DevExpress.XtraEditors.Controls.EditorButtonImageOptions();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject1 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject2 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject3 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject4 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.XtraEditors.Controls.EditorButtonImageOptions editorButtonImageOptions2 = new DevExpress.XtraEditors.Controls.EditorButtonImageOptions();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject5 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject6 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject7 = new DevExpress.Utils.SerializableAppearanceObject();
            DevExpress.Utils.SerializableAppearanceObject serializableAppearanceObject8 = new DevExpress.Utils.SerializableAppearanceObject();
            MainRibbon = new DevExpress.XtraBars.Ribbon.RibbonControl();
            NewBarBtn = new DevExpress.XtraBars.BarButtonItem();
            OpenDropdownBtn = new DevExpress.XtraBars.BarButtonItem();
            MruPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            CloseSaveBarItem = new DevExpress.XtraBars.BarButtonItem();
            MdiChildrenListItem = new DevExpress.XtraBars.BarMdiChildrenListItem();
            TimeStatusButton = new DevExpress.XtraBars.BarButtonItem();
            CloseBtn = new DevExpress.XtraBars.BarButtonItem();
            CloseSaveBtn = new DevExpress.XtraBars.BarButtonItem();
            TableToolsRibbonCat = new DevExpress.XtraBars.Ribbon.RibbonPageCategory();
            TableDesignRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            FileRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            CommonRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ExportToRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            InfoRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ribbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            CoreMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            topSpacerPanel = new DevExpress.XtraEditors.PanelControl();
            sharedDictionaryStore = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(components);
            repositoryItemRibbonSearchEdit1 = new DevExpress.XtraBars.Ribbon.Internal.RepositoryItemRibbonSearchEdit();
            ((System.ComponentModel.ISupportInitialize)MainRibbon).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)CoreMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).BeginInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemRibbonSearchEdit1).BeginInit();
            SuspendLayout();
            // 
            // MainRibbon
            // 
            MainRibbon.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(33, 34, 33, 34);
            MainRibbon.ExpandCollapseItem.Id = 0;
            MainRibbon.Items.AddRange(new DevExpress.XtraBars.BarItem[] { MainRibbon.ExpandCollapseItem, NewBarBtn, OpenDropdownBtn, CloseSaveBarItem, MdiChildrenListItem, TimeStatusButton, CloseBtn, CloseSaveBtn });
            MainRibbon.Location = new System.Drawing.Point(0, 0);
            MainRibbon.Margin = new System.Windows.Forms.Padding(2);
            MainRibbon.MaxItemId = 18;
            MainRibbon.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            MainRibbon.Name = "MainRibbon";
            MainRibbon.OptionsMenuMinWidth = 220;
            MainRibbon.OptionsTouch.ShowTouchUISelectorInQAT = true;
            MainRibbon.OptionsTouch.ShowTouchUISelectorVisibilityItemInQATMenu = true;
            MainRibbon.PageCategories.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageCategory[] { TableToolsRibbonCat });
            MainRibbon.PageHeaderItemLinks.Add(MdiChildrenListItem);
            MainRibbon.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { FileRibbonPage });
            MainRibbon.QuickToolbarItemLinks.Add(NewBarBtn);
            MainRibbon.QuickToolbarItemLinks.Add(OpenDropdownBtn);
            MainRibbon.QuickToolbarItemLinks.Add(CloseSaveBarItem);
            MainRibbon.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office365;
            MainRibbon.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            MainRibbon.Size = new System.Drawing.Size(983, 203);
            MainRibbon.StatusBar = ribbonStatusBar;
            MainRibbon.Merge += MainRibbon_Merge;
            // 
            // NewBarBtn
            // 
            NewBarBtn.Caption = "New";
            NewBarBtn.Id = 1;
            NewBarBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("NewBarBtn.ImageOptions.SvgImage");
            NewBarBtn.Name = "NewBarBtn";
            NewBarBtn.ItemClick += NewBarBtn_ItemClick;
            // 
            // OpenDropdownBtn
            // 
            OpenDropdownBtn.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            OpenDropdownBtn.Caption = "Open";
            OpenDropdownBtn.DropDownControl = MruPopupMenu;
            OpenDropdownBtn.Id = 2;
            OpenDropdownBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("OpenDropdownBtn.ImageOptions.SvgImage");
            OpenDropdownBtn.Name = "OpenDropdownBtn";
            OpenDropdownBtn.ItemClick += OpenDropdownBtn_ItemClick;
            // 
            // MruPopupMenu
            // 
            MruPopupMenu.MenuCaption = "Recent Documents";
            MruPopupMenu.Name = "MruPopupMenu";
            MruPopupMenu.Ribbon = MainRibbon;
            MruPopupMenu.ShowCaption = true;
            // 
            // CloseSaveBarItem
            // 
            CloseSaveBarItem.Caption = "Save and Close";
            CloseSaveBarItem.Id = 3;
            CloseSaveBarItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseSaveBarItem.ImageOptions.SvgImage");
            CloseSaveBarItem.Name = "CloseSaveBarItem";
            CloseSaveBarItem.RememberLastCommand = true;
            CloseSaveBarItem.ItemClick += CloseDocBarBtn_ItemClick;
            // 
            // MdiChildrenListItem
            // 
            MdiChildrenListItem.Caption = "Documents";
            MdiChildrenListItem.Id = 5;
            MdiChildrenListItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("MdiChildrenListItem.ImageOptions.SvgImage");
            MdiChildrenListItem.MenuCaption = "Documents";
            MdiChildrenListItem.Name = "MdiChildrenListItem";
            MdiChildrenListItem.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText;
            MdiChildrenListItem.ShowMenuCaption = true;
            MdiChildrenListItem.ShowNavigationHeader = DevExpress.Utils.DefaultBoolean.True;
            MdiChildrenListItem.ShowNumbers = false;
            // 
            // TimeStatusButton
            // 
            TimeStatusButton.Alignment = DevExpress.XtraBars.BarItemLinkAlignment.Right;
            TimeStatusButton.Caption = "00:00";
            TimeStatusButton.Id = 6;
            TimeStatusButton.MergeOrder = 99;
            TimeStatusButton.Name = "TimeStatusButton";
            TimeStatusButton.ItemClick += TimeStatusButton_ItemClick;
            // 
            // CloseBtn
            // 
            CloseBtn.Caption = "Close";
            CloseBtn.Id = 7;
            CloseBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseBtn.ImageOptions.SvgImage");
            CloseBtn.Name = "CloseBtn";
            // 
            // CloseSaveBtn
            // 
            CloseSaveBtn.Caption = "Save and Close";
            CloseSaveBtn.Id = 8;
            CloseSaveBtn.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseSaveBtn.ImageOptions.SvgImage");
            CloseSaveBtn.Name = "CloseSaveBtn";
            // 
            // TableToolsRibbonCat
            // 
            TableToolsRibbonCat.Name = "TableToolsRibbonCat";
            TableToolsRibbonCat.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { TableDesignRibbonPage });
            TableToolsRibbonCat.Text = "Table Tools";
            TableToolsRibbonCat.Visible = false;
            // 
            // TableDesignRibbonPage
            // 
            TableDesignRibbonPage.Name = "TableDesignRibbonPage";
            TableDesignRibbonPage.Text = "Design";
            TableDesignRibbonPage.Visible = false;
            // 
            // FileRibbonPage
            // 
            FileRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { CommonRibbonGroup, ExportToRibbonGroup, InfoRibbonGroup, OptionsRibbonGroup });
            FileRibbonPage.MergeOrder = 1;
            FileRibbonPage.Name = "FileRibbonPage";
            FileRibbonPage.Text = "File";
            // 
            // CommonRibbonGroup
            // 
            CommonRibbonGroup.ItemLinks.Add(NewBarBtn);
            CommonRibbonGroup.ItemLinks.Add(OpenDropdownBtn);
            CommonRibbonGroup.ItemLinks.Add(CloseSaveBarItem);
            CommonRibbonGroup.Name = "CommonRibbonGroup";
            CommonRibbonGroup.Text = "Common";
            // 
            // ExportToRibbonGroup
            // 
            ExportToRibbonGroup.Name = "ExportToRibbonGroup";
            ExportToRibbonGroup.Text = "Export To";
            // 
            // InfoRibbonGroup
            // 
            InfoRibbonGroup.Name = "InfoRibbonGroup";
            InfoRibbonGroup.Text = "Info";
            // 
            // OptionsRibbonGroup
            // 
            OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            OptionsRibbonGroup.Text = "Options";
            // 
            // ribbonStatusBar
            // 
            ribbonStatusBar.ItemLinks.Add(TimeStatusButton, true);
            ribbonStatusBar.Location = new System.Drawing.Point(0, 582);
            ribbonStatusBar.Margin = new System.Windows.Forms.Padding(2);
            ribbonStatusBar.Name = "ribbonStatusBar";
            ribbonStatusBar.Ribbon = MainRibbon;
            ribbonStatusBar.Size = new System.Drawing.Size(983, 37);
            // 
            // CoreMdiManager
            // 
            CoreMdiManager.MdiParent = this;
            CoreMdiManager.PageAdded += CoreMdiManager_PageAdded;
            CoreMdiManager.PageRemoved += CoreMdiManager_PageRemoved;
            // 
            // topSpacerPanel
            // 
            topSpacerPanel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            topSpacerPanel.Dock = System.Windows.Forms.DockStyle.Top;
            topSpacerPanel.Location = new System.Drawing.Point(0, 203);
            topSpacerPanel.Name = "topSpacerPanel";
            topSpacerPanel.Size = new System.Drawing.Size(983, 10);
            topSpacerPanel.TabIndex = 4;
            // 
            // repositoryItemRibbonSearchEdit1
            // 
            repositoryItemRibbonSearchEdit1.AllowFocused = false;
            repositoryItemRibbonSearchEdit1.AutoHeight = false;
            repositoryItemRibbonSearchEdit1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            editorButtonImageOptions1.AllowGlyphSkinning = DevExpress.Utils.DefaultBoolean.True;
            editorButtonImageOptions1.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("editorButtonImageOptions1.SvgImage");
            repositoryItemRibbonSearchEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] { new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Glyph, "", -1, true, true, true, editorButtonImageOptions1, new DevExpress.Utils.KeyShortcut(System.Windows.Forms.Keys.None), serializableAppearanceObject1, serializableAppearanceObject2, serializableAppearanceObject3, serializableAppearanceObject4, "", null, null, DevExpress.Utils.ToolTipAnchor.Default), new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Clear, "", -1, true, false, false, editorButtonImageOptions2, new DevExpress.Utils.KeyShortcut(System.Windows.Forms.Keys.None), serializableAppearanceObject5, serializableAppearanceObject6, serializableAppearanceObject7, serializableAppearanceObject8, "", null, null, DevExpress.Utils.ToolTipAnchor.Default) });
            repositoryItemRibbonSearchEdit1.Name = "repositoryItemRibbonSearchEdit1";
            repositoryItemRibbonSearchEdit1.NullText = "Search";
            // 
            // MainForm
            // 
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(983, 619);
            Controls.Add(topSpacerPanel);
            Controls.Add(ribbonStatusBar);
            Controls.Add(MainRibbon);
            Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            IconOptions.ShowIcon = false;
            IsMdiContainer = true;
            Margin = new System.Windows.Forms.Padding(2);
            Name = "MainForm";
            Ribbon = MainRibbon;
            StatusBar = ribbonStatusBar;
            Text = "MainForm";
            Load += MainForm_Load;
            Shown += MainForm_Shown;
            ((System.ComponentModel.ISupportInitialize)MainRibbon).EndInit();
            ((System.ComponentModel.ISupportInitialize)MruPopupMenu).EndInit();
            ((System.ComponentModel.ISupportInitialize)CoreMdiManager).EndInit();
            ((System.ComponentModel.ISupportInitialize)topSpacerPanel).EndInit();
            ((System.ComponentModel.ISupportInitialize)repositoryItemRibbonSearchEdit1).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl MainRibbon;
        private DevExpress.XtraBars.Ribbon.RibbonPage FileRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup CommonRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager CoreMdiManager;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ExportToRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup InfoRibbonGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup OptionsRibbonGroup;
        private DevExpress.XtraBars.BarButtonItem NewBarBtn;
        private DevExpress.XtraBars.BarButtonItem OpenDropdownBtn;
        private DevExpress.XtraBars.BarButtonItem CloseSaveBarItem;
        private DevExpress.XtraBars.PopupMenu MruPopupMenu;
        private DevExpress.XtraEditors.PanelControl topSpacerPanel;
        private DevExpress.XtraBars.BarMdiChildrenListItem MdiChildrenListItem;
        private DevExpress.XtraBars.BarButtonItem TimeStatusButton;
        private DevExpress.XtraSpellChecker.SharedDictionaryStorage sharedDictionaryStore;
        private DevExpress.XtraBars.BarButtonItem CloseBtn;
        private DevExpress.XtraBars.BarButtonItem CloseSaveBtn;
        private DevExpress.XtraBars.Ribbon.RibbonPageCategory TableToolsRibbonCat;
        private DevExpress.XtraBars.Ribbon.RibbonPage TableDesignRibbonPage;
        private DevExpress.XtraBars.Ribbon.Internal.RepositoryItemRibbonSearchEdit repositoryItemRibbonSearchEdit1;
    }
}