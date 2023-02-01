namespace RichEditCommandExample {
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
            this.btnToggleReadonly = new DevExpress.XtraEditors.SimpleButton();
            this.btnRedo = new DevExpress.XtraEditors.SimpleButton();
            this.chkToggleFontBold = new DevExpress.XtraEditors.CheckEdit();
            this.btnUndo = new RichEditCommandExample.CommandButton();
            ((System.ComponentModel.ISupportInitialize)(this.chkToggleFontBold.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // richEditControl1
            // 
            this.richEditControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.richEditControl1.Location = new System.Drawing.Point(12, 66);
            this.richEditControl1.Name = "richEditControl1";
            this.richEditControl1.Size = new System.Drawing.Size(542, 323);
            this.richEditControl1.TabIndex = 0;
            this.richEditControl1.Text = "richEditControl1";
            // 
            // btnToggleReadonly
            // 
            this.btnToggleReadonly.Location = new System.Drawing.Point(430, 12);
            this.btnToggleReadonly.Name = "btnToggleReadonly";
            this.btnToggleReadonly.Size = new System.Drawing.Size(124, 23);
            this.btnToggleReadonly.TabIndex = 3;
            this.btnToggleReadonly.Text = "Toggle ReadOnly";
            this.btnToggleReadonly.Click += new System.EventHandler(this.btnToggleReadOnly_Click);
            // 
            // btnRedo
            // 
            this.btnRedo.Location = new System.Drawing.Point(76, 12);
            this.btnRedo.Name = "btnRedo";
            this.btnRedo.Size = new System.Drawing.Size(58, 23);
            this.btnRedo.TabIndex = 1;
            this.btnRedo.Text = "Redo";
            // 
            // chkToggleFontBold
            // 
            this.chkToggleFontBold.Location = new System.Drawing.Point(12, 41);
            this.chkToggleFontBold.Name = "chkToggleFontBold";
            this.chkToggleFontBold.Properties.Caption = "Toggle Font Bold";
            this.chkToggleFontBold.Size = new System.Drawing.Size(122, 19);
            this.chkToggleFontBold.TabIndex = 4;
            // 
            // btnUndo
            // 
            this.btnUndo.Location = new System.Drawing.Point(12, 12);
            this.btnUndo.Name = "btnUndo";
            this.btnUndo.Size = new System.Drawing.Size(58, 23);
            this.btnUndo.TabIndex = 1;
            this.btnUndo.Text = "Undo";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(566, 401);
            this.Controls.Add(this.chkToggleFontBold);
            this.Controls.Add(this.btnToggleReadonly);
            this.Controls.Add(this.btnRedo);
            this.Controls.Add(this.btnUndo);
            this.Controls.Add(this.richEditControl1);
            this.Name = "Form1";
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.chkToggleFontBold.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraRichEdit.RichEditControl richEditControl1;
        private CommandButton btnUndo;
        private DevExpress.XtraEditors.SimpleButton btnToggleReadonly;
        private DevExpress.XtraEditors.SimpleButton btnRedo;
        private DevExpress.XtraEditors.CheckEdit chkToggleFontBold;
    }
}

