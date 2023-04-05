Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports DevExpress.XtraSpreadsheet.Services


Namespace SpreadsheetCustomCommand
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        #Region "#substituteservice"
        Private Sub SubstituteService()
            Dim service As ISpreadsheetCommandFactoryService = DirectCast(spreadsheetControl1.GetService(GetType(ISpreadsheetCommandFactoryService)), ISpreadsheetCommandFactoryService)
            Dim customService As New CustomService(service)
            spreadsheetControl1.ReplaceService(Of ISpreadsheetCommandFactoryService)(customService)
            customService.Control = spreadsheetControl1
        End Sub
        #End Region ' #substituteservice

        Public Sub New()
            InitializeComponent()
            SubstituteService()
        End Sub
    End Class
End Namespace