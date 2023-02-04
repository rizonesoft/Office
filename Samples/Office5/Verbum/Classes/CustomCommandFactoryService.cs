

namespace Rizonesoft.Office.Verbum.Classes
{
    using DevExpress.XtraRichEdit.Commands;
    using DevExpress.XtraRichEdit;
    using DevExpress.XtraRichEdit.Services;
    using System.IO;
    using System;
    using DevExpress.XtraBars;
    using DevExpress.XtraEditors;

    public class CustomCommandFactoryService : IRichEditCommandFactoryService
    {
        readonly IRichEditCommandFactoryService service;
        readonly RichEditControl control;
        

        public CustomCommandFactoryService(RichEditControl control, IRichEditCommandFactoryService service)
        {
            DevExpress.Utils.Guard.ArgumentNotNull(control, "control");
            DevExpress.Utils.Guard.ArgumentNotNull(service, "service");
            this.control = control;
            this.service = service;
        }

        public RichEditCommand CreateCommand(RichEditCommandId id)
        {
            if (id == RichEditCommandId.FileSaveAs)
            {
                return new CustomSaveDocumentAsCommand(control);
            }
            if (id == RichEditCommandId.FileSave)
            {
                return new CustomSaveDocumentCommand(control);
            }
            return service.CreateCommand(id);
        }

    }

    public class CustomSaveDocumentCommand : SaveDocumentCommand
    {
        public CustomSaveDocumentCommand(IRichEditControl richEdit) : base(richEdit) { }

        protected override void ExecuteCore()
        {
            base.ExecuteCore();
            if (!(this.Control as RichEditControl).Modified)
            {
                // MessageBox.Show("Document is saved successfully");
            }
        }
    }


    public class CustomSaveDocumentAsCommand : SaveDocumentAsCommand
    {

        public CustomSaveDocumentAsCommand(IRichEditControl richEdit) : base(richEdit) { }

        protected override void ExecuteCore()
        {
            (this.Control as RichEditControl).Modified = true;
            base.ExecuteCore();
            if (!(this.Control as RichEditControl).Modified)
            {

                // MessageBox.Show("Document is saved successfully");
                MainForm.AddFileToMRUList(Options.DocumentSaveOptions.CurrentFileName);
            }
        }


    }


}
