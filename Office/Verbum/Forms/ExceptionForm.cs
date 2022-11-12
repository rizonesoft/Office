using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace Rizonesoft.Office.Verbum
{
    public partial class ExceptionForm : Form
    {
        public ExceptionForm()
        {
            InitializeComponent();
            this.textBoxError.Text = String.Format("{0}\r\n\r\n{1}",
                EnvironmentInfo.EnvironmentToString(),
                "Exception:");
        }

        public ExceptionForm(Exception ex)
        {
            InitializeComponent();
            this.textBoxError.Text = String.Format("{0}\r\n\r\n{1}",
                EnvironmentInfo.EnvironmentToString(),
                EnvironmentInfo.ExceptionToString(ex));
        }

        private void buttonCopy_Click(object sender, EventArgs e)
        {
            this.textBoxError.SelectAll();
            this.textBoxError.Copy();
        }

        private void buttonEmail_Click(object sender, EventArgs e)
        {
            System.Diagnostics.Process.Start("mailto:support@rizonesoft.com?subject=Rizonesoft Office Error!");
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
