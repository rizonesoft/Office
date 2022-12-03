using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsFormsApplication1.InsertFieldModules {
    public partial class ucDOCVARIABLE : UserControl, IFieldParametersDialog {
        public ucDOCVARIABLE() {
            InitializeComponent();
        }

        #region IFieldParametersDialog Members

        public string GenerateFieldParametersString() {
            string resultString = "";
            if(textEditVariableName.Text.Trim() == "") return InsertFieldRichEditHelper.EmptyFieldCode;

            resultString += textEditVariableName.Text.Trim();
            if(textEditArgument1.Text.Trim() != "")
                resultString += " " + textEditArgument1.Text.Trim();
            if(textEditArgument2.Text.Trim() != "")
                resultString += " " + textEditArgument2.Text.Trim();
            if(textEditArgument3.Text.Trim() != "")
                resultString += " " + textEditArgument3.Text.Trim();
            if(textEditArgument4.Text.Trim() != "")
                resultString += " " + textEditArgument4.Text.Trim();
            return resultString;
        }

        #endregion
    }
}
