using DevExpress.Pdf;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Scholar.Controls;
using Rizonesoft.Office.Scholar.Forms;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.UI;
using Rizonesoft.Office.Utilities;
using SautinSoft;
using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Drawing.Imaging;
using System.IO;
using Rizonesoft.Office.Scholar.Classes;
using System.Runtime.InteropServices;
using System.Security;
using System.Windows.Forms;
using Rizonesoft.Office.Settings;

namespace Rizonesoft.Office.Scholar
{

    public partial class DocForm : RibbonForm
    {

        public event EventHandler FileNameChanged;
        private string fileName;
        private int passwordAttempts;

        public string FileName
        {
            get => fileName;
            private set
            {
                if (fileName == value) return;
                fileName = value;
                OnFileNameChanged();
            }
        }

        #region Document Password (SecureString)

        private SecureString docPassword;

        // Public property to interact with the password
        public string PdfPassword
        {
            get => docPassword == null ? null : ConvertToUnsecureString(docPassword);
            set => docPassword = value == null ? null : ConvertToSecureString(value);
        }

        // Convert plain string to SecureString
        private static SecureString ConvertToSecureString(string plainPassword)
        {
            if (plainPassword == null)
                throw new ArgumentNullException(nameof(plainPassword));

            var secure = new SecureString();
            foreach (var c in plainPassword)
                secure.AppendChar(c);

            secure.MakeReadOnly();
            return secure;
        }

        // Convert SecureString to plain string
        private static string ConvertToUnsecureString(SecureString securePassword)
        {
            if (securePassword == null)
                return null;

            var unmanagedString = IntPtr.Zero;
            try
            {
                unmanagedString = Marshal.SecureStringToGlobalAllocUnicode(securePassword);
                return Marshal.PtrToStringUni(unmanagedString);
            }
            finally
            {
                Marshal.ZeroFreeGlobalAllocUnicode(unmanagedString);
            }
        }

        #endregion Document PdfPassword (SecureString)

        protected virtual void OnFileNameChanged()
        {
            FileNameChanged?.Invoke(this, EventArgs.Empty);
        }

        public DocForm()
        {
            InitializeComponent();
            ChildPDFViewer.NavigationPaneWidth = ScholarSettings.NavigationPaneWidth;
            UpdateUi();

            ChildPDFViewer.PasswordAttemptsLimit = 3;
            ChildPDFViewer.PasswordRequested += ChildPDFViewer_PasswordRequested;
        }





        private void UpdateUi()
        {
            HomeRibbonPage.Text = Strings.RibbonMain_Home;
        }

        public void OpenFile(string openFileName, int docIndex)
        {

            if (!string.IsNullOrEmpty(openFileName))
            {
                FileName = openFileName;
                ChildPDFViewer.LoadDocument(openFileName);
                ChildDocHelper.SetDocumentCaption(openFileName, this);
            }
            else
            {
                Text = FileName = $@"Document {docIndex}";
            }
        }

        private void RotateLeftBarButton_ItemClick(object sender, ItemClickEventArgs e)
        {
            ChildPDFViewer.RotationAngle = (ChildPDFViewer.RotationAngle - 90) % 360;
        }

        private void RotateRightBarButton_ItemClick(object sender, ItemClickEventArgs e)
        {
            ChildPDFViewer.RotationAngle = (ChildPDFViewer.RotationAngle + 90) % 360;
        }

        private void ChildPDFViewer_PasswordRequested(object sender, PdfPasswordRequestedEventArgs e)
        {
            passwordAttempts++;

            var passwordBox = new PasswordBoxControl();

            if (XtraDialog.Show(passwordBox, "Enter a password:", MessageBoxButtons.OKCancel) == DialogResult.Cancel)
            {
                e.PasswordString = null;
                passwordAttempts = 0;
            }
            else
            {
                e.PasswordString = passwordBox.Password;
                PdfPassword = passwordBox.Password;

                // Check if the number of attempts has reached the limit
                if (passwordAttempts < ChildPDFViewer.PasswordAttemptsLimit) return;
                XtraMessageBox.Show("Incorrect password. Maximum attempts reached.");
                PdfPassword = null;
                passwordAttempts = 0;

            }
        }
    }
}