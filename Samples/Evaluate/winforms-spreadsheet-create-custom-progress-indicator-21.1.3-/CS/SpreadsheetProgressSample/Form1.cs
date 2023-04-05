using System;
using System.Windows.Forms;
using System.Threading;
using DevExpress.Office.Services;
using DevExpress.Office.Services.Implementation;
using DevExpress.Services;

namespace SpreadsheetProgressSample {
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm, IProgressIndicationService
    {
        CancellationTokenSource cancellationTokenSource;
        ICancellationTokenProvider savedCancellationTokenProvider;

        public Form1() {
            InitializeComponent();
            // Replace the default progress indication service
            // with a custom service.
            spreadsheetControl1.ReplaceService<IProgressIndicationService>(this);
        }

        void IProgressIndicationService.Begin(string displayName, int minProgress, int maxProgress, int currentProgress) {
            cancellationTokenSource = new CancellationTokenSource();
            // Register a new CancellationTokenProvider instance
            // to process cancellation requests. Save the reference
            // to the previously registered service.
            savedCancellationTokenProvider = spreadsheetControl1.ReplaceService<ICancellationTokenProvider>(new CancellationTokenProvider(cancellationTokenSource.Token));
            splashScreenManager1.ShowWaitForm();
            // Display the name of the running operation in the Wait Form.
            splashScreenManager1.SetWaitFormCaption(displayName);
            // Display the progress of the running operation in the Wait Form.
            splashScreenManager1.SetWaitFormDescription($"{currentProgress}%");
            // Send a command to the Wait Form
            // to specify the CancellationTokenSource object
            // used to generate cancellation tokens for the task cancellation.
            splashScreenManager1.SendCommand(WaitForm1.WaitFormCommand.SetCancellationTokenSource, cancellationTokenSource);
        }

        void IProgressIndicationService.End() {
            // Close the Wait Form.
            if (splashScreenManager1.IsSplashFormVisible)
                splashScreenManager1.CloseWaitForm();
            // Restore previous CancellationTokenProvider.
            spreadsheetControl1.ReplaceService(savedCancellationTokenProvider);
            spreadsheetControl1.UpdateCommandUI();
            // Dispose the CancellationTokenSource object.
            cancellationTokenSource?.Dispose();
            cancellationTokenSource = null;
        }

        void IProgressIndicationService.SetProgress(int currentProgress) {
            // Display the progress of the running operation in the Wait Form.
            splashScreenManager1.SetWaitFormDescription($"{currentProgress}%");
        }

        void spreadsheetControl1_UnhandledException(object sender, DevExpress.XtraSpreadsheet.SpreadsheetUnhandledExceptionEventArgs e) {
            // Handle OperationCanceledException
            // that is thrown when a user cancels the operation.
            if (e.Exception is OperationCanceledException)
                e.Handled = true;
        }
    }
}
