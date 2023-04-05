using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.Spreadsheet.Functions;
using Microsoft.Office.Interop.Excel;
using System.Globalization;
using DevExpress.Spreadsheet;

namespace SpreadsheetAddIn
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        IWorkbook workbook;
        ExcelAppHelper excelHelper;
        string path = System.Windows.Forms.Application.StartupPath;
        
        public Form1()
        {
            InitializeComponent();
            workbook = spreadsheetControl1.Document;
            workbook.LoadDocument("Documents\\SphereMaterial.xlsx", DocumentFormat.OpenXml);
            DefineCustomFunctions();
            CalculateCustomFunction();
        }
     
        void DefineCustomFunctions()
        {
            // Open Excel Add-In file in the background.
            excelHelper = new ExcelAppHelper();

            if (!excelHelper.Initialize(path + @"\AddIns\SphereMassAddIn.xlam"))
            {
                MessageBox.Show("Can not start Excel application");
                return;
            }

            // Specify a new instance of the custom function and add it to the collection of custom functions in a workbook.
            AddInFunction function = new AddInFunction("SPHEREMASS", excelHelper);
            spreadsheetControl1.Document.CustomFunctions.Add(function);
        }

        private void CalculateCustomFunction()
        {
            //DevExpress.Spreadsheet.Worksheet worksheet = workbook.Worksheets[0];
            //worksheet.Range["E4:E8"].ArrayFormula = "=SPHEREMASS(D4:D8, C4:C8)";
        }

        void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (excelHelper != null)
                excelHelper.Dispose();
        }

        public class AddInFunction : ICustomFunction
        {
            static ParameterInfo[] parameters = PrepareParameters();
            static Dictionary<int, DevExpress.Spreadsheet.CellValue> ErrorToValueDictonary = CreateErrorToValueDictionary();
            static Dictionary<DevExpress.Spreadsheet.ErrorValueInfo, int> ValueToErrorDictonary = CreateValueToErrorDictionary();

            static Dictionary<int, DevExpress.Spreadsheet.CellValue> CreateErrorToValueDictionary()
            {
                Dictionary<int, DevExpress.Spreadsheet.CellValue> result = new Dictionary<int, DevExpress.Spreadsheet.CellValue>();
                result.Add(-2146826281, DevExpress.Spreadsheet.CellValue.ErrorDivisionByZero);
                result.Add(-2146826246, DevExpress.Spreadsheet.CellValue.ErrorValueNotAvailable);
                result.Add(-2146826259, DevExpress.Spreadsheet.CellValue.ErrorName);
                result.Add(-2146826288, DevExpress.Spreadsheet.CellValue.ErrorNullIntersection);
                result.Add(-2146826252, DevExpress.Spreadsheet.CellValue.ErrorNumber);
                result.Add(-2146826265, DevExpress.Spreadsheet.CellValue.ErrorReference);
                result.Add(-2146826273, DevExpress.Spreadsheet.CellValue.ErrorInvalidValueInFunction);
                return result;
            }

            static Dictionary<DevExpress.Spreadsheet.ErrorValueInfo, int> CreateValueToErrorDictionary()
            {
                Dictionary<DevExpress.Spreadsheet.ErrorValueInfo, int> result = new Dictionary<DevExpress.Spreadsheet.ErrorValueInfo, int>();
                foreach (KeyValuePair<int, DevExpress.Spreadsheet.CellValue> pair in ErrorToValueDictonary)
                    result.Add(pair.Value.ErrorValue, pair.Key);
                return result;
            }
            readonly ExcelAppHelper excelApp;
            readonly string name;

            public AddInFunction(string name, ExcelAppHelper excelApp)
            {
                this.name = name;
                this.excelApp = excelApp;
            }

            static ParameterInfo[] PrepareParameters()
            {
                // Missing optional parameters do not result in error message.
                return new ParameterInfo[] { new ParameterInfo(ParameterType.Value, ParameterAttributes.Required), new ParameterInfo(ParameterType.Value, ParameterAttributes.Optional) };
            }

            #region ICustomFunction Members
            public string Name { get { return name; } }
            public ParameterInfo[] Parameters { get { return parameters; } }
            public ParameterType ReturnType { get { return ParameterType.Value; } }
            // Do not reevaluate cells on every recalculation.
            public bool Volatile { get { return false; } }
            public string GetName(CultureInfo culture)
            {
                return name;
            }

            public ParameterValue Evaluate(IList<ParameterValue> parameters, EvaluationContext context)
            {
                List<object> args = new List<object>();
                // Provide conversion of function parameters for further evaluation in Excel.
                for (int i = 0; i < parameters.Count; i++)
                    args.Add(ConvertParameter(parameters[i]));
                // Run Excel macro to evaluate custom function. 
                dynamic objResult = excelApp.RunMacros(name, args);
                // Convert the function result value to the SpreadsheetControl's value for the correct displaying.
                return ConvertResultValue(objResult);
            }
            #endregion

            #region ParameterValue->object conversion
            // Convert the SpreadsheetControl's parameters to Excel parameters. 
            object ConvertParameter(ParameterValue parameter)
            {
                if (parameter.IsNumeric)
                    return parameter.NumericValue;
                else if (parameter.IsBoolean)
                    return parameter.BooleanValue;
                else if (parameter.IsText)
                    return parameter.TextValue;
                else if (parameter.IsError)
                    return ValueToErrorDictonary[parameter.ErrorValue];
                else if (parameter.IsRange)
                    return ConvertRefParameter(parameter.RangeValue);
                else if (parameter.IsArray)
                    return ConvertArrayParameter(parameter.ArrayValue);
                else
                    return System.Reflection.Missing.Value;
            }

            object[,] ConvertArrayParameter(DevExpress.Spreadsheet.CellValue[,] parameter)
            {
                int height = parameter.GetLength(0);
                int width = parameter.GetLength(1);
                object[,] result = (object[,])Array.CreateInstance(typeof(object), new[] { height, width }, new[] { 1, 1 });
                for (int i = 0; i < height; i++)
                    for (int j = 0; j < width; j++)
                    {
                        DevExpress.Spreadsheet.CellValue value = parameter[i, j];
                        if (value.IsEmpty)
                            result[i + 1, j + 1] = null;
                        else
                            result[i + 1, j + 1] = value;
                    }
                return result;
            }

            object[,] ConvertRefParameter(DevExpress.Spreadsheet.CellRange parameter)
            {
                int height = parameter.RowCount;
                int width = parameter.ColumnCount;
                object[,] result = (object[,])Array.CreateInstance(typeof(object), new[] { height, width }, new[] { 1, 1 });
                for (int i = 0; i < height; i++)
                    for (int j = 0; j < width; j++)
                    {
                        DevExpress.Spreadsheet.CellValue value = parameter[i, j].Value;
                        result[i + 1, j + 1] = ConvertParameter(value);
                    }
                return result;
            }
            #endregion

            #region object->ParameterValue conversion
            // Convert Excel parameters to the SpreadsheetControl's parameters.
            ParameterValue ConvertResultValue(dynamic value)
            {
                ParameterValue result;
                Array objArrayRes = value as Array;
                if (objArrayRes != null)
                {
                    int height = objArrayRes.GetLength(0);
                    int lowerY = objArrayRes.GetLowerBound(0);
                    int width = objArrayRes.GetLength(1);
                    int lowerX = objArrayRes.GetLowerBound(1);
                    DevExpress.Spreadsheet.CellValue[,] arrayResult = new DevExpress.Spreadsheet.CellValue[height, width];
                    for (int i = 0; i < height; i++)
                        for (int j = 0; j < width; j++)
                            arrayResult[i, j] = ConvertResultValueCore(objArrayRes.GetValue(i + lowerY, j + lowerX));
                    result = arrayResult;
                }
                else
                    result = ConvertResultValueCore(value);
                return result;
            }

            DevExpress.Spreadsheet.CellValue ConvertResultValueCore(dynamic value)
            {
                if (value == null)
                    return DevExpress.Spreadsheet.CellValue.Empty;
                if (value is int)
                {
                    if (ErrorToValueDictonary.ContainsKey(value))
                        return ErrorToValueDictonary[value];
                    else
                        return value;
                }
                return value;
            }
            #endregion

        }
    }
}
