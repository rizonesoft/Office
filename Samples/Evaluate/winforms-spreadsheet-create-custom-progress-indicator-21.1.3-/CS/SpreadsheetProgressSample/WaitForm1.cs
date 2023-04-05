using System;
using System.Threading;
using DevExpress.XtraWaitForm;

namespace SpreadsheetProgressSample {
    public partial class WaitForm1 : WaitForm {
        CancellationTokenSource cancellationTokenSource;

        public WaitForm1() {
            InitializeComponent();
            progressPanel1.AutoSize = true;
        }

        public override void SetCaption(string caption) {
            base.SetCaption(caption);
            progressPanel1.Caption = caption;
        }

        public override void SetDescription(string description) {
            base.SetDescription(description);
            progressPanel1.Description = description;
        }

        public override void ProcessCommand(Enum cmd, object arg) {
            base.ProcessCommand(cmd, arg);
            WaitFormCommand command = (WaitFormCommand)cmd;
            if (command == WaitFormCommand.SetCancellationTokenSource)
                cancellationTokenSource = (CancellationTokenSource)arg;
        }

        public enum WaitFormCommand {
            SetCancellationTokenSource
        }

        void Cancel_Click(object sender, EventArgs e) {
            cancellationTokenSource?.Cancel();
        }
    }
}