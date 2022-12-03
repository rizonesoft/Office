using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.Services;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.Utils;
using DevExpress.Utils.Commands;

namespace CustomCommand
{
    public partial class Form1 : Form
    {
        public Form1() {
            InitializeComponent();
            MyFactoryHelper.SetMyNewCommandFactory(this.richEditControl1);
            richEditControl1.CreateNewDocument();
            richEditControl1.Document.AppendSingleLineText("Type at least 7 paragraphs to be able to save the document.");
        }
    }

    #region #iricheditcommandfactoryservice
    public static class MyFactoryHelper {
        public static void SetMyNewCommandFactory(RichEditControl control) {
            var myCommandFactory = new CustomRichEditCommandFactoryService(control, control.GetService<IRichEditCommandFactoryService>());
            control.ReplaceService<IRichEditCommandFactoryService>(myCommandFactory);
        }
    }

    public class CustomRichEditCommandFactoryService : IRichEditCommandFactoryService {
        readonly IRichEditCommandFactoryService service;
        readonly RichEditControl control;

        public CustomRichEditCommandFactoryService(RichEditControl control,
            IRichEditCommandFactoryService service) {
            this.control = control;
            this.service = service;
        }
        public RichEditCommand CreateCommand(RichEditCommandId id) {
            if (id == RichEditCommandId.FileSave)
                return new CustomSaveDocumentCommand(control);
            return service.CreateCommand(id);
        }
    }

    public class CustomSaveDocumentCommand : SaveDocumentCommand {
        public CustomSaveDocumentCommand(IRichEditControl control)
            : base(control) {
        }
        protected override void UpdateUIStateCore(ICommandUIState state) {
            base.UpdateUIStateCore(state);
            // Disable the command if the document has less than 5 paragraphs.
            state.Enabled = Control.Document.Paragraphs.Count > 5;
        }

        protected override void ExecuteCore() {
            // Cancel execution if the document contains less than 7 paragraphs.
            if (Control.Document.Paragraphs.Count > 7)
                base.ExecuteCore();
            else MessageBox.Show(@"You should type at least 7 paragraphs to be able to save the document.",
                "Please be creative", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }
    #endregion #iricheditcommandfactoryservice
}