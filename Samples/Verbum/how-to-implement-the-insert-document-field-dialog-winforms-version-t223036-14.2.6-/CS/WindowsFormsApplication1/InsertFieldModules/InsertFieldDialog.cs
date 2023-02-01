using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;

namespace WindowsFormsApplication1.InsertFieldModules {
    public partial class InsertFieldDialog : XtraForm {

        private RichEditControl richEditControl;

        public InsertFieldDialog(RichEditControl control) {
            InitializeComponent();
            richEditControl = control;
        }

        private void InsertFieldDialog_Load(object sender, EventArgs e) {
            simpleButtonOk.Enabled = InsertFieldRichEditHelper.VariableTypes.Keys.Count > 0;
            if(listBoxFieldNames.Items.Count == 0) {
                for(int i = 0; i < InsertFieldRichEditHelper.VariableTypes.Keys.Count; i++) {
                    listBoxFieldNames.Items.Add(InsertFieldRichEditHelper.VariableTypes.Keys.ToList()[i]);
                }
                listBoxFieldNames.SelectedIndex = 0;
            }
        }

        private void simpleButtonOk_Click(object sender, EventArgs e) {
            string fieldCode = InsertFieldRichEditHelper.CurrentVariableType;
            IFieldParametersDialog parametersDialog = InsertFieldRichEditHelper.VariableTypes[InsertFieldRichEditHelper.CurrentVariableType] as IFieldParametersDialog;
            if(parametersDialog != null) {
                string parametersString = parametersDialog.GenerateFieldParametersString();
                SubDocument currentDocument = richEditControl.Document.CaretPosition.BeginUpdateDocument();

                if(parametersDialog is ucIFFIELD) {
                    ucIFFIELD IFFieldInsertDialog = parametersDialog as ucIFFIELD;
                    if(IFFieldInsertDialog.IsFieldParametersValid()) {
                        
                        Field newField = currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode + " " + parametersString);
                        
                        List<string> nestedFiueldsList = IFFieldInsertDialog.GetNestedFieldsList();
                        
                        foreach(string nestedFieldCode in nestedFiueldsList) {
                            DocumentRange[] ranges = currentDocument.FindAll(nestedFieldCode, SearchOptions.WholeWord);
                            foreach(DocumentRange range in ranges) {
                                currentDocument.Fields.Create(range);
                            }
                        }
                    }
                }
                else {
                    if(parametersString != InsertFieldRichEditHelper.EmptyFieldCode)
                        currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode + " " + parametersString);
                    else
                        currentDocument.Fields.Create(richEditControl.Document.CaretPosition, fieldCode);
                }

                currentDocument.Fields.Update();
                richEditControl.Document.CaretPosition.EndUpdateDocument(currentDocument);
            }
            Close();
        }

        private void listBoxFieldNames_SelectedIndexChanged(object sender, EventArgs e) {
            InsertFieldRichEditHelper.CurrentVariableType = listBoxFieldNames.SelectedItem.ToString();
            layoutControl1.BeginUpdate();
            Control previousControl = layoutControlItemMainContent.Control;
            layoutControlItemMainContent.Control = InsertFieldRichEditHelper.VariableTypes[InsertFieldRichEditHelper.CurrentVariableType];
            previousControl.Parent = null;
            layoutControl1.EndUpdate();
        }
    }
}
