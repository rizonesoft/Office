namespace Rizonesoft.Office.MessagesEx
{
    partial class MessageForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MessageForm));
            directXFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            messageAlertControl = new DevExpress.XtraBars.Alerter.AlertControl(components);
            updateSVGImageCollection = new DevExpress.Utils.SvgImageCollection(components);
            ((System.ComponentModel.ISupportInitialize)updateSVGImageCollection).BeginInit();
            SuspendLayout();
            // 
            // directXFormContainerControl1
            // 
            directXFormContainerControl1.Location = new Point(1, 31);
            directXFormContainerControl1.Name = "directXFormContainerControl1";
            directXFormContainerControl1.Size = new Size(134, 68);
            directXFormContainerControl1.TabIndex = 0;
            // 
            // messageAlertControl
            // 
            messageAlertControl.AllowHtmlText = true;
            messageAlertControl.HtmlImages = updateSVGImageCollection;
            messageAlertControl.HtmlTemplate.Styles = resources.GetString("updateAlertControl.HtmlTemplate.Styles");
            messageAlertControl.HtmlTemplate.Template = resources.GetString("updateAlertControl.HtmlTemplate.Template");
            messageAlertControl.FormClosing += MessageAlertControl_FormClosing;
            // 
            // updateSVGImageCollection
            // 
            updateSVGImageCollection.Add("del", "image://svgimages/diagramicons/del.svg");
            updateSVGImageCollection.Add("automaticupdates", "image://svgimages/dashboards/automaticupdates.svg");
            updateSVGImageCollection.Add("business_world", "image://svgimages/icon builder/business_world.svg");
            updateSVGImageCollection.Add("bo_notifications", "image://svgimages/business objects/bo_notifications.svg");
            // 
            // MessageForm
            // 
            AutoScaleDimensions = new SizeF(6F, 13F);
            AutoScaleMode = AutoScaleMode.Font;
            ChildControls.Add(directXFormContainerControl1);
            ClientSize = new Size(136, 100);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            Name = "MessageForm";
            Text = "Update Form";
            ((System.ComponentModel.ISupportInitialize)updateSVGImageCollection).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraEditors.DirectXFormContainerControl directXFormContainerControl1;
        private DevExpress.XtraBars.Alerter.AlertControl messageAlertControl;
        private DevExpress.Utils.SvgImageCollection updateSVGImageCollection;
    }
}