Imports System
Imports System.Collections.Generic
Imports System.Globalization
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks

Namespace SpreadsheetAddIn
    Public Class ExcelAppHelper
        Implements IDisposable

        Private Const OFFICE_APP_ID As String = "Excel.Application"
        Private Const EXCEL_PROCESS_NAME As String = "EXCEL"
        Private excelApp As Object
        Private excelWorkbook As Object
        Private oMissing As Object = System.Reflection.Missing.Value

        Public ReadOnly Property Workbook() As Object
            Get
                Return excelWorkbook
            End Get
        End Property

        Public Function Initialize(ByVal filePath As String) As Boolean
            excelApp = InitializeExcelApplication()
            If excelApp Is Nothing Then
                Return False
            End If

            excelWorkbook = LoadWorkbook(filePath, excelApp)
            Return excelWorkbook IsNot Nothing
        End Function

        Private Function InitializeExcelApplication() As Object
            Dim excelApp As Object = Nothing
            Dim culture As CultureInfo = System.Threading.Thread.CurrentThread.CurrentCulture
            Try
                System.Threading.Thread.CurrentThread.CurrentCulture = New CultureInfo("en-US")
                Dim appType As Type = Type.GetTypeFromProgID(OFFICE_APP_ID, False)
                If appType IsNot Nothing Then
                    excelApp = Activator.CreateInstance(appType)
                    SetExcelAppVisible(excelApp, False)
                End If
            Catch
                excelApp = Nothing
            Finally
                System.Threading.Thread.CurrentThread.CurrentCulture = culture
            End Try
            Return excelApp
        End Function

        Private Function LoadWorkbook(ByVal filePath As String, ByVal excelApp As Object) As Object
            Dim culture As CultureInfo = System.Threading.Thread.CurrentThread.CurrentCulture
            System.Threading.Thread.CurrentThread.CurrentCulture = New CultureInfo("en-US")
            Try
                Return LoadWorkbookCore(filePath, excelApp)
            Catch
                Return Nothing
            Finally
                System.Threading.Thread.CurrentThread.CurrentCulture = culture
            End Try
        End Function

        Private Function LoadWorkbookCore(ByVal fileName As String, ByVal application As Object) As Object
            Try
                application.GetType().InvokeMember("DisplayAlerts", System.Reflection.BindingFlags.SetProperty, Nothing, application, New Object() { False })
            Catch
            End Try
            Try
                application.GetType().InvokeMember("AskToUpdateLinks", System.Reflection.BindingFlags.SetProperty, Nothing, application, New Object() { False })
            Catch
            End Try
            Dim Books As Object = application.GetType().InvokeMember("Workbooks", System.Reflection.BindingFlags.GetProperty, Nothing, application, Nothing)

            Dim updateExternalLinks As Object = 2 ' http://msdn.microsoft.com/en-us/library/microsoft.office.interop.excel.workbooks.open(v=office.11).aspx
            Dim args() As Object = { fileName, updateExternalLinks }
            Return Books.GetType().InvokeMember("Open", System.Reflection.BindingFlags.InvokeMethod, Nothing, Books, args)
        End Function

        Private Sub SetExcelAppVisible(ByVal excelApp As Object, ByVal newValue As Boolean)
            excelApp.GetType().InvokeMember("Visible", System.Reflection.BindingFlags.SetProperty, Nothing, excelApp, New Object() { newValue })
        End Sub

        #Region "IDisposable Members"
        Public Sub Dispose() Implements IDisposable.Dispose
            Dispose(True)
        End Sub
        Protected Overridable Sub Dispose(ByVal disposing As Boolean)
            If disposing Then
                If excelWorkbook IsNot Nothing Then
                    CloseExcelWorkBook(excelWorkbook)
                End If
                If excelApp IsNot Nothing Then
                    TerminateAllExcelAppInstances()
                End If
            End If
        End Sub
        #End Region
        Private Sub CloseExcelWorkBook(ByVal excelWorkbook As Object)
            If excelWorkbook Is Nothing Then
                Return
            End If

            Dim culture As CultureInfo = System.Threading.Thread.CurrentThread.CurrentCulture
            System.Threading.Thread.CurrentThread.CurrentCulture = New CultureInfo("en-US")
            Try
                Dim closeArgs() As Object = { False, oMissing, oMissing }
                Dim type As Type = excelWorkbook.GetType()
                If type Is Nothing Then
                    Return
                End If
                Try
                    type.InvokeMember("Close", System.Reflection.BindingFlags.InvokeMethod, Nothing, excelWorkbook, closeArgs)
                Catch
                End Try
            Finally
                System.Threading.Thread.CurrentThread.CurrentCulture = culture
            End Try
        End Sub

        Private Sub TerminateAllExcelAppInstances()
            Try
                excelApp.GetType().InvokeMember("Quit", System.Reflection.BindingFlags.InvokeMethod, Nothing, excelApp, Nothing)
            Catch
                If excelApp IsNot Nothing Then
                    Try
                        SetExcelAppVisible(excelApp, True)
                    Catch
                        excelApp = Nothing
                    End Try
                End If
                If excelApp IsNot Nothing Then
                    Try
                        excelApp.GetType().InvokeMember("Quit", System.Reflection.BindingFlags.InvokeMethod, Nothing, excelApp, Nothing)
                    Catch
                        excelApp = Nothing
                    End Try
                End If
            End Try
            excelApp = Nothing
        End Sub

        Public Function RunMacros(ByVal name As String, ByVal args As List(Of Object)) As Object
            args.Insert(0, name)
            Try
                Return excelApp.GetType().InvokeMember("Run", System.Reflection.BindingFlags.Default Or System.Reflection.BindingFlags.InvokeMethod, Nothing, excelApp, args.ToArray())
            Catch
                Return Nothing
            End Try
        End Function
    End Class
End Namespace
