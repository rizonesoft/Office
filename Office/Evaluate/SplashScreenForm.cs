﻿namespace Rizonesoft.Office.Evaluate
{
    using DevExpress.XtraSplashScreen;
    using Rizonesoft.Office.Evaluate.Utilities;
    using System;

    public partial class SplashScreenForm : SplashScreen
    {
        public SplashScreenForm()
        {
            InitializeComponent();
            labelNameVersion.Text = $"{EvaluateEx.ProductName} {Office.Utilities.RizonesoftEx.ProductVersionMajor}";
            labelCopyright.Text = $"Copyright © 1998-{DateTime.Now.Year}";
        }

        #region Overrides
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
        #endregion

        public enum SplashScreenCommand
        {
            SetStatusLabel
        }
    }
}