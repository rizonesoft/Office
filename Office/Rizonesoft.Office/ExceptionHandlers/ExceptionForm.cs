using NLog;


namespace Rizonesoft.Office.ExceptionHandlers
{
    public partial class ExceptionForm : DevExpress.XtraEditors.DirectXForm
    {
        private static Logger nlogger = NLog.LogManager.GetCurrentClassLogger();

        public ExceptionForm()
        {
            InitializeComponent();
            bugMemoEdit.Text = String.Format("{0}\r\n\r\n{1}",
                EnvironmentInfo.EnvironmentToString(),
                "Exception:");
        }

        public ExceptionForm(Exception ex)
        {
            var nlogConfig = new NLog.Config.LoggingConfiguration();
            // Targets where to log to: File and Console.
            var nlogFile = new NLog.Targets.FileTarget("logfile") { FileName = Utilities.loggingFilePath };
            var nlogConsole = new NLog.Targets.ConsoleTarget("logconsole");

            // Rules for mapping loggers to targets.            
            nlogConfig.AddRule(LogLevel.Info, LogLevel.Fatal, nlogConsole);
            nlogConfig.AddRule(LogLevel.Debug, LogLevel.Fatal, nlogFile);

            // Apply config           
            LogManager.Configuration = nlogConfig;

            InitializeComponent();
            bugMemoEdit.Text = String.Format("{0}\r\n\r\n{1}",
                EnvironmentInfo.EnvironmentToString(),
                EnvironmentInfo.ExceptionToString(ex));
            nlogger.Error(ex, "Whoops!");
        }

        private void copyButton_Click(object sender, EventArgs e)
        {
            bugMemoEdit.Focus();
            bugMemoEdit.Copy();
        }

        private void cancelButton_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}