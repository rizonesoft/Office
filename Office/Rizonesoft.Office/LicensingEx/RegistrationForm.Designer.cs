namespace Rizonesoft.Office.LicensingEx
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
            components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(RegistrationForm));
            directXFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            tablePanel1 = new DevExpress.Utils.Layout.TablePanel();
            CloseButton = new DevExpress.XtraEditors.SimpleButton();
            PasteButton = new DevExpress.XtraEditors.SimpleButton();
            ThanksLabel = new DevExpress.XtraEditors.LabelControl();
            mainSVGImageBox = new DevExpress.XtraEditors.SvgImageBox();
            RemoveActivationLink = new DevExpress.XtraEditors.HyperlinkLabelControl();
            ActivateLabel = new DevExpress.XtraEditors.LabelControl();
            textLicenseCode = new DevExpress.XtraEditors.TextEdit();
            PurchaseButton = new DevExpress.XtraEditors.SimpleButton();
            ActivateButton = new DevExpress.XtraEditors.SimpleButton();
            coreSVGImageCollection = new DevExpress.Utils.SvgImageCollection(components);
            directXFormContainerControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)tablePanel1).BeginInit();
            tablePanel1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)mainSVGImageBox).BeginInit();
            ((System.ComponentModel.ISupportInitialize)textLicenseCode.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)coreSVGImageCollection).BeginInit();
            SuspendLayout();
            // 
            // directXFormContainerControl1
            // 
            directXFormContainerControl1.Controls.Add(tablePanel1);
            directXFormContainerControl1.Location = new Point(1, 31);
            directXFormContainerControl1.Name = "directXFormContainerControl1";
            directXFormContainerControl1.Size = new Size(598, 248);
            directXFormContainerControl1.TabIndex = 0;
            // 
            // tablePanel1
            // 
            tablePanel1.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 48F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 55F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F) });
            tablePanel1.Controls.Add(CloseButton);
            tablePanel1.Controls.Add(PasteButton);
            tablePanel1.Controls.Add(ThanksLabel);
            tablePanel1.Controls.Add(mainSVGImageBox);
            tablePanel1.Controls.Add(RemoveActivationLink);
            tablePanel1.Controls.Add(ActivateLabel);
            tablePanel1.Controls.Add(textLicenseCode);
            tablePanel1.Controls.Add(PurchaseButton);
            tablePanel1.Controls.Add(ActivateButton);
            tablePanel1.Dock = DockStyle.Fill;
            tablePanel1.Location = new Point(0, 0);
            tablePanel1.Name = "tablePanel1";
            tablePanel1.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 48F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 80F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 50F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 50F) });
            tablePanel1.Size = new Size(598, 248);
            tablePanel1.TabIndex = 8;
            tablePanel1.UseSkinIndents = true;
            // 
            // CloseButton
            // 
            CloseButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            CloseButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(CloseButton, 3);
            CloseButton.DialogResult = DialogResult.Cancel;
            CloseButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseButton.ImageOptions.SvgImage");
            CloseButton.Location = new Point(447, 190);
            CloseButton.Name = "CloseButton";
            CloseButton.Padding = new Padding(10, 0, 0, 0);
            tablePanel1.SetRow(CloseButton, 3);
            CloseButton.Size = new Size(138, 45);
            CloseButton.TabIndex = 10;
            CloseButton.Text = "Close";
            // 
            // PasteButton
            // 
            PasteButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            PasteButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(PasteButton, 0);
            PasteButton.Dock = DockStyle.Fill;
            PasteButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("PasteButton.ImageOptions.SvgImage");
            PasteButton.Location = new Point(13, 140);
            PasteButton.Name = "PasteButton";
            PasteButton.Padding = new Padding(10, 0, 0, 0);
            tablePanel1.SetRow(PasteButton, 2);
            PasteButton.Size = new Size(132, 46);
            PasteButton.TabIndex = 9;
            PasteButton.Text = "Paste";
            PasteButton.Click += PasteButton_Click;
            // 
            // ThanksLabel
            // 
            ThanksLabel.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            ThanksLabel.Appearance.Options.UseFont = true;
            ThanksLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel1.SetColumn(ThanksLabel, 1);
            tablePanel1.SetColumnSpan(ThanksLabel, 3);
            ThanksLabel.Dock = DockStyle.Fill;
            ThanksLabel.Location = new Point(149, 60);
            ThanksLabel.Name = "ThanksLabel";
            tablePanel1.SetRow(ThanksLabel, 1);
            ThanksLabel.Size = new Size(436, 76);
            ThanksLabel.TabIndex = 8;
            ThanksLabel.Text = "Thank you for your support. All disabled features are enabled forever. Please feel free to contact us for premium support and make sure to tell your friends about the Rizonesoft Office suite.";
            // 
            // mainSVGImageBox
            // 
            mainSVGImageBox.AutoSizeInLayoutControl = true;
            tablePanel1.SetColumn(mainSVGImageBox, 0);
            mainSVGImageBox.Dock = DockStyle.Fill;
            mainSVGImageBox.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            mainSVGImageBox.ImeMode = ImeMode.NoControl;
            mainSVGImageBox.Location = new Point(13, 12);
            mainSVGImageBox.Name = "mainSVGImageBox";
            mainSVGImageBox.Padding = new Padding(0, 0, 30, 30);
            tablePanel1.SetRow(mainSVGImageBox, 0);
            tablePanel1.SetRowSpan(mainSVGImageBox, 2);
            mainSVGImageBox.Size = new Size(132, 124);
            mainSVGImageBox.SizeMode = DevExpress.XtraEditors.SvgImageSizeMode.Zoom;
            mainSVGImageBox.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("mainSVGImageBox.SvgImage");
            mainSVGImageBox.TabIndex = 0;
            // 
            // RemoveActivationLink
            // 
            RemoveActivationLink.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            RemoveActivationLink.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(RemoveActivationLink, 3);
            RemoveActivationLink.Dock = DockStyle.Right;
            RemoveActivationLink.Location = new Point(485, 12);
            RemoveActivationLink.Name = "RemoveActivationLink";
            tablePanel1.SetRow(RemoveActivationLink, 0);
            RemoveActivationLink.Size = new Size(100, 44);
            RemoveActivationLink.TabIndex = 6;
            RemoveActivationLink.Text = "Remove Activation";
            RemoveActivationLink.Click += RemoveActivationLink_Click;
            // 
            // ActivateLabel
            // 
            ActivateLabel.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            ActivateLabel.Appearance.ForeColor = Color.DarkRed;
            ActivateLabel.Appearance.Options.UseFont = true;
            ActivateLabel.Appearance.Options.UseForeColor = true;
            ActivateLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel1.SetColumn(ActivateLabel, 1);
            tablePanel1.SetColumnSpan(ActivateLabel, 2);
            ActivateLabel.Location = new Point(149, 25);
            ActivateLabel.Name = "ActivateLabel";
            tablePanel1.SetRow(ActivateLabel, 0);
            ActivateLabel.Size = new Size(294, 17);
            ActivateLabel.TabIndex = 5;
            ActivateLabel.Text = "License key not activated!";
            // 
            // textLicenseCode
            // 
            tablePanel1.SetColumn(textLicenseCode, 1);
            tablePanel1.SetColumnSpan(textLicenseCode, 3);
            textLicenseCode.Dock = DockStyle.Fill;
            textLicenseCode.Location = new Point(149, 140);
            textLicenseCode.Name = "textLicenseCode";
            textLicenseCode.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            textLicenseCode.Properties.Appearance.Options.UseFont = true;
            textLicenseCode.Properties.MaskSettings.Set("MaskManagerType", typeof(DevExpress.Data.Mask.SimpleMaskManager));
            textLicenseCode.Properties.MaskSettings.Set("MaskManagerSignature", "ignoreMaskBlank=True");
            textLicenseCode.Properties.MaskSettings.Set("mask", "AAAAA-AAAAA-AAAAA-AAAAA-AAAAA-AAAAA-AA");
            textLicenseCode.Properties.UseMaskAsDisplayFormat = true;
            tablePanel1.SetRow(textLicenseCode, 2);
            textLicenseCode.Size = new Size(436, 22);
            textLicenseCode.TabIndex = 1;
            textLicenseCode.TextChanged += TextLicenseCode_TextChanged;
            // 
            // PurchaseButton
            // 
            PurchaseButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            PurchaseButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(PurchaseButton, 1);
            PurchaseButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("PurchaseButton.ImageOptions.SvgImage");
            PurchaseButton.Location = new Point(149, 190);
            PurchaseButton.Name = "PurchaseButton";
            PurchaseButton.Padding = new Padding(10, 0, 0, 0);
            tablePanel1.SetRow(PurchaseButton, 3);
            PurchaseButton.Size = new Size(152, 45);
            PurchaseButton.TabIndex = 3;
            PurchaseButton.Text = "Get Licensed";
            // 
            // ActivateButton
            // 
            ActivateButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            ActivateButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(ActivateButton, 0);
            ActivateButton.Dock = DockStyle.Fill;
            ActivateButton.Enabled = false;
            ActivateButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ActivateButton.ImageOptions.SvgImage");
            ActivateButton.Location = new Point(13, 190);
            ActivateButton.Name = "ActivateButton";
            ActivateButton.Padding = new Padding(10, 0, 0, 0);
            tablePanel1.SetRow(ActivateButton, 3);
            ActivateButton.Size = new Size(132, 45);
            ActivateButton.TabIndex = 2;
            ActivateButton.Text = "Activate";
            ActivateButton.Click += ActivateButton_Click;
            // 
            // coreSVGImageCollection
            // 
            coreSVGImageCollection.Add("security_key", "image://svgimages/icon builder/security_key.svg");
            coreSVGImageCollection.Add("security_security", "image://svgimages/icon builder/security_security.svg");
            coreSVGImageCollection.Add("security_fingerprint", "image://svgimages/icon builder/security_fingerprint.svg");
            // 
            // RegistrationForm
            // 
            AutoScaleDimensions = new SizeF(6F, 13F);
            AutoScaleMode = AutoScaleMode.Font;
            CancelButton = CloseButton;
            ChildControls.Add(directXFormContainerControl1);
            ClientSize = new Size(600, 280);
            ForceDirectX = DevExpress.Utils.DefaultBoolean.True;
            FormBorderStyle = FormBorderStyle.FixedSingle;
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("RegistrationForm.IconOptions.SvgImage");
            MaximizeBox = false;
            Name = "RegistrationForm";
            Text = "Registration";
            FormClosed += RegistrationForm_FormClosed;
            directXFormContainerControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)tablePanel1).EndInit();
            tablePanel1.ResumeLayout(false);
            tablePanel1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)mainSVGImageBox).EndInit();
            ((System.ComponentModel.ISupportInitialize)textLicenseCode.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)coreSVGImageCollection).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraEditors.DirectXFormContainerControl directXFormContainerControl1;
        private DevExpress.XtraEditors.SvgImageBox mainSVGImageBox;
        private DevExpress.XtraEditors.LabelControl ActivateLabel;
        private DevExpress.XtraEditors.SimpleButton PurchaseButton;
        private DevExpress.XtraEditors.SimpleButton ActivateButton;
        private DevExpress.XtraEditors.TextEdit textLicenseCode;
        private DevExpress.XtraEditors.HyperlinkLabelControl RemoveActivationLink;
        private DevExpress.Utils.Layout.TablePanel tablePanel1;
        private DevExpress.Utils.SvgImageCollection coreSVGImageCollection;
        private DevExpress.XtraEditors.LabelControl ThanksLabel;
        private DevExpress.XtraEditors.SimpleButton PasteButton;
        private DevExpress.XtraEditors.SimpleButton CloseButton;
    }
}