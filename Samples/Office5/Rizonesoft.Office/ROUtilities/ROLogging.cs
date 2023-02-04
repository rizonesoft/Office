namespace Rizonesoft.Office.ROUtilities
{
    using NLog;

    public static class ROLogging
    {
        public static readonly Logger ROLogger = LogManager.GetCurrentClassLogger();

        public static void ConfigureLogging()
        {
            DateTime dateNow = DateTime.Now;
            string padMonth = dateNow.Month.ToString().PadLeft(2, '0');
            string loggingFilePath = $"{ROGlobals.UserAppDirectory}\\Logging\\{dateNow.Year}-{padMonth}.log";

            var nlogConfig = new NLog.Config.LoggingConfiguration();
            var nlogFile = new NLog.Targets.FileTarget("logfile")
            {
                FileName = loggingFilePath,
                Layout = "${longdate}|${level}|${message}|${appdomain}|${assembly-version}|${exception}"
            };
            var nlogConsole = new NLog.Targets.ConsoleTarget("logconsole");

            nlogConfig.AddRule(LogLevel.Info, LogLevel.Fatal, nlogFile);
            nlogConfig.AddRule(LogLevel.Debug, LogLevel.Fatal, nlogConsole);

            LogManager.Configuration = nlogConfig;
        }
    }
}
