using System;
using System.IO;
using System.Text;
using DevExpress.Utils;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Internal;
using DevExpress.XtraRichEdit.Model;
using System.Drawing;
using DevExpress.Office;
using DevExpress.Office.Export;
using DevExpress.Office.Internal;
using DevExpress.XtraRichEdit.API.Native.Implementation;

namespace RichEditBBCExporter {
    public class BBCodeDocumentExporter : IExporter<DocumentFormat, bool> {
        internal static readonly FileDialogFilter filter = new FileDialogFilter("Bulletin Board Code", "bbc");

        public FileDialogFilter Filter { get { return filter; } }
        public DocumentFormat Format { get { return BBCodeDocumentFormat.Id; } }
        public IExporterOptions SetupSaving() {
            return new BBCodeDocumentExporterOptions();
        }

        public bool SaveDocument(IDocumentModel documentModel, Stream stream, IExporterOptions options) {
            BBCodeExporter exporter = new BBCodeExporter((DocumentModel)documentModel, (BBCodeDocumentExporterOptions)options);
            exporter.Export(stream);
            return true;

        }

        public static void Register(IServiceProvider provider) {
            if(provider == null)
                return;
            IDocumentExportManagerService service = provider.GetService(typeof(IDocumentExportManagerService)) as IDocumentExportManagerService;
            if(service != null)
                service.RegisterExporter(new BBCodeDocumentExporter());
        }
    }

    public class BBCodeDocumentExporterOptions : DocumentExporterOptions {
        protected override DocumentFormat Format { get { return BBCodeDocumentFormat.Id; } }
    }

    public class BBCodeExporter : DocumentModelExporter {
        readonly BBCodeDocumentExporterOptions options;
        Stream outputStream;
        StreamWriter documentContentWriter;
        bool hyperlinkExporting;

        public BBCodeExporter(DocumentModel documentModel, BBCodeDocumentExporterOptions options)
            : base(documentModel) {
            Guard.ArgumentNotNull(options, "options");
            this.options = options;
        }

        protected BBCodeDocumentExporterOptions Options { get { return options; } }
        protected internal StreamWriter DocumentContentWriter { get { return documentContentWriter; } set { documentContentWriter = value; } }

        public virtual void Export(Stream outputStream) {
            this.outputStream = outputStream;
            using(StreamWriter streamWriter = new StreamWriter(outputStream, Encoding.UTF8)) {
                DocumentContentWriter = streamWriter;
                Export();
                streamWriter.Flush();
            }
        }
        protected override void ExportTextRun(TextRun run) {
            string text = run.GetPlainText(PieceTable.TextBuffer);

            if(!hyperlinkExporting) {
                if(run.FontBold)
                    DocumentContentWriter.Write("[b]");
                if(run.FontItalic)
                    DocumentContentWriter.Write("[i]");
                if(run.FontUnderlineType != UnderlineType.None)
                    DocumentContentWriter.Write("[u]");
                if(run.FontStrikeoutType != StrikeoutType.None)
                    DocumentContentWriter.Write("[s]");
                if(run.ForeColorIndex != DevExpress.Office.Model.ColorModelInfoCache.EmptyColorIndex)
                    DocumentContentWriter.Write(string.Format("[color=#{0}]", ColorTranslator.ToHtml(DocumentModel.GetColor(run.ForeColorIndex))));
                if(run.DoubleFontSize != DocumentModel.DefaultCharacterProperties.DoubleFontSize)
                    DocumentContentWriter.Write(string.Format("[size={0}]", Math.Min(run.DoubleFontSize, 39)));
            }

            DocumentContentWriter.Write(text);

            if(!hyperlinkExporting) {
                if(run.DoubleFontSize != DocumentModel.DefaultCharacterProperties.DoubleFontSize)
                    DocumentContentWriter.Write("[/size]");
                if(run.ForeColorIndex != DevExpress.Office.Model.ColorModelInfoCache.EmptyColorIndex)
                    DocumentContentWriter.Write("[/color]");
                if(run.FontStrikeoutType != StrikeoutType.None)
                    DocumentContentWriter.Write("[/s]");
                if(run.FontUnderlineType != UnderlineType.None)
                    DocumentContentWriter.Write("[/u]");
                if(run.FontBold)
                    DocumentContentWriter.Write("[/b]");
                if(run.FontItalic)
                    DocumentContentWriter.Write("[/i]");
            }

            base.ExportTextRun(run);
        }

        protected override void ExportFieldCodeStartRun(FieldCodeStartRun run) {
            base.ExportFieldCodeStartRun(run);
            HyperlinkInfo hyperlinkInfo = GetHyperlinkInfo(run);
            if(hyperlinkInfo == null)
                return;

            DocumentContentWriter.Write(string.Format("[url={0}]", hyperlinkInfo.NavigateUri));
            hyperlinkExporting = true;
        }

        protected override void ExportFieldResultEndRun(FieldResultEndRun run) {
            base.ExportFieldResultEndRun(run);
            if(GetHyperlinkInfo(run) == null)
                return;

            DocumentContentWriter.Write("[/url]");
            hyperlinkExporting = false;
        }

        protected override void ExportInlinePictureRun(InlinePictureRun run) {
            DocumentContentWriter.Write(string.Format("[img]{0}[/img]", run.Image.Uri));
            base.ExportInlinePictureRun(run);
        }

        protected override ParagraphIndex ExportParagraph(Paragraph paragraph) {
            ParagraphIndex pi = base.ExportParagraph(paragraph);
            DocumentContentWriter.Write(Environment.NewLine);
            return pi;
        }

        HyperlinkInfo GetHyperlinkInfo(TextRun run) {
            RunIndex runIndex = run.GetRunIndex();
            Field field = PieceTable.FindFieldByRunIndex(runIndex);
            System.Diagnostics.Debug.Assert(field != null);
            HyperlinkInfo hyperlinkInfo = null;
            if(PieceTable.HyperlinkInfos.TryGetHyperlinkInfo(field.Index, out hyperlinkInfo))
                return hyperlinkInfo;
            return null;
        }
    }

    public static class BBCodeDocumentFormat {
        public static readonly DocumentFormat Id = new DocumentFormat(431);
    }
}
