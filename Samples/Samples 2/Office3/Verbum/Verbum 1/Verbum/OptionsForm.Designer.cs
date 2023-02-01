namespace Rizonesoft.Verbum
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
            this.coreOptionsTab = new DevExpress.XtraTab.XtraTabControl();
            this.pageGeneral = new DevExpress.XtraTab.XtraTabPage();
            this.pageSkins = new DevExpress.XtraTab.XtraTabPage();
            this.gallSkins = new DevExpress.XtraBars.Ribbon.GalleryControl();
            this.galleryControlClient1 = new DevExpress.XtraBars.Ribbon.GalleryControlClient();
            this.groupSkinOptions = new DevExpress.XtraEditors.GroupControl();
            this.checkAllowWindowGhosting = new DevExpress.XtraEditors.CheckEdit();
            this.checkAllowArrowDragIndicators = new DevExpress.XtraEditors.CheckEdit();
            this.checkAllowFormSkins = new DevExpress.XtraEditors.CheckEdit();
            this.buttonApply = new DevExpress.XtraEditors.SimpleButton();
            this.buttonCancel = new DevExpress.XtraEditors.SimpleButton();
            this.buttonOK = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.coreOptionsTab)).BeginInit();
            this.coreOptionsTab.SuspendLayout();
            this.pageSkins.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.gallSkins)).BeginInit();
            this.gallSkins.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.groupSkinOptions)).BeginInit();
            this.groupSkinOptions.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowWindowGhosting.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowArrowDragIndicators.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowFormSkins.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // coreOptionsTab
            // 
            this.coreOptionsTab.Dock = System.Windows.Forms.DockStyle.Top;
            this.coreOptionsTab.HeaderOrientation = DevExpress.XtraTab.TabOrientation.Horizontal;
            this.coreOptionsTab.Location = new System.Drawing.Point(8, 7);
            this.coreOptionsTab.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.coreOptionsTab.Name = "coreOptionsTab";
            this.coreOptionsTab.SelectedTabPage = this.pageGeneral;
            this.coreOptionsTab.ShowHeaderFocus = DevExpress.Utils.DefaultBoolean.True;
            this.coreOptionsTab.ShowTabHeader = DevExpress.Utils.DefaultBoolean.True;
            this.coreOptionsTab.ShowToolTips = DevExpress.Utils.DefaultBoolean.True;
            this.coreOptionsTab.Size = new System.Drawing.Size(650, 618);
            this.coreOptionsTab.TabIndex = 0;
            this.coreOptionsTab.TabPages.AddRange(new DevExpress.XtraTab.XtraTabPage[] {
            this.pageGeneral,
            this.pageSkins});
            // 
            // pageGeneral
            // 
            this.pageGeneral.ImageOptions.Padding = new System.Windows.Forms.Padding(0, 0, 7, 0);
            this.pageGeneral.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.pageGeneral.Name = "pageGeneral";
            this.pageGeneral.Size = new System.Drawing.Size(648, 587);
            this.pageGeneral.Text = "General";
            // 
            // pageSkins
            // 
            this.pageSkins.Controls.Add(this.gallSkins);
            this.pageSkins.Controls.Add(this.groupSkinOptions);
            this.pageSkins.ImageOptions.Padding = new System.Windows.Forms.Padding(0, 0, 7, 0);
            this.pageSkins.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.pageSkins.Name = "pageSkins";
            this.pageSkins.Padding = new System.Windows.Forms.Padding(15, 15, 15, 15);
            this.pageSkins.Size = new System.Drawing.Size(648, 587);
            this.pageSkins.Text = "Skins";
            // 
            // gallSkins
            // 
            this.gallSkins.Controls.Add(this.galleryControlClient1);
            this.gallSkins.Dock = System.Windows.Forms.DockStyle.Top;
            this.gallSkins.Location = new System.Drawing.Point(15, 15);
            this.gallSkins.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.gallSkins.Name = "gallSkins";
            this.gallSkins.Size = new System.Drawing.Size(618, 389);
            this.gallSkins.TabIndex = 0;
            this.gallSkins.Text = "Skins Gallery";
            this.gallSkins.Click += new System.EventHandler(this.gallSkins_Click);
            // 
            // galleryControlClient1
            // 
            this.galleryControlClient1.GalleryControl = this.gallSkins;
            this.galleryControlClient1.Location = new System.Drawing.Point(2, 2);
            this.galleryControlClient1.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.galleryControlClient1.Size = new System.Drawing.Size(588, 385);
            // 
            // groupSkinOptions
            // 
            this.groupSkinOptions.Controls.Add(this.checkAllowWindowGhosting);
            this.groupSkinOptions.Controls.Add(this.checkAllowArrowDragIndicators);
            this.groupSkinOptions.Controls.Add(this.checkAllowFormSkins);
            this.groupSkinOptions.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.groupSkinOptions.Location = new System.Drawing.Point(15, 426);
            this.groupSkinOptions.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.groupSkinOptions.Name = "groupSkinOptions";
            this.groupSkinOptions.Padding = new System.Windows.Forms.Padding(8, 7, 8, 7);
            this.groupSkinOptions.Size = new System.Drawing.Size(618, 146);
            this.groupSkinOptions.TabIndex = 1;
            this.groupSkinOptions.Text = "Skin Options";
            // 
            // checkAllowWindowGhosting
            // 
            this.checkAllowWindowGhosting.Dock = System.Windows.Forms.DockStyle.Top;
            this.checkAllowWindowGhosting.Location = new System.Drawing.Point(10, 91);
            this.checkAllowWindowGhosting.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.checkAllowWindowGhosting.Name = "checkAllowWindowGhosting";
            this.checkAllowWindowGhosting.Properties.Caption = "Allow Window Ghosting";
            this.checkAllowWindowGhosting.Size = new System.Drawing.Size(598, 25);
            this.checkAllowWindowGhosting.TabIndex = 2;
            this.checkAllowWindowGhosting.CheckedChanged += new System.EventHandler(this.checkAllowWindowGhosting_CheckedChanged);
            // 
            // checkAllowArrowDragIndicators
            // 
            this.checkAllowArrowDragIndicators.Dock = System.Windows.Forms.DockStyle.Top;
            this.checkAllowArrowDragIndicators.Location = new System.Drawing.Point(10, 66);
            this.checkAllowArrowDragIndicators.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.checkAllowArrowDragIndicators.Name = "checkAllowArrowDragIndicators";
            this.checkAllowArrowDragIndicators.Properties.Caption = "Allow Arrow Drag Indicators";
            this.checkAllowArrowDragIndicators.Size = new System.Drawing.Size(598, 25);
            this.checkAllowArrowDragIndicators.TabIndex = 1;
            this.checkAllowArrowDragIndicators.CheckedChanged += new System.EventHandler(this.checkAllowArrowDragIndicators_CheckedChanged);
            // 
            // checkAllowFormSkins
            // 
            this.checkAllowFormSkins.Dock = System.Windows.Forms.DockStyle.Top;
            this.checkAllowFormSkins.Location = new System.Drawing.Point(10, 41);
            this.checkAllowFormSkins.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.checkAllowFormSkins.Name = "checkAllowFormSkins";
            this.checkAllowFormSkins.Properties.Caption = "Allow Form Skins";
            this.checkAllowFormSkins.Size = new System.Drawing.Size(598, 25);
            this.checkAllowFormSkins.TabIndex = 0;
            this.checkAllowFormSkins.CheckedChanged += new System.EventHandler(this.checkAllowFrmSkins_CheckedChanged);
            // 
            // buttonApply
            // 
            this.buttonApply.Location = new System.Drawing.Point(502, 634);
            this.buttonApply.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.buttonApply.Name = "buttonApply";
            this.buttonApply.Size = new System.Drawing.Size(148, 44);
            this.buttonApply.TabIndex = 1;
            this.buttonApply.Text = "Apply";
            this.buttonApply.Click += new System.EventHandler(this.buttonApply_Click);
            // 
            // buttonCancel
            // 
            this.buttonCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.buttonCancel.Location = new System.Drawing.Point(345, 634);
            this.buttonCancel.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.buttonCancel.Name = "buttonCancel";
            this.buttonCancel.Size = new System.Drawing.Size(148, 44);
            this.buttonCancel.TabIndex = 2;
            this.buttonCancel.Text = "Cancel";
            this.buttonCancel.Click += new System.EventHandler(this.buttonCancel_Click);
            // 
            // buttonOK
            // 
            this.buttonOK.Location = new System.Drawing.Point(188, 634);
            this.buttonOK.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.buttonOK.Name = "buttonOK";
            this.buttonOK.Size = new System.Drawing.Size(148, 44);
            this.buttonOK.TabIndex = 3;
            this.buttonOK.Text = "OK";
            this.buttonOK.Click += new System.EventHandler(this.buttonOK_Click);
            // 
            // OptionsForm
            // 
            this.AcceptButton = this.buttonOK;
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.buttonCancel;
            this.ClientSize = new System.Drawing.Size(666, 690);
            this.Controls.Add(this.buttonOK);
            this.Controls.Add(this.buttonCancel);
            this.Controls.Add(this.buttonApply);
            this.Controls.Add(this.coreOptionsTab);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.IconOptions.Icon = ((System.Drawing.Icon)(resources.GetObject("OptionsForm.IconOptions.Icon")));
            this.Margin = new System.Windows.Forms.Padding(4, 4, 4, 4);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "OptionsForm";
            this.Padding = new System.Windows.Forms.Padding(8, 7, 8, 7);
            this.Text = "Verbum Options";
            ((System.ComponentModel.ISupportInitialize)(this.coreOptionsTab)).EndInit();
            this.coreOptionsTab.ResumeLayout(false);
            this.pageSkins.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.gallSkins)).EndInit();
            this.gallSkins.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.groupSkinOptions)).EndInit();
            this.groupSkinOptions.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowWindowGhosting.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowArrowDragIndicators.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.checkAllowFormSkins.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraTab.XtraTabPage pageGeneral;
        private DevExpress.XtraTab.XtraTabPage pageSkins;
        private DevExpress.XtraBars.Ribbon.GalleryControl gallSkins;
        private DevExpress.XtraBars.Ribbon.GalleryControlClient galleryControlClient1;
        private DevExpress.XtraEditors.SimpleButton buttonApply;
        private DevExpress.XtraEditors.SimpleButton buttonCancel;
        private DevExpress.XtraEditors.SimpleButton buttonOK;
        public DevExpress.XtraTab.XtraTabControl coreOptionsTab;
        private DevExpress.XtraEditors.GroupControl groupSkinOptions;
        private DevExpress.XtraEditors.CheckEdit checkAllowWindowGhosting;
        private DevExpress.XtraEditors.CheckEdit checkAllowArrowDragIndicators;
        private DevExpress.XtraEditors.CheckEdit checkAllowFormSkins;
    }
}