using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsFormsApplication1.InsertFieldModules {
    public partial class ucIFFIELD : UserControl, IFieldParametersDialog {
        public ucIFFIELD() {
            InitializeComponent();
        }

        private void comboBoxEdit1_SelectedIndexChanged(object sender, EventArgs e) {
            GenerateLayoutControlGroupsCaptions();
        }

        protected override void OnLoad(EventArgs e) {
            base.OnLoad(e);
            GenerateLayoutControlGroupsCaptions();
        }

        void GenerateLayoutControlGroupsCaptions() {
            string leftTemplate = "A value isnerted when the LEFT expression";
            string rightTemplate = "the RIGHT expression";

            string trueText = "";
            string falseText = "";

            switch(comboBoxEditOperation.Text) {
                case "=":
                    trueText = "EQUALS";
                    falseText = "DOESN'T EQUAL";
                    break;
                case "<>":
                    trueText = "DOESN'T EQUAL";
                    falseText = "EQUALS";
                    break;
                case ">":
                    trueText = "IS GREATER THAN";
                    falseText = "IS NOT GREATER THAN";
                    break;
                case "<":
                    trueText = "IS LESS THAN";
                    falseText = "IS NOT LESS THAN";
                    break;
                case ">=":
                    trueText = "IS GREATER THAN OR EQUALS";
                    falseText = "IS LESS THAN";
                    break;
                case "<=":
                    trueText = "IS LESS THAN OR EQUALS";
                    falseText = "IS GREATER THAN";
                    break;
                default:
                    break;
            }

            layoutControlGroup4.Text = leftTemplate + " " + trueText + " "  + rightTemplate;
            layoutControlGroup5.Text = leftTemplate + " " + falseText + " " + rightTemplate;
        
        }

        #region IFieldParametersDialog Members

        public string GenerateFieldParametersString() {
            string resultString = "";
            resultString += textEditLeftExpression.Text.Trim();
            resultString += " " + comboBoxEditOperation.Text + " ";
            resultString += textEditRIGHTExpression.Text.Trim();
            resultString += " " + textEditResultTRUE.Text.Trim() + " ";
            resultString += textEditResultFALSE.Text.Trim();
            return resultString;            
        }
        #endregion

        public bool IsFieldParametersValid() {
            if(textEditLeftExpression.Text.Trim() == "") return false;
            if(textEditRIGHTExpression.Text.Trim() == "") return false;
            if(textEditResultFALSE.Text.Trim() == "") return false;
            if(textEditResultTRUE.Text.Trim() == "") return false;
            return true;
        }

        public List<string> GetNestedFieldsList() {
            List<string> nestedFieldsList = new List<string>();
            if(checkEditInsertLeftAsField.Checked) nestedFieldsList.Add(textEditLeftExpression.Text.Trim());
            if(checkEditInsertRightAsField.Checked) nestedFieldsList.Add(textEditRIGHTExpression.Text.Trim());
            if(checkEditInsertResultFALSEAsField.Checked) nestedFieldsList.Add(textEditResultFALSE.Text.Trim());
            if(checkEditInsertResultTRUEAsField.Checked) nestedFieldsList.Add(textEditResultTRUE.Text.Trim());
            return nestedFieldsList;
        }
    }
}
