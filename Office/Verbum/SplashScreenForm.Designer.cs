namespace Rizonesoft.Office.Verbum
{
    internal sealed partial class SplashScreenForm
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
            StatusLabel = new DevExpress.XtraEditors.LabelControl();
            labelNameVersion = new DevExpress.XtraEditors.LabelControl();
            progressPanel1 = new DevExpress.XtraWaitForm.ProgressPanel();
            labelCopyright = new DevExpress.XtraEditors.LabelControl();
            peLogo = new DevExpress.XtraEditors.PictureEdit();
            ((System.ComponentModel.ISupportInitialize)peLogo.Properties).BeginInit();
            SuspendLayout();
            // 
            // StatusLabel
            // 
            StatusLabel.Appearance.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            StatusLabel.Appearance.Options.UseFont = true;
            StatusLabel.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            StatusLabel.Location = new System.Drawing.Point(22, 51);
            StatusLabel.Name = "StatusLabel";
            StatusLabel.Size = new System.Drawing.Size(0, 17);
            StatusLabel.TabIndex = 19;
            // 
            // labelNameVersion
            // 
            labelNameVersion.Appearance.Font = new System.Drawing.Font("Segoe UI", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            labelNameVersion.Appearance.Options.UseFont = true;
            labelNameVersion.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            labelNameVersion.Location = new System.Drawing.Point(22, 15);
            labelNameVersion.Name = "labelNameVersion";
            labelNameVersion.Size = new System.Drawing.Size(227, 30);
            labelNameVersion.TabIndex = 18;
            labelNameVersion.Text = "Rizonesoft Verbum 2023";
            // 
            // progressPanel1
            // 
            progressPanel1.Appearance.BackColor = System.Drawing.Color.Transparent;
            progressPanel1.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            progressPanel1.Appearance.Options.UseBackColor = true;
            progressPanel1.Appearance.Options.UseFont = true;
            progressPanel1.LineAnimationElementHeight = 20;
            progressPanel1.Location = new System.Drawing.Point(4, 122);
            progressPanel1.Name = "progressPanel1";
            progressPanel1.ShowCaption = false;
            progressPanel1.ShowDescription = false;
            progressPanel1.Size = new System.Drawing.Size(442, 63);
            progressPanel1.TabIndex = 17;
            progressPanel1.Text = "progressPanel1";
            // 
            // labelCopyright
            // 
            labelCopyright.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            labelCopyright.Appearance.Options.UseFont = true;
            labelCopyright.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            labelCopyright.Location = new System.Drawing.Point(22, 212);
            labelCopyright.Name = "labelCopyright";
            labelCopyright.Size = new System.Drawing.Size(67, 15);
            labelCopyright.TabIndex = 15;
            labelCopyright.Text = "Copyright ©";
            // 
            // peLogo
            // 
            peLogo.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right;
            peLogo.EditValue = resources.GetObject("peLogo.EditValue");
            peLogo.Location = new System.Drawing.Point(324, 170);
            peLogo.Name = "peLogo";
            peLogo.Properties.AllowFocused = false;
            peLogo.Properties.Appearance.BackColor = System.Drawing.Color.Transparent;
            peLogo.Properties.Appearance.Options.UseBackColor = true;
            peLogo.Properties.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            peLogo.Properties.ShowMenu = false;
            peLogo.Properties.SizeMode = DevExpress.XtraEditors.Controls.PictureSizeMode.Stretch;
            peLogo.Size = new System.Drawing.Size(100, 96);
            peLogo.TabIndex = 16;
            // 
            // SplashScreenForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(450, 250);
            Controls.Add(StatusLabel);
            Controls.Add(labelNameVersion);
            Controls.Add(progressPanel1);
            Controls.Add(labelCopyright);
            Controls.Add(peLogo);
            Name = "SplashScreenForm";
            Padding = new System.Windows.Forms.Padding(1);
            Text = "SplashScreenForm";
            ((System.ComponentModel.ISupportInitialize)peLogo.Properties).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraEditors.LabelControl StatusLabel;
        private DevExpress.XtraEditors.LabelControl labelNameVersion;
        private DevExpress.XtraWaitForm.ProgressPanel progressPanel1;
        private DevExpress.XtraEditors.LabelControl labelCopyright;
        private DevExpress.XtraEditors.PictureEdit peLogo;
    }
}
