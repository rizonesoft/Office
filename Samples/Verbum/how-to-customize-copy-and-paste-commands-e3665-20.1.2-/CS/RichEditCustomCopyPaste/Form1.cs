using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Services;

namespace RichEditCustomCopyPaste {
    public partial class Form1 : Form {
        public bool UseCustomCopy { get { return cbCopyHtml.Checked; } }
        public bool UseCustomPaste { get { return cbPastePlainText.Checked; } }
        
        public Form1() {
            InitializeComponent();

            CustomRichEditCommandFactoryService commandFactory = new CustomRichEditCommandFactoryService(richEditControl1, richEditControl1.GetService<IRichEditCommandFactoryService>());
            richEditControl1.RemoveService(typeof(IRichEditCommandFactoryService));
            richEditControl1.AddService(typeof(IRichEditCommandFactoryService), commandFactory);
        }
    }

    public class CustomRichEditCommandFactoryService : IRichEditCommandFactoryService {
        readonly IRichEditCommandFactoryService service;
        readonly RichEditControl control;

        public CustomRichEditCommandFactoryService(RichEditControl control, IRichEditCommandFactoryService service) {
            DevExpress.Utils.Guard.ArgumentNotNull(control, "control");
            DevExpress.Utils.Guard.ArgumentNotNull(service, "service");
            this.control = control;
            this.service = service;
        }

        public RichEditCommand CreateCommand(RichEditCommandId id) {
            if (id == RichEditCommandId.CopySelection && ((Form1)Application.OpenForms[0]).UseCustomCopy)
                return new CustomCopySelectionCommand(control);
            if (id == RichEditCommandId.PasteSelection && ((Form1)Application.OpenForms[0]).UseCustomPaste)
                return new CustomPasteSelectionCommand(control);

            return service.CreateCommand(id);
        }
    }
}