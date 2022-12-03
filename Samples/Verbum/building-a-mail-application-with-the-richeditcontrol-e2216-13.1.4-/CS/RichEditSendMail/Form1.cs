using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Net.Mail;
using DevExpress.XtraRichEdit;
using DevExpress.Utils;
using DevExpress.Office.Services;
using System.Net.Mime;
using System.IO;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Export.Html;
using System.Net;
using DevExpress.Office.Utils;

namespace RichEditSendMail {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            richEdit.LoadDocument("Hello.docx");
        }

        private void btnSend_Click(object sender, EventArgs e) {
            if ((edtTo.Text.Trim() == "") || (edtSubject.Text.Trim() == "") || (edtSmtp.Text.Trim() == ""))
            {
                MessageBox.Show("Fill in required fields");
                return;
            }

            try
            {
                MailMessage mailMessage = new MailMessage("XtraRichEdit@devexpress.com", edtTo.Text);
                mailMessage.Subject = edtSubject.Text;

                RichEditMailMessageExporter exporter = new RichEditMailMessageExporter(richEdit, mailMessage);
                exporter.Export();

                SmtpClient mailSender = new SmtpClient(edtSmtp.Text);
                //specify your login/password to log on to the SMTP server, if required
                //mailSender.Credentials = new NetworkCredential("login", "password");
                mailSender.Send(mailMessage);
                MessageBox.Show("Message sent", "RichEditSendMail", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception exc) {
                MessageBox.Show(exc.Message);
            
            }
        }

        public class RichEditMailMessageExporter : IUriProvider {
            readonly RichEditControl control;
            readonly MailMessage message;
            List<AttachementInfo> attachments;
            int imageId;

            public RichEditMailMessageExporter(RichEditControl control, MailMessage message) {
                Guard.ArgumentNotNull(control, "control");
                Guard.ArgumentNotNull(message, "message");

                this.control = control;
                this.message = message;
                
            }

            public virtual void Export() {
                this.attachments = new List<AttachementInfo>();

                AlternateView htmlView = CreateHtmlView();
                message.AlternateViews.Add(htmlView);
                message.IsBodyHtml = true;
            }

            protected internal virtual AlternateView CreateHtmlView() {
                control.BeforeExport += OnBeforeExport;
                string htmlBody = control.Document.GetHtmlText(control.Document.Range, this);
                AlternateView view = AlternateView.CreateAlternateViewFromString(htmlBody, Encoding.UTF8, MediaTypeNames.Text.Html);
                control.BeforeExport -= OnBeforeExport;

                int count = attachments.Count;
                for (int i = 0; i < count; i++) {
                    AttachementInfo info = attachments[i]; 
                    LinkedResource resource = new LinkedResource(info.Stream, info.MimeType);
                    resource.ContentId = info.ContentId;
                    view.LinkedResources.Add(resource);
                }
                return view;
            }

            void OnBeforeExport(object sender, BeforeExportEventArgs e) {
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
                string imageName = String.Format("image{0}", imageId);
                imageId++;

                OfficeImageFormat imageFormat = GetActualImageFormat(image.RawFormat);
                Stream stream = new MemoryStream(image.GetImageBytes(imageFormat));
                string mediaContentType = OfficeImage.GetContentType(imageFormat);
                AttachementInfo info = new AttachementInfo(stream, mediaContentType, imageName);
                attachments.Add(info);

                return "cid:" + imageName;
            }

            OfficeImageFormat GetActualImageFormat(OfficeImageFormat _officeImageFormat) {
                if (_officeImageFormat == OfficeImageFormat.Exif ||
                    _officeImageFormat == OfficeImageFormat.MemoryBmp)
                    return OfficeImageFormat.Png;
                else
                    return _officeImageFormat;
            }
            #endregion
        }

        public class AttachementInfo {
            Stream stream;
            string mimeType;
            string contentId;

            public AttachementInfo(Stream stream, string mimeType, string contentId) {
                this.stream = stream;
                this.mimeType = mimeType;
                this.contentId = contentId;
            }

            public Stream Stream { get { return stream; } }
            public string MimeType { get { return mimeType; } }
            public string ContentId { get { return contentId; } }
        }
    }
}