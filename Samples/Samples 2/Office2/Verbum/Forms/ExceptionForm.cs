using System;
using DevExpress.XtraEditors;
using Rizonesoft.Office.Verbum.Classes;


namespace Rizonesoft.Office.Verbum.Forms
{
    public partial class ExceptionForm : XtraForm
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
