namespace Rizonesoft.Verbum
{
    partial class HealthForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(HealthForm));
            this.tabHealth = new DevExpress.XtraTab.XtraTabControl();
            this.imagesHealth = new DevExpress.Utils.ImageCollection(this.components);
            this.pageHealthOutput = new DevExpress.XtraTab.XtraTabPage();
            this.memoBoxConsole = new DevExpress.XtraEditors.MemoEdit();
            this.healthBarManager = new DevExpress.XtraBars.BarManager(this.components);
            this.barLogging = new DevExpress.XtraBars.Bar();
            this.barDockControlTop = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlBottom = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlLeft = new DevExpress.XtraBars.BarDockControl();
            this.barDockControlRight = new DevExpress.XtraBars.BarDockControl();
            this.pageHealthSystem = new DevExpress.XtraTab.XtraTabPage();
            this.systemLayout = new System.Windows.Forms.TableLayoutPanel();
            this.componentsButton = new DevExpress.XtraEditors.SimpleButton();
            this.panelHealth = new DevExpress.XtraEditors.PanelControl();
            this.fileRibugWatcher = new System.IO.FileSystemWatcher();
            ((System.ComponentModel.ISupportInitialize)(this.tabHealth)).BeginInit();
            this.tabHealth.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.imagesHealth)).BeginInit();
            this.pageHealthOutput.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.memoBoxConsole.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.healthBarManager)).BeginInit();
            this.pageHealthSystem.SuspendLayout();
            this.systemLayout.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.panelHealth)).BeginInit();
            this.panelHealth.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.fileRibugWatcher)).BeginInit();
            this.SuspendLayout();
            // 
            // tabHealth
            // 
            this.tabHealth.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabHealth.Images = this.imagesHealth;
            this.tabHealth.Location = new System.Drawing.Point(8, 7);
            this.tabHealth.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.tabHealth.Name = "tabHealth";
            this.tabHealth.SelectedTabPage = this.pageHealthOutput;
            this.tabHealth.Size = new System.Drawing.Size(935, 567);
            this.tabHealth.TabIndex = 1;
            this.tabHealth.TabPages.AddRange(new DevExpress.XtraTab.XtraTabPage[] {
            this.pageHealthOutput,
            this.pageHealthSystem});
            // 
            // imagesHealth
            // 
            this.imagesHealth.ImageStream = ((DevExpress.Utils.ImageCollectionStreamer)(resources.GetObject("imagesHealth.ImageStream")));
            this.imagesHealth.Images.SetKeyName(0, "Console.png");
            this.imagesHealth.Images.SetKeyName(1, "Secure.png");
            // 
            // pageHealthOutput
            // 
            this.pageHealthOutput.Controls.Add(this.memoBoxConsole);
            this.pageHealthOutput.ImageOptions.ImageIndex = 0;
            this.pageHealthOutput.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.pageHealthOutput.Name = "pageHealthOutput";
            this.pageHealthOutput.Padding = new System.Windows.Forms.Padding(8, 7, 8, 7);
            this.pageHealthOutput.Size = new System.Drawing.Size(933, 536);
            this.pageHealthOutput.Text = "Logging";
            // 
            // memoBoxConsole
            // 
            this.memoBoxConsole.Dock = System.Windows.Forms.DockStyle.Fill;
            this.memoBoxConsole.Location = new System.Drawing.Point(8, 7);
            this.memoBoxConsole.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.memoBoxConsole.MenuManager = this.healthBarManager;
            this.memoBoxConsole.Name = "memoBoxConsole";
            this.memoBoxConsole.Properties.AllowHtmlDraw = DevExpress.Utils.DefaultBoolean.False;
            this.memoBoxConsole.Properties.Appearance.Font = new System.Drawing.Font("Courier New", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.memoBoxConsole.Properties.Appearance.Options.UseFont = true;
            this.memoBoxConsole.Properties.Appearance.Options.UseTextOptions = true;
            this.memoBoxConsole.Properties.EditValueChangedDelay = 500;
            this.memoBoxConsole.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Buffered;
            this.memoBoxConsole.Properties.ExportMode = DevExpress.XtraEditors.Repository.ExportMode.DisplayText;
            this.memoBoxConsole.Properties.NullValuePrompt = "Nothing here";
            this.memoBoxConsole.Properties.ReadOnly = true;
            this.memoBoxConsole.Properties.ScrollBars = System.Windows.Forms.ScrollBars.Both;
            this.memoBoxConsole.Properties.WordWrap = false;
            this.memoBoxConsole.Size = new System.Drawing.Size(917, 522);
            this.memoBoxConsole.TabIndex = 0;
            this.memoBoxConsole.TextChanged += new System.EventHandler(this.memoBoxConsole_TextChanged);
            // 
            // healthBarManager
            // 
            this.healthBarManager.AllowCustomization = false;
            this.healthBarManager.AllowMoveBarOnToolbar = false;
            this.healthBarManager.AllowQuickCustomization = false;
            this.healthBarManager.AllowShowToolbarsPopup = false;
            this.healthBarManager.Bars.AddRange(new DevExpress.XtraBars.Bar[] {
            this.barLogging});
            this.healthBarManager.DockControls.Add(this.barDockControlTop);
            this.healthBarManager.DockControls.Add(this.barDockControlBottom);
            this.healthBarManager.DockControls.Add(this.barDockControlLeft);
            this.healthBarManager.DockControls.Add(this.barDockControlRight);
            this.healthBarManager.Form = this;
            this.healthBarManager.MaxItemId = 1;
            this.healthBarManager.MdiMenuMergeStyle = DevExpress.XtraBars.BarMdiMenuMergeStyle.Never;
            // 
            // barLogging
            // 
            this.barLogging.BarName = "Logging";
            this.barLogging.DockCol = 0;
            this.barLogging.DockRow = 0;
            this.barLogging.DockStyle = DevExpress.XtraBars.BarDockStyle.Top;
            this.barLogging.OptionsBar.AllowQuickCustomization = false;
            this.barLogging.OptionsBar.DisableCustomization = true;
            this.barLogging.Text = "Logging";
            // 
            // barDockControlTop
            // 
            this.barDockControlTop.CausesValidation = false;
            this.barDockControlTop.Dock = System.Windows.Forms.DockStyle.Top;
            this.barDockControlTop.Location = new System.Drawing.Point(0, 0);
            this.barDockControlTop.Manager = this.healthBarManager;
            this.barDockControlTop.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.barDockControlTop.Size = new System.Drawing.Size(951, 21);
            // 
            // barDockControlBottom
            // 
            this.barDockControlBottom.CausesValidation = false;
            this.barDockControlBottom.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.barDockControlBottom.Location = new System.Drawing.Point(0, 602);
            this.barDockControlBottom.Manager = this.healthBarManager;
            this.barDockControlBottom.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.barDockControlBottom.Size = new System.Drawing.Size(951, 0);
            // 
            // barDockControlLeft
            // 
            this.barDockControlLeft.CausesValidation = false;
            this.barDockControlLeft.Dock = System.Windows.Forms.DockStyle.Left;
            this.barDockControlLeft.Location = new System.Drawing.Point(0, 21);
            this.barDockControlLeft.Manager = this.healthBarManager;
            this.barDockControlLeft.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.barDockControlLeft.Size = new System.Drawing.Size(0, 581);
            // 
            // barDockControlRight
            // 
            this.barDockControlRight.CausesValidation = false;
            this.barDockControlRight.Dock = System.Windows.Forms.DockStyle.Right;
            this.barDockControlRight.Location = new System.Drawing.Point(951, 21);
            this.barDockControlRight.Manager = this.healthBarManager;
            this.barDockControlRight.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.barDockControlRight.Size = new System.Drawing.Size(0, 581);
            // 
            // pageHealthSystem
            // 
            this.pageHealthSystem.Controls.Add(this.systemLayout);
            this.pageHealthSystem.ImageOptions.ImageIndex = 1;
            this.pageHealthSystem.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.pageHealthSystem.Name = "pageHealthSystem";
            this.pageHealthSystem.Padding = new System.Windows.Forms.Padding(8, 7, 8, 7);
            this.pageHealthSystem.Size = new System.Drawing.Size(933, 536);
            this.pageHealthSystem.Text = "System";
            // 
            // systemLayout
            // 
            this.systemLayout.ColumnCount = 2;
            this.systemLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.systemLayout.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
            this.systemLayout.Controls.Add(this.componentsButton, 1, 1);
            this.systemLayout.Dock = System.Windows.Forms.DockStyle.Fill;
            this.systemLayout.Location = new System.Drawing.Point(8, 7);
            this.systemLayout.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.systemLayout.Name = "systemLayout";
            this.systemLayout.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.systemLayout.RowCount = 2;
            this.systemLayout.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.systemLayout.RowStyles.Add(new System.Windows.Forms.RowStyle());
            this.systemLayout.Size = new System.Drawing.Size(917, 522);
            this.systemLayout.TabIndex = 1;
            // 
            // componentsButton
            // 
            this.componentsButton.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.componentsButton.Location = new System.Drawing.Point(707, 470);
            this.componentsButton.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.componentsButton.Name = "componentsButton";
            this.componentsButton.Size = new System.Drawing.Size(202, 44);
            this.componentsButton.TabIndex = 0;
            this.componentsButton.Text = "Components";
            this.componentsButton.Click += new System.EventHandler(this.componentsButton_Click);
            // 
            // panelHealth
            // 
            this.panelHealth.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.panelHealth.Controls.Add(this.tabHealth);
            this.panelHealth.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelHealth.Location = new System.Drawing.Point(0, 21);
            this.panelHealth.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelHealth.Name = "panelHealth";
            this.panelHealth.Padding = new System.Windows.Forms.Padding(8, 7, 8, 7);
            this.panelHealth.Size = new System.Drawing.Size(951, 581);
            this.panelHealth.TabIndex = 6;
            // 
            // fileRibugWatcher
            // 
            this.fileRibugWatcher.EnableRaisingEvents = true;
            this.fileRibugWatcher.NotifyFilter = System.IO.NotifyFilters.Size;
            this.fileRibugWatcher.SynchronizingObject = this;
            this.fileRibugWatcher.Changed += new System.IO.FileSystemEventHandler(this.fileSystemWatcher_Changed);
            // 
            // HealthForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(951, 602);
            this.Controls.Add(this.panelHealth);
            this.Controls.Add(this.barDockControlLeft);
            this.Controls.Add(this.barDockControlRight);
            this.Controls.Add(this.barDockControlBottom);
            this.Controls.Add(this.barDockControlTop);
            this.DoubleBuffered = true;
            this.IconOptions.Icon = ((System.Drawing.Icon)(resources.GetObject("HealthForm.IconOptions.Icon")));
            this.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.Name = "HealthForm";
            this.Text = "Verbum Health";
            ((System.ComponentModel.ISupportInitialize)(this.tabHealth)).EndInit();
            this.tabHealth.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.imagesHealth)).EndInit();
            this.pageHealthOutput.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.memoBoxConsole.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.healthBarManager)).EndInit();
            this.pageHealthSystem.ResumeLayout(false);
            this.systemLayout.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.panelHealth)).EndInit();
            this.panelHealth.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.fileRibugWatcher)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraTab.XtraTabControl tabHealth;
        private DevExpress.XtraTab.XtraTabPage pageHealthOutput;
        private DevExpress.XtraTab.XtraTabPage pageHealthSystem;
        private DevExpress.Utils.ImageCollection imagesHealth;
        private DevExpress.XtraBars.BarManager healthBarManager;
        private DevExpress.XtraBars.Bar barLogging;
        private DevExpress.XtraBars.BarDockControl barDockControlTop;
        private DevExpress.XtraBars.BarDockControl barDockControlBottom;
        private DevExpress.XtraBars.BarDockControl barDockControlLeft;
        private DevExpress.XtraBars.BarDockControl barDockControlRight;
        private DevExpress.XtraEditors.PanelControl panelHealth;
        private System.IO.FileSystemWatcher fileRibugWatcher;
        private DevExpress.XtraEditors.MemoEdit memoBoxConsole;
        private DevExpress.XtraEditors.SimpleButton componentsButton;
        private System.Windows.Forms.TableLayoutPanel systemLayout;

    }
}