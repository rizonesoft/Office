Imports DevExpress.XtraRichEdit.API.Native
Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Windows.Forms

Namespace HyperlinkClickExample.Forms
    Partial Public Class SelectProductForm
        Inherits DevExpress.XtraEditors.XtraForm

        #Region "#Properties"

        Private editValue_Renamed As Object

        Private range_Renamed As DocumentRange
        Public Overridable ReadOnly Property EditValue() As Object
            Get
                Return editValue_Renamed
            End Get
        End Property
        Public Property Range() As DocumentRange
            Get
                Return range_Renamed
            End Get
            Set(ByVal value As DocumentRange)
                range_Renamed = value
            End Set
        End Property
        #End Region ' #Properties
        Public Sub New()
            InitializeComponent()
        End Sub

        #Region "#PopulateListBox"
        'Populate the ListBoxControl with items based on the custom list retrieved from the main form:
        Private Sub PopulateListBox(ByVal list As List(Of String))
            Me.listBoxControl.Items.AddRange(list.ToArray())
            If list.Count > 0 Then
                Me.listBoxControl.SelectedIndex = 0
            End If
        End Sub
        Public Sub New(ByVal list As List(Of String))
            Me.New()
            PopulateListBox(list)
        End Sub
        #End Region ' #PopulateListBox

        #Region "#Events"
        'Handle the MouseMove and MouseClick events to support item selection by using mouse:
        Private Sub listBoxControl_MouseMove(ByVal sender As Object, ByVal e As MouseEventArgs) Handles listBoxControl.MouseMove
            For i As Integer = 0 To Me.listBoxControl.ItemCount - 1
                Dim rect As Rectangle = Me.listBoxControl.GetItemRectangle(i)
                If rect.Contains(e.X, e.Y) Then
                    Me.listBoxControl.SelectedIndex = i
                    Exit For
                End If
            Next i
        End Sub
        Private Sub listBoxControl_MouseClick(ByVal sender As Object, ByVal e As MouseEventArgs) Handles listBoxControl.MouseClick
            If e.Button <> MouseButtons.Left OrElse Me.listBoxControl.SelectedIndex < 0 Then
                Return
            End If
            Dim rect As Rectangle = Me.listBoxControl.GetItemRectangle(Me.listBoxControl.SelectedIndex)
            If Not rect.Contains(e.X, e.Y) Then
                Return
            End If
            OnCommit()
        End Sub
        'Handle the form KeyDown event to support keyboard navigation and item selection using the Enter key:
        Private Sub SelectProductForm_KeyDown(ByVal sender As Object, ByVal e As KeyEventArgs) Handles MyBase.KeyDown
            If e.KeyData = Keys.Escape Then
                Close()
            ElseIf e.KeyData = Keys.Enter Then
                OnCommit()
            End If
        End Sub
        Protected Overridable Sub OnCommit()
            Me.editValue_Renamed = CStr(Me.listBoxControl.SelectedItem)
            If Not onCommit_RenamedEvent Is Nothing Then
                RaiseEvent onCommit_Renamed(Me, EventArgs.Empty)
            End If
            Close()
        End Sub
#End Region ' #Events

#Region "#Commit"

        Private Event onCommit_Renamed As EventHandler
        Public Custom Event Commit As EventHandler
            AddHandler(ByVal value As EventHandler)
                AddHandler onCommit_Renamed, value
            End AddHandler
            RemoveHandler(ByVal value As EventHandler)
                RemoveHandler onCommit_Renamed, value
            End RemoveHandler
            RaiseEvent(ByVal sender As System.Object, ByVal e As System.EventArgs)
            End RaiseEvent
        End Event
#End Region ' #Commit
    End Class
End Namespace





