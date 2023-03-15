using DevExpress.XtraEditors;

namespace Rizonesoft.Office.TimeEx
{
    public partial class TimeForm : XtraForm
    {
        public TimeForm()
        {
            if (!SystemInformation.TerminalServerSession && Screen.AllScreens.Length > 1)
            {
                WindowsFormsSettings.SetPerMonitorDpiAware();
            }
            else
            {
                WindowsFormsSettings.SetDPIAware();
            }

            InitializeComponent();
            SetTimeDate();
        }


        private void CoreTimer_Tick(object sender, EventArgs e)
        {
            SetTimeDate();
        }

        public static TimeForm? CheckInstance { get; private set; }

        // Create a public static property that will create an instance of the form and return it
        public static TimeForm CreateInstance
        {
            get
            {
                CheckInstance ??= new TimeForm();
                return CheckInstance;
            }
        }

        private void SetTimeDate()
        {
            DigitalTime.Text = DateTime.Now.ToString("HH:mm:ss.");
            DateLabel.Text = DateTime.Now.ToString("dddd, dd MMMM yyyy");
        }

        private void TimeForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            CheckInstance = null;
        }
    }
}