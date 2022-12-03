namespace BeforeImport {
    partial class Form1 {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing) {
            if(disposing && (components != null)) {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent() {
            this.panelControl1 = new DevExpress.XtraEditors.PanelControl();
            this.rgImgPath = new DevExpress.XtraEditors.RadioGroup();
            this.labelControl1 = new DevExpress.XtraEditors.LabelControl();
            this.richEditControl1 = new DevExpress.XtraRichEdit.RichEditControl();
            this.xtraTabControl1 = new DevExpress.XtraTab.XtraTabControl();
            this.tbLoadHTML = new DevExpress.XtraTab.XtraTabPage();
            this.tbLoadText = new DevExpress.XtraTab.XtraTabPage();
            this.richEditControl2 = new DevExpress.XtraRichEdit.RichEditControl();
            this.panelControl2 = new DevExpress.XtraEditors.PanelControl();
            this.btnLoadRTF = new DevExpress.XtraEditors.SimpleButton();
            this.cmbEncodings = new DevExpress.XtraEditors.ComboBoxEdit();
            this.labelControl2 = new DevExpress.XtraEditors.LabelControl();
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).BeginInit();
            this.panelControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.rgImgPath.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.xtraTabControl1)).BeginInit();
            this.xtraTabControl1.SuspendLayout();
            this.tbLoadHTML.SuspendLayout();
            this.tbLoadText.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.panelControl2)).BeginInit();
            this.panelControl2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.cmbEncodings.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // panelControl1
            // 
            this.panelControl1.Controls.Add(this.rgImgPath);
            this.panelControl1.Controls.Add(this.labelControl1);
            this.panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelControl1.Location = new System.Drawing.Point(0, 0);
            this.panelControl1.Name = "panelControl1";
            this.panelControl1.Size = new System.Drawing.Size(717, 40);
            this.panelControl1.TabIndex = 0;
            // 
            // rgImgPath
            // 
            this.rgImgPath.EditValue = "//Img01/";
            this.rgImgPath.Location = new System.Drawing.Point(5, 5);
            this.rgImgPath.Name = "rgImgPath";
            this.rgImgPath.Properties.Items.AddRange(new DevExpress.XtraEditors.Controls.RadioGroupItem[] {
            new DevExpress.XtraEditors.Controls.RadioGroupItem("//Img01/", "Img01"),
            new DevExpress.XtraEditors.Controls.RadioGroupItem("//Img02/", "Img02")});
            this.rgImgPath.Size = new System.Drawing.Size(132, 30);
            this.rgImgPath.TabIndex = 2;
            this.rgImgPath.SelectedIndexChanged += new System.EventHandler(this.rgImgPath_SelectedIndexChanged);
            // 
            // labelControl1
            // 
            this.labelControl1.Location = new System.Drawing.Point(143, 21);
            this.labelControl1.Name = "labelControl1";
            this.labelControl1.Size = new System.Drawing.Size(63, 13);
            this.labelControl1.TabIndex = 1;
            this.labelControl1.Text = "labelControl1";
            // 
            // richEditControl1
            // 
            this.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEditControl1.Location = new System.Drawing.Point(0, 40);
            this.richEditControl1.Name = "richEditControl1";
            this.richEditControl1.Size = new System.Drawing.Size(717, 365);
            this.richEditControl1.TabIndex = 1;
            this.richEditControl1.Text = "richEditControl1";
            this.richEditControl1.BeforeImport += new DevExpress.XtraRichEdit.BeforeImportEventHandler(this.richEditControl1_BeforeImport);
            // 
            // xtraTabControl1
            // 
            this.xtraTabControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.xtraTabControl1.Location = new System.Drawing.Point(0, 0);
            this.xtraTabControl1.Name = "xtraTabControl1";
            this.xtraTabControl1.SelectedTabPage = this.tbLoadHTML;
            this.xtraTabControl1.Size = new System.Drawing.Size(724, 434);
            this.xtraTabControl1.TabIndex = 2;
            this.xtraTabControl1.TabPages.AddRange(new DevExpress.XtraTab.XtraTabPage[] {
            this.tbLoadHTML,
            this.tbLoadText});
            // 
            // tbLoadHTML
            // 
            this.tbLoadHTML.Controls.Add(this.richEditControl1);
            this.tbLoadHTML.Controls.Add(this.panelControl1);
            this.tbLoadHTML.Name = "tbLoadHTML";
            this.tbLoadHTML.Size = new System.Drawing.Size(717, 405);
            this.tbLoadHTML.Text = "Load HTML";
            // 
            // tbLoadText
            // 
            this.tbLoadText.Controls.Add(this.richEditControl2);
            this.tbLoadText.Controls.Add(this.panelControl2);
            this.tbLoadText.Name = "tbLoadText";
            this.tbLoadText.Size = new System.Drawing.Size(717, 405);
            this.tbLoadText.Text = "Load Text";
            // 
            // richEditControl2
            // 
            this.richEditControl2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEditControl2.Location = new System.Drawing.Point(0, 40);
            this.richEditControl2.Name = "richEditControl2";
            this.richEditControl2.Size = new System.Drawing.Size(717, 365);
            this.richEditControl2.TabIndex = 0;
            this.richEditControl2.Text = "richEditControl2";
            this.richEditControl2.BeforeImport += new DevExpress.XtraRichEdit.BeforeImportEventHandler(this.richEditControl2_BeforeImport);
            // 
            // panelControl2
            // 
            this.panelControl2.Controls.Add(this.btnLoadRTF);
            this.panelControl2.Controls.Add(this.cmbEncodings);
            this.panelControl2.Controls.Add(this.labelControl2);
            this.panelControl2.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelControl2.Location = new System.Drawing.Point(0, 0);
            this.panelControl2.Name = "panelControl2";
            this.panelControl2.Size = new System.Drawing.Size(717, 40);
            this.panelControl2.TabIndex = 1;
            // 
            // btnLoadRTF
            // 
            this.btnLoadRTF.Location = new System.Drawing.Point(143, 10);
            this.btnLoadRTF.Name = "btnLoadRTF";
            this.btnLoadRTF.Size = new System.Drawing.Size(75, 20);
            this.btnLoadRTF.TabIndex = 3;
            this.btnLoadRTF.Text = "Load";
            this.btnLoadRTF.Click += new System.EventHandler(this.btnLoadRTF_Click);
            // 
            // cmbEncodings
            // 
            this.cmbEncodings.Location = new System.Drawing.Point(5, 10);
            this.cmbEncodings.Name = "cmbEncodings";
            this.cmbEncodings.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.cmbEncodings.Properties.TextEditStyle = DevExpress.XtraEditors.Controls.TextEditStyles.DisableTextEditor;
            this.cmbEncodings.Size = new System.Drawing.Size(132, 20);
            this.cmbEncodings.TabIndex = 2;
            // 
            // labelControl2
            // 
            this.labelControl2.Location = new System.Drawing.Point(224, 14);
            this.labelControl2.Name = "labelControl2";
            this.labelControl2.Size = new System.Drawing.Size(63, 13);
            this.labelControl2.TabIndex = 1;
            this.labelControl2.Text = "labelControl2";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(724, 434);
            this.Controls.Add(this.xtraTabControl1);
            this.Name = "Form1";
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).EndInit();
            this.panelControl1.ResumeLayout(false);
            this.panelControl1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.rgImgPath.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.xtraTabControl1)).EndInit();
            this.xtraTabControl1.ResumeLayout(false);
            this.tbLoadHTML.ResumeLayout(false);
            this.tbLoadText.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.panelControl2)).EndInit();
            this.panelControl2.ResumeLayout(false);
            this.panelControl2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.cmbEncodings.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.PanelControl panelControl1;
        private DevExpress.XtraRichEdit.RichEditControl richEditControl1;
        private DevExpress.XtraEditors.LabelControl labelControl1;
        private DevExpress.XtraEditors.RadioGroup rgImgPath;
        private DevExpress.XtraTab.XtraTabControl xtraTabControl1;
        private DevExpress.XtraTab.XtraTabPage tbLoadHTML;
        private DevExpress.XtraTab.XtraTabPage tbLoadText;
        private DevExpress.XtraEditors.PanelControl panelControl2;
        private DevExpress.XtraEditors.LabelControl labelControl2;
        private DevExpress.XtraRichEdit.RichEditControl richEditControl2;
        private DevExpress.XtraEditors.ComboBoxEdit cmbEncodings;
        private DevExpress.XtraEditors.SimpleButton btnLoadRTF;
    }
}

