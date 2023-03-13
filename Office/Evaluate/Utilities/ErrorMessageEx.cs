namespace Rizonesoft.Office.Evaluate.Utilities
{
    using DevExpress.XtraEditors;
    using System.Windows.Forms;

    internal class ErrorMessageEx
    {
        public static void Show(string title, string message)
        {
            XtraMessageBoxArgs mArgs = new();
            mArgs.AutoCloseOptions.Delay = 5000;
            mArgs.Caption = title;
            mArgs.Text = message;
            mArgs.Buttons = new DialogResult[] { DialogResult.OK, DialogResult.Cancel };
            XtraMessageBox.Show(mArgs).ToString();
        }


    }
}