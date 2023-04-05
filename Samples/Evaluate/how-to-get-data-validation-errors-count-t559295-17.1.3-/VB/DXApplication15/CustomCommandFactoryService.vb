Imports Microsoft.VisualBasic
Imports DevExpress.XtraSpreadsheet
Imports DevExpress.XtraSpreadsheet.Commands
Imports DevExpress.XtraSpreadsheet.Services
Imports System
Imports System.Linq
Imports System.Windows.Forms

Namespace DXApplication15
	Public Class CustomCommandFactoryService
		Inherits SpreadsheetCommandFactoryServiceWrapper
		Public Sub New(ByVal service As ISpreadsheetCommandFactoryService)
			MyBase.New(service)
		End Sub
		Private privateControl As SpreadsheetControl
		Public Property Control() As SpreadsheetControl
			Get
				Return privateControl
			End Get
			Set(ByVal value As SpreadsheetControl)
				privateControl = value
			End Set
		End Property

		Public Overrides Function CreateCommand(ByVal id As SpreadsheetCommandId) As SpreadsheetCommand
            If id = SpreadsheetCommandId.DataToolsCircleInvalidData Then
                Return New CustomCircleInvalidDataCommand(Control)
            End If

            Return MyBase.CreateCommand(id)
		End Function

	End Class
	Public Class CustomCircleInvalidDataCommand
		Inherits CircleInvalidDataCommand
		Public Sub New(ByVal control As ISpreadsheetControl)
			MyBase.New(control)
		End Sub
		Private count As Integer = 0
		Public ReadOnly Property ErrorsCount() As Integer
			Get
				Return count
			End Get
		End Property
		Protected Overrides Sub ExecuteCore()
			MyBase.ExecuteCore()
			count = Me.ActiveSheet.InvalidDataCircles.Count
			MessageBox.Show("Data valiadtion errors count = " & count)
		End Sub
	End Class
End Namespace