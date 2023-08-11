namespace Rizonesoft.Office.ErrorHandling
{
    /// <summary>
    /// Handles unhandled exceptions for the application.
    /// </summary>
    public class UnhandledExceptionHandler
    {
        // Capture the UI thread's synchronization context
        private static readonly SynchronizationContext? uiContext = SynchronizationContext.Current;

        /// <summary>
        /// Registers event handlers for unhandled exceptions.
        /// </summary>
        /// <param name="isWindowsFormsApp">Indicates whether the application is a Windows Forms application.</param>
        public static void Register(bool isWindowsFormsApp = false)
        {
            AppDomain.CurrentDomain.UnhandledException += HandleUnhandledException;
            TaskScheduler.UnobservedTaskException += HandleUnobservedTaskException;

            if (isWindowsFormsApp)
            {
                Application.ThreadException += HandleThreadException;
            }
        }

        /// <summary>
        /// Handles unhandled exceptions from the current application domain.
        /// </summary>
        private static void HandleUnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            if (e.ExceptionObject is Exception exception)
            {
                HandleException(exception, e.IsTerminating);
            }
        }

        /// <summary>
        /// Handles unobserved task exceptions.
        /// </summary>
        private static void HandleUnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
        {
            HandleException(e.Exception, false);
            e.SetObserved(); // Prevent the process from being terminated
        }

        /// <summary>
        /// Handles thread exceptions.
        /// </summary>
        private static void HandleThreadException(object sender, ThreadExceptionEventArgs e)
        {
            HandleException(e.Exception, false);
        }

        /// <summary>
        /// Handles exceptions, displays an error message, and logs the exception.
        /// </summary>
        /// <param name="exception">The exception to handle.</param>
        /// <param name="isTerminating">Indicates whether the application is terminating due to the exception.</param>
        private static void HandleException(Exception exception, bool isTerminating)
        {
            Serilogger.LogMessage(LogLevel.Error, "Unhandled exception occurred. You can blame the developer for this mess!", exception);

            // Show ExceptionForm on the UI thread
            uiContext?.Send(_ => ShowExceptionForm(exception, isTerminating), null);
        }

        private static void ShowExceptionForm(Exception exception, bool isTerminating)
        {
            using var exceptionForm = new ExceptionForm(exception);
            var result = exceptionForm.ShowDialog();

            if (result == DialogResult.Cancel || isTerminating)
            {
                Environment.Exit(-1);
            }
        }
    }
}
