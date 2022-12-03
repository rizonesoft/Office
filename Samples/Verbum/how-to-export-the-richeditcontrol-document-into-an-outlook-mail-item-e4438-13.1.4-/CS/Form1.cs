using System;
using System.IO;
using System.Text;
using System.Windows.Forms;
using System.Drawing.Imaging;
using DevExpress.Utils;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.Office.Utils;
using DevExpress.Office.Services;
using Outlook = Microsoft.Office.Interop.Outlook;

namespace RichEditOpenInOutlook {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            richEdit.LoadDocument("Hello.docx");
        }

        private void btnSend_Click(object sender, EventArgs e) {
            if ((edtTo.Text.Trim() == "") || (edtSubject.Text.Trim() == "")) {
                MessageBox.Show("Fill in required fields");
                return;
            }
            try {
                Outlook.Application application = new Outlook.Application();
                Outlook.MailItem mailItem = (Outlook.MailItem)application.CreateItem(Outlook.OlItemType.olMailItem);

                mailItem.To = edtTo.Text;
                mailItem.Subject = edtSubject.Text;

                RichEditMailMessageExporter exporter = new RichEditMailMessageExporter(richEdit, mailItem);
                exporter.Export();

                mailItem.Display(false);
            }
            catch (Exception exc) {
                MessageBox.Show(exc.Message);
            }
        }

        public class RichEditMailMessageExporter : IUriProvider {
            readonly RichEditControl control;
            readonly Outlook.MailItem mailItem;
            int imageId;
            string tempFiles = Path.Combine(Directory.GetCurrentDirectory(), "TempFiles");

            public RichEditMailMessageExporter(RichEditControl control, Outlook.MailItem mailItem) {
                Guard.ArgumentNotNull(control, "control");
                Guard.ArgumentNotNull(mailItem, "mailItem");

                this.control = control;
                this.mailItem = mailItem;
            }

            public virtual void Export() {
                if (!Directory.Exists(tempFiles))
                    Directory.CreateDirectory(tempFiles);
                
                control.BeforeExport += OnBeforeExport;
                string htmlBody = control.Document.GetHtmlText(control.Document.Range, this);
                control.BeforeExport -= OnBeforeExport;
                
                mailItem.BodyFormat = Outlook.OlBodyFormat.olFormatHTML;
                mailItem.HTMLBody = htmlBody;
            }

            private void OnBeforeExport(object sender, BeforeExportEventArgs e) {
                HtmlDocumentExporterOptions options = e.Options as HtmlDocumentExporterOptions;
                if (options != null) {
                    options.Encoding = Encoding.UTF8;
                }
            }

            #region IUriProvider Members
            public string CreateCssUri(string rootUri, string styleText, string relativeUri) {
                return String.Empty;
            }

            public string CreateImageUri(string rootUri, OfficeImage image, string relativeUri) {
                string imageName = String.Format("image{0}.png", imageId);
                imageId++;

                string imagePath = Path.Combine(tempFiles, imageName);

                image.NativeImage.Save(imagePath, ImageFormat.Png);

                mailItem.Attachments.Add(imagePath, Outlook.OlAttachmentType.olByValue, 0, Type.Missing);

                return "cid:" + imageName;
            }
            #endregion
        }
    }
}