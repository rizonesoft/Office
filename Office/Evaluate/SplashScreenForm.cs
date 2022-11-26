using DevExpress.XtraSplashScreen;
using System;

namespace Rizonesoft.Office.Evaluate
{
    public partial class SplashScreenForm : SplashScreen
    {
        public SplashScreenForm()
        {

            InitializeComponent();
            labelCopyright.Text = "Copyright © 1998-" + DateTime.Now.Year.ToString();
            labelProductName.Text = Globals.ProductName + " 20" + Globals.ProductVersion.Major.ToString();

        }

        #region Overrides

        public override void ProcessCommand(Enum cmd, object arg)
        {
            base.ProcessCommand(cmd, arg);
            SplashScreenCommand command = (SplashScreenCommand)cmd;
            if (command == SplashScreenCommand.SetStatusLabel)
            {
                string labelText = (string)arg;
                StatusLabel.Text = labelText;
            }

        }

        #endregion

        public enum SplashScreenCommand
        {
            SetStatusLabel,
            Command2,
            Command3
        }


    }
}