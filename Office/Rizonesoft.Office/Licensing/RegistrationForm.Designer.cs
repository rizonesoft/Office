namespace Rizonesoft.Office.Licensing
{
    partial class RegistrationForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(RegistrationForm));
            this.directXFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            this.labelControl1 = new DevExpress.XtraEditors.LabelControl();
            this.textLicenseCode = new DevExpress.XtraEditors.TextEdit();
            this.ButtonActivate = new DevExpress.XtraEditors.SimpleButton();
            this.simpleButton2 = new DevExpress.XtraEditors.SimpleButton();
            this.ButtonCancel = new DevExpress.XtraEditors.SimpleButton();
            this.regErrorProvider = new DevExpress.XtraEditors.DXErrorProvider.DXErrorProvider(this.components);
            this.svgImageBox1 = new DevExpress.XtraEditors.SvgImageBox();
            this.directXFormContainerControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.textLicenseCode.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.regErrorProvider)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.svgImageBox1)).BeginInit();
            this.SuspendLayout();
            // 
            // directXFormContainerControl1
            // 
            this.directXFormContainerControl1.Controls.Add(this.svgImageBox1);
            this.directXFormContainerControl1.Controls.Add(this.labelControl1);
            this.directXFormContainerControl1.Controls.Add(this.textLicenseCode);
            this.directXFormContainerControl1.Controls.Add(this.ButtonActivate);
            this.directXFormContainerControl1.Controls.Add(this.simpleButton2);
            this.directXFormContainerControl1.Controls.Add(this.ButtonCancel);
            this.directXFormContainerControl1.Location = new System.Drawing.Point(1, 31);
            this.directXFormContainerControl1.Name = "directXFormContainerControl1";
            this.directXFormContainerControl1.Size = new System.Drawing.Size(548, 268);
            this.directXFormContainerControl1.TabIndex = 0;
            // 
            // labelControl1
            // 
            this.labelControl1.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.labelControl1.Appearance.Options.UseFont = true;
            this.labelControl1.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            this.labelControl1.Location = new System.Drawing.Point(84, 10);
            this.labelControl1.Name = "labelControl1";
            this.labelControl1.Size = new System.Drawing.Size(430, 15);
            this.labelControl1.TabIndex = 8;
            this.labelControl1.Text = "Please enter your license code and press \'Activate\" for business use.";
            // 
            // textLicenseCode
            // 
            this.textLicenseCode.Location = new System.Drawing.Point(40, 130);
            this.textLicenseCode.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.textLicenseCode.Name = "textLicenseCode";
            this.textLicenseCode.Properties.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.textLicenseCode.Properties.Appearance.Options.UseFont = true;
            this.textLicenseCode.Properties.NullValuePrompt = "License Code";
            this.textLicenseCode.Size = new System.Drawing.Size(466, 22);
            this.textLicenseCode.TabIndex = 4;
            this.textLicenseCode.TextChanged += new System.EventHandler(this.textLicenseCode_TextChanged);
            // 
            // ButtonActivate
            // 
            this.ButtonActivate.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.ButtonActivate.Appearance.Options.UseFont = true;
            this.ButtonActivate.Enabled = false;
            this.ButtonActivate.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("ButtonActivate.ImageOptions.SvgImage")));
            this.ButtonActivate.Location = new System.Drawing.Point(356, 158);
            this.ButtonActivate.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.ButtonActivate.Name = "ButtonActivate";
            this.ButtonActivate.Size = new System.Drawing.Size(150, 35);
            this.ButtonActivate.TabIndex = 5;
            this.ButtonActivate.Text = "Activate";
            this.ButtonActivate.Click += new System.EventHandler(this.ButtonActivate_Click);
            // 
            // simpleButton2
            // 
            this.simpleButton2.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.simpleButton2.Appearance.Options.UseFont = true;
            this.simpleButton2.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("simpleButton2.ImageOptions.SvgImage")));
            this.simpleButton2.Location = new System.Drawing.Point(198, 158);
            this.simpleButton2.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.simpleButton2.Name = "simpleButton2";
            this.simpleButton2.Size = new System.Drawing.Size(150, 35);
            this.simpleButton2.TabIndex = 6;
            this.simpleButton2.Text = "Register";
            // 
            // ButtonCancel
            // 
            this.ButtonCancel.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.ButtonCancel.Appearance.Options.UseFont = true;
            this.ButtonCancel.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("ButtonCancel.ImageOptions.SvgImage")));
            this.ButtonCancel.Location = new System.Drawing.Point(40, 158);
            this.ButtonCancel.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.ButtonCancel.Name = "ButtonCancel";
            this.ButtonCancel.Size = new System.Drawing.Size(150, 35);
            this.ButtonCancel.TabIndex = 7;
            this.ButtonCancel.Text = "Cancel";
            this.ButtonCancel.Click += new System.EventHandler(this.ButtonCancel_Click);
            // 
            // regErrorProvider
            // 
            this.regErrorProvider.ContainerControl = this;
            // 
            // svgImageBox1
            // 
            this.svgImageBox1.Location = new System.Drawing.Point(10, 10);
            this.svgImageBox1.Name = "svgImageBox1";
            this.svgImageBox1.Size = new System.Drawing.Size(64, 64);
            this.svgImageBox1.SizeMode = DevExpress.XtraEditors.SvgImageSizeMode.Stretch;
            this.svgImageBox1.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("svgImageBox1.SvgImage")));
            this.svgImageBox1.TabIndex = 9;
            this.svgImageBox1.Text = "svgImageBox1";
            // 
            // RegistrationForm
            // 
            this.AcceptButton = this.ButtonActivate;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(550, 300);
            this.Controls.Add(this.directXFormContainerControl1);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.IconOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("RegistrationForm.IconOptions.SvgImage")));
            this.Name = "RegistrationForm";
            this.Text = "Registration";
            this.directXFormContainerControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.textLicenseCode.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.regErrorProvider)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.svgImageBox1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.DirectXFormContainerControl directXFormContainerControl1;
        private DevExpress.XtraEditors.TextEdit textLicenseCode;
        private DevExpress.XtraEditors.SimpleButton simpleButton2;
        private DevExpress.XtraEditors.SimpleButton ButtonCancel;
        private DevExpress.XtraEditors.LabelControl labelControl1;
        private DevExpress.XtraEditors.SimpleButton ButtonActivate;
        private DevExpress.XtraEditors.DXErrorProvider.DXErrorProvider regErrorProvider;
        // private DevExpress.XtraEditors.DirectXFormContainerControl directxFormContainerControl2;
        private DevExpress.XtraEditors.SvgImageBox svgImageBox1;
    }
}