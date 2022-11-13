
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
            this.lblCaption = new DevExpress.XtraEditors.LabelControl();
            this.lblParagraphsCount = new DevExpress.XtraEditors.LabelControl();
            this.lblWithSpacesCharactersCount = new DevExpress.XtraEditors.LabelControl();
            this.lblNoSpacesCharactersCount = new DevExpress.XtraEditors.LabelControl();
            this.lblWordsCount = new DevExpress.XtraEditors.LabelControl();
            this.chkIncludeTextboxes = new DevExpress.XtraEditors.CheckEdit();
            this.lblParagraphs = new DevExpress.XtraEditors.LabelControl();
            this.lblWithSpacesCharacters = new DevExpress.XtraEditors.LabelControl();
            this.lblNoSpacesCharacters = new DevExpress.XtraEditors.LabelControl();
            this.lblWords = new DevExpress.XtraEditors.LabelControl();
            this.btnClose = new DevExpress.XtraEditors.SimpleButton();
            ((System.ComponentModel.ISupportInitialize)(this.chkIncludeTextboxes.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // lblCaption
            // 
            this.lblCaption.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.None;
            this.lblCaption.LineVisible = true;
            this.lblCaption.Location = new System.Drawing.Point(12, 12);
            this.lblCaption.Name = "lblCaption";
            this.lblCaption.Size = new System.Drawing.Size(227, 13);
            this.lblCaption.TabIndex = 29;
            this.lblCaption.Text = "Statistics";
            // 
            // lblParagraphsCount
            // 
            this.lblParagraphsCount.Location = new System.Drawing.Point(217, 92);
            this.lblParagraphsCount.Name = "lblParagraphsCount";
            this.lblParagraphsCount.Size = new System.Drawing.Size(0, 13);
            this.lblParagraphsCount.TabIndex = 28;
            // 
            // lblWithSpacesCharactersCount
            // 
            this.lblWithSpacesCharactersCount.Location = new System.Drawing.Point(217, 72);
            this.lblWithSpacesCharactersCount.Name = "lblWithSpacesCharactersCount";
            this.lblWithSpacesCharactersCount.Size = new System.Drawing.Size(0, 13);
            this.lblWithSpacesCharactersCount.TabIndex = 27;
            // 
            // lblNoSpacesCharactersCount
            // 
            this.lblNoSpacesCharactersCount.Location = new System.Drawing.Point(217, 52);
            this.lblNoSpacesCharactersCount.Name = "lblNoSpacesCharactersCount";
            this.lblNoSpacesCharactersCount.Size = new System.Drawing.Size(0, 13);
            this.lblNoSpacesCharactersCount.TabIndex = 26;
            // 
            // lblWordsCount
            // 
            this.lblWordsCount.Location = new System.Drawing.Point(217, 32);
            this.lblWordsCount.Name = "lblWordsCount";
            this.lblWordsCount.Size = new System.Drawing.Size(0, 13);
            this.lblWordsCount.TabIndex = 25;
            // 
            // chkIncludeTextboxes
            // 
            this.chkIncludeTextboxes.Location = new System.Drawing.Point(24, 111);
            this.chkIncludeTextboxes.Name = "chkIncludeTextboxes";
            this.chkIncludeTextboxes.Properties.Caption = "Include textboxes";
            this.chkIncludeTextboxes.Size = new System.Drawing.Size(111, 18);
            this.chkIncludeTextboxes.TabIndex = 24;
            // 
            // lblParagraphs
            // 
            this.lblParagraphs.Location = new System.Drawing.Point(24, 92);
            this.lblParagraphs.Name = "lblParagraphs";
            this.lblParagraphs.Size = new System.Drawing.Size(58, 13);
            this.lblParagraphs.TabIndex = 23;
            this.lblParagraphs.Text = "Paragraphs";
            // 
            // lblWithSpacesCharacters
            // 
            this.lblWithSpacesCharacters.Location = new System.Drawing.Point(24, 72);
            this.lblWithSpacesCharacters.Name = "lblWithSpacesCharacters";
            this.lblWithSpacesCharacters.Size = new System.Drawing.Size(123, 13);
            this.lblWithSpacesCharacters.TabIndex = 22;
            this.lblWithSpacesCharacters.Text = "Characters (with spaces)";
            // 
            // lblNoSpacesCharacters
            // 
            this.lblNoSpacesCharacters.Location = new System.Drawing.Point(24, 52);
            this.lblNoSpacesCharacters.Name = "lblNoSpacesCharacters";
            this.lblNoSpacesCharacters.Size = new System.Drawing.Size(114, 13);
            this.lblNoSpacesCharacters.TabIndex = 21;
            this.lblNoSpacesCharacters.Text = "Characters (no spaces)";
            // 
            // lblWords
            // 
            this.lblWords.Location = new System.Drawing.Point(24, 32);
            this.lblWords.Name = "lblWords";
            this.lblWords.Size = new System.Drawing.Size(34, 13);
            this.lblWords.TabIndex = 20;
            this.lblWords.Text = "Words";
            // 
            // btnClose
            // 
            this.btnClose.Location = new System.Drawing.Point(164, 141);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 23);
            this.btnClose.TabIndex = 19;
            this.btnClose.Text = "Close";
            // 
            // DocumentStatisticsForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(251, 176);
            this.Controls.Add(this.lblCaption);
            this.Controls.Add(this.lblParagraphsCount);
            this.Controls.Add(this.lblWithSpacesCharactersCount);
            this.Controls.Add(this.lblNoSpacesCharactersCount);
            this.Controls.Add(this.lblWordsCount);
            this.Controls.Add(this.chkIncludeTextboxes);
            this.Controls.Add(this.lblParagraphs);
            this.Controls.Add(this.lblWithSpacesCharacters);
            this.Controls.Add(this.lblNoSpacesCharacters);
            this.Controls.Add(this.lblWords);
            this.Controls.Add(this.btnClose);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.IconOptions.ShowIcon = false;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "DocumentStatisticsForm";
            this.ShowInTaskbar = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Document Statistics";
            ((System.ComponentModel.ISupportInitialize)(this.chkIncludeTextboxes.Properties)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

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