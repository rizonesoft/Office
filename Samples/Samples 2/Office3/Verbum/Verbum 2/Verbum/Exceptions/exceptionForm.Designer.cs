namespace Rizonesoft.Verbum
{
    partial class exceptionForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(exceptionForm));
            this.picExceptionIcon = new System.Windows.Forms.PictureBox();
            this.lblHead = new System.Windows.Forms.Label();
            this.lblDescription = new System.Windows.Forms.Label();
            this.memoDescription = new DevExpress.XtraEditors.MemoEdit();
            this.btnClose = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.picExceptionIcon)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoDescription.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // picExceptionIcon
            // 
            this.picExceptionIcon.Image = global::Verbum.Properties.Resources.Health;
            this.picExceptionIcon.Location = new System.Drawing.Point(12, 12);
            this.picExceptionIcon.Name = "picExceptionIcon";
            this.picExceptionIcon.Size = new System.Drawing.Size(48, 48);
            this.picExceptionIcon.TabIndex = 0;
            this.picExceptionIcon.TabStop = false;
            // 
            // lblHead
            // 
            this.lblHead.Font = new System.Drawing.Font("Tahoma", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblHead.Location = new System.Drawing.Point(80, 12);
            this.lblHead.Name = "lblHead";
            this.lblHead.Size = new System.Drawing.Size(439, 23);
            this.lblHead.TabIndex = 1;
            this.lblHead.Text = "Sorry, an unexpected error occurred!";
            // 
            // lblDescription
            // 
            this.lblDescription.Font = new System.Drawing.Font("Tahoma", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblDescription.Location = new System.Drawing.Point(80, 46);
            this.lblDescription.Name = "lblDescription";
            this.lblDescription.Size = new System.Drawing.Size(439, 78);
            this.lblDescription.TabIndex = 2;
            this.lblDescription.Text = resources.GetString("lblDescription.Text");
            // 
            // memoDescription
            // 
            this.memoDescription.Location = new System.Drawing.Point(12, 163);
            this.memoDescription.Name = "memoDescription";
            this.memoDescription.Size = new System.Drawing.Size(507, 200);
            this.memoDescription.TabIndex = 3;
            // 
            // btnClose
            // 
            this.btnClose.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.btnClose.Location = new System.Drawing.Point(388, 370);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(130, 40);
            this.btnClose.TabIndex = 4;
            this.btnClose.Text = "&Close";
            // 
            // exceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.btnClose;
            this.ClientSize = new System.Drawing.Size(534, 422);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.memoDescription);
            this.Controls.Add(this.lblDescription);
            this.Controls.Add(this.lblHead);
            this.Controls.Add(this.picExceptionIcon);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "exceptionForm";
            this.Text = "Booboo!";
            ((System.ComponentModel.ISupportInitialize)(this.picExceptionIcon)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoDescription.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox picExceptionIcon;
        private System.Windows.Forms.Label lblHead;
        private System.Windows.Forms.Label lblDescription;
        private DevExpress.XtraEditors.MemoEdit memoDescription;
        private DevExpress.XtraEditors.SimpleButton btnClose;
    }
}