using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using DevExpress.XtraRichEdit;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraBars;
using System.Drawing;
using System.Windows.Forms;

namespace WindowsFormsApplication1.InsertFieldModules {

    public static class InsertFieldRichEditHelper {
        public static RichEditControl RichControl { get; set; }
        public static InsertFieldDialog InsertDialog { get; set; }

        private static System.Collections.Generic.SortedDictionary<string, UserControl> _variableTypes = new System.Collections.Generic.SortedDictionary<string, UserControl>();
        public static System.Collections.Generic.SortedDictionary<string, UserControl> VariableTypes { get { return _variableTypes; } }
        public static string CurrentVariableType { get; set; }


        public static void RegisterInsertFieldDialogCommand(this RichEditControl richEdit, RibbonPageGroup pageGroup, Image commandImage) {
            BarButtonItem buttonInsertFieldDialog = new BarButtonItem(pageGroup.Ribbon.Manager, "Insert Field");
            buttonInsertFieldDialog.LargeGlyph = commandImage != null ? commandImage : Image.FromFile("InsertFieldModules\\insertFieldIcon.png");
            buttonInsertFieldDialog.ItemClick += new ItemClickEventHandler(buttonInsertFieldDialog_ItemClick);
            pageGroup.ItemLinks.Add(buttonInsertFieldDialog);

            RichControl = richEdit;
        }


        private static void CreateVariablesTypes() {
            _variableTypes.Add("DOCVARIABLE", new ucDOCVARIABLE());
            _variableTypes.Add("PAGE", new ucPAGENUMBER("PAGE"));
            _variableTypes.Add("NUMPAGES", new ucPAGENUMBER("NUMPAGES"));
            _variableTypes.Add("CREATEDATE", new ucCREATEDATE());
            _variableTypes.Add("DATE", new ucCREATEDATE());
            _variableTypes.Add("TIME", new ucCREATEDATE());
            _variableTypes.Add("IF", new ucIFFIELD());
            
        }

        static void buttonInsertFieldDialog_ItemClick(object sender, ItemClickEventArgs e) {
            if(VariableTypes.Keys.Count == 0) {
                CreateVariablesTypes();    
            }
            if(InsertDialog == null) {
                InsertDialog = new InsertFieldDialog(RichControl);    
            }
            InsertDialog.ShowDialog();
        }

        public const string EmptyFieldCode = "EMPTYFIELD";
    }

    // Additional service classes
    public interface IFieldParametersDialog {
        string GenerateFieldParametersString();
    }

    public class FieldAttributeItem {
        public string DisplayName { get; set; }
        public string AttributeValue { get; set; }    
    }
}
