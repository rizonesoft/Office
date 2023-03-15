namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraSplashScreen;
    using System;
    using Utilities;

    internal sealed partial class SplashScreenForm : SplashScreen
    {
        public SplashScreenForm()
        {
            InitializeComponent();
            labelNameVersion.Text = $@"{StcVerbum.ProductName} {Office.Utilities.RizonesoftEx.ProductVersionMajor}";
            labelCopyright.Text = $@"Copyright © 1998-{DateTime.Now.Year}";
        }

        public override void ProcessCommand(Enum cmd, object arg)
        {
            base.ProcessCommand(cmd, arg);
            var command = (SplashScreenCommand)cmd;
            if (command != SplashScreenCommand.WS_SET_STATUS_LABEL)
            {
                return;
            }

            var labelText = (string)arg;
            StatusLabel.Text = labelText;
        }

        public enum SplashScreenCommand
        {
            WS_SET_STATUS_LABEL
        }
    }
}