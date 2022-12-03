namespace RichEditTOCGeneration {
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
            this.richEditControl1 = new DevExpress.XtraRichEdit.RichEditControl();
            this.label1 = new System.Windows.Forms.Label();
            this.btnStyles = new System.Windows.Forms.Button();
            this.btnOutlineLevels = new System.Windows.Forms.Button();
            this.btnTCFields = new System.Windows.Forms.Button();
            this.btnLoadTemplate = new System.Windows.Forms.Button();
            this.btnShowAllFieldCodes = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // richEditControl1
            // 
            this.richEditControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.richEditControl1.Location = new System.Drawing.Point(12, 42);
            this.richEditControl1.Name = "richEditControl1";
            this.richEditControl1.Size = new System.Drawing.Size(1263, 620);
            this.richEditControl1.TabIndex = 0;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft Sans Serif", 7.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.label1.Location = new System.Drawing.Point(398, 15);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(208, 17);
            this.label1.TabIndex = 1;
            this.label1.Text = "Build Table Of Contents by:";
            // 
            // btnStyles
            // 
            this.btnStyles.Location = new System.Drawing.Point(612, 11);
            this.btnStyles.Name = "btnStyles";
            this.btnStyles.Size = new System.Drawing.Size(127, 25);
            this.btnStyles.TabIndex = 2;
            this.btnStyles.Text = "Styles";
            this.btnStyles.UseVisualStyleBackColor = true;
            this.btnStyles.Click += new System.EventHandler(this.btnStyles_Click);
            // 
            // btnOutlineLevels
            // 
            this.btnOutlineLevels.Location = new System.Drawing.Point(745, 11);
            this.btnOutlineLevels.Name = "btnOutlineLevels";
            this.btnOutlineLevels.Size = new System.Drawing.Size(127, 25);
            this.btnOutlineLevels.TabIndex = 3;
            this.btnOutlineLevels.Text = "Outline Levels";
            this.btnOutlineLevels.UseVisualStyleBackColor = true;
            this.btnOutlineLevels.Click += new System.EventHandler(this.btnOutlineLevels_Click);
            // 
            // btnTCFields
            // 
            this.btnTCFields.Location = new System.Drawing.Point(878, 11);
            this.btnTCFields.Name = "btnTCFields";
            this.btnTCFields.Size = new System.Drawing.Size(127, 25);
            this.btnTCFields.TabIndex = 4;
            this.btnTCFields.Text = "TC Fields";
            this.btnTCFields.UseVisualStyleBackColor = true;
            this.btnTCFields.Click += new System.EventHandler(this.btnTCFields_Click);
            // 
            // btnLoadTemplate
            // 
            this.btnLoadTemplate.Location = new System.Drawing.Point(12, 11);
            this.btnLoadTemplate.Name = "btnLoadTemplate";
            this.btnLoadTemplate.Size = new System.Drawing.Size(127, 25);
            this.btnLoadTemplate.TabIndex = 5;
            this.btnLoadTemplate.Text = "Load Template";
            this.btnLoadTemplate.UseVisualStyleBackColor = true;
            this.btnLoadTemplate.Click += new System.EventHandler(this.btnLoadTemplate_Click);
            // 
            // btnShowAllFieldCodes
            // 
            this.btnShowAllFieldCodes.Location = new System.Drawing.Point(145, 11);
            this.btnShowAllFieldCodes.Name = "btnShowAllFieldCodes";
            this.btnShowAllFieldCodes.Size = new System.Drawing.Size(127, 25);
            this.btnShowAllFieldCodes.TabIndex = 6;
            this.btnShowAllFieldCodes.Text = "Show All Field Codes";
            this.btnShowAllFieldCodes.UseVisualStyleBackColor = true;
            this.btnShowAllFieldCodes.Click += new System.EventHandler(this.btnShowAllFieldCodes_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1287, 674);
            this.Controls.Add(this.btnShowAllFieldCodes);
            this.Controls.Add(this.btnLoadTemplate);
            this.Controls.Add(this.btnTCFields);
            this.Controls.Add(this.btnOutlineLevels);
            this.Controls.Add(this.btnStyles);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.richEditControl1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraRichEdit.RichEditControl richEditControl1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Button btnStyles;
        private System.Windows.Forms.Button btnOutlineLevels;
        private System.Windows.Forms.Button btnTCFields;
        private System.Windows.Forms.Button btnLoadTemplate;
        private System.Windows.Forms.Button btnShowAllFieldCodes;
    }
}

