using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsFormsApplication1.InsertFieldModules {
    public partial class ucCREATEDATE : UserControl, IFieldParametersDialog {
        public ucCREATEDATE() {
            InitializeComponent();
            InitializeListBoxItemsDateFormats();
        }

        void InitializeListBoxItemsDateFormats() {
            listBoxControlFormats.SelectedValueChanged += listBoxControlFormats_SelectedValueChanged;
            string[] dateTimeFormats = new string[] { 
                "dd.MM.yyyy",
                "dddd, d. MMMM yyyy",
                "d. MMMM yyyy",
                "dd.MM.yy",
                "yyyy-MM-dd",
                "yy-MM-dd",
                "dd/MM/yyyy",
                "dd. MMM. yyyy",
                "dd/MM/yy",
                "MMMM yy",
                "MMM-yy",
                "dd.MM.yyyy HH:mm",
                "dd.MM.yyyy HH:mm:ss",
                "h:mm am/pm",
                "h:mm:ss am/pm",
                "HH:mm",
                "HH:mm:ss",                           
            };

            List<FieldAttributeItem> listSource = new List<FieldAttributeItem>();
            for(int i = 0; i < dateTimeFormats.Length; i++) {
                listSource.Add(new FieldAttributeItem() { DisplayName = DateTime.Now.ToString(dateTimeFormats[i].Replace("am/pm", "tt")), AttributeValue = dateTimeFormats[i] });                
            }

            listBoxControlFormats.DataSource = listSource;
            listBoxControlFormats.DisplayMember = "DisplayName";
            listBoxControlFormats.ValueMember = "AttributeValue";
        }

        void listBoxControlFormats_SelectedValueChanged(object sender, EventArgs e) {
            textEditCurrentFormat.Text = listBoxControlFormats.SelectedValue == null ? "" : listBoxControlFormats.SelectedValue.ToString();
        }

        #region IFieldParametersDialog Members

        public string GenerateFieldParametersString() {
            string resultString = "";
            if(textEditCurrentFormat.Text.Trim() != "") {
                resultString = "\\@ \"" + textEditCurrentFormat.Text.Trim() + "\"";
            }
            return resultString;
        }

        #endregion
    }
}
