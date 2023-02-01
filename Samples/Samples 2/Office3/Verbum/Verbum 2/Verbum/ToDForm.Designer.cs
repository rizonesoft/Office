namespace Rizonesoft.Verbum
{
    partial class ToDForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ToDForm));
            this.panelBasic = new System.Windows.Forms.Panel();
            this.lblTip = new System.Windows.Forms.Label();
            this.lblTipHead = new DevExpress.XtraEditors.LabelControl();
            this.picTip = new System.Windows.Forms.PictureBox();
            this.chkShowTips = new DevExpress.XtraEditors.CheckEdit();
            this.smBtnNext = new DevExpress.XtraEditors.SimpleButton();
            this.smBtnCancel = new DevExpress.XtraEditors.SimpleButton();
            this.smBtnOK = new DevExpress.XtraEditors.SimpleButton();
            this.panelBasic.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picTip)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.chkShowTips.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // panelBasic
            // 
            this.panelBasic.BackColor = System.Drawing.Color.White;
            this.panelBasic.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panelBasic.Controls.Add(this.lblTip);
            this.panelBasic.Controls.Add(this.lblTipHead);
            this.panelBasic.Controls.Add(this.picTip);
            this.panelBasic.Location = new System.Drawing.Point(15, 12);
            this.panelBasic.Name = "panelBasic";
            this.panelBasic.Size = new System.Drawing.Size(362, 230);
            this.panelBasic.TabIndex = 0;
            // 
            // lblTip
            // 
            this.lblTip.Font = new System.Drawing.Font("Tahoma", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTip.Location = new System.Drawing.Point(20, 95);
            this.lblTip.Name = "lblTip";
            this.lblTip.Size = new System.Drawing.Size(320, 100);
            this.lblTip.TabIndex = 2;
            this.lblTip.Text = "Will display tips here...";
            // 
            // lblTipHead
            // 
            this.lblTipHead.Appearance.Font = new System.Drawing.Font("Tahoma", 15.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblTipHead.Location = new System.Drawing.Point(90, 35);
            this.lblTipHead.Name = "lblTipHead";
            this.lblTipHead.Size = new System.Drawing.Size(155, 25);
            this.lblTipHead.TabIndex = 1;
            this.lblTipHead.Text = "Did you know...?";
            // 
            // picTip
            // 
            this.picTip.Image = global::Verbum.Properties.Resources.Tips48;
            this.picTip.Location = new System.Drawing.Point(14, 12);
            this.picTip.Name = "picTip";
            this.picTip.Size = new System.Drawing.Size(48, 48);
            this.picTip.TabIndex = 0;
            this.picTip.TabStop = false;
            // 
            // chkShowTips
            // 
            this.chkShowTips.Location = new System.Drawing.Point(13, 248);
            this.chkShowTips.Name = "chkShowTips";
            this.chkShowTips.Properties.Caption = "&Show tips on startup";
            this.chkShowTips.Size = new System.Drawing.Size(263, 19);
            this.chkShowTips.TabIndex = 1;
            // 
            // smBtnNext
            // 
            this.smBtnNext.Location = new System.Drawing.Point(15, 279);
            this.smBtnNext.Name = "smBtnNext";
            this.smBtnNext.Size = new System.Drawing.Size(130, 30);
            this.smBtnNext.TabIndex = 3;
            this.smBtnNext.Text = "&Next Tip";
            this.smBtnNext.Click += new System.EventHandler(this.smBtnNext_Click);
            // 
            // smBtnCancel
            // 
            this.smBtnCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.smBtnCancel.Location = new System.Drawing.Point(282, 279);
            this.smBtnCancel.Name = "smBtnCancel";
            this.smBtnCancel.Size = new System.Drawing.Size(95, 30);
            this.smBtnCancel.TabIndex = 5;
            this.smBtnCancel.Text = "Cancel";
            // 
            // smBtnOK
            // 
            this.smBtnOK.Location = new System.Drawing.Point(181, 279);
            this.smBtnOK.Name = "smBtnOK";
            this.smBtnOK.Size = new System.Drawing.Size(95, 30);
            this.smBtnOK.TabIndex = 4;
            this.smBtnOK.Text = "OK";
            this.smBtnOK.Click += new System.EventHandler(this.smBtnOK_Click);
            // 
            // TipsForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.smBtnCancel;
            this.ClientSize = new System.Drawing.Size(394, 322);
            this.Controls.Add(this.panelBasic);
            this.Controls.Add(this.chkShowTips);
            this.Controls.Add(this.smBtnOK);
            this.Controls.Add(this.smBtnCancel);
            this.Controls.Add(this.smBtnNext);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "TipsForm";
            this.ShowInTaskbar = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Tip of the Day";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.TipsForm_FormClosing);
            this.panelBasic.ResumeLayout(false);
            this.panelBasic.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picTip)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.chkShowTips.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.CheckEdit chkShowTips;
        private System.Windows.Forms.Panel panelBasic;
        private System.Windows.Forms.PictureBox picTip;
        private DevExpress.XtraEditors.SimpleButton smBtnNext;
        private DevExpress.XtraEditors.SimpleButton smBtnCancel;
        private DevExpress.XtraEditors.SimpleButton smBtnOK;
        private System.Windows.Forms.Label lblTip;
        private DevExpress.XtraEditors.LabelControl lblTipHead;
    }
}