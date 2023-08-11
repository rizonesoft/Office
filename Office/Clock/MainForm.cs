using System;
using System.Collections.Generic;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Navigation;
using Rizonesoft.Office.UI.Forms;

namespace Rizonesoft.Office.Clock
{
    /// <summary>
    /// Represents the main form of the application.
    /// </summary>
    public partial class MainForm : RibbonFormBase
    {
        private Dictionary<BarButtonItem, NavigationPage> ButtonPageMap { get; } = new();
        private bool IsSwitchingPage { get; set; }
        private readonly object lockObj = new();

        /// <summary>
        /// Initializes a new instance of the MainForm class.
        /// </summary>
        public MainForm()
        {
            InitializeComponent();
            AfterInitializeComponents();
            SetTimeDate();

            ButtonPageMap.Add(ClockButton, ClockPage);
            ButtonPageMap.Add(TimerButton, TimerPage);
            ButtonPageMap.Add(StopwatchButton, StopwatchPage);
            ButtonPageMap.Add(AlarmButton, AlarmPage);
            ButtonPageMap.Add(FocusButton, FocusPage);
        }

        /// <summary>
        /// Sets the time and date in the UI.
        /// </summary>
        private void SetTimeDate()
        {
            if (InvokeRequired)
            {
                Invoke((Action)SetTimeDate);
                return;
            }

            var now = DateTime.Now;
            ClockLabel.Text = now.ToString("HH:mm:ss");
            DateStatusItem.Caption = now.ToString("dddd, dd MMMM yyyy");
        }

        /// <summary>
        /// Event handler for ClockTimer Tick event. 
        /// </summary>
        private void ClockTimer_Tick(object sender, EventArgs e)
        {
            SetTimeDate();
        }

        /// <summary>
        /// Sets the selected page in the main navigation frame.
        /// </summary>
        private void SetPage(NavigationPage page, BarButtonItem button)
        {
            lock (lockObj)
            {
                IsSwitchingPage = true;
                MainNavigationFrame.SelectedPage = page;

                foreach (var barButton in ButtonPageMap.Keys)
                {
                    barButton.Down = false;
                }

                button.Down = true;
                IsSwitchingPage = false;
            }
        }

        /// <summary>
        /// Event handler for RibbonButton Click event.
        /// </summary>
        private void RibbonButton_DownChanged(object sender, ItemClickEventArgs e)
        {
            if (IsSwitchingPage)
            {
                return;
            }

            if (sender is not BarButtonItem button)
            {
                throw new InvalidOperationException($"Unknown {nameof(sender)} clicked.");
            }
            else if (ButtonPageMap.TryGetValue(button, out var page))
            {
                SetPage(page, button);
            }
            else
            {
                throw new InvalidOperationException($"Button '{button.Name}' clicked has no corresponding page.");
            }
        }

        private void MinutesSpinEdit_ValueChanged(object sender, EventArgs e)
        {
            var timerSpan = TimeSpan.FromMinutes((int)MinutesSpinEdit.Value);
            TimerLabel.Text = timerSpan.ToString(@"hh\:mm\:ss");
        }
    }
}
