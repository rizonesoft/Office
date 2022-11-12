namespace Rizonesoft.Office.Verbum
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
            this.tableLayoutCore = new System.Windows.Forms.TableLayoutPanel();
            this.picErrorIcon = new System.Windows.Forms.PictureBox();
            this.labelErrorTitle = new System.Windows.Forms.Label();
            this.labelErrorDesc = new System.Windows.Forms.Label();
            this.textBoxError = new System.Windows.Forms.TextBox();
            this.tableLayoutPanel1 = new System.Windows.Forms.TableLayoutPanel();
            this.buttonClose = new System.Windows.Forms.Button();
            this.buttonEmail = new System.Windows.Forms.Button();
            this.buttonCopy = new System.Windows.Forms.Button();
            this.tableLayoutCore.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picErrorIcon)).BeginInit();
            this.tableLayoutPanel1.SuspendLayout();
            this.SuspendLayout();
            // 
            // tableLayoutCore
            // 
            this.tableLayoutCore.ColumnCount = 2;
            this.tableLayoutCore.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 122F));
            this.tableLayoutCore.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutCore.Controls.Add(this.picErrorIcon, 0, 0);
            this.tableLayoutCore.Controls.Add(this.labelErrorTitle, 1, 0);
            this.tableLayoutCore.Controls.Add(this.labelErrorDesc, 1, 1);
            this.tableLayoutCore.Controls.Add(this.textBoxError, 0, 2);
            this.tableLayoutCore.Controls.Add(this.tableLayoutPanel1, 0, 3);
            this.tableLayoutCore.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tableLayoutCore.Location = new System.Drawing.Point(9, 9);
            this.tableLayoutCore.Name = "tableLayoutCore";
            this.tableLayoutCore.RowCount = 4;
            this.tableLayoutCore.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 33F));
            this.tableLayoutCore.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 90F));
            this.tableLayoutCore.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutCore.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 60F));
            this.tableLayoutCore.Size = new System.Drawing.Size(616, 493);
            this.tableLayoutCore.TabIndex = 0;
            // 
            // picErrorIcon
            // 
            this.picErrorIcon.Dock = System.Windows.Forms.DockStyle.Top;
            this.picErrorIcon.Image = global::Rizonesoft.Office.Verbum.Properties.Resources.button_error_64px;
            this.picErrorIcon.Location = new System.Drawing.Point(3, 3);
            this.picErrorIcon.Name = "picErrorIcon";
            this.tableLayoutCore.SetRowSpan(this.picErrorIcon, 2);
            this.picErrorIcon.Size = new System.Drawing.Size(116, 117);
            this.picErrorIcon.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
            this.picErrorIcon.TabIndex = 0;
            this.picErrorIcon.TabStop = false;
            // 
            // labelErrorTitle
            // 
            this.labelErrorTitle.AutoSize = true;
            this.labelErrorTitle.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelErrorTitle.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.labelErrorTitle.ForeColor = System.Drawing.SystemColors.ControlText;
            this.labelErrorTitle.Location = new System.Drawing.Point(125, 0);
            this.labelErrorTitle.Name = "labelErrorTitle";
            this.labelErrorTitle.Padding = new System.Windows.Forms.Padding(9, 0, 0, 0);
            this.labelErrorTitle.Size = new System.Drawing.Size(488, 33);
            this.labelErrorTitle.TabIndex = 1;
            this.labelErrorTitle.Text = "Something went wrong!";
            // 
            // labelErrorDesc
            // 
            this.labelErrorDesc.AutoSize = true;
            this.labelErrorDesc.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelErrorDesc.Location = new System.Drawing.Point(125, 33);
            this.labelErrorDesc.Name = "labelErrorDesc";
            this.labelErrorDesc.Padding = new System.Windows.Forms.Padding(9, 0, 0, 0);
            this.labelErrorDesc.Size = new System.Drawing.Size(488, 90);
            this.labelErrorDesc.TabIndex = 2;
            this.labelErrorDesc.Text = resources.GetString("labelErrorDesc.Text");
            // 
            // textBoxError
            // 
            this.tableLayoutCore.SetColumnSpan(this.textBoxError, 2);
            this.textBoxError.Dock = System.Windows.Forms.DockStyle.Fill;
            this.textBoxError.Location = new System.Drawing.Point(3, 126);
            this.textBoxError.Multiline = true;
            this.textBoxError.Name = "textBoxError";
            this.textBoxError.ReadOnly = true;
            this.textBoxError.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.textBoxError.Size = new System.Drawing.Size(610, 304);
            this.textBoxError.TabIndex = 3;
            // 
            // tableLayoutPanel1
            // 
            this.tableLayoutPanel1.ColumnCount = 5;
            this.tableLayoutCore.SetColumnSpan(this.tableLayoutPanel1, 2);
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 143F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 143F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 143F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 143F));
            this.tableLayoutPanel1.Controls.Add(this.buttonClose, 4, 0);
            this.tableLayoutPanel1.Controls.Add(this.buttonEmail, 2, 0);
            this.tableLayoutPanel1.Controls.Add(this.buttonCopy, 1, 0);
            this.tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tableLayoutPanel1.Location = new System.Drawing.Point(3, 436);
            this.tableLayoutPanel1.Name = "tableLayoutPanel1";
            this.tableLayoutPanel1.RowCount = 1;
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutPanel1.Size = new System.Drawing.Size(610, 54);
            this.tableLayoutPanel1.TabIndex = 4;
            // 
            // buttonClose
            // 
            this.buttonClose.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonClose.Location = new System.Drawing.Point(470, 3);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(137, 48);
            this.buttonClose.TabIndex = 0;
            this.buttonClose.Text = "Close";
            this.buttonClose.UseVisualStyleBackColor = true;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);
            // 
            // buttonEmail
            // 
            this.buttonEmail.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonEmail.Image = global::Rizonesoft.Office.Verbum.Properties.Resources.mail_32px;
            this.buttonEmail.ImageAlign = System.Drawing.ContentAlignment.MiddleLeft;
            this.buttonEmail.Location = new System.Drawing.Point(184, 3);
            this.buttonEmail.Name = "buttonEmail";
            this.buttonEmail.Padding = new System.Windows.Forms.Padding(11, 0, 0, 0);
            this.buttonEmail.Size = new System.Drawing.Size(137, 48);
            this.buttonEmail.TabIndex = 1;
            this.buttonEmail.Text = "Email";
            this.buttonEmail.UseVisualStyleBackColor = true;
            this.buttonEmail.Click += new System.EventHandler(this.buttonEmail_Click);
            // 
            // buttonCopy
            // 
            this.buttonCopy.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonCopy.Image = global::Rizonesoft.Office.Verbum.Properties.Resources.clipboard_text_32px;
            this.buttonCopy.ImageAlign = System.Drawing.ContentAlignment.MiddleLeft;
            this.buttonCopy.Location = new System.Drawing.Point(41, 3);
            this.buttonCopy.Name = "buttonCopy";
            this.buttonCopy.Padding = new System.Windows.Forms.Padding(11, 0, 0, 0);
            this.buttonCopy.Size = new System.Drawing.Size(137, 48);
            this.buttonCopy.TabIndex = 2;
            this.buttonCopy.Text = "Copy";
            this.buttonCopy.UseVisualStyleBackColor = true;
            this.buttonCopy.Click += new System.EventHandler(this.buttonCopy_Click);
            // 
            // ExceptionForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(634, 511);
            this.Controls.Add(this.tableLayoutCore);
            this.DoubleBuffered = true;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "ExceptionForm";
            this.Padding = new System.Windows.Forms.Padding(9, 9, 9, 9);
            this.Text = "Something went wrong!";
            this.TopMost = true;
            this.tableLayoutCore.ResumeLayout(false);
            this.tableLayoutCore.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picErrorIcon)).EndInit();
            this.tableLayoutPanel1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TableLayoutPanel tableLayoutCore;
        private System.Windows.Forms.PictureBox picErrorIcon;
        private System.Windows.Forms.Label labelErrorTitle;
        private System.Windows.Forms.Label labelErrorDesc;
        private System.Windows.Forms.TextBox textBoxError;
        private System.Windows.Forms.TableLayoutPanel tableLayoutPanel1;
        private System.Windows.Forms.Button buttonClose;
        private System.Windows.Forms.Button buttonEmail;
        private System.Windows.Forms.Button buttonCopy;
    }
}