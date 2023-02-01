using System;
using System.Windows.Forms;


namespace Datum.Verbum.UnhandledExceptions
{
    public partial class exceptionForm : DevExpress.XtraEditors.XtraForm
    {
        public exceptionForm(Exception ex)
        {
            InitializeComponent();
            this.memoDescription.Text = String.Format("{0}\r\n{1}",
                environmentInfo.EnvironmentToString(),
                environmentInfo.ExceptionToString(ex));
        }

        private void yesButton_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void noButton_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

    }
}