namespace Rizonesoft.Verbum
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
            this.picExIcon = new System.Windows.Forms.PictureBox();
            this.lblHead = new DevExpress.XtraEditors.LabelControl();
            this.lblDesc = new DevExpress.XtraEditors.LabelControl();
            this.linkSupport = new System.Windows.Forms.LinkLabel();
            this.memoExDesc = new DevExpress.XtraEditors.MemoEdit();
            this.btnClose = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // picExIcon
            // 
            this.picExIcon.Image = global::Rizonesoft.Properties.Resources.ShieldError;
            this.picExIcon.Location = new System.Drawing.Point(12, 12);
            this.picExIcon.Name = "picExIcon";
            this.picExIcon.Size = new System.Drawing.Size(70, 70);
            this.picExIcon.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this.picExIcon.TabIndex = 0;
            this.picExIcon.TabStop = false;
            // 
            // lblHead
            // 
            this.lblHead.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.lblHead.Appearance.Font = new System.Drawing.Font("Tahoma", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblHead.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.lblHead.Location = new System.Drawing.Point(88, 12);
            this.lblHead.Name = "lblHead";
            this.lblHead.Size = new System.Drawing.Size(430, 25);
            this.lblHead.TabIndex = 1;
            this.lblHead.Text = "Sorry, an unexpected error occurred.";
            // 
            // lblDesc
            // 
            this.lblDesc.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.lblDesc.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            this.lblDesc.Location = new System.Drawing.Point(88, 43);
            this.lblDesc.Name = "lblDesc";
            this.lblDesc.Size = new System.Drawing.Size(430, 52);
            this.lblDesc.TabIndex = 2;
            this.lblDesc.Text = resources.GetString("lblDesc.Text");
            // 
            // linkSupport
            // 
            this.linkSupport.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.linkSupport.Location = new System.Drawing.Point(85, 98);
            this.linkSupport.Name = "linkSupport";
            this.linkSupport.Size = new System.Drawing.Size(433, 20);
            this.linkSupport.TabIndex = 3;
            this.linkSupport.TabStop = true;
            this.linkSupport.Text = "http://www.rizonesoft.com/support";
            this.linkSupport.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // memoExDesc
            // 
            this.memoExDesc.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.memoExDesc.Location = new System.Drawing.Point(12, 134);
            this.memoExDesc.Name = "memoExDesc";
            this.memoExDesc.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Buffered;
            this.memoExDesc.Properties.HideSelection = false;
            this.memoExDesc.Properties.UseParentBackground = true;
            this.memoExDesc.Size = new System.Drawing.Size(510, 200);
            this.memoExDesc.TabIndex = 4;
            // 
            // btnClose
            // 
            this.btnClose.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClose.Location = new System.Drawing.Point(422, 341);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(100, 30);
            this.btnClose.TabIndex = 5;
            this.btnClose.Text = "Close";
            // 
            // XtraForm1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(534, 382);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.memoExDesc);
            this.Controls.Add(this.linkSupport);
            this.Controls.Add(this.lblDesc);
            this.Controls.Add(this.lblHead);
            this.Controls.Add(this.picExIcon);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "XtraForm1";
            this.Text = "Booboo!";
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox picExIcon;
        private DevExpress.XtraEditors.LabelControl lblHead;
        private DevExpress.XtraEditors.LabelControl lblDesc;
        private System.Windows.Forms.LinkLabel linkSupport;
        private DevExpress.XtraEditors.MemoEdit memoExDesc;
        private DevExpress.XtraEditors.SimpleButton btnClose;
    }
}