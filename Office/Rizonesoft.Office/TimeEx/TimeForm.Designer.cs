namespace Rizonesoft.Office.TimeEx
{
    partial class TimeForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(TimeForm));
            tabPane1 = new DevExpress.XtraBars.Navigation.TabPane();
            tabNavigationPage1 = new DevExpress.XtraBars.Navigation.TabNavigationPage();
            gaugeControl1 = new DevExpress.XtraGauges.Win.GaugeControl();
            DigitalTime = new DevExpress.XtraGauges.Win.Gauges.Digital.DigitalGauge();
            digitalBackgroundLayerComponent1 = new DevExpress.XtraGauges.Win.Gauges.Digital.DigitalBackgroundLayerComponent();
            tabNavigationPage2 = new DevExpress.XtraBars.Navigation.TabNavigationPage();
            CoreTimer = new System.Windows.Forms.Timer(components);
            DateLabel = new DevExpress.XtraEditors.LabelControl();
            ((System.ComponentModel.ISupportInitialize)tabPane1).BeginInit();
            tabPane1.SuspendLayout();
            tabNavigationPage1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)DigitalTime).BeginInit();
            ((System.ComponentModel.ISupportInitialize)digitalBackgroundLayerComponent1).BeginInit();
            SuspendLayout();
            // 
            // tabPane1
            // 
            tabPane1.Controls.Add(tabNavigationPage1);
            tabPane1.Controls.Add(tabNavigationPage2);
            tabPane1.Dock = DockStyle.Top;
            tabPane1.Location = new Point(0, 0);
            tabPane1.Name = "tabPane1";
            tabPane1.Pages.AddRange(new DevExpress.XtraBars.Navigation.NavigationPageBase[] { tabNavigationPage1, tabNavigationPage2 });
            tabPane1.RegularSize = new Size(348, 170);
            tabPane1.SelectedPage = tabNavigationPage1;
            tabPane1.Size = new Size(348, 170);
            tabPane1.TabIndex = 0;
            tabPane1.Text = "tabPane1";
            // 
            // tabNavigationPage1
            // 
            tabNavigationPage1.Caption = "Clock";
            tabNavigationPage1.Controls.Add(gaugeControl1);
            tabNavigationPage1.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("tabNavigationPage1.ImageOptions.SvgImage");
            tabNavigationPage1.ImageOptions.SvgImageSize = new Size(24, 24);
            tabNavigationPage1.ItemShowMode = DevExpress.XtraBars.Navigation.ItemShowMode.ImageAndText;
            tabNavigationPage1.Name = "tabNavigationPage1";
            tabNavigationPage1.Properties.ShowMode = DevExpress.XtraBars.Navigation.ItemShowMode.ImageAndText;
            tabNavigationPage1.Size = new Size(348, 135);
            // 
            // gaugeControl1
            // 
            gaugeControl1.BackColor = SystemColors.ControlLight;
            gaugeControl1.Dock = DockStyle.Top;
            gaugeControl1.Gauges.AddRange(new DevExpress.XtraGauges.Base.IGauge[] { DigitalTime });
            gaugeControl1.Location = new Point(0, 0);
            gaugeControl1.Name = "gaugeControl1";
            gaugeControl1.Size = new Size(348, 129);
            gaugeControl1.TabIndex = 0;
            // 
            // DigitalTime
            // 
            DigitalTime.AppearanceOff.ContentBrush = new DevExpress.XtraGauges.Core.Drawing.SolidBrushObject("Color:#0A151A");
            DigitalTime.AppearanceOn.ContentBrush = new DevExpress.XtraGauges.Core.Drawing.SolidBrushObject("Color:#289FB8");
            DigitalTime.BackgroundLayers.AddRange(new DevExpress.XtraGauges.Win.Gauges.Digital.DigitalBackgroundLayerComponent[] { digitalBackgroundLayerComponent1 });
            DigitalTime.Bounds = new Rectangle(6, 6, 336, 117);
            DigitalTime.DigitCount = 6;
            DigitalTime.Name = "DigitalTime";
            DigitalTime.Padding = new DevExpress.XtraGauges.Core.Base.TextSpacing(26, 20, 26, 20);
            DigitalTime.Text = "";
            // 
            // digitalBackgroundLayerComponent1
            // 
            digitalBackgroundLayerComponent1.BottomRight = new DevExpress.XtraGauges.Core.Base.PointF2D(313.775F, 99.9625F);
            digitalBackgroundLayerComponent1.Name = "digitalBackgroundLayerComponent1";
            digitalBackgroundLayerComponent1.ShapeType = DevExpress.XtraGauges.Core.Model.DigitalBackgroundShapeSetType.Style21;
            digitalBackgroundLayerComponent1.TopLeft = new DevExpress.XtraGauges.Core.Base.PointF2D(26F, 0F);
            digitalBackgroundLayerComponent1.ZOrder = 1000;
            // 
            // tabNavigationPage2
            // 
            tabNavigationPage2.Caption = "Timer";
            tabNavigationPage2.ImageOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("tabNavigationPage2.ImageOptions.SvgImage");
            tabNavigationPage2.ImageOptions.SvgImageSize = new Size(24, 24);
            tabNavigationPage2.ItemShowMode = DevExpress.XtraBars.Navigation.ItemShowMode.ImageAndText;
            tabNavigationPage2.Name = "tabNavigationPage2";
            tabNavigationPage2.Properties.ShowMode = DevExpress.XtraBars.Navigation.ItemShowMode.ImageAndText;
            tabNavigationPage2.Size = new Size(348, 170);
            // 
            // CoreTimer
            // 
            CoreTimer.Enabled = true;
            CoreTimer.Interval = 1000;
            CoreTimer.Tick += CoreTimer_Tick;
            // 
            // DateLabel
            // 
            DateLabel.Appearance.Font = new Font("Segoe UI", 9.75F, FontStyle.Regular, GraphicsUnit.Point);
            DateLabel.Appearance.Options.UseFont = true;
            DateLabel.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical;
            DateLabel.Dock = DockStyle.Left;
            DateLabel.Location = new Point(0, 170);
            DateLabel.Name = "DateLabel";
            DateLabel.Padding = new Padding(20, 0, 0, 0);
            DateLabel.Size = new Size(214, 17);
            DateLabel.TabIndex = 1;
            DateLabel.Text = "Monday, 01 January 2000";
            // 
            // TimeForm
            // 
            AutoScaleDimensions = new SizeF(6F, 13F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(348, 198);
            Controls.Add(DateLabel);
            Controls.Add(tabPane1);
            DoubleBuffered = true;
            FormBorderStyle = FormBorderStyle.FixedSingle;
            IconOptions.SvgImage = (DevExpress.Utils.Svg.SvgImage)resources.GetObject("TimeForm.IconOptions.SvgImage");
            Name = "TimeForm";
            Text = "Time";
            TopMost = true;
            FormClosed += TimeForm_FormClosed;
            ((System.ComponentModel.ISupportInitialize)tabPane1).EndInit();
            tabPane1.ResumeLayout(false);
            tabNavigationPage1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)DigitalTime).EndInit();
            ((System.ComponentModel.ISupportInitialize)digitalBackgroundLayerComponent1).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private DevExpress.XtraBars.Navigation.TabPane tabPane1;
        private DevExpress.XtraBars.Navigation.TabNavigationPage tabNavigationPage1;
        private DevExpress.XtraGauges.Win.GaugeControl gaugeControl1;
        private DevExpress.XtraGauges.Win.Gauges.Digital.DigitalGauge DigitalTime;
        private DevExpress.XtraGauges.Win.Gauges.Digital.DigitalBackgroundLayerComponent digitalBackgroundLayerComponent1;
        private DevExpress.XtraBars.Navigation.TabNavigationPage tabNavigationPage2;
        private System.Windows.Forms.Timer CoreTimer;
        private DevExpress.XtraEditors.LabelControl DateLabel;
    }
}