namespace Rizone.Verbum.Forms
{
    partial class OptionsForm
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
            this.panelOptions = new DevExpress.XtraEditors.PanelControl();
            this.xtraTabControl1 = new DevExpress.XtraTab.XtraTabControl();
            this.pageSave = new DevExpress.XtraTab.XtraTabPage();
            this.panelSave1 = new System.Windows.Forms.Panel();
            this.checkCompFormat = new DevExpress.XtraEditors.CheckEdit();
            this.pageGeneral = new DevExpress.XtraTab.XtraTabPage();
            this.simpleButton1 = new DevExpress.XtraEditors.SimpleButton();
            this.pageSkins = new DevExpress.XtraTab.XtraTabPage();
            this.panelInt2 = new System.Windows.Forms.Panel();
            this.gallerySkins = new DevExpress.XtraBars.Ribbon.GalleryControl();
            this.galleryControlClient1 = new DevExpress.XtraBars.Ribbon.GalleryControlClient();
            this.panelInt1 = new System.Windows.Forms.Panel();
            this.panelOpBtns = new DevExpress.XtraEditors.PanelControl();
            this.btnOK = new DevExpress.XtraEditors.SimpleButton();
            this.btnCancel = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.panelOptions)).BeginInit();
            this.panelOptions.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.xtraTabControl1)).BeginInit();
            this.xtraTabControl1.SuspendLayout();
            this.pageSave.SuspendLayout();
            this.panelSave1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.checkCompFormat.Properties)).BeginInit();
            this.pageGeneral.SuspendLayout();
            this.pageSkins.SuspendLayout();
            this.panelInt2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.gallerySkins)).BeginInit();
            this.gallerySkins.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.panelOpBtns)).BeginInit();
            this.panelOpBtns.SuspendLayout();
            this.SuspendLayout();
            // 
            // panelOptions
            // 
            this.panelOptions.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.panelOptions.Controls.Add(this.xtraTabControl1);
            this.panelOptions.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelOptions.Location = new System.Drawing.Point(0, 0);
            this.panelOptions.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelOptions.Name = "panelOptions";
            this.panelOptions.Padding = new System.Windows.Forms.Padding(8, 8, 8, 8);
            this.panelOptions.Size = new System.Drawing.Size(876, 527);
            this.panelOptions.TabIndex = 1;
            // 
            // xtraTabControl1
            // 
            this.xtraTabControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.xtraTabControl1.HeaderLocation = DevExpress.XtraTab.TabHeaderLocation.Left;
            this.xtraTabControl1.HeaderOrientation = DevExpress.XtraTab.TabOrientation.Horizontal;
            this.xtraTabControl1.Location = new System.Drawing.Point(8, 8);
            this.xtraTabControl1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.xtraTabControl1.Name = "xtraTabControl1";
            this.xtraTabControl1.SelectedTabPage = this.pageSave;
            this.xtraTabControl1.ShowTabHeader = DevExpress.Utils.DefaultBoolean.True;
            this.xtraTabControl1.Size = new System.Drawing.Size(860, 511);
            this.xtraTabControl1.TabIndex = 3;
            this.xtraTabControl1.TabPages.AddRange(new DevExpress.XtraTab.XtraTabPage[] {
            this.pageGeneral,
            this.pageSave,
            this.pageSkins});
            // 
            // pageSave
            // 
            this.pageSave.AutoScroll = true;
            this.pageSave.AutoScrollMinSize = new System.Drawing.Size(300, 250);
            this.pageSave.Controls.Add(this.panelSave1);
            this.pageSave.Margin = new System.Windows.Forms.Padding(6, 6, 6, 6);
            this.pageSave.Name = "pageSave";
            this.pageSave.Size = new System.Drawing.Size(765, 509);
            this.pageSave.Text = "Save";
            // 
            // panelSave1
            // 
            this.panelSave1.Controls.Add(this.checkCompFormat);
            this.panelSave1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelSave1.Location = new System.Drawing.Point(0, 0);
            this.panelSave1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelSave1.Name = "panelSave1";
            this.panelSave1.Padding = new System.Windows.Forms.Padding(8, 8, 8, 8);
            this.panelSave1.Size = new System.Drawing.Size(765, 45);
            this.panelSave1.TabIndex = 5;
            // 
            // checkCompFormat
            // 
            this.checkCompFormat.Dock = System.Windows.Forms.DockStyle.Fill;
            this.checkCompFormat.Location = new System.Drawing.Point(8, 8);
            this.checkCompFormat.Margin = new System.Windows.Forms.Padding(6, 6, 6, 6);
            this.checkCompFormat.MinimumSize = new System.Drawing.Size(450, 0);
            this.checkCompFormat.Name = "checkCompFormat";
            this.checkCompFormat.Properties.Caption = "Specify the compact format for a saved file";
            this.checkCompFormat.Size = new System.Drawing.Size(749, 29);
            this.checkCompFormat.TabIndex = 4;
            this.checkCompFormat.ToolTip = "You can reduce the file size by preventing dual picture saving although it affect" +
    "s file portability.";
            this.checkCompFormat.ToolTipIconType = DevExpress.Utils.ToolTipIconType.Information;
            // 
            // pageGeneral
            // 
            this.pageGeneral.Controls.Add(this.simpleButton1);
            this.pageGeneral.Margin = new System.Windows.Forms.Padding(6, 6, 6, 6);
            this.pageGeneral.Name = "pageGeneral";
            this.pageGeneral.Size = new System.Drawing.Size(765, 509);
            this.pageGeneral.Text = "General";
            // 
            // simpleButton1
            // 
            this.simpleButton1.Location = new System.Drawing.Point(195, 252);
            this.simpleButton1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.simpleButton1.Name = "simpleButton1";
            this.simpleButton1.Size = new System.Drawing.Size(112, 34);
            this.simpleButton1.TabIndex = 0;
            this.simpleButton1.Text = "simpleButton1";
            this.simpleButton1.Click += new System.EventHandler(this.simpleButton1_Click);
            // 
            // pageSkins
            // 
            this.pageSkins.Controls.Add(this.panelInt2);
            this.pageSkins.Controls.Add(this.panelInt1);
            this.pageSkins.ImageOptions.Image = global::Verbum.Properties.Resources.Skins32;
            this.pageSkins.Margin = new System.Windows.Forms.Padding(6, 6, 6, 6);
            this.pageSkins.Name = "pageSkins";
            this.pageSkins.Size = new System.Drawing.Size(765, 509);
            this.pageSkins.Text = "Skins";
            // 
            // panelInt2
            // 
            this.panelInt2.Controls.Add(this.gallerySkins);
            this.panelInt2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panelInt2.Location = new System.Drawing.Point(0, 48);
            this.panelInt2.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelInt2.Name = "panelInt2";
            this.panelInt2.Padding = new System.Windows.Forms.Padding(8, 8, 8, 8);
            this.panelInt2.Size = new System.Drawing.Size(765, 461);
            this.panelInt2.TabIndex = 2;
            // 
            // gallerySkins
            // 
            this.gallerySkins.Controls.Add(this.galleryControlClient1);
            this.gallerySkins.Dock = System.Windows.Forms.DockStyle.Fill;
            // 
            // 
            // 
            this.gallerySkins.Gallery.AllowHoverImages = true;
            this.gallerySkins.Gallery.ImageSize = new System.Drawing.Size(48, 48);
            this.gallerySkins.Gallery.UseMaxImageSize = true;
            this.gallerySkins.Location = new System.Drawing.Point(8, 8);
            this.gallerySkins.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.gallerySkins.Name = "gallerySkins";
            this.gallerySkins.Size = new System.Drawing.Size(749, 445);
            this.gallerySkins.TabIndex = 0;
            // 
            // galleryControlClient1
            // 
            this.galleryControlClient1.GalleryControl = this.gallerySkins;
            this.galleryControlClient1.Location = new System.Drawing.Point(2, 2);
            this.galleryControlClient1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.galleryControlClient1.Size = new System.Drawing.Size(719, 441);
            // 
            // panelInt1
            // 
            this.panelInt1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelInt1.Location = new System.Drawing.Point(0, 0);
            this.panelInt1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelInt1.Name = "panelInt1";
            this.panelInt1.Padding = new System.Windows.Forms.Padding(8, 8, 8, 8);
            this.panelInt1.Size = new System.Drawing.Size(765, 48);
            this.panelInt1.TabIndex = 1;
            // 
            // panelOpBtns
            // 
            this.panelOpBtns.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.panelOpBtns.Controls.Add(this.btnOK);
            this.panelOpBtns.Controls.Add(this.btnCancel);
            this.panelOpBtns.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.panelOpBtns.Location = new System.Drawing.Point(0, 527);
            this.panelOpBtns.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelOpBtns.Name = "panelOpBtns";
            this.panelOpBtns.Padding = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.panelOpBtns.Size = new System.Drawing.Size(876, 75);
            this.panelOpBtns.TabIndex = 2;
            // 
            // btnOK
            // 
            this.btnOK.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.btnOK.DialogResult = System.Windows.Forms.DialogResult.OK;
            this.btnOK.Location = new System.Drawing.Point(492, 9);
            this.btnOK.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.btnOK.Name = "btnOK";
            this.btnOK.Size = new System.Drawing.Size(180, 48);
            this.btnOK.TabIndex = 1;
            this.btnOK.Text = "OK";
            this.btnOK.Click += new System.EventHandler(this.btnOK_Click);
            // 
            // btnCancel
            // 
            this.btnCancel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.btnCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.btnCancel.Location = new System.Drawing.Point(681, 9);
            this.btnCancel.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(180, 48);
            this.btnCancel.TabIndex = 2;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            // 
            // OptionsForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(876, 602);
            this.Controls.Add(this.panelOptions);
            this.Controls.Add(this.panelOpBtns);
            this.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.MinimumSize = new System.Drawing.Size(300, 300);
            this.Name = "OptionsForm";
            this.Text = "OptionsForm";
            ((System.ComponentModel.ISupportInitialize)(this.panelOptions)).EndInit();
            this.panelOptions.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.xtraTabControl1)).EndInit();
            this.xtraTabControl1.ResumeLayout(false);
            this.pageSave.ResumeLayout(false);
            this.panelSave1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.checkCompFormat.Properties)).EndInit();
            this.pageGeneral.ResumeLayout(false);
            this.pageSkins.ResumeLayout(false);
            this.panelInt2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.gallerySkins)).EndInit();
            this.gallerySkins.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.panelOpBtns)).EndInit();
            this.panelOpBtns.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.PanelControl panelOptions;
        private DevExpress.XtraEditors.PanelControl panelOpBtns;
        private DevExpress.XtraEditors.SimpleButton btnOK;
        private DevExpress.XtraEditors.SimpleButton btnCancel;
        private DevExpress.XtraTab.XtraTabControl xtraTabControl1;
        private DevExpress.XtraTab.XtraTabPage pageSave;
        private DevExpress.XtraEditors.CheckEdit checkCompFormat;
        private DevExpress.XtraTab.XtraTabPage pageSkins;
        private DevExpress.XtraBars.Ribbon.GalleryControl gallerySkins;
        private DevExpress.XtraBars.Ribbon.GalleryControlClient galleryControlClient1;
        private System.Windows.Forms.Panel panelInt2;
        private System.Windows.Forms.Panel panelInt1;
        private System.Windows.Forms.Panel panelSave1;
        private DevExpress.XtraTab.XtraTabPage pageGeneral;
        private DevExpress.XtraEditors.SimpleButton simpleButton1;
    }
}