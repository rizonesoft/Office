namespace Datum.Verbum.UnhandledExceptions
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
            this.labelHeading = new DevExpress.XtraEditors.LabelControl();
            this.descriptionLabel = new DevExpress.XtraEditors.LabelControl();
            this.memoDescription = new DevExpress.XtraEditors.MemoEdit();
            this.labelQuestion = new DevExpress.XtraEditors.LabelControl();
            this.yesButton = new DevExpress.XtraEditors.SimpleButton();
            this.noButton = new DevExpress.XtraEditors.SimpleButton();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.memoDescription.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            this.SuspendLayout();
            // 
            // labelHeading
            // 
            this.labelHeading.Appearance.Font = new System.Drawing.Font("Tahoma", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.labelHeading.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.labelHeading.Location = new System.Drawing.Point(81, 14);
            this.labelHeading.Name = "labelHeading";
            this.labelHeading.Size = new System.Drawing.Size(430, 18);
            this.labelHeading.TabIndex = 1;
            this.labelHeading.Text = "Sorry, an unexpected error occurred!";
            // 
            // descriptionLabel
            // 
            this.descriptionLabel.AllowHtmlString = true;
            this.descriptionLabel.AllowHtmlTextInToolTip = DevExpress.Utils.DefaultBoolean.True;
            this.descriptionLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.descriptionLabel.Location = new System.Drawing.Point(81, 38);
            this.descriptionLabel.Name = "descriptionLabel";
            this.descriptionLabel.Size = new System.Drawing.Size(430, 70);
            this.descriptionLabel.TabIndex = 2;
            this.descriptionLabel.Text = resources.GetString("descriptionLabel.Text");
            // 
            // memoDescription
            // 
            this.memoDescription.Location = new System.Drawing.Point(12, 124);
            this.memoDescription.Name = "memoDescription";
            this.memoDescription.Size = new System.Drawing.Size(510, 280);
            this.memoDescription.TabIndex = 3;
            // 
            // labelQuestion
            // 
            this.labelQuestion.AllowHtmlString = true;
            this.labelQuestion.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.labelQuestion.Location = new System.Drawing.Point(12, 411);
            this.labelQuestion.Name = "labelQuestion";
            this.labelQuestion.Size = new System.Drawing.Size(510, 30);
            this.labelQuestion.TabIndex = 5;
            this.labelQuestion.Text = "Would you like to continue using Verbum so that you can save your work?   ";
            // 
            // yesButton
            // 
            this.yesButton.Appearance.Font = new System.Drawing.Font("Tahoma", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.yesButton.Appearance.Options.UseFont = true;
            this.yesButton.DialogResult = System.Windows.Forms.DialogResult.Yes;
            this.yesButton.Image = global::Datum.Verbum.Properties.Resources.Ok;
            this.yesButton.ImageLocation = DevExpress.XtraEditors.ImageLocation.MiddleLeft;
            this.yesButton.Location = new System.Drawing.Point(286, 460);
            this.yesButton.Name = "yesButton";
            this.yesButton.Size = new System.Drawing.Size(115, 40);
            this.yesButton.TabIndex = 7;
            this.yesButton.Text = "Yes";
            this.yesButton.Click += new System.EventHandler(this.yesButton_Click);
            // 
            // noButton
            // 
            this.noButton.Appearance.Font = new System.Drawing.Font("Tahoma", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.noButton.Appearance.Options.UseFont = true;
            this.noButton.DialogResult = System.Windows.Forms.DialogResult.No;
            this.noButton.Image = global::Datum.Verbum.Properties.Resources.Stop;
            this.noButton.ImageLocation = DevExpress.XtraEditors.ImageLocation.MiddleLeft;
            this.noButton.Location = new System.Drawing.Point(407, 460);
            this.noButton.Name = "noButton";
            this.noButton.Size = new System.Drawing.Size(115, 40);
            this.noButton.TabIndex = 6;
            this.noButton.Text = "No";
            this.noButton.Click += new System.EventHandler(this.noButton_Click);
            // 
            // pictureBox1
            // 
            this.pictureBox1.Image = global::Datum.Verbum.Properties.Resources.ShieldError;
            this.pictureBox1.Location = new System.Drawing.Point(12, 12);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(48, 48);
            this.pictureBox1.TabIndex = 0;
            this.pictureBox1.TabStop = false;
            // 
            // exceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(534, 512);
            this.Controls.Add(this.yesButton);
            this.Controls.Add(this.noButton);
            this.Controls.Add(this.labelQuestion);
            this.Controls.Add(this.memoDescription);
            this.Controls.Add(this.descriptionLabel);
            this.Controls.Add(this.labelHeading);
            this.Controls.Add(this.pictureBox1);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "exceptionForm";
            this.Text = "Booboo!";
            this.TopMost = true;
            ((System.ComponentModel.ISupportInitialize)(this.memoDescription.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox pictureBox1;
        private DevExpress.XtraEditors.LabelControl labelHeading;
        private DevExpress.XtraEditors.LabelControl descriptionLabel;
        private DevExpress.XtraEditors.MemoEdit memoDescription;
        private DevExpress.XtraEditors.LabelControl labelQuestion;
        private DevExpress.XtraEditors.SimpleButton noButton;
        private DevExpress.XtraEditors.SimpleButton yesButton;
    }
}