Imports Microsoft.VisualBasic
#Region "#usings"
Imports DevExpress.Spreadsheet.Functions
Imports System
Imports System.Collections.Generic
Imports System.Windows.Forms
#End Region ' #usings

Namespace FunctionWrapperSample
	Partial Public Class Form1
		Inherits Form

		Public Sub New()
			InitializeComponent()
			ReplaceSinFunction()
			InitializeWorksheet()
		End Sub

		Private Sub InitializeWorksheet()
			Dim sheet As DevExpress.Spreadsheet.Worksheet = spreadsheetControl1.ActiveWorksheet
			sheet.Cells(0, 0).Formula = "SIN(B1)"
			sheet.Cells(0, 1).Value = 30
		End Sub
#Region "#replacesinfunction"
        Private Sub ReplaceSinFunction()
            Dim functions As WorkbookFunctions = spreadsheetControl1.Document.Functions
            ' Obtain the built-in function to override.
            Dim sinFunction As IFunction = functions.Math.Sin
            ' Create a new function descending from the FunctionWrapper
            ' to replace the built-in function.
            Dim [function] As New OverridenFunction(sinFunction)
            ' Substitute the built-in function with the custom function.
            functions.OverrideFunction([function].Name, [function])
        End Sub

        ' A custom function that calculates the sine function for the angle measured in degerees.
        Public Class OverridenFunction
            Inherits FunctionWrapper

            Public Sub New(ByVal [function] As IFunction)
                MyBase.New([function])
            End Sub

            Public Overrides Function Evaluate(ByVal parameters As IList(Of ParameterValue), ByVal context As EvaluationContext) As ParameterValue
                Dim value As ParameterValue = parameters(0)
                If value.IsError Then
                    Return value
                End If

                Dim angle As Double = parameters(0).NumericValue * Math.PI / 180
                Dim sin As Double = Math.Sin(angle)
                Return Math.Round(sin, 5)
            End Function
        End Class
#End Region ' #replacesinfunction
    End Class
End Namespace