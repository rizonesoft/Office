namespace Rizonesoft.Office.Toast
{
    partial class ToastForm
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
            components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ToastForm));
            alertToast = new DevExpress.XtraBars.Alerter.AlertControl(components);
            SuspendLayout();
            // 
            // alertToast
            // 
            alertToast.AutoFormDelay = 30000;
            alertToast.HtmlTemplate.Styles = resources.GetString("alertToast.HtmlTemplate.Styles");
            alertToast.HtmlTemplate.Template = resources.GetString("alertToast.HtmlTemplate.Template");
            // 
            // ToastForm
            // 
            AutoScaleDimensions = new SizeF(9F, 19F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(221, 117);
            ControlBox = false;
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "ToastForm";
            Opacity = 0D;
            Text = "Message";
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraBars.Alerter.AlertControl alertToast;
    }
}