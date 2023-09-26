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
            ExportBarItem = new DevExpress.XtraBars.BarButtonItem();
            exportDropDown = new DevExpress.XtraBars.BarButtonItem();
            exportPopupMenu = new DevExpress.XtraBars.PopupMenu(components);
            exportDocxItem = new DevExpress.XtraBars.BarButtonItem();
            exportXlsItem = new DevExpress.XtraBars.BarButtonItem();
            exportImageItem = new DevExpress.XtraBars.BarButtonItem();
            exportHtmlItem = new DevExpress.XtraBars.BarButtonItem();
            exportXmlItem = new DevExpress.XtraBars.BarButtonItem();
            exportTextItem = new DevExpress.XtraBars.BarButtonItem();
            exportOptionsItem = new DevExpress.XtraBars.BarButtonItem();
            ocrBarCheckItem = new DevExpress.XtraBars.BarButtonItem();
            HomeRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            FileRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ConvertRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            OptionsRibbonGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            ToolsRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            ToolsRibPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            mainMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(components);
            panelControl1 = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)ribbonMain).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mruPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)exportPopupMenu).BeginInit();
            ((System.ComponentModel.ISupportInitialize)mainMdiManager).BeginInit();
            ((System.ComponentModel.ISupportInitialize)panelControl1).BeginInit();
            SuspendLayout();
            // 
            // ribbonMain
            // 
            ribbonMain.AllowCustomization = true;
            ribbonMain.EmptyAreaImageOptions.ImagePadding = new System.Windows.Forms.Padding(40);
            ribbonMain.ExpandCollapseItem.Id = 0;
            ribbonMain.Items.AddRange(new DevExpress.XtraBars.BarItem[] { ribbonMain.ExpandCollapseItem, OpenBarItem, CompressBarButton, ExportBarItem, exportDropDown, exportOptionsItem, ocrBarCheckItem, exportDocxItem, exportXlsItem, exportImageItem, exportHtmlItem, exportXmlItem, exportTextItem });
            ribbonMain.Location = new System.Drawing.Point(0, 0);
            ribbonMain.Margin = new System.Windows.Forms.Padding(4);
            ribbonMain.MaxItemId = 19;
            ribbonMain.MdiMergeStyle = DevExpress.XtraBars.Ribbon.RibbonMdiMergeStyle.Always;
            ribbonMain.Name = "ribbonMain";
            ribbonMain.OptionsMenuMinWidth = 495;
            ribbonMain.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] { HomeRibbonPage, ToolsRibbonPage });
            ribbonMain.QuickToolbarItemLinks.Add(OpenBarItem);
            ribbonMain.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office2019;
            ribbonMain.SearchItemPosition = DevExpress.XtraBars.Ribbon.SearchItemPosition.Caption;
            ribbonMain.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.False;
            ribbonMain.Size = new System.Drawing.Size(981, 158);
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
            // ExportBarItem
            // 
            ExportBarItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            ExportBarItem.Caption = "barButtonItem2";
            ExportBarItem.Id = 9;
            ExportBarItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ExportBarItem.ImageOptions.SvgImage");
            ExportBarItem.Name = "ExportBarItem";
            // 
            // exportDropDown
            // 
            exportDropDown.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.DropDown;
            exportDropDown.Caption = "Export to Docx";
            exportDropDown.DropDownControl = exportPopupMenu;
            exportDropDown.Id = 10;
            exportDropDown.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportDropDown.ImageOptions.SvgImage");
            exportDropDown.Name = "exportDropDown";
            exportDropDown.RememberLastCommand = true;
            // 
            // exportPopupMenu
            // 
            exportPopupMenu.ItemLinks.Add(exportDocxItem);
            exportPopupMenu.ItemLinks.Add(exportXlsItem);
            exportPopupMenu.ItemLinks.Add(exportImageItem);
            exportPopupMenu.ItemLinks.Add(exportHtmlItem);
            exportPopupMenu.ItemLinks.Add(exportXmlItem);
            exportPopupMenu.ItemLinks.Add(exportTextItem);
            exportPopupMenu.MenuDrawMode = DevExpress.XtraBars.MenuDrawMode.LargeImagesTextDescription;
            exportPopupMenu.Name = "exportPopupMenu";
            exportPopupMenu.Ribbon = ribbonMain;
            // 
            // exportDocxItem
            // 
            exportDocxItem.Caption = "Export to Docx";
            exportDocxItem.Description = "Microsoft Word Document";
            exportDocxItem.Id = 13;
            exportDocxItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportDocxItem.ImageOptions.SvgImage");
            exportDocxItem.Name = "exportDocxItem";
            exportDocxItem.Tag = "DOCX";
            // 
            // exportXlsItem
            // 
            exportXlsItem.Caption = "Export to Xls";
            exportXlsItem.Description = "Microsoft Excel Document";
            exportXlsItem.Id = 14;
            exportXlsItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportXlsItem.ImageOptions.SvgImage");
            exportXlsItem.Name = "exportXlsItem";
            exportXlsItem.Tag = "XLS";
            // 
            // exportImageItem
            // 
            exportImageItem.Caption = "Export to Image";
            exportImageItem.Description = "JPEG, PNG, TIFF, BMP, GIF";
            exportImageItem.Id = 15;
            exportImageItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportImageItem.ImageOptions.SvgImage");
            exportImageItem.Name = "exportImageItem";
            exportImageItem.Tag = "Image";
            // 
            // exportHtmlItem
            // 
            exportHtmlItem.Caption = "Export to Html";
            exportHtmlItem.Description = "Hyper Text Markup Language";
            exportHtmlItem.Id = 16;
            exportHtmlItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportHtmlItem.ImageOptions.SvgImage");
            exportHtmlItem.Name = "exportHtmlItem";
            exportHtmlItem.Tag = "HTML";
            // 
            // exportXmlItem
            // 
            exportXmlItem.Caption = "Export to Xml";
            exportXmlItem.Description = "Extensible Markup Language";
            exportXmlItem.Id = 17;
            exportXmlItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportXmlItem.ImageOptions.SvgImage");
            exportXmlItem.Name = "exportXmlItem";
            exportXmlItem.Tag = "XML";
            // 
            // exportTextItem
            // 
            exportTextItem.Caption = "Export to Text";
            exportTextItem.Description = "Plain Text";
            exportTextItem.Id = 18;
            exportTextItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportTextItem.ImageOptions.SvgImage");
            exportTextItem.Name = "exportTextItem";
            exportTextItem.Tag = "TXT";
            // 
            // exportOptionsItem
            // 
            exportOptionsItem.Caption = "Export Options";
            exportOptionsItem.Id = 11;
            exportOptionsItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("exportOptionsItem.ImageOptions.SvgImage");
            exportOptionsItem.Name = "exportOptionsItem";
            exportOptionsItem.ItemClick += ExportOptionsItem_ItemClick;
            // 
            // ocrBarCheckItem
            // 
            ocrBarCheckItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.Check;
            ocrBarCheckItem.Caption = "OCR";
            ocrBarCheckItem.Id = 12;
            ocrBarCheckItem.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ocrBarCheckItem.ImageOptions.SvgImage");
            ocrBarCheckItem.Name = "ocrBarCheckItem";
            // 
            // HomeRibbonPage
            // 
            HomeRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { FileRibbonGroup, ConvertRibbonGroup, OptionsRibbonGroup });
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
            // ConvertRibbonGroup
            // 
            ConvertRibbonGroup.ItemLinks.Add(ocrBarCheckItem, true);
            ConvertRibbonGroup.ItemLinks.Add(exportDropDown, true);
            ConvertRibbonGroup.ItemLinks.Add(exportOptionsItem);
            ConvertRibbonGroup.MergeOrder = 1;
            ConvertRibbonGroup.Name = "ConvertRibbonGroup";
            ConvertRibbonGroup.Text = "Convert";
            // 
            // OptionsRibbonGroup
            // 
            OptionsRibbonGroup.MergeOrder = 99;
            OptionsRibbonGroup.Name = "OptionsRibbonGroup";
            OptionsRibbonGroup.Text = "Options";
            // 
            // ToolsRibbonPage
            // 
            ToolsRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] { ToolsRibPageGroup });
            ToolsRibbonPage.MergeOrder = 2;
            ToolsRibbonPage.Name = "ToolsRibbonPage";
            ToolsRibbonPage.Text = "Tools";
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
            mainMdiManager.PageAdded += MainMdiManager_PageAdded;
            // 
            // panelControl1
            // 
            panelControl1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            panelControl1.Location = new System.Drawing.Point(0, 158);
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
            ((System.ComponentModel.ISupportInitialize)exportPopupMenu).EndInit();
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
        private DevExpress.XtraBars.Ribbon.RibbonPage ToolsRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ToolsRibPageGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup ConvertRibbonGroup;
        private DevExpress.XtraBars.BarButtonItem ExportBarItem;
        private DevExpress.XtraBars.BarButtonItem exportDropDown;
        private DevExpress.XtraBars.BarButtonItem exportOptionsItem;
        private DevExpress.XtraBars.BarButtonItem ocrBarCheckItem;
        private DevExpress.XtraBars.PopupMenu exportPopupMenu;
        private DevExpress.XtraBars.BarButtonItem exportDocxItem;
        private DevExpress.XtraBars.BarButtonItem exportXlsItem;
        private DevExpress.XtraBars.BarButtonItem exportImageItem;
        private DevExpress.XtraBars.BarButtonItem exportHtmlItem;
        private DevExpress.XtraBars.BarButtonItem exportXmlItem;
        private DevExpress.XtraBars.BarButtonItem exportTextItem;
    }
}

