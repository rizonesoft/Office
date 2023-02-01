using System;
using System.IO;

using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Model;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Internal;


namespace Rizonesoft.Verbum
{
    #region #EmlDocumentExporter
    public class EmlDocumentExporter : IExporter<DocumentFormat, bool>
    {
        internal static readonly FileDialogFilter filter = new FileDialogFilter("E-Mail document", "eml");

        #region IDocumentExporter Members
        public FileDialogFilter Filter { get { return filter; } }
        public DocumentFormat Format { get { return EmlDocumentFormat.Id; } }
        public IExporterOptions SetupSaving()
        {
            return new EmlDocumentExporterOptions();
        }

        public bool SaveDocument(DocumentModel documentModel, Stream stream, IExporterOptions options)
        {
            documentModel.InternalAPI.SaveDocumentMhtContent(stream, (EmlDocumentExporterOptions)options);
            return true;
        }
        #endregion

        public static void Register(IServiceProvider provider)
        {
            if (provider == null)
                return;
            IDocumentExportManagerService service = provider.GetService(typeof(IDocumentExportManagerService)) as IDocumentExportManagerService;
            if (service != null)
                service.RegisterExporter(new EmlDocumentExporter());
        }
    }
    #endregion #EmlDocumentExporter

    #region #EmlDocumentExporterOptions
    public class EmlDocumentExporterOptions : MhtDocumentExporterOptions
    {
        protected override DocumentFormat Format { get { return EmlDocumentFormat.Id; } }
    }
    #endregion #EmlDocumentExporterOptions
}