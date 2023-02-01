namespace Verbum
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
            DevExpress.Utils.SuperToolTip superToolTip1 = new DevExpress.Utils.SuperToolTip();
            DevExpress.Utils.ToolTipTitleItem toolTipTitleItem1 = new DevExpress.Utils.ToolTipTitleItem();
            DevExpress.Utils.ToolTipItem toolTipItem1 = new DevExpress.Utils.ToolTipItem();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.mainBarManager = new DevExpress.XtraBars.BarManager(this.components);
            this.mBar = new DevExpress.XtraBars.Bar();
            this.mFile = new DevExpress.XtraBars.BarSubItem();
            this.newItem = new DevExpress.XtraBars.BarButtonItem();
            this.openItem = new DevExpress.XtraBars.BarButtonItem();
            this.mWindow = new DevExpress.XtraBars.BarSubItem();
            this.mdiChildrenListItem = new DevExpress.XtraBars.BarMdiChildrenListItem();
            this.statusBar = new DevExpress.XtraBars.Bar();
            this.fileBar = new DevExpress.XtraBars.Bar();
            this.formatBar = new DevExpress.XtraBars.Bar();
            this.utilitieBar = new DevExpress.XtraBars.Bar();
            this.barDockControlTop = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlBottom = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlLeft = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlRight = new DevExpress.XtraBars.BarDockControl();
            this.spellChecker = new DevExpress.XtraSpellChecker.SpellChecker();
            ((System.ComponentModel.ISupportInitialize)(this.mainBarManager)).BeginInit();
            this.SuspendLayout();
            // 
            // mainBarManager
            // 
            this.mainBarManager.Bars.AddRange(new DevExpress.XtraBars.Bar[] {
            this.mBar,
            this.statusBar,
            this.fileBar,
            this.formatBar,
            this.utilitieBar});
            this.mainBarManager.DockControls.Add(this.barDockControlTop);
            this.mainBarManager.DockControls.Add(this.barDockControlBottom);
            this.mainBarManager.DockControls.Add(this.barDockControlLeft);
            this.mainBarManager.DockControls.Add(this.barDockControlRight);
            this.mainBarManager.Form = this;
            this.mainBarManager.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.mFile,
            this.mWindow,
            this.openItem,
            this.newItem,
            this.mdiChildrenListItem});
            this.mainBarManager.MainMenu = this.mBar;
            this.mainBarManager.MaxItemId = 18;
            this.mainBarManager.StatusBar = this.statusBar;
            // 
            // mBar
            // 
            this.mBar.BarName = "Main menu";
            this.mBar.DockCol = 0;
            this.mBar.DockRow = 0;
            this.mBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.mBar.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.mFile),
            new DevExpress.XtraBars.LinkPersistInfo(this.mWindow)});
            this.mBar.OptionsBar.MultiLine = true;
            this.mBar.OptionsBar.UseWholeRow = true;
            this.mBar.Text = "Main menu";
            // 
            // mFile
            // 
            this.mFile.Caption = "&File";
            this.mFile.Id = 0;
            this.mFile.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.newItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.openItem)});
            this.mFile.Name = "mFile";
            // 
            // newItem
            // 
            this.newItem.Caption = "&New";
            this.newItem.Glyph = global::Verbum.Properties.Resources.New;
            this.newItem.Id = 14;
            this.newItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.N));
            this.newItem.LargeGlyph = global::Verbum.Properties.Resources.New32;
            this.newItem.MergeType = DevExpress.XtraBars.BarMenuMerge.Replace;
            this.newItem.Name = "newItem";
            toolTipTitleItem1.Text = "New Blank Document (Ctrl+N)";
            toolTipItem1.Appearance.Image = global::Verbum.Properties.Resources.New;
            toolTipItem1.Appearance.Options.UseImage = true;
            toolTipItem1.Image = global::Verbum.Properties.Resources.New;
            toolTipItem1.LeftIndent = 6;
            toolTipItem1.Text = "Create a document.";
            superToolTip1.Items.Add(toolTipTitleItem1);
            superToolTip1.Items.Add(toolTipItem1);
            this.newItem.SuperTip = superToolTip1;
            // 
            // openItem
            // 
            this.openItem.Caption = "&Open";
            this.openItem.Glyph = global::Verbum.Properties.Resources.Open;
            this.openItem.Id = 13;
            this.openItem.ItemShortcut = new DevExpress.XtraBars.BarShortcut((System.Windows.Forms.Keys.Control | System.Windows.Forms.Keys.O));
            this.openItem.LargeGlyph = global::Verbum.Properties.Resources.Open32;
            this.openItem.MergeType = DevExpress.XtraBars.BarMenuMerge.Replace;
            this.openItem.Name = "openItem";
            // 
            // mWindow
            // 
            this.mWindow.Caption = "&Window";
            this.mWindow.Id = 10;
            this.mWindow.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.mdiChildrenListItem)});
            this.mWindow.Name = "mWindow";
            // 
            // mdiChildrenListItem
            // 
            this.mdiChildrenListItem.Caption = "Documents";
            this.mdiChildrenListItem.Id = 15;
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
            this.statusBar.OptionsBar.UseWholeRow = true;
            this.statusBar.Text = "Status bar";
            // 
            // fileBar
            // 
            this.fileBar.BarName = "File";
            this.fileBar.DockCol = 0;
            this.fileBar.DockRow = 1;
            this.fileBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.fileBar.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.newItem),
            new DevExpress.XtraBars.LinkPersistInfo(this.openItem)});
            this.fileBar.OptionsBar.UseWholeRow = true;
            this.fileBar.Text = "File";
            // 
            // formatBar
            // 
            this.formatBar.BarName = "Format";
            this.formatBar.DockCol = 0;
            this.formatBar.DockRow = 2;
            this.formatBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.formatBar.OptionsBar.UseWholeRow = true;
            this.formatBar.Text = "Format";
            // 
            // utilitieBar
            // 
            this.utilitieBar.BarName = "Utilities";
            this.utilitieBar.DockCol = 0;
            this.utilitieBar.DockRow = 3;
            this.utilitieBar.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.utilitieBar.OptionsBar.UseWholeRow = true;
            this.utilitieBar.Text = "Utilities";
            // 
            // barDockControlTop
            // 
            this.barDockControlTop.CausesValidation = false;
            this.barDockControlTop.Dock = System.Windows.Forms.DockStyle.Top;
            this.barDockControlTop.Location = new System.Drawing.Point(0, 0);
            this.barDockControlTop.Size = new System.Drawing.Size(834, 111);
            // 
            // barDockControlBottom
            // 
            this.barDockControlBottom.CausesValidation = false;
            this.barDockControlBottom.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.barDockControlBottom.Location = new System.Drawing.Point(0, 488);
            this.barDockControlBottom.Size = new System.Drawing.Size(834, 23);
            // 
            // barDockControlLeft
            // 
            this.barDockControlLeft.CausesValidation = false;
            this.barDockControlLeft.Dock = System.Windows.Forms.DockStyle.Left;
            this.barDockControlLeft.Location = new System.Drawing.Point(0, 111);
            this.barDockControlLeft.Size = new System.Drawing.Size(0, 377);
            // 
            // barDockControlRight
            // 
            this.barDockControlRight.CausesValidation = false;
            this.barDockControlRight.Dock = System.Windows.Forms.DockStyle.Right;
            this.barDockControlRight.Location = new System.Drawing.Point(834, 111);
            this.barDockControlRight.Size = new System.Drawing.Size(0, 377);
            // 
            // spellChecker
            // 
            this.spellChecker.Culture = new System.Globalization.CultureInfo("ru-RU");
            this.spellChecker.ParentContainer = null;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(834, 511);
            this.Controls.Add(this.barDockControlLeft);
            this.Controls.Add(this.barDockControlRight);
            this.Controls.Add(this.barDockControlBottom);
            this.Controls.Add(this.barDockControlTop);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.IsMdiContainer = true;
            this.Name = "MainForm";
            this.Text = "Datum Verbum 2018";
            ((System.ComponentModel.ISupportInitialize)(this.mainBarManager)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraBars.BarManager mainBarManager;
        private DevExpress.XtraBars.Bar mBar;
        private DevExpress.XtraBars.BarDockControl barDockControlTop;
        private DevExpress.XtraBars.BarDockControl barDockControlBottom;
        private DevExpress.XtraBars.BarDockControl barDockControlLeft;
        private DevExpress.XtraBars.BarDockControl barDockControlRight;
        private DevExpress.XtraBars.BarSubItem mFile;
        private DevExpress.XtraBars.BarButtonItem barButtonItem2;
        private DevExpress.XtraBars.BarButtonItem iOpen;
        private DevExpress.XtraBars.BarButtonItem iClose;
        private DevExpress.XtraBars.BarButtonItem iSave;
        private DevExpress.XtraBars.BarButtonItem iSaveAs;
        private DevExpress.XtraBars.BarButtonItem iExit;
        private DevExpress.XtraBars.BarSubItem mWindow;
        private DevExpress.XtraSpellChecker.SpellChecker spellChecker;
        private DevExpress.XtraBars.Bar statusBar;
        private DevExpress.XtraBars.Bar fileBar;
        private DevExpress.XtraBars.Bar formatBar;
        private DevExpress.XtraBars.Bar utilitieBar;
        private DevExpress.XtraBars.BarButtonItem openItem;
        private DevExpress.XtraBars.BarButtonItem newItem;
        private DevExpress.XtraBars.BarMdiChildrenListItem mdiChildrenListItem;
        private DevExpress.XtraBars.BarToolbarsListItem toolbarsListItem;

    }
}
