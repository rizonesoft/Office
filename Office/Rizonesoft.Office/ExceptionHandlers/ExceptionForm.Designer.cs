namespace Rizonesoft.Office.ExceptionHandlers
{
    partial class ExceptionForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ExceptionForm));
            this.directXFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            this.mainTablePanel = new DevExpress.Utils.Layout.TablePanel();
            this.bugIntroLabel = new DevExpress.XtraEditors.LabelControl();
            this.buglTitelabel = new DevExpress.XtraEditors.LabelControl();
            this.bugSVGImage = new DevExpress.XtraEditors.SvgImageBox();
            this.cancelButton = new DevExpress.XtraEditors.SimpleButton();
            this.mailButton = new DevExpress.XtraEditors.SimpleButton();
            this.copyButton = new DevExpress.XtraEditors.SimpleButton();
            this.bugMemoEdit = new DevExpress.XtraEditors.MemoEdit();
            this.directXFormContainerControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.mainTablePanel)).BeginInit();
            this.mainTablePanel.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.bugSVGImage)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.bugMemoEdit.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // directXFormContainerControl1
            // 
            this.directXFormContainerControl1.Controls.Add(this.mainTablePanel);
            this.directXFormContainerControl1.Location = new System.Drawing.Point(1, 31);
            this.directXFormContainerControl1.Name = "directXFormContainerControl1";
            this.directXFormContainerControl1.Size = new System.Drawing.Size(648, 518);
            this.directXFormContainerControl1.TabIndex = 0;
            // 
            // mainTablePanel
            // 
            this.mainTablePanel.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] {
            new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 128F),
            new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 52F),
            new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 180F),
            new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 50F),
            new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 180F)});
            this.mainTablePanel.Controls.Add(this.bugIntroLabel);
            this.mainTablePanel.Controls.Add(this.buglTitelabel);
            this.mainTablePanel.Controls.Add(this.bugSVGImage);
            this.mainTablePanel.Controls.Add(this.cancelButton);
            this.mainTablePanel.Controls.Add(this.mailButton);
            this.mainTablePanel.Controls.Add(this.copyButton);
            this.mainTablePanel.Controls.Add(this.bugMemoEdit);
            this.mainTablePanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.mainTablePanel.Location = new System.Drawing.Point(0, 0);
            this.mainTablePanel.Name = "mainTablePanel";
            this.mainTablePanel.Padding = new System.Windows.Forms.Padding(5);
            this.mainTablePanel.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] {
            new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 28F),
            new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 100F),
            new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 1000F),
            new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 50F)});
            this.mainTablePanel.Size = new System.Drawing.Size(648, 518);
            this.mainTablePanel.TabIndex = 0;
            // 
            // bugIntroLabel
            // 
            this.bugIntroLabel.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.bugIntroLabel.Appearance.Options.UseFont = true;
            this.bugIntroLabel.Appearance.Options.UseTextOptions = true;
            this.bugIntroLabel.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            this.bugIntroLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            this.mainTablePanel.SetColumn(this.bugIntroLabel, 1);
            this.mainTablePanel.SetColumnSpan(this.bugIntroLabel, 4);
            this.bugIntroLabel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.bugIntroLabel.LineLocation = DevExpress.XtraEditors.LineLocation.Top;
            this.bugIntroLabel.Location = new System.Drawing.Point(136, 36);
            this.bugIntroLabel.Name = "bugIntroLabel";
            this.bugIntroLabel.Padding = new System.Windows.Forms.Padding(0, 5, 0, 0);
            this.mainTablePanel.SetRow(this.bugIntroLabel, 1);
            this.bugIntroLabel.Size = new System.Drawing.Size(504, 94);
            this.bugIntroLabel.TabIndex = 6;
            this.bugIntroLabel.Text = resources.GetString("bugIntroLabel.Text");
            // 
            // buglTitelabel
            // 
            this.buglTitelabel.Appearance.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.buglTitelabel.Appearance.Options.UseFont = true;
            this.buglTitelabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            this.mainTablePanel.SetColumn(this.buglTitelabel, 1);
            this.mainTablePanel.SetColumnSpan(this.buglTitelabel, 4);
            this.buglTitelabel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buglTitelabel.Location = new System.Drawing.Point(136, 8);
            this.buglTitelabel.Name = "buglTitelabel";
            this.mainTablePanel.SetRow(this.buglTitelabel, 0);
            this.buglTitelabel.Size = new System.Drawing.Size(504, 22);
            this.buglTitelabel.TabIndex = 5;
            this.buglTitelabel.Text = "Something went wrong!";
            // 
            // bugSVGImage
            // 
            this.mainTablePanel.SetColumn(this.bugSVGImage, 0);
            this.bugSVGImage.Dock = System.Windows.Forms.DockStyle.Fill;
            this.bugSVGImage.Location = new System.Drawing.Point(8, 8);
            this.bugSVGImage.Name = "bugSVGImage";
            this.bugSVGImage.Padding = new System.Windows.Forms.Padding(25);
            this.mainTablePanel.SetRow(this.bugSVGImage, 0);
            this.mainTablePanel.SetRowSpan(this.bugSVGImage, 2);
            this.bugSVGImage.Size = new System.Drawing.Size(122, 122);
            this.bugSVGImage.SizeMode = DevExpress.XtraEditors.SvgImageSizeMode.Zoom;
            this.bugSVGImage.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("bugSVGImage.SvgImage")));
            this.bugSVGImage.TabIndex = 4;
            this.bugSVGImage.Text = "svgImageBox1";
            // 
            // cancelButton
            // 
            this.cancelButton.Appearance.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.cancelButton.Appearance.Options.UseFont = true;
            this.mainTablePanel.SetColumn(this.cancelButton, 4);
            this.cancelButton.Dock = System.Windows.Forms.DockStyle.Fill;
            this.cancelButton.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("cancelButton.ImageOptions.SvgImage")));
            this.cancelButton.Location = new System.Drawing.Point(466, 466);
            this.cancelButton.Name = "cancelButton";
            this.mainTablePanel.SetRow(this.cancelButton, 3);
            this.cancelButton.Size = new System.Drawing.Size(174, 44);
            this.cancelButton.TabIndex = 3;
            this.cancelButton.Text = "Cancel";
            this.cancelButton.Click += new System.EventHandler(this.cancelButton_Click);
            // 
            // mailButton
            // 
            this.mailButton.Appearance.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.mailButton.Appearance.Options.UseFont = true;
            this.mainTablePanel.SetColumn(this.mailButton, 2);
            this.mailButton.Dock = System.Windows.Forms.DockStyle.Fill;
            this.mailButton.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("mailButton.ImageOptions.SvgImage")));
            this.mailButton.Location = new System.Drawing.Point(188, 466);
            this.mailButton.Name = "mailButton";
            this.mainTablePanel.SetRow(this.mailButton, 3);
            this.mailButton.Size = new System.Drawing.Size(174, 44);
            this.mailButton.TabIndex = 2;
            this.mailButton.Text = "Mail";
            // 
            // copyButton
            // 
            this.copyButton.Appearance.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.copyButton.Appearance.Options.UseFont = true;
            this.mainTablePanel.SetColumn(this.copyButton, 0);
            this.mainTablePanel.SetColumnSpan(this.copyButton, 2);
            this.copyButton.Dock = System.Windows.Forms.DockStyle.Fill;
            this.copyButton.ImageOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("copyButton.ImageOptions.SvgImage")));
            this.copyButton.Location = new System.Drawing.Point(8, 466);
            this.copyButton.Name = "copyButton";
            this.mainTablePanel.SetRow(this.copyButton, 3);
            this.copyButton.Size = new System.Drawing.Size(174, 44);
            this.copyButton.TabIndex = 1;
            this.copyButton.Text = "Copy";
            this.copyButton.Click += new System.EventHandler(this.copyButton_Click);
            // 
            // bugMemoEdit
            // 
            this.mainTablePanel.SetColumn(this.bugMemoEdit, 0);
            this.mainTablePanel.SetColumnSpan(this.bugMemoEdit, 5);
            this.bugMemoEdit.Dock = System.Windows.Forms.DockStyle.Fill;
            this.bugMemoEdit.Location = new System.Drawing.Point(8, 136);
            this.bugMemoEdit.Name = "bugMemoEdit";
            this.bugMemoEdit.Properties.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.bugMemoEdit.Properties.Appearance.Options.UseFont = true;
            this.mainTablePanel.SetRow(this.bugMemoEdit, 2);
            this.bugMemoEdit.Size = new System.Drawing.Size(632, 324);
            this.bugMemoEdit.TabIndex = 0;
            // 
            // ExceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(650, 550);
            this.Controls.Add(this.directXFormContainerControl1);
            this.DoubleBuffered = true;
            this.IconOptions.SvgImage = ((DevExpress.Utils.Svg.SvgImage)(resources.GetObject("ExceptionForm.IconOptions.SvgImage")));
            this.Name = "ExceptionForm";
            this.Padding = new System.Windows.Forms.Padding(5);
            this.Text = "Woops!";
            this.directXFormContainerControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.mainTablePanel)).EndInit();
            this.mainTablePanel.ResumeLayout(false);
            this.mainTablePanel.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.bugSVGImage)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.bugMemoEdit.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.DirectXFormContainerControl directXFormContainerControl1;
        private DevExpress.Utils.Layout.TablePanel mainTablePanel;
        private DevExpress.XtraEditors.SimpleButton cancelButton;
        private DevExpress.XtraEditors.SimpleButton mailButton;
        private DevExpress.XtraEditors.SimpleButton copyButton;
        private DevExpress.XtraEditors.MemoEdit bugMemoEdit;
        private DevExpress.XtraEditors.LabelControl bugIntroLabel;
        private DevExpress.XtraEditors.LabelControl buglTitelabel;
        private DevExpress.XtraEditors.SvgImageBox bugSVGImage;
    }
}