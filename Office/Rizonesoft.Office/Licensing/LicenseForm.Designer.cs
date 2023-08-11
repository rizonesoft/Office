namespace Rizonesoft.Office.Licensing
{
    partial class LicenseForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(LicenseForm));
            tablePanel1 = new DevExpress.Utils.Layout.TablePanel();
            LicenseCodeText = new DevExpress.XtraEditors.TextEdit();
            ThanksLabel = new DevExpress.XtraEditors.LabelControl();
            LicenseActiveLabel = new DevExpress.XtraEditors.LabelControl();
            DeleteLicenseLink = new DevExpress.XtraEditors.HyperlinkLabelControl();
            CloseButton = new DevExpress.XtraEditors.SimpleButton();
            GetLicenseButton = new DevExpress.XtraEditors.SimpleButton();
            ActivateButton = new DevExpress.XtraEditors.SimpleButton();
            PasteButton = new DevExpress.XtraEditors.SimpleButton();
            FormSVGIcon = new DevExpress.XtraEditors.SvgImageBox();
            ((System.ComponentModel.ISupportInitialize)tablePanel1).BeginInit();
            tablePanel1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)LicenseCodeText.Properties).BeginInit();
            ((System.ComponentModel.ISupportInitialize)FormSVGIcon).BeginInit();
            SuspendLayout();
            // 
            // tablePanel1
            // 
            tablePanel1.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 80F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 80F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 150F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 150F) });
            tablePanel1.Controls.Add(LicenseCodeText);
            tablePanel1.Controls.Add(ThanksLabel);
            tablePanel1.Controls.Add(LicenseActiveLabel);
            tablePanel1.Controls.Add(DeleteLicenseLink);
            tablePanel1.Controls.Add(CloseButton);
            tablePanel1.Controls.Add(GetLicenseButton);
            tablePanel1.Controls.Add(ActivateButton);
            tablePanel1.Controls.Add(PasteButton);
            tablePanel1.Controls.Add(FormSVGIcon);
            tablePanel1.Dock = DockStyle.Fill;
            tablePanel1.Location = new Point(0, 0);
            tablePanel1.Name = "tablePanel1";
            tablePanel1.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 45F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 45F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 45F) });
            tablePanel1.Size = new Size(598, 318);
            tablePanel1.TabIndex = 0;
            tablePanel1.UseSkinIndents = true;
            // 
            // LicenseCodeText
            // 
            LicenseCodeText.CausesValidation = false;
            tablePanel1.SetColumn(LicenseCodeText, 2);
            tablePanel1.SetColumnSpan(LicenseCodeText, 3);
            LicenseCodeText.Dock = DockStyle.Fill;
            LicenseCodeText.Location = new Point(173, 219);
            LicenseCodeText.Name = "LicenseCodeText";
            LicenseCodeText.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            LicenseCodeText.Properties.Appearance.Options.UseFont = true;
            LicenseCodeText.Properties.MaskSettings.Set("MaskManagerType", typeof(DevExpress.Data.Mask.SimpleMaskManager));
            LicenseCodeText.Properties.MaskSettings.Set("mask", "AAAAA-AAAAA-AAAAA-AAAAA-AAAAA-AAAAA-AA");
            LicenseCodeText.Properties.UseMaskAsDisplayFormat = true;
            tablePanel1.SetRow(LicenseCodeText, 2);
            LicenseCodeText.Size = new Size(412, 22);
            LicenseCodeText.TabIndex = 2;
            // 
            // ThanksLabel
            // 
            ThanksLabel.AllowHtmlString = true;
            ThanksLabel.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            ThanksLabel.Appearance.Options.UseFont = true;
            ThanksLabel.Appearance.Options.UseTextOptions = true;
            ThanksLabel.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            ThanksLabel.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            ThanksLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel1.SetColumn(ThanksLabel, 1);
            tablePanel1.SetColumnSpan(ThanksLabel, 4);
            ThanksLabel.Dock = DockStyle.Fill;
            ThanksLabel.ImageAlignToText = DevExpress.XtraEditors.ImageAlignToText.LeftTop;
            ThanksLabel.Location = new Point(93, 57);
            ThanksLabel.Name = "ThanksLabel";
            ThanksLabel.Padding = new Padding(10, 0, 0, 0);
            tablePanel1.SetRow(ThanksLabel, 1);
            ThanksLabel.Size = new Size(492, 158);
            ThanksLabel.TabIndex = 7;
            ThanksLabel.Text = resources.GetString("ThanksLabel.Text");
            ThanksLabel.HyperlinkClick += ThanksLabel_HyperlinkClick;
            // 
            // LicenseActiveLabel
            // 
            LicenseActiveLabel.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            LicenseActiveLabel.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(LicenseActiveLabel, 0);
            tablePanel1.SetColumnSpan(LicenseActiveLabel, 3);
            LicenseActiveLabel.Dock = DockStyle.Fill;
            LicenseActiveLabel.Location = new Point(13, 12);
            LicenseActiveLabel.Name = "LicenseActiveLabel";
            tablePanel1.SetRow(LicenseActiveLabel, 0);
            LicenseActiveLabel.Size = new Size(306, 41);
            LicenseActiveLabel.TabIndex = 6;
            LicenseActiveLabel.Text = "License not activated!";
            // 
            // DeleteLicenseLink
            // 
            DeleteLicenseLink.Appearance.Font = new Font("Segoe UI", 10F, FontStyle.Regular, GraphicsUnit.Point);
            DeleteLicenseLink.Appearance.Options.UseFont = true;
            DeleteLicenseLink.Appearance.Options.UseTextOptions = true;
            DeleteLicenseLink.Appearance.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Far;
            DeleteLicenseLink.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            tablePanel1.SetColumn(DeleteLicenseLink, 3);
            tablePanel1.SetColumnSpan(DeleteLicenseLink, 2);
            DeleteLicenseLink.Dock = DockStyle.Fill;
            DeleteLicenseLink.ImageAlignToText = DevExpress.XtraEditors.ImageAlignToText.LeftCenter;
            DeleteLicenseLink.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("DeleteLicenseLink.ImageOptions.SvgImage");
            DeleteLicenseLink.ImageOptions.SvgImageSize = new Size(24, 24);
            DeleteLicenseLink.Location = new Point(323, 12);
            DeleteLicenseLink.Name = "DeleteLicenseLink";
            tablePanel1.SetRow(DeleteLicenseLink, 0);
            DeleteLicenseLink.Size = new Size(262, 41);
            DeleteLicenseLink.TabIndex = 5;
            DeleteLicenseLink.Text = "Delete License";
            DeleteLicenseLink.HyperlinkClick += DeleteLicenseLink_HyperlinkClick;
            // 
            // CloseButton
            // 
            CloseButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            CloseButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(CloseButton, 4);
            CloseButton.Dock = DockStyle.Fill;
            CloseButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("CloseButton.ImageOptions.SvgImage");
            CloseButton.Location = new Point(439, 264);
            CloseButton.Name = "CloseButton";
            tablePanel1.SetRow(CloseButton, 3);
            CloseButton.Size = new Size(146, 41);
            CloseButton.TabIndex = 5;
            CloseButton.Text = "Close";
            // 
            // GetLicenseButton
            // 
            GetLicenseButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            GetLicenseButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(GetLicenseButton, 2);
            GetLicenseButton.Dock = DockStyle.Fill;
            GetLicenseButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("GetLicenseButton.ImageOptions.SvgImage");
            GetLicenseButton.Location = new Point(173, 264);
            GetLicenseButton.Name = "GetLicenseButton";
            tablePanel1.SetRow(GetLicenseButton, 3);
            GetLicenseButton.Size = new Size(146, 41);
            GetLicenseButton.TabIndex = 4;
            GetLicenseButton.Text = "Get License";
            // 
            // ActivateButton
            // 
            ActivateButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            ActivateButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(ActivateButton, 0);
            tablePanel1.SetColumnSpan(ActivateButton, 2);
            ActivateButton.Dock = DockStyle.Fill;
            ActivateButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ActivateButton.ImageOptions.SvgImage");
            ActivateButton.Location = new Point(13, 264);
            ActivateButton.Name = "ActivateButton";
            tablePanel1.SetRow(ActivateButton, 3);
            ActivateButton.Size = new Size(156, 41);
            ActivateButton.TabIndex = 3;
            ActivateButton.Text = "Activate";
            ActivateButton.Click += ActivateButton_Click;
            // 
            // PasteButton
            // 
            PasteButton.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            PasteButton.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(PasteButton, 0);
            tablePanel1.SetColumnSpan(PasteButton, 2);
            PasteButton.Dock = DockStyle.Fill;
            PasteButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("PasteButton.ImageOptions.SvgImage");
            PasteButton.Location = new Point(13, 219);
            PasteButton.Name = "PasteButton";
            tablePanel1.SetRow(PasteButton, 2);
            PasteButton.Size = new Size(156, 41);
            PasteButton.TabIndex = 1;
            PasteButton.Text = "Paste";
            // 
            // FormSVGIcon
            // 
            tablePanel1.SetColumn(FormSVGIcon, 0);
            FormSVGIcon.Dock = DockStyle.Fill;
            FormSVGIcon.ImageAlignment = ContentAlignment.TopCenter;
            FormSVGIcon.Location = new Point(13, 57);
            FormSVGIcon.Name = "FormSVGIcon";
            tablePanel1.SetRow(FormSVGIcon, 1);
            tablePanel1.SetRowSpan(FormSVGIcon, 2);
            FormSVGIcon.Size = new Size(76, 203);
            FormSVGIcon.SizeMode = DevExpress.XtraEditors.SvgImageSizeMode.Zoom;
            FormSVGIcon.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("FormSVGIcon.SvgImage");
            FormSVGIcon.TabIndex = 0;
            // 
            // LicenseForm
            // 
            AcceptButton = ActivateButton;
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new SizeF(6F, 13F);
            AutoScaleMode = AutoScaleMode.Font;
            CancelButton = CloseButton;
            ClientSize = new Size(598, 318);
            Controls.Add(tablePanel1);
            DoubleBuffered = true;
            Font = new Font("Segoe UI", 8.25F, FontStyle.Regular, GraphicsUnit.Point);
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("LicenseForm.IconOptions.SvgImage");
            Name = "LicenseForm";
            Text = "Activation";
            ((System.ComponentModel.ISupportInitialize)tablePanel1).EndInit();
            tablePanel1.ResumeLayout(false);
            tablePanel1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)LicenseCodeText.Properties).EndInit();
            ((System.ComponentModel.ISupportInitialize)FormSVGIcon).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.Utils.Layout.TablePanel tablePanel1;
        private DevExpress.XtraEditors.SvgImageBox FormSVGIcon;
        private DevExpress.XtraEditors.SimpleButton CloseButton;
        private DevExpress.XtraEditors.SimpleButton GetLicenseButton;
        private DevExpress.XtraEditors.SimpleButton ActivateButton;
        private DevExpress.XtraEditors.SimpleButton PasteButton;
        private DevExpress.XtraEditors.LabelControl ThanksLabel;
        private DevExpress.XtraEditors.LabelControl LicenseActiveLabel;
        private DevExpress.XtraEditors.HyperlinkLabelControl DeleteLicenseLink;
        private DevExpress.XtraEditors.TextEdit LicenseCodeText;
    }
}