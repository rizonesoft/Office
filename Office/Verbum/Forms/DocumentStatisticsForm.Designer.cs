
namespace Rizonesoft.Office.Verbum.Forms
{
    partial class DocumentStatisticsForm
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
            lblCaption = new DevExpress.XtraEditors.LabelControl();
            lblParagraphsCount = new DevExpress.XtraEditors.LabelControl();
            lblWithSpacesCharactersCount = new DevExpress.XtraEditors.LabelControl();
            lblNoSpacesCharactersCount = new DevExpress.XtraEditors.LabelControl();
            lblWordsCount = new DevExpress.XtraEditors.LabelControl();
            chkIncludeTextboxes = new DevExpress.XtraEditors.CheckEdit();
            lblParagraphs = new DevExpress.XtraEditors.LabelControl();
            lblWithSpacesCharacters = new DevExpress.XtraEditors.LabelControl();
            lblNoSpacesCharacters = new DevExpress.XtraEditors.LabelControl();
            lblWords = new DevExpress.XtraEditors.LabelControl();
            btnClose = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)chkIncludeTextboxes.Properties).BeginInit();
            SuspendLayout();
            // 
            // lblCaption
            // 
            lblCaption.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            lblCaption.LineVisible = true;
            lblCaption.Location = new System.Drawing.Point(12, 12);
            lblCaption.Name = "lblCaption";
            lblCaption.Size = new System.Drawing.Size(227, 13);
            lblCaption.TabIndex = 29;
            lblCaption.Text = "Statistics";
            // 
            // lblParagraphsCount
            // 
            lblParagraphsCount.Location = new System.Drawing.Point(217, 92);
            lblParagraphsCount.Name = "lblParagraphsCount";
            lblParagraphsCount.Size = new System.Drawing.Size(0, 13);
            lblParagraphsCount.TabIndex = 28;
            // 
            // lblWithSpacesCharactersCount
            // 
            lblWithSpacesCharactersCount.Location = new System.Drawing.Point(217, 72);
            lblWithSpacesCharactersCount.Name = "lblWithSpacesCharactersCount";
            lblWithSpacesCharactersCount.Size = new System.Drawing.Size(0, 13);
            lblWithSpacesCharactersCount.TabIndex = 27;
            // 
            // lblNoSpacesCharactersCount
            // 
            lblNoSpacesCharactersCount.Location = new System.Drawing.Point(217, 52);
            lblNoSpacesCharactersCount.Name = "lblNoSpacesCharactersCount";
            lblNoSpacesCharactersCount.Size = new System.Drawing.Size(0, 13);
            lblNoSpacesCharactersCount.TabIndex = 26;
            // 
            // lblWordsCount
            // 
            lblWordsCount.Location = new System.Drawing.Point(217, 32);
            lblWordsCount.Name = "lblWordsCount";
            lblWordsCount.Size = new System.Drawing.Size(0, 13);
            lblWordsCount.TabIndex = 25;
            // 
            // chkIncludeTextboxes
            // 
            chkIncludeTextboxes.Location = new System.Drawing.Point(24, 111);
            chkIncludeTextboxes.Name = "chkIncludeTextboxes";
            chkIncludeTextboxes.Properties.Caption = "Include textboxes";
            chkIncludeTextboxes.Size = new System.Drawing.Size(215, 22);
            chkIncludeTextboxes.TabIndex = 24;
            chkIncludeTextboxes.CheckStateChanged += ChkIncludeTextboxes_CheckStateChanged;
            // 
            // lblParagraphs
            // 
            lblParagraphs.Location = new System.Drawing.Point(24, 92);
            lblParagraphs.Name = "lblParagraphs";
            lblParagraphs.Size = new System.Drawing.Size(55, 13);
            lblParagraphs.TabIndex = 23;
            lblParagraphs.Text = "Paragraphs";
            // 
            // lblWithSpacesCharacters
            // 
            lblWithSpacesCharacters.Location = new System.Drawing.Point(24, 72);
            lblWithSpacesCharacters.Name = "lblWithSpacesCharacters";
            lblWithSpacesCharacters.Size = new System.Drawing.Size(120, 13);
            lblWithSpacesCharacters.TabIndex = 22;
            lblWithSpacesCharacters.Text = "Characters (with spaces)";
            // 
            // lblNoSpacesCharacters
            // 
            lblNoSpacesCharacters.Location = new System.Drawing.Point(24, 52);
            lblNoSpacesCharacters.Name = "lblNoSpacesCharacters";
            lblNoSpacesCharacters.Size = new System.Drawing.Size(112, 13);
            lblNoSpacesCharacters.TabIndex = 21;
            lblNoSpacesCharacters.Text = "Characters (no spaces)";
            // 
            // lblWords
            // 
            lblWords.Location = new System.Drawing.Point(24, 32);
            lblWords.Name = "lblWords";
            lblWords.Size = new System.Drawing.Size(31, 13);
            lblWords.TabIndex = 20;
            lblWords.Text = "Words";
            // 
            // btnClose
            // 
            btnClose.Location = new System.Drawing.Point(164, 141);
            btnClose.Name = "btnClose";
            btnClose.Size = new System.Drawing.Size(75, 23);
            btnClose.TabIndex = 19;
            btnClose.Text = "Close";
            btnClose.Click += BtnClose_Click;
            // 
            // DocumentStatisticsForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(251, 176);
            Controls.Add(lblCaption);
            Controls.Add(lblParagraphsCount);
            Controls.Add(lblWithSpacesCharactersCount);
            Controls.Add(lblNoSpacesCharactersCount);
            Controls.Add(lblWordsCount);
            Controls.Add(chkIncludeTextboxes);
            Controls.Add(lblParagraphs);
            Controls.Add(lblWithSpacesCharacters);
            Controls.Add(lblNoSpacesCharacters);
            Controls.Add(lblWords);
            Controls.Add(btnClose);
            FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            IconOptions.ShowIcon = false;
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "DocumentStatisticsForm";
            ShowInTaskbar = false;
            StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            Text = "Document Statistics";
            ((System.ComponentModel.ISupportInitialize)chkIncludeTextboxes.Properties).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private DevExpress.XtraEditors.LabelControl lblCaption;
        private DevExpress.XtraEditors.LabelControl lblParagraphsCount;
        private DevExpress.XtraEditors.LabelControl lblWithSpacesCharactersCount;
        private DevExpress.XtraEditors.LabelControl lblNoSpacesCharactersCount;
        private DevExpress.XtraEditors.LabelControl lblWordsCount;
        private DevExpress.XtraEditors.CheckEdit chkIncludeTextboxes;
        private DevExpress.XtraEditors.LabelControl lblParagraphs;
        private DevExpress.XtraEditors.LabelControl lblWithSpacesCharacters;
        private DevExpress.XtraEditors.LabelControl lblNoSpacesCharacters;
        private DevExpress.XtraEditors.LabelControl lblWords;
        private DevExpress.XtraEditors.SimpleButton btnClose;
    }
}