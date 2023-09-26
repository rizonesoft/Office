using System.Windows.Forms;
using DevExpress.XtraEditors;
using DevExpress.XtraLayout;

namespace Rizonesoft.Office.Scholar.Controls
{
    public sealed class PasswordBoxControl : XtraUserControl
    {
        private readonly TextEdit tePassword;

        public PasswordBoxControl()
        {
            var lc = new LayoutControl
            {
                Dock = DockStyle.Fill
            };
            tePassword = new TextEdit
            {
                Properties = { UseSystemPasswordChar = true }
            };
            lc.AddItem(string.Empty, tePassword).TextVisible = false;
            this.Controls.Add(lc);
            this.Height = 100;
            this.Dock = DockStyle.Top;
        }

        // Password property to get or set the text from the tePassword control
        public string Password
        {
            get => tePassword.Text;
            set => tePassword.Text = value;
        }

        // Property to get or set the _passwordAttemptsLimit field
        public int PasswordAttemptsLimit { get; set; } = 5;
    }
}
