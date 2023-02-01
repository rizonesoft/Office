using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;

namespace Rizonesoft.Verbum
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
    }
}