// Developer Express Code Central Example:
// How to create an editor similar to Outlook Attachment Editor
// 
// This example demonstrates how the RichEditControl component can be used to
// emulate the Outlook Attachment Editor behavior.
// The main idea of the approach
// demonstrated in this sample is to use the DOCVARIABLE field
// (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
// display corresponding RTF content for each inserted file.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E4911

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit;

namespace WindowsFormsApplication1 {
    public partial class AttachmentsEditor : UserControl {
        public AttachmentsEditor() {
            InitializeComponent();
        }

        //int filesCount = 0;
        Dictionary<string, FileFieldInfo> filesCollection = new Dictionary<string, FileFieldInfo>();
        private void simpleButton1_Click(object sender, EventArgs e) {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Title = "Select a file";
            openFileDialog.Filter = "All files|*.*";
            if(openFileDialog.ShowDialog() == DialogResult.OK) {
                if(filesCollection.ContainsKey(openFileDialog.SafeFileName)) {
                    MessageBox.Show(String.Format("The file: {0} is already added to collection", openFileDialog.SafeFileName));
                    return;
                }
                richEditControl1.Document.Fields.Create(richEditControl1.Document.Range.End, "DOCVARIABLE " + openFileDialog.SafeFileName);
                filesCollection.Add(openFileDialog.SafeFileName, new FileFieldInfo() { DocField = richEditControl1.Document.Fields[richEditControl1.Document.Fields.Count - 1], FileName = openFileDialog.SafeFileName, FullFileName = openFileDialog.FileName });
                richEditControl1.Document.Fields.Update();

            }
        }

        private void AttachmentsEditor_Load(object sender, EventArgs e) {
            richEditControl1.CreateNewDocument();
            richEditControl1.Document.DefaultCharacterProperties.FontName = "Times New Roman";
            richEditControl1.Document.DefaultCharacterProperties.FontSize = 10;
            richEditControl1.SelectionChanged += new EventHandler(richEditControl1_SelectionChanged);
            richEditControl1.Document.ContentChanged += new EventHandler(Document_ContentChanged);
            richEditControl1.Document.CalculateDocumentVariable += new DevExpress.XtraRichEdit.CalculateDocumentVariableEventHandler(Document_CalculateDocumentVariable);

        }

        bool isLocked = false;
        void richEditControl1_SelectionChanged(object sender, EventArgs e) {
            if (isLocked) return;
            SyncronizeFilesCollection();

            DocumentPosition pos = richEditControl1.Document.CaretPosition;
            foreach (KeyValuePair<string, FileFieldInfo> item in filesCollection)
            {
                DocumentRange fieldRange = item.Value.DocField.ResultRange;
                if (fieldRange.Contains(pos) && fieldRange.Start.ToInt() != pos.ToInt() && fieldRange.End.ToInt() != pos.ToInt())
                {
                    isLocked = true;
                    int deltaFromStart = pos.ToInt() - fieldRange.Start.ToInt();
                    int deltaFromEnd = fieldRange.End.ToInt() - pos.ToInt();
                    if (deltaFromEnd > deltaFromStart)
                        richEditControl1.Document.CaretPosition = item.Value.DocField.Range.End;
                    else
                        richEditControl1.Document.CaretPosition = item.Value.DocField.Range.Start;
                    isLocked = false;
                    break;
                }
            }
        }


        void Document_CalculateDocumentVariable(object sender, DevExpress.XtraRichEdit.CalculateDocumentVariableEventArgs e) {
            if(filesCollection.ContainsKey(e.VariableName)) {
                IRichEditDocumentServer server = richEditControl1.CreateDocumentServer();
                FileFieldInfo info = filesCollection[e.VariableName];
                server.Document.Images.Insert(server.Document.Range.End, new Bitmap(Icon.ExtractAssociatedIcon(info.FullFileName).ToBitmap(), new Size(16, 16)));
                DocumentRange range = server.Document.AppendText(info.FileName + "; ");
                Hyperlink hyperlink = server.Document.Hyperlinks.Create(range.Start, range.Length - 1);
                hyperlink.Target = info.FullFileName;
                hyperlink.ToolTip = info.FileName;
                hyperlink.NavigateUri = info.FullFileName;

                e.Value = server.Document;
                e.Handled = true;
            }
        }

        void Document_ContentChanged(object sender, EventArgs e) { 
            SyncronizeFilesCollection();
        }

        private void SyncronizeFilesCollection() {
            List<string> removedKeys = new List<string>();
            foreach(string key in filesCollection.Keys) {
                bool keyExist = false;
                foreach(Field field in richEditControl1.Document.Fields) {
                    if(filesCollection[key].DocField == field) {
                        keyExist = true;
                        break;
                    }
                }
                if(!keyExist) removedKeys.Add(key);
            }
            foreach(string removedKey in removedKeys) {
                filesCollection.Remove(removedKey);
            }       
        }

    }

    public class FileFieldInfo {
        public Field DocField { get; set; }
        public string FileName { get; set; }
        public string FullFileName { get; set; }
    }
}
