using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.XtraEditors;

namespace RichEditControl_Encryption
{
    public partial class Form1 : XtraForm
    {
        int tryCount = 4;
        public Form1()
        {
            InitializeComponent();
            InitializeEncryptionComboBoxEdit1();
            InitializePasswordEdit();
            richEditControl1.LoadDocument("testEncrypted.docx");
        }
        private void RichEditControl1_BeforeImport(object sender, BeforeImportEventArgs e)
        {
            //Specify the password to load an encrypted file
            richEditControl1.Options.Import.EncryptionPassword = "test";
        }

        private void RichEditControl1_EncryptedFilePasswordRequested(object sender, EncryptedFilePasswordRequestedEventArgs e)
        {
            //Count the number of attempts to enter the password
            if (tryCount > 0)
            {
                tryCount--;
            }
        }

        private void RichEditControl1_EncryptedFilePasswordCheckFailed(object sender, EncryptedFilePasswordCheckFailedEventArgs e)
        {

            //Analyze the error that led to this event
            //Depending on the user input and number of attempts,
            //Prompt user to enter a password again
            //or create an empty file
            switch (e.Error)
            {
                case RichEditDecryptionError.PasswordRequired:
                    if (tryCount > 0)
                    {
                        e.TryAgain = true;
                        e.Handled = true;
                        MessageBox.Show("You did not enter the password!", String.Format(" {0} attempts left", tryCount));
                    }
                    else
                        e.TryAgain = false;

                    break;

                case RichEditDecryptionError.WrongPassword:
                    if (tryCount > 0)
                    {
                        if ((MessageBox.Show("The password is incorrect. Try Again?", String.Format(" {0} attempts left", tryCount),
                            MessageBoxButtons.YesNo)) == DialogResult.Yes)
                        {
                            e.TryAgain = true;
                            e.Handled = true;
                        }

                    }
                    break;
            }
            e.Handled = true;

        }

        private void InitializePasswordEdit()
        {
            passwordEdit1.EditValue = "123";
        }

        void InitializeEncryptionComboBoxEdit1()
        {
            foreach (EncryptionType currentValue in Enum.GetValues(typeof(EncryptionType)))
                encryptionComboBox1.Properties.Items.Add(currentValue.ToString());
            encryptionComboBox1.EditValue = EncryptionType.Strong.ToString();
        }

        private void SimpleButton1_Click(object sender, EventArgs e)
        {
            richEditControl1.Document.Encryption.Password = passwordEdit1.EditValue.ToString();
            richEditControl1.Document.Encryption.Type = (EncryptionType)Enum.Parse(typeof(EncryptionType), encryptionComboBox1.EditValue.ToString());
            richEditControl1.SaveDocumentAs();
        }

        private void RichEditControl1_DecryptionFailed(object sender, DecryptionFailedEventArgs e)
        {
            MessageBox.Show(e.Exception.Message.ToString(), "Exception");
        }
    }
    #region #CustomSaveFileDialog
    public class MyRichEditControl : RichEditControl
    {
        public override void SaveDocumentAs()
        {
            using (SaveFileDialog myFileDialog = new SaveFileDialog())
            {
                myFileDialog.Filter = "Word 2007 Document (*.docx)|*.docx|Microsoft Word Document (*.doc*)|*.doc*";
                myFileDialog.FilterIndex = 1;
                myFileDialog.CheckFileExists = false;
                DialogResult result = myFileDialog.ShowDialog();
                if (result == DialogResult.OK)
                {
                    string ext = Path.GetExtension(myFileDialog.FileName);
                    if (ext == ".docx")
                        this.SaveDocument(myFileDialog.FileName, DocumentFormat.OpenXml);
                    else
                        this.SaveDocument(myFileDialog.FileName, DocumentFormat.Doc);

                    if (MessageBox.Show("The document is saved with new password. Open the file?", "", MessageBoxButtons.YesNo) == DialogResult.Yes)
                    {
                        this.LoadDocument(myFileDialog.FileName);
                    }
                }
            }
        }
    }
    #endregion #CustomSaveFileDialog
}
