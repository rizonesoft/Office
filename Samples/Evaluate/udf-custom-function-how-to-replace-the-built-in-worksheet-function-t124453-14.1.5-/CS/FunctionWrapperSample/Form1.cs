#region #usings
using DevExpress.Spreadsheet.Functions;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
#endregion #usings

namespace FunctionWrapperSample
{
    public partial class Form1 : Form
    {

        public Form1()
        {
            InitializeComponent();
            ReplaceSinFunction();
            InitializeWorksheet();
        }

        private void InitializeWorksheet()
        {
            DevExpress.Spreadsheet.Worksheet sheet = spreadsheetControl1.ActiveWorksheet;
            sheet.Cells[0, 0].Formula = "SIN(B1)";
            sheet.Cells[0, 1].Value = 30;
        }
        #region #replacesinfunction
        private void ReplaceSinFunction()
        {
            WorkbookFunctions functions = spreadsheetControl1.Document.Functions;
            // Obtain the built-in function to override.
            IFunction sinFunction = functions.Math.Sin;
            // Create a new function descending from the FunctionWrapper
            // to replace the built-in function.
            OverridenFunction function = new OverridenFunction(sinFunction);
            // Substitute the built-in function with the custom function.
            functions.OverrideFunction(function.Name, function);
        }

        // A custom function that calculates the sine function for the angle measured in degerees.
        public class OverridenFunction : FunctionWrapper
        {

            public OverridenFunction(IFunction function)
                : base(function)
            {
            }

            public override ParameterValue Evaluate(IList<ParameterValue> parameters, EvaluationContext context)
            {
                ParameterValue value = parameters[0];
                if (value.IsError)
                    return value;

                double angle = parameters[0].NumericValue * Math.PI / 180;
                double sin = Math.Sin(angle);
                return Math.Round(sin, 5);
            }
        }
    }
    #endregion #replacesinfunction
}