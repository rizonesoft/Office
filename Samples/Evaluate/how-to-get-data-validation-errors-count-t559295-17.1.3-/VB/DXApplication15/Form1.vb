Imports Microsoft.VisualBasic
Imports DevExpress.Spreadsheet
Imports DevExpress.XtraEditors
Imports DevExpress.XtraSpreadsheet.Services
Imports System
Imports System.Linq


Namespace DXApplication15
	Partial Public Class Form1
		Inherits XtraForm
		Public Sub New()
			InitializeComponent()
			spreadsheetControl.LoadDocument("data.xlsx")

			SubstituteService()
		End Sub



		Private Sub SubstituteService()
			Dim service As ISpreadsheetCommandFactoryService = CType(spreadsheetControl.GetService(GetType(ISpreadsheetCommandFactoryService)), ISpreadsheetCommandFactoryService)
			Dim customService As New CustomCommandFactoryService(service)
			spreadsheetControl.ReplaceService(Of ISpreadsheetCommandFactoryService)(customService)
			customService.Control = spreadsheetControl
		End Sub



	End Class



End Namespace