Imports System
Imports System.Linq
Imports System.Windows
Imports DevExpress.Diagram.Core

Namespace XtraDiagram.CreateCustomShapes
    Public Class ShapeKey
        Inherits ResourceKey
        Implements IOrderedKey

        <ThreadStatic> _
        Private Shared idCore As Integer

        Private ReadOnly id_Renamed As Integer

        Private ReadOnly resourceKey_Renamed As String

        Public Overrides ReadOnly Property Assembly() As System.Reflection.Assembly
            Get
                Return Nothing
            End Get
        End Property

        Private ReadOnly Property IOrderedKey_Id As Integer Implements IOrderedKey.Id
            Get
                Return id_Renamed
            End Get
        End Property

        Private ReadOnly Property IOrderedKey_ResourceKey As String Implements IOrderedKey.ResourceKey
            Get
                Return resourceKey_Renamed
            End Get
        End Property

        Public Sub New(ByVal resourceKey As String)
            Me.id_Renamed = idCore
            idCore += 1
            Me.resourceKey_Renamed = resourceKey
        End Sub
    End Class
End Namespace
