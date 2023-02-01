namespace Rizonesoft.Verbum.Configuration
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(OptionsForm));
            this.coreOpTAB = new DevExpress.XtraTab.XtraTabControl();
            this.pageGeneral = new DevExpress.XtraTab.XtraTabPage();
            this.groupImport = new DevExpress.XtraEditors.GroupControl();
            this.checkConvStURLs = new DevExpress.XtraEditors.CheckEdit();
            this.pageSkins = new DevExpress.XtraTab.XtraTabPage();
            this.gallSkins = new DevExpress.XtraBars.Ribbon.GalleryControl();
            this.galleryControlClient1 = new DevExpress.XtraBars.Ribbon.GalleryControlClient();
            this.buttApply = new DevExpress.XtraEditors.SimpleButton();
            this.buttCancel = new DevExpress.XtraEditors.SimpleButton();
            this.buttOk = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.coreOpTAB)).BeginInit();
            this.coreOpTAB.SuspendLayout();
            this.pageGeneral.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.groupImport)).BeginInit();
            this.groupImport.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.checkConvStURLs.Properties)).BeginInit();
            this.pageSkins.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.gallSkins)).BeginInit();
            this.gallSkins.SuspendLayout();
            this.SuspendLayout();
            // 
            // coreOpTAB
            // 
            this.coreOpTAB.Location = new System.Drawing.Point(12, 12);
            this.coreOpTAB.Name = "coreOpTAB";
            this.coreOpTAB.SelectedTabPage = this.pageGeneral;
            this.coreOpTAB.Size = new System.Drawing.Size(420, 350);
            this.coreOpTAB.TabIndex = 0;
            this.coreOpTAB.TabPages.AddRange(new DevExpress.XtraTab.XtraTabPage[] {
            this.pageGeneral,
            this.pageSkins});
            // 
            // pageGeneral
            // 
            this.pageGeneral.Controls.Add(this.groupImport);
            this.pageGeneral.Name = "pageGeneral";
            this.pageGeneral.Size = new System.Drawing.Size(414, 322);
            this.pageGeneral.Text = "General";
            // 
            // groupImport
            // 
            this.groupImport.Controls.Add(this.checkConvStURLs);
            this.groupImport.Location = new System.Drawing.Point(13, 13);
            this.groupImport.Name = "groupImport";
            this.groupImport.Size = new System.Drawing.Size(385, 100);
            this.groupImport.TabIndex = 0;
            this.groupImport.Text = "Importing ";
            // 
            // checkConvStURLs
            // 
            this.checkConvStURLs.Location = new System.Drawing.Point(25, 30);
            this.checkConvStURLs.Name = "checkConvStURLs";
            this.checkConvStURLs.Properties.Caption = "Convert static URLs to hyperlinks after import";
            this.checkConvStURLs.Size = new System.Drawing.Size(355, 19);
            this.checkConvStURLs.TabIndex = 0;
            this.checkConvStURLs.CheckedChanged += new System.EventHandler(this.checkConvStURLs_CheckedChanged);
            // 
            // pageSkins
            // 
            this.pageSkins.Controls.Add(this.gallSkins);
            this.pageSkins.Name = "pageSkins";
            this.pageSkins.Padding = new System.Windows.Forms.Padding(5);
            this.pageSkins.Size = new System.Drawing.Size(414, 322);
            this.pageSkins.Text = "Skins";
            // 
            // gallSkins
            // 
            this.gallSkins.Controls.Add(this.galleryControlClient1);
            this.gallSkins.DesignGalleryGroupIndex = 0;
            this.gallSkins.DesignGalleryItemIndex = 0;
            this.gallSkins.Dock = System.Windows.Forms.DockStyle.Fill;
            // 
            // galleryControlGallery1
            // 
            this.gallSkins.Gallery.ItemClick += new DevExpress.XtraBars.Ribbon.GalleryItemClickEventHandler(this.galleryControlGallery1_ItemClick);
            this.gallSkins.Location = new System.Drawing.Point(5, 5);
            this.gallSkins.Name = "gallSkins";
            this.gallSkins.Size = new System.Drawing.Size(404, 312);
            this.gallSkins.TabIndex = 0;
            this.gallSkins.Text = "Skins Gallery";
            // 
            // galleryControlClient1
            // 
            this.galleryControlClient1.GalleryControl = this.gallSkins;
            this.galleryControlClient1.Location = new System.Drawing.Point(2, 2);
            this.galleryControlClient1.Size = new System.Drawing.Size(383, 308);
            // 
            // buttApply
            // 
            this.buttApply.Enabled = false;
            this.buttApply.Location = new System.Drawing.Point(337, 385);
            this.buttApply.Name = "buttApply";
            this.buttApply.Size = new System.Drawing.Size(90, 25);
            this.buttApply.TabIndex = 1;
            this.buttApply.Text = "Apply";
            this.buttApply.Click += new System.EventHandler(this.buttApply_Click);
            // 
            // buttCancel
            // 
            this.buttCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.buttCancel.Location = new System.Drawing.Point(241, 385);
            this.buttCancel.Name = "buttCancel";
            this.buttCancel.Size = new System.Drawing.Size(90, 25);
            this.buttCancel.TabIndex = 2;
            this.buttCancel.Text = "Cancel";
            // 
            // buttOk
            // 
            this.buttOk.Location = new System.Drawing.Point(145, 385);
            this.buttOk.Name = "buttOk";
            this.buttOk.Size = new System.Drawing.Size(90, 25);
            this.buttOk.TabIndex = 3;
            this.buttOk.Text = "OK";
            this.buttOk.Click += new System.EventHandler(this.buttOk_Click);
            // 
            // OptionsForm
            // 
            this.AcceptButton = this.buttOk;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.buttCancel;
            this.ClientSize = new System.Drawing.Size(444, 422);
            this.Controls.Add(this.buttOk);
            this.Controls.Add(this.buttCancel);
            this.Controls.Add(this.buttApply);
            this.Controls.Add(this.coreOpTAB);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "OptionsForm";
            this.Text = "Verbum Options";
            this.TopMost = true;
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.OptionsForm_FormClosing);
            ((System.ComponentModel.ISupportInitialize)(this.coreOpTAB)).EndInit();
            this.coreOpTAB.ResumeLayout(false);
            this.pageGeneral.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.groupImport)).EndInit();
            this.groupImport.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.checkConvStURLs.Properties)).EndInit();
            this.pageSkins.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.gallSkins)).EndInit();
            this.gallSkins.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraTab.XtraTabPage pageGeneral;
        private DevExpress.XtraTab.XtraTabPage pageSkins;
        private DevExpress.XtraEditors.SimpleButton buttApply;
        private DevExpress.XtraEditors.SimpleButton buttCancel;
        private DevExpress.XtraEditors.SimpleButton buttOk;
        private DevExpress.XtraEditors.GroupControl groupImport;
        private DevExpress.XtraEditors.CheckEdit checkConvStURLs;
        public DevExpress.XtraTab.XtraTabControl coreOpTAB;
        private DevExpress.XtraBars.Ribbon.GalleryControl gallSkins;
        private DevExpress.XtraBars.Ribbon.GalleryControlClient galleryControlClient1;
    }
}