namespace Rizonesoft.Office.Verbum
{
    using DevExpress.XtraSplashScreen;
    using System;

    public partial class SplashScreenForm : SplashScreen
    {
        public SplashScreenForm()
        {
            Version applicationVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;

            InitializeComponent();
            labelNameVersion.Text = "Rizonesoft Verbum 20" + applicationVersion.Major.ToString();
            labelCopyright.Text = "Copyright © 1998-" + DateTime.Now.Year.ToString();
        }

        #region Overrides
        public override void ProcessCommand(Enum cmd, object arg)
        {
            base.ProcessCommand(cmd, arg);
            SplashScreenCommand command = (SplashScreenCommand)cmd;
            if(command == SplashScreenCommand.SetStatusLabel)
            {
                string labelText = (string)arg;
                StatusLabel.Text = labelText;
            }
        }
        #endregion

        public enum SplashScreenCommand
        {
            SetStatusLabel
        }
    }
}