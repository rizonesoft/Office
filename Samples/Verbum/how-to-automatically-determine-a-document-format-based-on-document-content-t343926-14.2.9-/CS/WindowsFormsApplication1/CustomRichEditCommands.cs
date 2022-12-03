using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Internal;
using DevExpress.XtraRichEdit.Services;

namespace RichEditControlExtensions {
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
            if(id == RichEditCommandId.FileOpen)
                return new CustomLoadDocumentCommand(control);

            return service.CreateCommand(id);
        }
    }

    public class CustomLoadDocumentCommand : LoadDocumentCommand {
        public CustomLoadDocumentCommand(IRichEditControl richEdit) : base(richEdit) { }

        protected override void ExecuteCore() {

            OpenFileDialog openFileDialog1 = new OpenFileDialog();
            openFileDialog1.InitialDirectory = "";
            openFileDialog1.Filter = "All files (*.*)|*.*";
            openFileDialog1.Filter += "|Rich Text Format (*.rtf)|*.rtf";
            openFileDialog1.Filter += "|Text Files (*.txt)|*.txt";
            openFileDialog1.Filter += "|HyperText Markup Language Format (*.html)|*.html";
            openFileDialog1.Filter += "|Word 2007 Document (*.docx)|*.docx";
            openFileDialog1.Filter += "|OpenDocument Text Document (*.odt)|*.odt";
            openFileDialog1.Filter += "|Microsoft Word Document (*.doc)|*.doc";

            openFileDialog1.FilterIndex = 1;
            openFileDialog1.RestoreDirectory = true;

            if(openFileDialog1.ShowDialog() == DialogResult.OK) {
                try {
                    Control.LoadDocumentEx(openFileDialog1.FileName);
                }
                catch(Exception ex) {
                    MessageBox.Show("Error: Could not read file from disk. Original error: " + ex.Message);
                }
            }

            //base.ExecuteCore();
        }
    }
}
