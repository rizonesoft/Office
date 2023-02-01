namespace Rizone.Verbum
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
            this.labelDesc = new DevExpress.XtraEditors.LabelControl();
            this.memoExDesc = new DevExpress.XtraEditors.MemoEdit();
            this.labelHead = new DevExpress.XtraEditors.LabelControl();
            this.linkSupport = new System.Windows.Forms.LinkLabel();
            this.btnClose = new DevExpress.XtraEditors.SimpleButton();
            this.picExIcon = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).BeginInit();
            this.SuspendLayout();
            // 
            // labelDesc
            // 
            this.labelDesc.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.labelDesc.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            this.labelDesc.Location = new System.Drawing.Point(88, 33);
            this.labelDesc.MaximumSize = new System.Drawing.Size(500, 100);
            this.labelDesc.Name = "labelDesc";
            this.labelDesc.Size = new System.Drawing.Size(434, 52);
            this.labelDesc.TabIndex = 1;
            this.labelDesc.Text = resources.GetString("labelDesc.Text");
            // 
            // memoExDesc
            // 
            this.memoExDesc.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.memoExDesc.EditValue = "";
            this.memoExDesc.Location = new System.Drawing.Point(12, 116);
            this.memoExDesc.Name = "memoExDesc";
            this.memoExDesc.Properties.EditValueChangedFiringMode = DevExpress.XtraEditors.Controls.EditValueChangedFiringMode.Buffered;
            this.memoExDesc.Properties.HideSelection = false;
            this.memoExDesc.Properties.ReadOnly = true;
            this.memoExDesc.Properties.UseParentBackground = true;
            this.memoExDesc.Size = new System.Drawing.Size(510, 190);
            this.memoExDesc.TabIndex = 2;
            this.memoExDesc.TabStop = false;
            // 
            // labelHead
            // 
            this.labelHead.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.labelHead.Appearance.Font = new System.Drawing.Font("Tahoma", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.labelHead.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.labelHead.Location = new System.Drawing.Point(88, 3);
            this.labelHead.Name = "labelHead";
            this.labelHead.Size = new System.Drawing.Size(434, 24);
            this.labelHead.TabIndex = 3;
            this.labelHead.Text = "Sorry, an unexpected error occurred.";
            // 
            // linkSupport
            // 
            this.linkSupport.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.linkSupport.Location = new System.Drawing.Point(85, 88);
            this.linkSupport.Name = "linkSupport";
            this.linkSupport.Size = new System.Drawing.Size(442, 25);
            this.linkSupport.TabIndex = 4;
            this.linkSupport.TabStop = true;
            this.linkSupport.Text = "http://www.rizone3.com/support/support.php";
            this.linkSupport.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // btnClose
            // 
            this.btnClose.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClose.Location = new System.Drawing.Point(403, 312);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(119, 34);
            this.btnClose.TabIndex = 1;
            this.btnClose.Text = "Close";
            // 
            // picExIcon
            // 
            this.picExIcon.Image = global::Verbum.Properties.Resources.ShieldError;
            this.picExIcon.Location = new System.Drawing.Point(12, 6);
            this.picExIcon.Name = "picExIcon";
            this.picExIcon.Size = new System.Drawing.Size(70, 70);
            this.picExIcon.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this.picExIcon.TabIndex = 4;
            this.picExIcon.TabStop = false;
            // 
            // ExceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(534, 362);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.memoExDesc);
            this.Controls.Add(this.picExIcon);
            this.Controls.Add(this.linkSupport);
            this.Controls.Add(this.labelDesc);
            this.Controls.Add(this.labelHead);
            this.DoubleBuffered = true;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MinimumSize = new System.Drawing.Size(550, 400);
            this.Name = "ExceptionForm";
            this.Text = "Booboo!";
            ((System.ComponentModel.ISupportInitialize)(this.memoExDesc.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.picExIcon)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.MemoEdit memoExDesc;
        private DevExpress.XtraEditors.LabelControl labelDesc;
        private DevExpress.XtraEditors.LabelControl labelHead;
        private System.Windows.Forms.LinkLabel linkSupport;
        private DevExpress.XtraEditors.SimpleButton btnClose;
        private System.Windows.Forms.PictureBox picExIcon;
    }
}