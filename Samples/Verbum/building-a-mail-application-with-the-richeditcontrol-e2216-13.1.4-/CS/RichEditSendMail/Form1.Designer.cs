namespace RichEditSendMail {
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
            if (disposing && (components != null)) {
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
            this.richEdit = new DevExpress.XtraRichEdit.RichEditControl();
            this.btnSend = new System.Windows.Forms.Button();
            this.lblSubject = new System.Windows.Forms.Label();
            this.edtSubject = new System.Windows.Forms.TextBox();
            this.lblTo = new System.Windows.Forms.Label();
            this.edtTo = new System.Windows.Forms.TextBox();
            this.lblSmtp = new System.Windows.Forms.Label();
            this.edtSmtp = new System.Windows.Forms.TextBox();
            this.panelControl1 = new DevExpress.XtraEditors.PanelControl();
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).BeginInit();
            this.panelControl1.SuspendLayout();
            this.SuspendLayout();
            // 
            // richEdit
            // 
            this.richEdit.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEdit.Location = new System.Drawing.Point(0, 0);
            this.richEdit.Name = "richEdit";
            this.richEdit.Size = new System.Drawing.Size(805, 391);
            this.richEdit.TabIndex = 4;
            // 
            // btnSend
            // 
            this.btnSend.Dock = System.Windows.Forms.DockStyle.Right;
            this.btnSend.Location = new System.Drawing.Point(728, 2);
            this.btnSend.Name = "btnSend";
            this.btnSend.Size = new System.Drawing.Size(75, 58);
            this.btnSend.TabIndex = 3;
            this.btnSend.Text = "Send Mail";
            this.btnSend.UseVisualStyleBackColor = true;
            this.btnSend.Click += new System.EventHandler(this.btnSend_Click);
            // 
            // lblSubject
            // 
            this.lblSubject.AutoSize = true;
            this.lblSubject.Location = new System.Drawing.Point(7, 13);
            this.lblSubject.Name = "lblSubject";
            this.lblSubject.Size = new System.Drawing.Size(46, 13);
            this.lblSubject.TabIndex = 2;
            this.lblSubject.Text = "Subject:";
            // 
            // edtSubject
            // 
            this.edtSubject.Location = new System.Drawing.Point(59, 10);
            this.edtSubject.Name = "edtSubject";
            this.edtSubject.Size = new System.Drawing.Size(199, 20);
            this.edtSubject.TabIndex = 0;
            this.edtSubject.Text = "Hey, look at this!";
            // 
            // lblTo
            // 
            this.lblTo.AutoSize = true;
            this.lblTo.Location = new System.Drawing.Point(7, 39);
            this.lblTo.Name = "lblTo";
            this.lblTo.Size = new System.Drawing.Size(23, 13);
            this.lblTo.TabIndex = 2;
            this.lblTo.Text = "To:";
            // 
            // edtTo
            // 
            this.edtTo.Location = new System.Drawing.Point(59, 36);
            this.edtTo.Name = "edtTo";
            this.edtTo.Size = new System.Drawing.Size(199, 20);
            this.edtTo.TabIndex = 1;
            // 
            // lblSmtp
            // 
            this.lblSmtp.AutoSize = true;
            this.lblSmtp.Location = new System.Drawing.Point(272, 13);
            this.lblSmtp.Name = "lblSmtp";
            this.lblSmtp.Size = new System.Drawing.Size(60, 13);
            this.lblSmtp.TabIndex = 2;
            this.lblSmtp.Text = "MailServer:";
            // 
            // edtSmtp
            // 
            this.edtSmtp.Location = new System.Drawing.Point(338, 10);
            this.edtSmtp.Name = "edtSmtp";
            this.edtSmtp.Size = new System.Drawing.Size(199, 20);
            this.edtSmtp.TabIndex = 2;
            // 
            // panelControl1
            // 
            this.panelControl1.Controls.Add(this.btnSend);
            this.panelControl1.Controls.Add(this.edtTo);
            this.panelControl1.Controls.Add(this.lblSubject);
            this.panelControl1.Controls.Add(this.lblTo);
            this.panelControl1.Controls.Add(this.edtSubject);
            this.panelControl1.Controls.Add(this.edtSmtp);
            this.panelControl1.Controls.Add(this.lblSmtp);
            this.panelControl1.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.panelControl1.Location = new System.Drawing.Point(0, 391);
            this.panelControl1.Name = "panelControl1";
            this.panelControl1.Size = new System.Drawing.Size(805, 62);
            this.panelControl1.TabIndex = 4;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(805, 453);
            this.Controls.Add(this.richEdit);
            this.Controls.Add(this.panelControl1);
            this.Name = "Form1";
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).EndInit();
            this.panelControl1.ResumeLayout(false);
            this.panelControl1.PerformLayout();
            this.ResumeLayout(false);

        }

        DevExpress.XtraRichEdit.RichEditControl richEdit;
        #endregion
        private System.Windows.Forms.Button btnSend;
        private System.Windows.Forms.Label lblSubject;
        private System.Windows.Forms.TextBox edtSubject;
        private System.Windows.Forms.Label lblTo;
        private System.Windows.Forms.TextBox edtTo;
        private System.Windows.Forms.Label lblSmtp;
        private System.Windows.Forms.TextBox edtSmtp;
        private DevExpress.XtraEditors.PanelControl panelControl1;
    }
}

