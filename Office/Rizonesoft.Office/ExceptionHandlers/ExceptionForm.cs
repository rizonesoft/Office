using NLog;
using Rizonesoft.Office.EnvironmentEx;
using Rizonesoft.Office.ExceptionHandlers;
using Rizonesoft.Office.ROUtilities;

namespace Rizonesoft.Office.ExceptionHandlers
{
    public partial class ExceptionForm : DevExpress.XtraEditors.DirectXForm
    {

        public ExceptionForm()
        {
            InitializeComponent();
            bugMemoEdit.Text = String.Format("{0}\r\n\r\n{1}",
                ExceptionHandler.EnvironmentToString(),
                "Exception:");
        }

        public ExceptionForm(Exception ex)
        {

            InitializeComponent();
            bugMemoEdit.Text = String.Format("{0}\r\n\r\n{1}",
                ExceptionHandler.EnvironmentToString(),
                ExceptionHandler.ExceptionToString(ex));
            ROLogging.ROLogger.Error(ex, "Whoops!");
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