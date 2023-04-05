Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Windows.Forms
Imports DevExpress.XtraSpreadsheet
Imports DevExpress.XtraSpreadsheet.Commands

Namespace SpreadsheetCustomCommand
    #Region "#customcommand"
    Public Class CustomFormatClearContentsCommand
        Inherits FormatClearContentsCommand

        Public Sub New(ByVal control As ISpreadsheetControl)
            MyBase.New(control)
        End Sub

        Protected Overrides Sub ExecuteCore()
            MessageBox.Show("Custom command executed")
            MyBase.ExecuteCore()
        End Sub
    End Class
    #End Region ' #customcommand
End Namespace
