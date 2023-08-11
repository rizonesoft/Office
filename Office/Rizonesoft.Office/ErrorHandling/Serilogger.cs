using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Settings;
using Serilog;
using Serilog.Events;

#pragma warning disable CS1591

namespace Rizonesoft.Office.ErrorHandling
{
    /// <summary>
    /// Represents the log level for the Serilogger.
    /// </summary>
    public enum LogLevel
    {
        Debug,
        Info,
        Warning,
        Error,
        Fatal
    }

    /// <summary>
    /// Provides functionality to log messages with different log levels.
    /// </summary>
    public static class Serilogger
    {
        private static readonly ILogger _logger;

        static Serilogger()
        {
            var logRollingInterval = GlobalSettings.LogRollingInterval;
            var logFileLimit = GlobalSettings.LogFileLimit;

            _logger = new LoggerConfiguration()
                .MinimumLevel.Debug()
                .Enrich.WithThreadId()
                .Enrich.WithProcessId()
                .Enrich.With<CustomContextEnricher>()
                .WriteTo.Async(a => a.File(GlobalConfiguration.LogFilePath,
                    rollingInterval: (RollingInterval)logRollingInterval,
                    retainedFileCountLimit: logFileLimit,
                    shared: true,
                    outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] PID:{ProcessId} TID:{ThreadId} Context:{CustomContext} {Message:lj}{NewLine}{Exception}"))
                .CreateLogger();
        }

        /// <summary>
        /// Logs a message with the specified log level, exception, and custom context.
        /// </summary>
        /// <param name="level">The log level of the message.</param>
        /// <param name="message">The message to log.</param>
        /// <param name="exception">The exception related to the message, if any (optional).</param>
        /// <param name="customContext">The custom context to enrich the log event with (optional).</param>
        /// <exception cref="ArgumentNullException">Thrown when the message is null or empty.</exception>
        public static void LogMessage(LogLevel level, string message, Exception? exception = null, string? customContext = null)
        {
            if (string.IsNullOrEmpty(message))
            {
                throw new ArgumentNullException(nameof(message), @"Message cannot be null or empty.");
            }

            switch (level)
            {
                case LogLevel.Debug:
                    _logger.Debug(exception, "{Message} {CustomContext}", message, customContext);
                    break;
                case LogLevel.Info:
                    _logger.Information(exception, "{Message} {CustomContext}", message, customContext);
                    break;
                case LogLevel.Warning:
                    _logger.Warning(exception, "{Message} {CustomContext}", message, customContext);
                    break;
                case LogLevel.Error:
                    _logger.Error(exception, "{Message} {CustomContext}", message, customContext);
                    break;
                case LogLevel.Fatal:
                    _logger.Fatal(exception, "{Message} {CustomContext}", message, customContext);
                    break;
                default:
                    throw new ArgumentOutOfRangeException(nameof(level), level, null);
            }
        }

        private class CustomContextEnricher : Serilog.Core.ILogEventEnricher
        {
            public void Enrich(LogEvent logEvent, Serilog.Core.ILogEventPropertyFactory propertyFactory)
            {
                logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("CustomContext", logEvent.Properties["CustomContext"]));
            }
        }
    }
}
