Imports DevExpress.XtraSpreadsheet
Imports DevExpress.XtraSpreadsheet.Commands
Imports DevExpress.XtraSpreadsheet.Services

Namespace SpreadsheetCustomCommand
    #Region "#customservice"
    Public Class CustomService
        Inherits SpreadsheetCommandFactoryServiceWrapper

        Public Sub New(ByVal service As ISpreadsheetCommandFactoryService)
            MyBase.New(service)
        End Sub
        Public Property Control() As SpreadsheetControl

        Public Overrides Function CreateCommand(ByVal id As SpreadsheetCommandId) As SpreadsheetCommand
            If id = SpreadsheetCommandId.FormatClearContents OrElse id = SpreadsheetCommandId.FormatClearContentsContextMenuItem Then
                Return New CustomFormatClearContentsCommand(Control)
            End If

            Return MyBase.CreateCommand(id)
        End Function

    End Class
    #End Region ' #customservice
End Namespace
