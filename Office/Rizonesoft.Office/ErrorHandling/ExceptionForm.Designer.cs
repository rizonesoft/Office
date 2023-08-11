namespace Rizonesoft.Office.ErrorHandling
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
            tablePanel1 = new DevExpress.Utils.Layout.TablePanel();
            lblPrivacyStatement = new DevExpress.XtraEditors.LabelControl();
            btnCopy = new DevExpress.XtraEditors.SimpleButton();
            lblMessage = new DevExpress.XtraEditors.LabelControl();
            memoExceptionDetails = new DevExpress.XtraEditors.MemoEdit();
            btnRecover = new DevExpress.XtraEditors.SimpleButton();
            btnTerminate = new DevExpress.XtraEditors.SimpleButton();
            directxFormContainerControl1 = new DevExpress.XtraEditors.DirectXFormContainerControl();
            ((System.ComponentModel.ISupportInitialize)tablePanel1).BeginInit();
            tablePanel1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)memoExceptionDetails.Properties).BeginInit();
            directxFormContainerControl1.SuspendLayout();
            SuspendLayout();
            // 
            // tablePanel1
            // 
            tablePanel1.Columns.AddRange(new DevExpress.Utils.Layout.TablePanelColumn[] { new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 10F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 25F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 25F), new DevExpress.Utils.Layout.TablePanelColumn(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 25F) });
            tablePanel1.Controls.Add(lblPrivacyStatement);
            tablePanel1.Controls.Add(btnCopy);
            tablePanel1.Controls.Add(lblMessage);
            tablePanel1.Controls.Add(memoExceptionDetails);
            tablePanel1.Controls.Add(btnRecover);
            tablePanel1.Controls.Add(btnTerminate);
            tablePanel1.Dock = DockStyle.Fill;
            tablePanel1.Location = new Point(0, 0);
            tablePanel1.Margin = new Padding(3, 4, 3, 4);
            tablePanel1.Name = "tablePanel1";
            tablePanel1.Padding = new Padding(30);
            tablePanel1.Rows.AddRange(new DevExpress.Utils.Layout.TablePanelRow[] { new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 180F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Relative, 100F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 160F), new DevExpress.Utils.Layout.TablePanelRow(DevExpress.Utils.Layout.TablePanelEntityStyle.Absolute, 69F) });
            tablePanel1.Size = new Size(954, 883);
            tablePanel1.TabIndex = 0;
            tablePanel1.UseSkinIndents = true;
            // 
            // lblPrivacyStatement
            // 
            lblPrivacyStatement.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            lblPrivacyStatement.Appearance.Options.UseFont = true;
            lblPrivacyStatement.Appearance.Options.UseTextOptions = true;
            lblPrivacyStatement.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            lblPrivacyStatement.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            lblPrivacyStatement.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel1.SetColumn(lblPrivacyStatement, 0);
            tablePanel1.SetColumnSpan(lblPrivacyStatement, 4);
            lblPrivacyStatement.Dock = DockStyle.Fill;
            lblPrivacyStatement.ImageAlignToText = DevExpress.XtraEditors.ImageAlignToText.LeftTop;
            lblPrivacyStatement.IndentBetweenImageAndText = 20;
            lblPrivacyStatement.Location = new Point(33, 627);
            lblPrivacyStatement.Name = "lblPrivacyStatement";
            lblPrivacyStatement.Padding = new Padding(5);
            tablePanel1.SetRow(lblPrivacyStatement, 2);
            lblPrivacyStatement.Size = new Size(888, 154);
            lblPrivacyStatement.TabIndex = 6;
            lblPrivacyStatement.Text = "Privacy Statement";
            // 
            // btnCopy
            // 
            tablePanel1.SetColumn(btnCopy, 0);
            btnCopy.Dock = DockStyle.Fill;
            btnCopy.ImageOptions.ImageToTextAlignment = DevExpress.XtraEditors.ImageAlignToText.TopCenter;
            btnCopy.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("btnCopy.ImageOptions.SvgImage");
            btnCopy.ImageOptions.SvgImageSize = new Size(24, 24);
            btnCopy.Location = new Point(33, 787);
            btnCopy.Name = "btnCopy";
            tablePanel1.SetRow(btnCopy, 3);
            btnCopy.Size = new Size(99, 63);
            btnCopy.TabIndex = 5;
            btnCopy.Click += btnCopy_Click;
            // 
            // lblMessage
            // 
            lblMessage.AllowHtmlString = true;
            lblMessage.Appearance.Font = new Font("Segoe UI", 10F, FontStyle.Regular, GraphicsUnit.Point);
            lblMessage.Appearance.Options.UseFont = true;
            lblMessage.Appearance.Options.UseTextOptions = true;
            lblMessage.Appearance.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Top;
            lblMessage.Appearance.TextOptions.WordWrap = DevExpress.Utils.WordWrap.Wrap;
            lblMessage.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            tablePanel1.SetColumn(lblMessage, 0);
            tablePanel1.SetColumnSpan(lblMessage, 4);
            lblMessage.Dock = DockStyle.Fill;
            lblMessage.ImageAlignToText = DevExpress.XtraEditors.ImageAlignToText.LeftTop;
            lblMessage.IndentBetweenImageAndText = 20;
            lblMessage.Location = new Point(33, 34);
            lblMessage.Margin = new Padding(3, 4, 3, 4);
            lblMessage.Name = "lblMessage";
            lblMessage.Padding = new Padding(5);
            tablePanel1.SetRow(lblMessage, 0);
            lblMessage.Size = new Size(888, 172);
            lblMessage.TabIndex = 4;
            lblMessage.Text = "Description";
            // 
            // memoExceptionDetails
            // 
            tablePanel1.SetColumn(memoExceptionDetails, 0);
            tablePanel1.SetColumnSpan(memoExceptionDetails, 4);
            memoExceptionDetails.Dock = DockStyle.Fill;
            memoExceptionDetails.Location = new Point(33, 220);
            memoExceptionDetails.Margin = new Padding(3, 10, 3, 20);
            memoExceptionDetails.Name = "memoExceptionDetails";
            memoExceptionDetails.Properties.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            memoExceptionDetails.Properties.Appearance.Options.UseFont = true;
            tablePanel1.SetRow(memoExceptionDetails, 1);
            memoExceptionDetails.Size = new Size(888, 384);
            memoExceptionDetails.TabIndex = 3;
            memoExceptionDetails.Enter += MemoExceptionDetails_Enter;
            memoExceptionDetails.Leave += MemoExceptionDetails_Leave;
            // 
            // btnRecover
            // 
            btnRecover.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            btnRecover.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(btnRecover, 2);
            btnRecover.Dock = DockStyle.Fill;
            btnRecover.Location = new Point(401, 788);
            btnRecover.Margin = new Padding(3, 4, 5, 4);
            btnRecover.Name = "btnRecover";
            tablePanel1.SetRow(btnRecover, 3);
            btnRecover.Size = new Size(255, 61);
            btnRecover.TabIndex = 1;
            btnRecover.Text = "Recover";
            btnRecover.Click += BtnRecover_Click;
            // 
            // btnTerminate
            // 
            btnTerminate.Appearance.Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            btnTerminate.Appearance.Options.UseFont = true;
            tablePanel1.SetColumn(btnTerminate, 3);
            btnTerminate.DialogResult = DialogResult.Cancel;
            btnTerminate.Dock = DockStyle.Fill;
            btnTerminate.Location = new Point(666, 788);
            btnTerminate.Margin = new Padding(5, 4, 3, 4);
            btnTerminate.Name = "btnTerminate";
            tablePanel1.SetRow(btnTerminate, 3);
            btnTerminate.Size = new Size(255, 61);
            btnTerminate.TabIndex = 0;
            btnTerminate.Text = "Terminate";
            // 
            // directxFormContainerControl1
            // 
            directxFormContainerControl1.Controls.Add(tablePanel1);
            directxFormContainerControl1.Location = new Point(1, 46);
            directxFormContainerControl1.Margin = new Padding(3, 4, 3, 4);
            directxFormContainerControl1.Name = "directxFormContainerControl1";
            directxFormContainerControl1.Size = new Size(954, 883);
            directxFormContainerControl1.TabIndex = 0;
            // 
            // ExceptionForm
            // 
            AcceptButton = btnRecover;
            Appearance.Options.UseFont = true;
            AutoScaleDimensions = new SizeF(10F, 25F);
            AutoScaleMode = AutoScaleMode.Font;
            ChildControls.Add(directxFormContainerControl1);
            ClientSize = new Size(956, 930);
            ControlBox = false;
            Font = new Font("Segoe UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            Margin = new Padding(3, 4, 3, 4);
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "ExceptionForm";
            Text = "ExceptionForm";
            ((System.ComponentModel.ISupportInitialize)tablePanel1).EndInit();
            tablePanel1.ResumeLayout(false);
            tablePanel1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)memoExceptionDetails.Properties).EndInit();
            directxFormContainerControl1.ResumeLayout(false);
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.Utils.Layout.TablePanel tablePanel1;
        private DevExpress.XtraEditors.MemoEdit memoExceptionDetails;
        private DevExpress.XtraEditors.SimpleButton btnRecover;
        private DevExpress.XtraEditors.SimpleButton btnTerminate;
        private DevExpress.XtraEditors.DirectXFormContainerControl directxFormContainerControl1;
        private DevExpress.XtraEditors.LabelControl lblMessage;
        private DevExpress.XtraEditors.SimpleButton btnCopy;
        private DevExpress.XtraEditors.LabelControl lblPrivacyStatement;
    }
}