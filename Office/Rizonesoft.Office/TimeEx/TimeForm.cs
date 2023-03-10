using DevExpress.XtraEditors;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Rizonesoft.Office.TimeEx
{
    public partial class TimeForm : DevExpress.XtraEditors.XtraForm
    {
        public TimeForm()
        {
            InitializeComponent();
            SetTimeDate();
        }


        private static TimeForm? formInstance;

        private void CoreTimer_Tick(object sender, EventArgs e)
        {
            SetTimeDate();
        }

        public static TimeForm? CheckInstance
        {
            get
            {
                return formInstance;
            }
        }

        // Create a public static property that will create an instance of the form and return it
        public static TimeForm CreateInstance
        {
            get
            {
                formInstance ??= new TimeForm();
                return formInstance;
            }
        }

        private void SetTimeDate()
        {
            DigitalTime.Text = DateTime.Now.ToString("HH:mm:ss.");
            DateLabel.Text = DateTime.Now.ToString("dddd, dd MMMM yyyy");
        }

        private void TimeForm_FormClosed(object sender, FormClosedEventArgs e)
        {
            formInstance = null;
        }
    }
}