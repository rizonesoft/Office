namespace Rizonesoft.Office.ExceptionHandlers
{
    sealed partial class ExceptionForm
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
            directXFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            mainTablePanel = new DevExpress.Utils.Layout.TablePanel();
            bugIntroLabel = new DevExpress.XtraEditors.LabelControl();
            buglTitelabel = new DevExpress.XtraEditors.LabelControl();
            bugSVGImage = new DevExpress.XtraEditors.SvgImageBox();
            cancelButton = new DevExpress.XtraEditors.SimpleButton();
            loggingButton = new DevExpress.XtraEditors.SimpleButton();
            copyButton = new DevExpress.XtraEditors.SimpleButton();
            bugMemoEdit = new DevExpress.XtraEditors.MemoEdit();
            directXFormContainerControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)mainTablePanel).BeginInit();
            mainTablePanel.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)bugSVGImage).BeginInit();
            ((System.ComponentModel.ISupportInitialize)bugMemoEdit.Properties).BeginInit();
            SuspendLayout();
            // 
            // directXFormContainerControl1
            // 
            directXFormContainerControl1.Controls.Add(mainTablePanel);
            directXFormContainerControl1.Location = new Point(1, 46);
            directXFormContainerControl1.Margin = new Padding(4);
            directXFormContainerControl1.Name = "directXFormContainerControl1";
            directXFormContainerControl1.Size = new Size(998, 853);
            directXFormContainerControl1.TabIndex = 0;
            // 
            // mainTablePanel
            // 
            mainTablePanel.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 128F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 128F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 256F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 256F) });
            mainTablePanel.Controls.Add(bugIntroLabel);
            mainTablePanel.Controls.Add(buglTitelabel);
            mainTablePanel.Controls.Add(bugSVGImage);
            mainTablePanel.Controls.Add(cancelButton);
            mainTablePanel.Controls.Add(loggingButton);
            mainTablePanel.Controls.Add(copyButton);
            mainTablePanel.Controls.Add(bugMemoEdit);
            mainTablePanel.Dock = DockStyle.Fill;
            mainTablePanel.Location = new Point(0, 0);
            mainTablePanel.Margin = new Padding(4);
            mainTablePanel.Name = "mainTablePanel";
            mainTablePanel.Padding = new Padding(8, 7, 8, 7);
            mainTablePanel.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 50F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 120F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 1000F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 65F) });
            mainTablePanel.Size = new Size(998, 853);
            mainTablePanel.TabIndex = 0;
            // 
            // bugIntroLabel
            // 
            bugIntroLabel.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            bugIntroLabel.Appearance.Options.UseFont = true;
            bugIntroLabel.Appearance.Options.UseTextOptions = true;
            bugIntroLabel.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            bugIntroLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            mainTablePanel.SetColumn(bugIntroLabel, 1);
            mainTablePanel.SetColumnSpan(bugIntroLabel, 4);
            bugIntroLabel.Dock = DockStyle.Fill;
            bugIntroLabel.LineLocation = DevExpress.XtraEditors.LineLocation.Top;
            bugIntroLabel.Location = new Point(140, 61);
            bugIntroLabel.Margin = new Padding(4);
            bugIntroLabel.Name = "bugIntroLabel";
            bugIntroLabel.Padding = new Padding(0, 7, 0, 0);
            mainTablePanel.SetRow(bugIntroLabel, 1);
            bugIntroLabel.Size = new Size(846, 112);
            bugIntroLabel.TabIndex = 6;
            bugIntroLabel.Text = resources.GetString("bugIntroLabel.Text");
            // 
            // buglTitelabel
            // 
            buglTitelabel.Appearance.Font = new Font("Segoe UI", 12F, FontStyle.Regular, GraphicsUnit.Point);
            buglTitelabel.Appearance.Options.UseFont = true;
            buglTitelabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            mainTablePanel.SetColumn(buglTitelabel, 1);
            mainTablePanel.SetColumnSpan(buglTitelabel, 4);
            buglTitelabel.Dock = DockStyle.Fill;
            buglTitelabel.Location = new Point(140, 11);
            buglTitelabel.Margin = new Padding(4);
            buglTitelabel.Name = "buglTitelabel";
            mainTablePanel.SetRow(buglTitelabel, 0);
            buglTitelabel.Size = new Size(846, 42);
            buglTitelabel.TabIndex = 5;
            buglTitelabel.Text = "Something went wrong!";
            // 
            // bugSVGImage
            // 
            mainTablePanel.SetColumn(bugSVGImage, 0);
            bugSVGImage.Dock = DockStyle.Fill;
            bugSVGImage.Location = new Point(12, 11);
            bugSVGImage.Margin = new Padding(4);
            bugSVGImage.Name = "bugSVGImage";
            bugSVGImage.Padding = new Padding(15);
            mainTablePanel.SetRow(bugSVGImage, 0);
            mainTablePanel.SetRowSpan(bugSVGImage, 2);
            bugSVGImage.Size = new Size(120, 162);
            bugSVGImage.SizeMode = DevExpress.XtraEditors.SvgImageSizeMode.Zoom;
            bugSVGImage.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("bugSVGImage.SvgImage");
            bugSVGImage.TabIndex = 4;
            bugSVGImage.Text = "svgImageBox1";
            // 
            // cancelButton
            // 
            cancelButton.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            cancelButton.Appearance.Options.UseFont = true;
            mainTablePanel.SetColumn(cancelButton, 4);
            cancelButton.Dock = DockStyle.Fill;
            cancelButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("cancelButton.ImageOptions.SvgImage");
            cancelButton.Location = new Point(738, 785);
            cancelButton.Margin = new Padding(4);
            cancelButton.Name = "cancelButton";
            mainTablePanel.SetRow(cancelButton, 3);
            cancelButton.Size = new Size(248, 57);
            cancelButton.TabIndex = 3;
            cancelButton.Text = "Cancel";
            cancelButton.Click += cancelButton_Click;
            // 
            // loggingButton
            // 
            loggingButton.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            loggingButton.Appearance.Options.UseFont = true;
            mainTablePanel.SetColumn(loggingButton, 2);
            loggingButton.Dock = DockStyle.Fill;
            loggingButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("loggingButton.ImageOptions.SvgImage");
            loggingButton.Location = new Point(268, 785);
            loggingButton.Margin = new Padding(4);
            loggingButton.Name = "loggingButton";
            mainTablePanel.SetRow(loggingButton, 3);
            loggingButton.Size = new Size(248, 57);
            loggingButton.TabIndex = 2;
            loggingButton.Text = "Logging";
            loggingButton.Click += loggingButton_Click;
            // 
            // copyButton
            // 
            copyButton.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            copyButton.Appearance.Options.UseFont = true;
            mainTablePanel.SetColumn(copyButton, 0);
            mainTablePanel.SetColumnSpan(copyButton, 2);
            copyButton.Dock = DockStyle.Fill;
            copyButton.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("copyButton.ImageOptions.SvgImage");
            copyButton.Location = new Point(12, 785);
            copyButton.Margin = new Padding(4);
            copyButton.Name = "copyButton";
            mainTablePanel.SetRow(copyButton, 3);
            copyButton.Size = new Size(248, 57);
            copyButton.TabIndex = 1;
            copyButton.Text = "Copy";
            copyButton.Click += copyButton_Click;
            // 
            // bugMemoEdit
            // 
            mainTablePanel.SetColumn(bugMemoEdit, 0);
            mainTablePanel.SetColumnSpan(bugMemoEdit, 5);
            bugMemoEdit.Dock = DockStyle.Fill;
            bugMemoEdit.Location = new Point(12, 181);
            bugMemoEdit.Margin = new Padding(4);
            bugMemoEdit.Name = "bugMemoEdit";
            bugMemoEdit.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            bugMemoEdit.Properties.Appearance.Options.UseFont = true;
            mainTablePanel.SetRow(bugMemoEdit, 2);
            bugMemoEdit.Size = new Size(974, 596);
            bugMemoEdit.TabIndex = 0;
            // 
            // ExceptionForm
            // 
            AutoScaleDimensions = new SizeF(9F, 19F);
            AutoScaleMode = AutoScaleMode.Font;
            ChildControls.Add(directXFormContainerControl1);
            ClientSize = new Size(1000, 900);
            DoubleBuffered = true;
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("ExceptionForm.IconOptions.SvgImage");
            Margin = new Padding(4);
            Name = "ExceptionForm";
            Padding = new Padding(8, 7, 8, 7);
            Text = "Woops!";
            directXFormContainerControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)mainTablePanel).EndInit();
            mainTablePanel.ResumeLayout(false);
            mainTablePanel.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)bugSVGImage).EndInit();
            ((System.ComponentModel.ISupportInitialize)bugMemoEdit.Properties).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraEditors.DirectXFormContainerControl directXFormContainerControl1;
        private DevExpress.Utils.Layout.TablePanel mainTablePanel;
        private DevExpress.XtraEditors.SimpleButton cancelButton;
        private DevExpress.XtraEditors.SimpleButton loggingButton;
        private DevExpress.XtraEditors.SimpleButton copyButton;
        private DevExpress.XtraEditors.MemoEdit bugMemoEdit;
        private DevExpress.XtraEditors.LabelControl bugIntroLabel;
        private DevExpress.XtraEditors.LabelControl buglTitelabel;
        private DevExpress.XtraEditors.SvgImageBox bugSVGImage;
    }
}