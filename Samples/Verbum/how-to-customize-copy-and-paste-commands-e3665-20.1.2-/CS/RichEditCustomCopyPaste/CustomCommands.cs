using System;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Commands.Internal;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Export.Html;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.Office.Commands.Internal;
using DevExpress.Office.Utils;

namespace RichEditCustomCopyPaste {
    public class CustomCopySelectionCommand : CopySelectionCommand {
        public CustomCopySelectionCommand(IRichEditControl control)
            : base(control) {
        }
        protected override void ExecuteCore() {
            RichEditControl richEditControl = (RichEditControl)Control;
            richEditControl.BeforeExport += OnBeforeExport;
            string htmlForClipboard = String.Empty;

            richEditControl.Options.Export.Html.ExportRootTag = ExportRootTag.Html;
            
            try {
                string html = Control.Document.GetHtmlText(Control.Document.Selection, new CustomUriProvider(), richEditControl.Options.Export.Html);
                htmlForClipboard = CF_HTMLHelper.GetHtmlClipboardFormat(html);
            }
            finally {
                richEditControl.BeforeExport -= OnBeforeExport;
            }
            
            DataObject data = new DataObject();
            data.SetData(OfficeDataFormats.Rtf, richEditControl.Document.GetRtfText(richEditControl.Document.Selection));
            data.SetData(OfficeDataFormats.UnicodeText, richEditControl.Document.GetText(richEditControl.Document.Selection));
            data.SetData(OfficeDataFormats.Html, htmlForClipboard);
            Clipboard.Clear();
            Clipboard.SetDataObject(data, false);
        }

        void OnBeforeExport(object sender, BeforeExportEventArgs e) {
            HtmlDocumentExporterOptions exporterOptions = e.Options as HtmlDocumentExporterOptions;

            if (exporterOptions != null) {
                exporterOptions.CssPropertiesExportType = CssPropertiesExportType.Inline;
                exporterOptions.ExportRootTag = ExportRootTag.Body;
                exporterOptions.EmbedImages = false; // To delegate handling into a CustomUriProvider
            }
        }
    }
    public class CustomPasteSelectionCommand : PasteSelectionCommand {
        public CustomPasteSelectionCommand(IRichEditControl control)
            : base(control) {

        }

        protected override RichEditCommand CreateInsertObjectCommand() {
            return new CustomPasteSelectionCoreCommand(base.Control, new ClipboardPasteSource());
        }
    }

    public class CustomPasteSelectionCoreCommand : PasteSelectionCoreCommand {
        public CustomPasteSelectionCoreCommand(IRichEditControl control, PasteSource pasteSource)
            : base(control, pasteSource) {

        }

        public override void ForceExecute(DevExpress.Utils.Commands.ICommandUIState state) {
            Control.Document.InsertText(Control.Document.CaretPosition, Clipboard.GetText());
        }
    }
}