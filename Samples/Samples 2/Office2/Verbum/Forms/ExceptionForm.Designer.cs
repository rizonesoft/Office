namespace Rizonesoft.Office.Verbum.Forms
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
            this.btnClose = new DevExpress.XtraEditors.SimpleButton();
            this.memoExDesc = new DevExpress.XtraEditors.MemoEdit();
            this.linkSupport = new System.Windows.Forms.LinkLabel();
            this.labelDesc = new DevExpress.XtraEditors.LabelControl();
            this.labelHead = new DevExpress.XtraEditors.LabelControl();
            this.picExIcon = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).BeginInit();
            this.SuspendLayout();
            // 
            // btnClose
            // 
            this.btnClose.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClose.Location = new System.Drawing.Point(467, 422);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(119, 34);
            this.btnClose.TabIndex = 5;
            this.btnClose.Text = "Close";
            // 
            // memoExDesc
            // 
            this.memoExDesc.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.memoExDesc.EditValue = "";
            this.memoExDesc.Location = new System.Drawing.Point(12, 129);
            this.memoExDesc.Name = "memoExDesc";
            this.memoExDesc.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Buffered;
            this.memoExDesc.Properties.HideSelection = false;
            this.memoExDesc.Properties.ReadOnly = true;
            this.memoExDesc.Size = new System.Drawing.Size(574, 279);
            this.memoExDesc.TabIndex = 7;
            this.memoExDesc.TabStop = false;
            // 
            // linkSupport
            // 
            this.linkSupport.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.linkSupport.Location = new System.Drawing.Point(53, 101);
            this.linkSupport.Name = "linkSupport";
            this.linkSupport.Size = new System.Drawing.Size(533, 25);
            this.linkSupport.TabIndex = 10;
            this.linkSupport.TabStop = true;
            this.linkSupport.Text = "https://www.rizonesoft.com";
            this.linkSupport.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // labelDesc
            // 
            this.labelDesc.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.labelDesc.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            this.labelDesc.Location = new System.Drawing.Point(53, 46);
            this.labelDesc.MaximumSize = new System.Drawing.Size(500, 100);
            this.labelDesc.Name = "labelDesc";
            this.labelDesc.Size = new System.Drawing.Size(497, 52);
            this.labelDesc.TabIndex = 6;
            this.labelDesc.Text = resources.GetString("labelDesc.Text");
            // 
            // labelHead
            // 
            this.labelHead.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.labelHead.Appearance.Font = new System.Drawing.Font("Tahoma", 9.75F);
            this.labelHead.Appearance.Options.UseFont = true;
            this.labelHead.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.labelHead.Location = new System.Drawing.Point(53, 16);
            this.labelHead.Name = "labelHead";
            this.labelHead.Size = new System.Drawing.Size(533, 24);
            this.labelHead.TabIndex = 8;
            this.labelHead.Text = "Sorry, an unexpected error occurred.";
            // 
            // picExIcon
            // 
            this.picExIcon.Image = ((System.Drawing.Image)(resources.GetObject("picExIcon.Image")));
            this.picExIcon.InitialImage = ((System.Drawing.Image)(resources.GetObject("picExIcon.InitialImage")));
            this.picExIcon.Location = new System.Drawing.Point(12, 16);
            this.picExIcon.Name = "picExIcon";
            this.picExIcon.Size = new System.Drawing.Size(32, 32);
            this.picExIcon.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this.picExIcon.TabIndex = 9;
            this.picExIcon.TabStop = false;
            // 
            // ExceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(598, 468);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.memoExDesc);
            this.Controls.Add(this.picExIcon);
            this.Controls.Add(this.linkSupport);
            this.Controls.Add(this.labelDesc);
            this.Controls.Add(this.labelHead);
            this.IconOptions.Icon = ((System.Drawing.Icon)(resources.GetObject("ExceptionForm.IconOptions.Icon")));
            this.MinimumSize = new System.Drawing.Size(550, 400);
            this.Name = "ExceptionForm";
            this.Text = "A bug was detected!";
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.SimpleButton btnClose;
        private DevExpress.XtraEditors.MemoEdit memoExDesc;
        private System.Windows.Forms.LinkLabel linkSupport;
        private DevExpress.XtraEditors.LabelControl labelDesc;
        private DevExpress.XtraEditors.LabelControl labelHead;
        private System.Windows.Forms.PictureBox picExIcon;
    }
}