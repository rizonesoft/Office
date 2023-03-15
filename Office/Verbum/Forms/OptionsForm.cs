using System;

namespace Rizonesoft.Office.Verbum.Forms
{
    public partial class OptionsForm : DevExpress.XtraEditors.XtraForm
    {
        public OptionsForm()
        {

            InitializeComponent();
        }

        public static OptionsForm CheckInstance { get; private set; }

        // Create a public static property that will create an instance of the form and return it
        public static OptionsForm CreateInstance
        {
            get
            {
                CheckInstance = new OptionsForm();
                return CheckInstance;
            }
        }

        private void navigationPane1_Click(object sender, EventArgs e)
        {

        }
    }
}
