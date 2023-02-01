Imports System
Imports System.Collections.Generic
Imports System.Linq

Namespace RichEditControlEventViewer
    #Region "RichEditEventHooker"
    Public Class AutoCorrectEventHooker
        Inherits RichEditEventHooker

        Public Sub New(ByVal eventName As String, ByVal owner As Form1)
            MyBase.New(eventName, owner)
        End Sub
        Protected Overrides ReadOnly Property MethodName() As String
            Get
                Return "InitializeAutoCorrectEventLogger"
            End Get
        End Property
    End Class
    #End Region
End Namespace
