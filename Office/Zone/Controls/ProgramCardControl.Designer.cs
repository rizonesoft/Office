namespace Rizonesoft.Office.Zone.Controls
{
    sealed partial class ProgramCardControl
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

        #region Component Designer generated code

        /// <summary> 
        /// Required method for Designer support - do not modify 
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            DevExpress.XtraEditors.ButtonsPanelControl.ButtonImageOptions buttonImageOptions1 = new DevExpress.XtraEditors.ButtonsPanelControl.ButtonImageOptions();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ProgramCardControl));
            groupProgram = new DevExpress.XtraEditors.GroupControl();
            panelTools = new DevExpress.XtraEditors.PanelControl();
            labelProgram = new DevExpress.XtraEditors.LabelControl();
            lblImage = new DevExpress.XtraEditors.LabelControl();
            toggleShortcut = new DevExpress.XtraEditors.ToggleSwitch();
            ((System.ComponentModel.ISupportInitialize)groupProgram).BeginInit();
            groupProgram.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)panelTools).BeginInit();
            panelTools.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)toggleShortcut.Properties).BeginInit();
            SuspendLayout();
            // 
            // groupProgram
            // 
            groupProgram.AppearanceCaption.Font = new System.Drawing.Font("Segoe UI", 10F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            groupProgram.AppearanceCaption.Options.UseFont = true;
            groupProgram.AppearanceCaption.Options.UseTextOptions = true;
            groupProgram.AppearanceCaption.TextOptions.Trimming = DevExpress.Utils.Trimming.EllipsisWord;
            groupProgram.AutoSize = true;
            groupProgram.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            groupProgram.Controls.Add(panelTools);
            groupProgram.Controls.Add(toggleShortcut);
            buttonImageOptions1.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("buttonImageOptions1.SvgImage");
            buttonImageOptions1.SvgImageSize = new System.Drawing.Size(16, 16);
            groupProgram.CustomHeaderButtons.AddRange(new DevExpress.XtraEditors.ButtonPanel.IBaseButton[] { new DevExpress.XtraEditors.ButtonsPanelControl.GroupBoxButton("Run", false, buttonImageOptions1, DevExpress.XtraBars.Docking2010.ButtonStyle.PushButton, "", -1, true, null, true, false, true, "Run", -1) });
            groupProgram.CustomHeaderButtonsLocation = DevExpress.Utils.GroupElementLocation.AfterText;
            groupProgram.Dock = System.Windows.Forms.DockStyle.Fill;
            groupProgram.Location = new System.Drawing.Point(5, 6);
            groupProgram.Name = "groupProgram";
            groupProgram.Padding = new System.Windows.Forms.Padding(10);
            groupProgram.Size = new System.Drawing.Size(340, 320);
            groupProgram.TabIndex = 2;
            groupProgram.TabStop = true;
            groupProgram.Text = "Caption";
            groupProgram.CustomButtonClick += GroupProgram_CustomButtonClick;
            groupProgram.Paint += GroupControl1_Paint;
            // 
            // panelTools
            // 
            panelTools.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            panelTools.Controls.Add(labelProgram);
            panelTools.Controls.Add(lblImage);
            panelTools.Dock = System.Windows.Forms.DockStyle.Fill;
            panelTools.Location = new System.Drawing.Point(12, 53);
            panelTools.Name = "panelTools";
            panelTools.Padding = new System.Windows.Forms.Padding(5, 6, 5, 6);
            panelTools.Size = new System.Drawing.Size(316, 221);
            panelTools.TabIndex = 2;
            panelTools.MouseEnter += GroupProgram_MouseEnter;
            panelTools.MouseLeave += GroupProgram_MouseLeave;
            // 
            // labelProgram
            // 
            labelProgram.Appearance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            labelProgram.Appearance.Options.UseFont = true;
            labelProgram.Appearance.Options.UseTextOptions = true;
            labelProgram.Appearance.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Near;
            labelProgram.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Center;
            labelProgram.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            labelProgram.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            labelProgram.Dock = System.Windows.Forms.DockStyle.Top;
            labelProgram.ImageAlignToText = DevExpress.XtraEditors.ImageAlignToText.LeftCenter;
            labelProgram.ImageOptions.Alignment = System.Drawing.ContentAlignment.TopLeft;
            labelProgram.ImageOptions.SvgImageColorizationMode = DevExpress.Utils.SvgImageColorizationMode.None;
            labelProgram.ImageOptions.SvgImageSize = new System.Drawing.Size(48, 48);
            labelProgram.IndentBetweenImageAndText = 10;
            labelProgram.Location = new System.Drawing.Point(15, 6);
            labelProgram.Name = "labelProgram";
            labelProgram.Padding = new System.Windows.Forms.Padding(10, 10, 0, 10);
            labelProgram.Size = new System.Drawing.Size(296, 45);
            labelProgram.TabIndex = 0;
            labelProgram.Text = "Description";
            labelProgram.Click += labelProgram_Click;
            // 
            // lblImage
            // 
            lblImage.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Horizontal;
            lblImage.Dock = System.Windows.Forms.DockStyle.Left;
            lblImage.ImageOptions.SvgImageColorizationMode = DevExpress.Utils.SvgImageColorizationMode.None;
            lblImage.Location = new System.Drawing.Point(5, 6);
            lblImage.Name = "lblImage";
            lblImage.Padding = new System.Windows.Forms.Padding(0, 10, 10, 10);
            lblImage.Size = new System.Drawing.Size(10, 41);
            lblImage.TabIndex = 1;
            lblImage.Click += lblImage_Click;
            lblImage.MouseEnter += LabelProgram_MouseEnter;
            lblImage.MouseLeave += LabelProgram_MouseLeave;
            // 
            // toggleShortcut
            // 
            toggleShortcut.Dock = System.Windows.Forms.DockStyle.Bottom;
            toggleShortcut.Location = new System.Drawing.Point(12, 274);
            toggleShortcut.Margin = new System.Windows.Forms.Padding(3, 22, 3, 3);
            toggleShortcut.Name = "toggleShortcut";
            toggleShortcut.Properties.Appearance.Options.UseTextOptions = true;
            toggleShortcut.Properties.Appearance.TextOptions.Trimming = DevExpress.Utils.Trimming.Word;
            toggleShortcut.Properties.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            toggleShortcut.Properties.ContentAlignment = DevExpress.Utils.HorzAlignment.Near;
            toggleShortcut.Properties.GlyphAlignment = DevExpress.Utils.HorzAlignment.Far;
            toggleShortcut.Properties.OffText = "Off";
            toggleShortcut.Properties.OnText = "On";
            toggleShortcut.Size = new System.Drawing.Size(316, 34);
            toggleShortcut.TabIndex = 1;
            toggleShortcut.TabStop = false;
            toggleShortcut.MouseEnter += GroupProgram_MouseEnter;
            toggleShortcut.MouseLeave += GroupProgram_MouseLeave;
            // 
            // ProgramCardControl
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(9F, 21F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            Controls.Add(groupProgram);
            DoubleBuffered = true;
            MaximumSize = new System.Drawing.Size(500, 332);
            MinimumSize = new System.Drawing.Size(300, 300);
            Name = "ProgramCardControl";
            Padding = new System.Windows.Forms.Padding(5, 6, 5, 6);
            Size = new System.Drawing.Size(350, 332);
            Load += ProgramControl_Load;
            ((System.ComponentModel.ISupportInitialize)groupProgram).EndInit();
            groupProgram.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)panelTools).EndInit();
            panelTools.ResumeLayout(false);
            panelTools.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)toggleShortcut.Properties).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion
        private DevExpress.XtraEditors.GroupControl groupProgram;
        private DevExpress.XtraEditors.PanelControl panelTools;
        private DevExpress.XtraEditors.LabelControl labelProgram;
        private DevExpress.XtraEditors.LabelControl lblImage;
        private DevExpress.XtraEditors.ToggleSwitch toggleShortcut;
    }
}
