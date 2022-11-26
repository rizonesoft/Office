namespace Rizonesoft.Office.Evaluate
{
    partial class SplashScreenForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SplashScreenForm));
            this.peLogo = new DevExpress.XtraEditors.PictureEdit();
            this.labelCopyright = new DevExpress.XtraEditors.LabelControl();
            this.progressPanel1 = new DevExpress.XtraWaitForm.ProgressPanel();
            this.labelProductName = new DevExpress.XtraEditors.LabelControl();
            this.StatusLabel = new DevExpress.XtraEditors.LabelControl();
            ((System.ComponentModel.ISupportInitialize)(this.peLogo.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // peLogo
            // 
            this.peLogo.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.peLogo.EditValue = ((object)(resources.GetObject("peLogo.EditValue")));
            this.peLogo.Location = new System.Drawing.Point(324, 177);
            this.peLogo.Name = "peLogo";
            this.peLogo.Properties.AllowFocused = false;
            this.peLogo.Properties.Appearance.BackColor = System.Drawing.Color.Transparent;
            this.peLogo.Properties.Appearance.Options.UseBackColor = true;
            this.peLogo.Properties.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.peLogo.Properties.ShowMenu = false;
            this.peLogo.Properties.SizeMode = DevExpress.XtraEditors.Controls.PictureSizeMode.Stretch;
            this.peLogo.Size = new System.Drawing.Size(100, 96);
            this.peLogo.TabIndex = 11;
            // 
            // labelCopyright
            // 
            this.labelCopyright.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.labelCopyright.Appearance.Options.UseFont = true;
            this.labelCopyright.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.labelCopyright.Location = new System.Drawing.Point(22, 219);
            this.labelCopyright.Name = "labelCopyright";
            this.labelCopyright.Size = new System.Drawing.Size(67, 15);
            this.labelCopyright.TabIndex = 10;
            this.labelCopyright.Text = "Copyright ©";
            // 
            // progressPanel1
            // 
            this.progressPanel1.Appearance.BackColor = System.Drawing.Color.Transparent;
            this.progressPanel1.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.progressPanel1.Appearance.Options.UseBackColor = true;
            this.progressPanel1.Appearance.Options.UseFont = true;
            this.progressPanel1.LineAnimationElementHeight = 20;
            this.progressPanel1.Location = new System.Drawing.Point(4, 81);
            this.progressPanel1.Name = "progressPanel1";
            this.progressPanel1.ShowCaption = false;
            this.progressPanel1.ShowDescription = false;
            this.progressPanel1.Size = new System.Drawing.Size(442, 123);
            this.progressPanel1.TabIndex = 12;
            this.progressPanel1.Text = "progressPanel1";
            // 
            // labelProductName
            // 
            this.labelProductName.Appearance.Font = new System.Drawing.Font("Segoe UI", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.labelProductName.Appearance.Options.UseFont = true;
            this.labelProductName.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.labelProductName.Location = new System.Drawing.Point(22, 22);
            this.labelProductName.Name = "labelProductName";
            this.labelProductName.Size = new System.Drawing.Size(111, 30);
            this.labelProductName.TabIndex = 13;
            this.labelProductName.Text = "Sheets 2023";
            // 
            // StatusLabel
            // 
            this.StatusLabel.Appearance.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.StatusLabel.Appearance.Options.UseFont = true;
            this.StatusLabel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.StatusLabel.Location = new System.Drawing.Point(22, 58);
            this.StatusLabel.Name = "StatusLabel";
            this.StatusLabel.Size = new System.Drawing.Size(35, 17);
            this.StatusLabel.TabIndex = 14;
            this.StatusLabel.Text = "Status";
            // 
            // SplashScreenForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(450, 251);
            this.Controls.Add(this.StatusLabel);
            this.Controls.Add(this.labelProductName);
            this.Controls.Add(this.progressPanel1);
            this.Controls.Add(this.labelCopyright);
            this.Controls.Add(this.peLogo);
            this.Name = "SplashScreenForm";
            this.Padding = new System.Windows.Forms.Padding(1);
            this.Text = "MainSplashScreen";
            ((System.ComponentModel.ISupportInitialize)(this.peLogo.Properties)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private DevExpress.XtraEditors.PictureEdit peLogo;
        private DevExpress.XtraEditors.LabelControl labelCopyright;
        private DevExpress.XtraWaitForm.ProgressPanel progressPanel1;
        private DevExpress.XtraEditors.LabelControl labelProductName;
        private DevExpress.XtraEditors.LabelControl StatusLabel;
    }
}
