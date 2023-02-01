using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using DevExpress.Utils.Zip;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Services;

namespace RichEditControlExtensions {
    public static class RichEditLoadDocumentHelper {
        const byte P = (byte)'P';
        const byte K = (byte)'K';

        static readonly byte[] docSignature = { 0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1 };


        public static void RegisterCusomOpenFileCommand(this RichEditControl richEdit) {
            CustomRichEditCommandFactoryService commandFactory = new CustomRichEditCommandFactoryService(richEdit, richEdit.GetService<IRichEditCommandFactoryService>());
            richEdit.RemoveService(typeof(IRichEditCommandFactoryService));
            richEdit.AddService(typeof(IRichEditCommandFactoryService), commandFactory);
        }

        public static void LoadDocumentEx(this IRichEditControl richEdit, Stream stream) {
            DevExpress.XtraRichEdit.DocumentFormat currentFormat = AutoDetermineDocumentFormat(stream);
            stream.Seek(0, SeekOrigin.Begin);
            richEdit.InnerControl.LoadDocument(stream, currentFormat);
        }

        public static void LoadDocumentEx(this IRichEditControl richEdit, string fileName) {
            using(System.IO.FileStream fs = new FileStream(fileName, System.IO.FileMode.Open)) {
                richEdit.LoadDocumentEx(fs);
            }
        }

        public static DevExpress.XtraRichEdit.DocumentFormat AutoDetermineDocumentFormat(Stream stream) {
            byte[] buffer = new byte[8];

            if(stream.Length < 8) return DevExpress.XtraRichEdit.DocumentFormat.PlainText;
            stream.Read(buffer, 0, buffer.Length);

            if(buffer.SequenceEqual(docSignature))
                return DevExpress.XtraRichEdit.DocumentFormat.Doc;

            else if(buffer[0] == P && buffer[1] == K)
                return CheckZippedFileContent(stream);

            string fileBeginning = Encoding.ASCII.GetString(buffer);
            if(fileBeginning.Contains("{\\rtf")) return DevExpress.XtraRichEdit.DocumentFormat.Rtf;
            if(fileBeginning.Contains("<!")) return DevExpress.XtraRichEdit.DocumentFormat.Html;

            return DevExpress.XtraRichEdit.DocumentFormat.PlainText;
        }

        static DevExpress.XtraRichEdit.DocumentFormat CheckZippedFileContent(Stream stream) {
            stream.Seek(0, SeekOrigin.Begin);
            InternalZipFileCollection files = InternalZipArchive.Open(stream);
            foreach(InternalZipFile entry in files) {
                if(entry.FileName.Contains(".rels") || entry.FileName.Contains("document.xml")) return DevExpress.XtraRichEdit.DocumentFormat.OpenXml;
                if(entry.FileName.Contains("content.xml")) return DevExpress.XtraRichEdit.DocumentFormat.OpenDocument;
            }
            return DevExpress.XtraRichEdit.DocumentFormat.PlainText;
        }
    }
}
