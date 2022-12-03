// Developer Express Code Central Example:
// How to create an editor similar to Outlook Attachment Editor
// 
// This example demonstrates how the RichEditControl component can be used to
// emulate the Outlook Attachment Editor behavior.
// The main idea of the approach
// demonstrated in this sample is to use the DOCVARIABLE field
// (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
// display corresponding RTF content for each inserted file.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E4911

namespace WindowsFormsApplication1 {
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
            if(disposing && (components != null)) {
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
            this.attachmentsEditor1 = new WindowsFormsApplication1.AttachmentsEditor();
            this.SuspendLayout();
            // 
            // attachmentsEditor1
            // 
            this.attachmentsEditor1.Dock = System.Windows.Forms.DockStyle.Top;
            this.attachmentsEditor1.Location = new System.Drawing.Point(0, 0);
            this.attachmentsEditor1.Name = "attachmentsEditor1";
            this.attachmentsEditor1.Size = new System.Drawing.Size(828, 51);
            this.attachmentsEditor1.TabIndex = 0;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(828, 366);
            this.Controls.Add(this.attachmentsEditor1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);

        }

        #endregion

        private AttachmentsEditor attachmentsEditor1;









    }
}

