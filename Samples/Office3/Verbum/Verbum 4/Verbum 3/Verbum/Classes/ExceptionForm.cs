using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using DevExpress.XtraEditors;

using Rizone.Verbum;

namespace Rizone.Verbum
{
    public partial class ExceptionForm : DevExpress.XtraEditors.XtraForm
    {

        public ExceptionForm()
        {
            InitializeComponent();
        }

        public ExceptionForm(Exception ex)
        {
			InitializeComponent();
            this.memoExDesc.Text = String.Format("{0}\r\n{1}",
                EnvironmentInfo.EnvironmentToString(),
                EnvironmentInfo.ExceptionToString(ex));
		}

    }
}