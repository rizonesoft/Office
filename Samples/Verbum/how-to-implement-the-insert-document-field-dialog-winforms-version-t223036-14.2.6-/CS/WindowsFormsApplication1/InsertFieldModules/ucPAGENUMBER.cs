using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsFormsApplication1.InsertFieldModules {
    public partial class ucPAGENUMBER : UserControl, IFieldParametersDialog {
        public ucPAGENUMBER(string currentFieldName) {
            InitializeComponent();
            if(currentFieldName == "PAGE") {
                InitializeListBoxItemsPage();
                labelControl1.Text = "At present the PAGE (NUMPAGES) field attributes are not supported.\r\n";
                labelControl1.Text += "<href=https://www.devexpress.com/Support/Center/Question/Details/T221870>https://www.devexpress.com/Support/Center/Question/Details/T221870</href>";
                labelControl1.HyperlinkClick += labelControl1_HyperlinkClick;
            }
            else {
                InitializeListBoxItemsNumPages();
                layoutControlItem2.Visibility = DevExpress.XtraLayout.Utils.LayoutVisibility.Never;
            }
            
        }

        void labelControl1_HyperlinkClick(object sender, DevExpress.Utils.HyperlinkClickEventArgs e) {
            System.Diagnostics.Process.Start(e.Link);
        }

        void InitializeListBoxItemsPage() {
            List<FieldAttributeItem> listSource = new List<FieldAttributeItem>();
            listSource.Add(new FieldAttributeItem() { DisplayName = "1, 2, 3, ...", AttributeValue = @"\* Arabic"});
            listSource.Add(new FieldAttributeItem() { DisplayName = "- 1 -, - 2- , - 3- , ...", AttributeValue = @"\* ArabicDash" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "a, b, c, ...", AttributeValue = @"\* alphabetic" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "A, B, C, ...", AttributeValue = @"\* ALPHABETIC" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "i, ii, iii, ...", AttributeValue = @"\* roman" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "I, II, III, ...", AttributeValue = @"\* ROMAN" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "Use Default Numbering", AttributeValue = @"EMPTY" });

            listBoxControlAttributes.DataSource = listSource;
            listBoxControlAttributes.DisplayMember = "DisplayName";
            listBoxControlAttributes.ValueMember = "AttributeValue";        
        }

        void InitializeListBoxItemsNumPages() {
            List<FieldAttributeItem> listSource = new List<FieldAttributeItem>();
            listSource.Add(new FieldAttributeItem() { DisplayName = "(none)", AttributeValue = @"EMPTY" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "1, 2, 3, ...", AttributeValue = @"\* Arabic" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "a, b, c, ...", AttributeValue = @"\* alphabetic" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "A, B, C, ...", AttributeValue = @"\* ALPHABETIC" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "i, ii, iii, ...", AttributeValue = @"\* roman" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "I, II, III, ...", AttributeValue = @"\* ROMAN" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "1st, 2nd, 3rd, ...", AttributeValue = @"\* Ordinal" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "One, Two, Three, ...", AttributeValue = @"\* CardText" });
            listSource.Add(new FieldAttributeItem() { DisplayName = "First, Second, Third, ...", AttributeValue = @"\* OrdText" });

            listBoxControlAttributes.DataSource = listSource;
            listBoxControlAttributes.DisplayMember = "DisplayName";
            listBoxControlAttributes.ValueMember = "AttributeValue";
        }


        #region IFieldParametersDialog Members

        public string GenerateFieldParametersString() {
            string resultString = "";
            if(listBoxControlAttributes.SelectedValue != null && listBoxControlAttributes.SelectedValue.ToString() != "EMPTY") {
                resultString = listBoxControlAttributes.SelectedValue.ToString();
            }
            return resultString;            
        }

        #endregion
    }
}
