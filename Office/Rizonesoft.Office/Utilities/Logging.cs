namespace Rizonesoft.Office.Utilities
{
    using NLog;
    using System.Text.RegularExpressions;

    public static class Logging
    {
        public static readonly Logger ROLogger = LogManager.GetCurrentClassLogger();

        public static void ConfigureLogging()
        {
            DateTime dateNow = DateTime.Now;
            string padMonth = dateNow.Month.ToString().PadLeft(2, '0');
            string loggingFilePath = $"{GlobalProperties.UserAppDirectory}\\Logging\\{dateNow.Year}-{padMonth}.log";

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

        public static string CleanMessageForLogging(string sMessage)
        {
            string sReturn = Regex.Replace(sMessage, 
                                 @"\t|\n|\r", 
                                 " ");
            return sReturn;
        }


    }
}
