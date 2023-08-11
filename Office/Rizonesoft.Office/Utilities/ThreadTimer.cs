using Timer = System.Threading.Timer;

namespace Rizonesoft.Office.Utilities
{
    /// <summary>
    /// A utility class for running a task at regular intervals on a separate thread.
    /// </summary>
    public class ThreadTimer : IDisposable
    {
        private readonly Timer _timer;
        private readonly Action _action;
        private readonly int _interval;
        private bool _disposed;

        /// <summary>
        /// Initializes a new instance of the ThreadTimer class.
        /// </summary>
        /// <param name="action">The action to perform.</param>
        /// <param name="interval">The interval in milliseconds at which to perform the action.</param>
        public ThreadTimer(Action action, int interval)
        {
            _action = action ?? throw new ArgumentNullException(nameof(action));
            _interval = interval;
            _timer = new Timer(OnTimerElapsed);
        }

        /// <summary>
        /// Starts the timer.
        /// </summary>
        /// <param name="runNow">If true, the action will be performed immediately, as well as at intervals. Default is false.</param>
        public void Start(bool runNow = false)
        {
            _timer.Change(runNow ? 0 : _interval, _interval);
        }

        /// <summary>
        /// Stops the timer.
        /// </summary>
        public void Stop()
        {
            _timer.Change(Timeout.Infinite, Timeout.Infinite);
        }

        private void OnTimerElapsed(object? state)
        {
            try
            {
                _action();
            }
            catch (Exception ex)
            {
                // Here you can add logging or otherwise handle the exception
                Console.WriteLine($@"An error occurred: {ex}");
            }
        }

        #region IDisposable Support

        /// <summary>
        /// Releases the unmanaged resources used by the ThreadTimer and optionally releases the managed resources.
        /// </summary>
        /// <param name="disposing">true to release both managed and unmanaged resources; false to release only unmanaged resources.</param>
        protected virtual void Dispose(bool disposing)
        {
            if (_disposed) return;
            if (disposing)
            {
                _timer.Dispose();
            }

            _disposed = true;
        }

        /// <summary>
        /// Performs application-defined tasks associated with freeing, releasing, or resetting unmanaged resources.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        #endregion
    }
}

