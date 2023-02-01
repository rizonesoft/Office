using System.Windows.Forms;
using DevExpress.XtraRichEdit;

namespace RichEditApplicationFileAssociation {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            FileAssociationHelper.AssociateFileExtension(".myapp");
            
            ProcessCommandLineInput();
        }

        private void ProcessCommandLineInput() {
            string[] commandLineArguments = System.Environment.GetCommandLineArgs();

            if (commandLineArguments.Length > 1) {
                try {
                    richEditControl1.LoadDocument(commandLineArguments[1], DocumentFormat.Rtf);
                }
                catch (System.Exception ex) {
                    MessageBox.Show(string.Format("Cannot load {0}:\r\n{1}", commandLineArguments[1], ex.Message), "Error");
                }
            }
        }
    }
}