namespace Rizonesoft.Verbum
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
            DevExpress.XtraSplashScreen.SplashScreenManager splashManager = new DevExpress.XtraSplashScreen.SplashScreenManager(this, null, true, true);
            DevExpress.Utils.SuperToolTip superToolTip3 = new DevExpress.Utils.SuperToolTip();
            DevExpress.Utils.ToolTipTitleItem toolTipTitleItem3 = new DevExpress.Utils.ToolTipTitleItem();
            DevExpress.Utils.ToolTipItem toolTipItem3 = new DevExpress.Utils.ToolTipItem();
            DevExpress.Utils.SuperToolTip superToolTip4 = new DevExpress.Utils.SuperToolTip();
            DevExpress.Utils.ToolTipTitleItem toolTipTitleItem4 = new DevExpress.Utils.ToolTipTitleItem();
            DevExpress.Utils.ToolTipItem toolTipItem4 = new DevExpress.Utils.ToolTipItem();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.mainBarManager = new DevExpress.XtraBars.BarManager(this.components);
            this.commonBar = new DevExpress.XtraBars.Bar();
            this.newItem = new DevExpress.XtraBars.BarButtonItem();
            this.openItem = new DevExpress.XtraBars.BarButtonItem();
            this.mainMenu = new DevExpress.XtraBars.Bar();
            this.mnuFile = new DevExpress.XtraBars.BarSubItem();
            this.closeAllItem = new DevExpress.XtraBars.BarButtonItem();
            this.shutdownItem = new DevExpress.XtraBars.BarButtonItem();
            this.mnuWindow = new DevExpress.XtraBars.BarSubItem();
            this.mdiChildrenListItem = new DevExpress.XtraBars.BarMdiChildrenListItem();
            this.statusBar = new DevExpress.XtraBars.Bar();
            this.formatBar = new DevExpress.XtraBars.Bar();
            this.utilitiesBar = new DevExpress.XtraBars.Bar();
            this.barDockControlTop = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlBottom = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlLeft = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlRight = new DevExpress.XtraBars.BarDockControl();
            this.closeDocumentItem = new DevExpress.XtraBars.BarButtonItem();
            this.tabbedMdiManager = new DevExpress.XtraTabbedMdi.XtraTabbedMdiManager(this.components);
            this.defaultLook = new DevExpress.LookAndFeel.DefaultLookAndFeel(this.components);
            this.openFileDlg = new System.Windows.Forms.OpenFileDialog();
            this.dictionariesWorker = new System.ComponentModel.BackgroundWorker();
            this.coreDictionaryStorage = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.mainBarManager)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.tabbedMdiManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainBarManager
            // 
            this.mainBarManager.AllowMoveBarOnToolbar = false;
            this.mainBarManager.Bars.AddRange(new DevExpress.XtraBars.Bar[] {
            this.commonBar,
            this.mainMenu,
            this.statusBar,
            this.formatBar,
            this.utilitiesBar});
            this.mainBarManager.DockControls.Add(this.barDockControlTop);
            this.mainBarManager.DockControls.Add(this.barDockControlBottom);
            this.mainBarManager.DockControls.Add(this.barDockControlLeft);
            this.mainBarManager.DockControls.Add(this.barDockControlRight);
            this.mainBarManager.Form = this;
            this.mainBarManager.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.newItem,
            this.mnuFile,
            this.openItem,
            this.shutdownItem,
            this.mnuWindow,
            this.mdiChildrenListItem,
            this.closeDocumentItem,
            this.closeAllItem});
            this.mainBarManager.LayoutVersion = "150";
            this.mainBarManager.MainMenu = this.mainMenu;
            this.mainBarManager.MaxItemId = 14;
            this.mainBarManager.RegistryPath = "HKEY_CURRENT_USER\\Software\\Rizonesoft\\Verbum";
            this.mainBarManager.StatusBar = this.statusBar;
            this.mainBarManager.Merge += new DevExpress.XtraBars.BarManagerMergeEventHandler(this.mainBarManager_Merge);
            this.mainBarManager.UnMerge += new DevExpress.XtraBars.BarManagerMergeEventHandler(this.mainBarManager_UnMerge);
            // 
            // commonBar
            // 
            this.commonBar.BarName = "Common";
            this.commonBar.DockCol = 0;
            this.commonBar.DockRow = 1;
            this.commonBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.commonBar.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.newItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.openItem)});
            this.commonBar.OptionsBar.DisableCustomization = true;
            this.commonBar.OptionsBar.UseWholeRow = true;
            this.commonBar.Text = "Common";
            // 
            // newItem
            // 
            this.newItem.Caption = "New";
            this.newItem.Glyph = global::Rizonesoft.Verbum.Properties.Resources.New;
            this.newItem.Id = 1;
            this.newItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.N));
            this.newItem.LargeGlyph = global::Rizonesoft.Verbum.Properties.Resources.New32;
            this.newItem.Name = "newItem";
            toolTipTitleItem3.Text = "New (Ctrl+N)";
            toolTipItem3.LeftIndent = 6;
            toolTipItem3.Text = "Create a new document.";
            superToolTip3.Items.Add(toolTipTitleItem3);
            superToolTip3.Items.Add(toolTipItem3);
            this.newItem.SuperTip = superToolTip3;
            this.newItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.newDocItem_ItemClick);
            // 
            // openItem
            // 
            this.openItem.Caption = "Open";
            this.openItem.Glyph = global::Rizonesoft.Verbum.Properties.Resources.Open;
            this.openItem.Id = 2;
            this.openItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.O));
            this.openItem.LargeGlyph = global::Rizonesoft.Verbum.Properties.Resources.Open32;
            this.openItem.MergeOrder = 1;
            this.openItem.MergeType = DevExpress.XtraBars.BarMenuMerge.Replace;
            this.openItem.Name = "openItem";
            toolTipTitleItem4.Text = "Open (Ctrl+O)";
            toolTipItem4.LeftIndent = 6;
            toolTipItem4.Text = "Open a document.";
            superToolTip4.Items.Add(toolTipTitleItem4);
            superToolTip4.Items.Add(toolTipItem4);
            this.openItem.SuperTip = superToolTip4;
            this.openItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.openItem_ItemClick);
            // 
            // mainMenu
            // 
            this.mainMenu.BarName = "Main menu";
            this.mainMenu.DockCol = 0;
            this.mainMenu.DockRow = 0;
            this.mainMenu.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.mainMenu.FloatLocation = new System.Drawing.Point(360, 211);
            this.mainMenu.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.mnuFile),
            new DevExpress.XtraBars.LinkPersistInfo(this.mnuWindow)});
            this.mainMenu.OptionsBar.MultiLine = true;
            this.mainMenu.OptionsBar.UseWholeRow = true;
            this.mainMenu.Text = "Main menu";
            // 
            // mnuFile
            // 
            this.mnuFile.Caption = "File";
            this.mnuFile.Id = 3;
            this.mnuFile.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.newItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.openItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.closeAllItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.shutdownItem, true)});
            this.mnuFile.MergeType = DevExpress.XtraBars.BarMenuMerge.MergeItems;
            this.mnuFile.Name = "mnuFile";
            // 
            // closeAllItem
            // 
            this.closeAllItem.Caption = "Close All";
            this.closeAllItem.Glyph = global::Rizonesoft.Verbum.Properties.Resources.CloseAll;
            this.closeAllItem.Id = 13;
            this.closeAllItem.LargeGlyph = global::Rizonesoft.Verbum.Properties.Resources.CloseAll32;
            this.closeAllItem.MergeOrder = 5;
            this.closeAllItem.Name = "closeAllItem";
            this.closeAllItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.closeAllItem_ItemClick);
            // 
            // shutdownItem
            // 
            this.shutdownItem.Caption = "Shutdown Verbum";
            this.shutdownItem.Glyph = global::Rizonesoft.Verbum.Properties.Resources.Shutdown;
            this.shutdownItem.Id = 4;
            this.shutdownItem.LargeGlyph = global::Rizonesoft.Verbum.Properties.Resources.Shutdown32;
            this.shutdownItem.MergeOrder = 25;
            this.shutdownItem.Name = "shutdownItem";
            this.shutdownItem.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.shutdownItem_ItemClick);
            // 
            // mnuWindow
            // 
            this.mnuWindow.Caption = "Window";
            this.mnuWindow.Id = 10;
            this.mnuWindow.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.mdiChildrenListItem, true)});
            this.mnuWindow.MergeOrder = 9;
            this.mnuWindow.Name = "mnuWindow";
            // 
            // mdiChildrenListItem
            // 
            this.mdiChildrenListItem.Caption = "Documents";
            this.mdiChildrenListItem.Id = 11;
            this.mdiChildrenListItem.Name = "mdiChildrenListItem";
            // 
            // statusBar
            // 
            this.statusBar.BarName = "Status bar";
            this.statusBar.CanDockStyle = DevExpress.XtraBars.BarCanDockStyle.Bottom;
            this.statusBar.DockCol = 0;
            this.statusBar.DockRow = 0;
            this.statusBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Bottom;
            this.statusBar.OptionsBar.AllowQuickCustomization = false;
            this.statusBar.OptionsBar.DrawDragBorder = false;
            this.statusBar.OptionsBar.DrawSizeGrip = true;
            this.statusBar.OptionsBar.UseWholeRow = true;
            this.statusBar.Text = "Status bar";
            // 
            // formatBar
            // 
            this.formatBar.BarName = "Format";
            this.formatBar.DockCol = 0;
            this.formatBar.DockRow = 2;
            this.formatBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.formatBar.OptionsBar.UseWholeRow = true;
            this.formatBar.Text = "Format";
            this.formatBar.Visible = false;
            // 
            // utilitiesBar
            // 
            this.utilitiesBar.BarName = "Utilities";
            this.utilitiesBar.DockCol = 0;
            this.utilitiesBar.DockRow = 3;
            this.utilitiesBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.utilitiesBar.OptionsBar.UseWholeRow = true;
            this.utilitiesBar.Text = "Utilities";
            this.utilitiesBar.Visible = false;
            // 
            // barDockControlTop
            // 
            this.barDockControlTop.CausesValidation = false;
            this.barDockControlTop.Dock = System.Windows.Forms.DockStyle.Top;
            this.barDockControlTop.Location = new System.Drawing.Point(0, 0);
            this.barDockControlTop.Size = new System.Drawing.Size(909, 105);
            // 
            // barDockControlBottom
            // 
            this.barDockControlBottom.CausesValidation = false;
            this.barDockControlBottom.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.barDockControlBottom.Location = new System.Drawing.Point(0, 566);
            this.barDockControlBottom.Size = new System.Drawing.Size(909, 21);
            // 
            // barDockControlLeft
            // 
            this.barDockControlLeft.CausesValidation = false;
            this.barDockControlLeft.Dock = System.Windows.Forms.DockStyle.Left;
            this.barDockControlLeft.Location = new System.Drawing.Point(0, 105);
            this.barDockControlLeft.Size = new System.Drawing.Size(0, 461);
            // 
            // barDockControlRight
            // 
            this.barDockControlRight.CausesValidation = false;
            this.barDockControlRight.Dock = System.Windows.Forms.DockStyle.Right;
            this.barDockControlRight.Location = new System.Drawing.Point(909, 105);
            this.barDockControlRight.Size = new System.Drawing.Size(0, 461);
            // 
            // closeDocumentItem
            // 
            this.closeDocumentItem.Caption = "Close Document";
            this.closeDocumentItem.Glyph = global::Rizonesoft.Verbum.Properties.Resources.Close;
            this.closeDocumentItem.Id = 12;
            this.closeDocumentItem.LargeGlyph = global::Rizonesoft.Verbum.Properties.Resources.Close32;
            this.closeDocumentItem.Name = "closeDocumentItem";
            // 
            // tabbedMdiManager
            // 
            this.tabbedMdiManager.ClosePageButtonShowMode = DevExpress.XtraTab.ClosePageButtonShowMode.InActiveTabPageAndTabControlHeader;
            this.tabbedMdiManager.FloatOnDoubleClick = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.FloatOnDrag = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.FloatPageDragMode = DevExpress.XtraTabbedMdi.FloatPageDragMode.FullWindow;
            this.tabbedMdiManager.HeaderButtons = ((DevExpress.XtraTab.TabButtons)((((DevExpress.XtraTab.TabButtons.Prev | DevExpress.XtraTab.TabButtons.Next) 
            | DevExpress.XtraTab.TabButtons.Close) 
            | DevExpress.XtraTab.TabButtons.Default)));
            this.tabbedMdiManager.MdiParent = this;
            this.tabbedMdiManager.PreviewPageZoomRatio = 1F;
            this.tabbedMdiManager.SetNextMdiChildMode = DevExpress.XtraTabbedMdi.SetNextMdiChildMode.TabControl;
            this.tabbedMdiManager.ShowFloatingDropHint = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.ShowToolTips = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.UseDocumentSelector = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.UseFormIconAsPageImage = DevExpress.Utils.DefaultBoolean.True;
            this.tabbedMdiManager.SelectedPageChanged += new System.EventHandler(this.tabbedMdiManager_SelectedPageChanged);
            this.tabbedMdiManager.PageAdded += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.tabbedMdiManager_PageAdded);
            this.tabbedMdiManager.PageRemoved += new DevExpress.XtraTabbedMdi.MdiTabPageEventHandler(this.tabbedMdiManager_PageRemoved);
            this.tabbedMdiManager.BeginFloating += new DevExpress.XtraTabbedMdi.FloatingCancelEventHandler(this.tabbedMdiManager_BeginFloating);
            this.tabbedMdiManager.EndFloating += new DevExpress.XtraTabbedMdi.FloatingEventHandler(this.tabbedMdiManager_EndFloating);
            // 
            // defaultLook
            // 
            this.defaultLook.LookAndFeel.SkinName = "Office 2010 Silver";
            // 
            // dictionariesWorker
            // 
            this.dictionariesWorker.DoWork += new System.ComponentModel.DoWorkEventHandler(this.dictionariesWorker_DoWork);
            // 
            // MainForm
            // 
            this.AllowMdiBar = true;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(909, 587);
            this.Controls.Add(this.barDockControlLeft);
            this.Controls.Add(this.barDockControlRight);
            this.Controls.Add(this.barDockControlBottom);
            this.Controls.Add(this.barDockControlTop);
            this.DoubleBuffered = true;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.IsMdiContainer = true;
            this.LookAndFeel.SkinName = "Office 2010 Silver";
            this.Name = "MainForm";
            this.Text = "Rizonesoft Verbum Alpha 3 ( )";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.MainForm_FormClosing);
            ((System.ComponentModel.ISupportInitialize)(this.mainBarManager)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.tabbedMdiManager)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraBars.BarManager mainBarManager;
        private DevExpress.XtraBars.Bar commonBar;
        private DevExpress.XtraBars.Bar mainMenu;
        private DevExpress.XtraBars.Bar statusBar;
        private DevExpress.XtraBars.BarDockControl barDockControlTop;
        private DevExpress.XtraBars.BarDockControl barDockControlBottom;
        private DevExpress.XtraBars.BarDockControl barDockControlLeft;
        private DevExpress.XtraBars.BarDockControl barDockControlRight;
        private DevExpress.XtraBars.BarButtonItem newItem;
        private DevExpress.XtraTabbedMdi.XtraTabbedMdiManager tabbedMdiManager;
        private DevExpress.XtraBars.BarSubItem mnuFile;
        private DevExpress.LookAndFeel.DefaultLookAndFeel defaultLook;
        private DevExpress.XtraBars.BarButtonItem openItem;
        private System.Windows.Forms.OpenFileDialog openFileDlg;
        private System.ComponentModel.BackgroundWorker dictionariesWorker;
        private DevExpress.XtraSpellChecker.SharedDictionaryStorage coreDictionaryStorage;
        private DevExpress.XtraBars.BarButtonItem shutdownItem;
        private DevExpress.XtraBars.Bar formatBar;
        private DevExpress.XtraBars.Bar utilitiesBar;
        private DevExpress.XtraBars.BarSubItem mnuWindow;
        private DevExpress.XtraBars.BarMdiChildrenListItem mdiChildrenListItem;
        private DevExpress.XtraBars.BarButtonItem closeDocumentItem;
        private DevExpress.XtraBars.BarButtonItem closeAllItem;
    }
}