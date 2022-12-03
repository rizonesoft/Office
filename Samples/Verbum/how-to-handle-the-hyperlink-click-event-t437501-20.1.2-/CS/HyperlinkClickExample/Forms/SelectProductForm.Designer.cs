namespace HyperlinkClickExample.Forms
{
    partial class SelectProductForm
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
            this.listBoxControl = new DevExpress.XtraEditors.ListBoxControl();
            ((System.ComponentModel.ISupportInitialize)(this.listBoxControl)).BeginInit();
            this.SuspendLayout();
            // 
            // listBoxControl
            // 
            this.listBoxControl.Cursor = System.Windows.Forms.Cursors.Default;
            this.listBoxControl.Dock = System.Windows.Forms.DockStyle.Fill;
            this.listBoxControl.Location = new System.Drawing.Point(0, 0);
            this.listBoxControl.Name = "listBoxControl";
            this.listBoxControl.Size = new System.Drawing.Size(268, 248);
            this.listBoxControl.TabIndex = 0;
            this.listBoxControl.MouseClick += new System.Windows.Forms.MouseEventHandler(this.listBoxControl_MouseClick);
            this.listBoxControl.MouseMove += new System.Windows.Forms.MouseEventHandler(this.listBoxControl_MouseMove);
            // 
            // SelectProductForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.AutoSize = true;
            this.ClientSize = new System.Drawing.Size(268, 248);
            this.Controls.Add(this.listBoxControl);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedToolWindow;
            this.KeyPreview = true;
            this.MaximizeBox = false;
            this.Name = "SelectProductForm";
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.Manual;
            this.Text = "Select a Product:";
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.SelectProductForm_KeyDown);
            ((System.ComponentModel.ISupportInitialize)(this.listBoxControl)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.ListBoxControl listBoxControl;
    }
}