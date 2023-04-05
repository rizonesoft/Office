namespace Rizonesoft.Office.Flow
{
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Flow.Utilities;
    using Rizonesoft.Office.Utilities;
    using System;

    public partial class SplashScreenForm : SplashScreen
    {
        public SplashScreenForm()
        {
            InitializeComponent();
            labelNameVersion.Text = $"{StcFlow.ProductName} {Office.Utilities.RizonesoftEx.ProductVersionMajor}";
            labelCopyright.Text = $"Copyright © 1998-{DateTime.Now.Year}";
        }

        public override void ProcessCommand(Enum cmd, object arg)
        {
            base.ProcessCommand(cmd, arg);
            SplashScreenCommand command = (SplashScreenCommand)cmd;
            if (command != SplashScreenCommand.SetStatusLabel)
            {
                return;
            }

            string labelText = (string)arg;
            StatusLabel.Text = labelText;
        }

        public enum SplashScreenCommand
        {
            SetStatusLabel
        }
    }
}