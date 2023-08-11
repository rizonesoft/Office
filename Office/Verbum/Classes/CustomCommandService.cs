using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Services;

namespace Rizonesoft.Office.Verbum.Classes
{
    public class CustomCommandService : IRichEditCommandFactoryService {
        private readonly IRichEditCommandFactoryService service;
        private readonly RichEditControl control;

        public CustomCommandService(RichEditControl control, IRichEditCommandFactoryService service) 
        {
            DevExpress.Utils.Guard.ArgumentNotNull(control, "control");
            DevExpress.Utils.Guard.ArgumentNotNull(service, "service");
            this.control = control;
            this.service = service;
        }

        public RichEditCommand CreateCommand(RichEditCommandId id) 
        {
            if(id == RichEditCommandId.FileSaveAs) 
            {
                return new CustomSaveDocumentAsCommand(control);
            }
            return id == RichEditCommandId.FileSave ? new CustomSaveDocumentCommand(control) : service.CreateCommand(id);
        }
    }

    public class CustomSaveDocumentCommand : SaveDocumentCommand {
        public CustomSaveDocumentCommand(IRichEditControl richEdit) : base(richEdit) { }

        protected override void ExecuteCore() 
        {
            base.ExecuteCore();
            if(!((RichEditControl)Control).Modified) 
            {
                // MessageBox.Show(Strings.CustomSaveDocumentCommand_DocumentSaved);
            }
        }
    }

    public class CustomSaveDocumentAsCommand : SaveDocumentAsCommand {
        public CustomSaveDocumentAsCommand(IRichEditControl richEdit) : base(richEdit) { }

        protected override void ExecuteCore() 
        {
            ((RichEditControl)Control).Modified = true;

            base.ExecuteCore();
            if (((RichEditControl)Control).Modified) return;
            // MessageBox.Show(Strings.CustomSaveDocumentCommand_DocumentSaved);   
            MainForm.AddFileToMruList(Options.DocumentSaveOptions.CurrentFileName);
        }
    }
}
