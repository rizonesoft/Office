Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Layout.Export

Namespace RichEdit
    Friend Class CustomSearchForm
        Inherits DevExpress.XtraRichEdit.Forms.SearchTextForm

        Public Sub New(ByVal parameters As DevExpress.XtraRichEdit.Forms.SearchFormControllerParameters)
            MyBase.New(parameters)
            AddHandler Me.cbFndSearchString.EditValueChanged, AddressOf cbFndSearchString_EditValueChanged
            AddHandler Me.chbFndMatchCase.CheckedChanged, AddressOf chbFndMatchCase_CheckedChanged
            AddHandler Me.chbFndFindWholeWord.CheckedChanged, AddressOf chbFndMatchCase_CheckedChanged
            AddHandler Me.FormClosed, AddressOf CustomSearchForm_FormClosed
        End Sub

        Private Sub chbFndMatchCase_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs)
            Me.cbFndSearchString.EditValue = Nothing
        End Sub

        Private Sub CustomSearchForm_FormClosed(ByVal sender As Object, ByVal e As FormClosedEventArgs)
            ClearCustomMarks()
            RemoveHandler Me.cbFndSearchString.EditValueChanged, AddressOf cbFndSearchString_EditValueChanged
            RemoveHandler Me.chbFndMatchCase.CheckedChanged, AddressOf chbFndMatchCase_CheckedChanged
            RemoveHandler Me.chbFndFindWholeWord.CheckedChanged, AddressOf chbFndMatchCase_CheckedChanged
        End Sub
        Private Sub cbFndSearchString_EditValueChanged(ByVal sender As Object, ByVal e As EventArgs)
            ClearCustomMarks()
            If Me.cbFndSearchString.EditValue IsNot Nothing Then
                Dim text As String = Me.cbFndSearchString.EditValue.ToString()
                If Not String.IsNullOrEmpty(text) Then
                    CreateCustomMarks(text)
                End If
            End If
        End Sub
        Private Sub CreateCustomMarks(ByVal text As String)
            Dim options As DevExpress.XtraRichEdit.API.Native.SearchOptions = DevExpress.XtraRichEdit.API.Native.SearchOptions.None
            If Controller.FindWholeWord Then
                options = options Or DevExpress.XtraRichEdit.API.Native.SearchOptions.WholeWord
            End If
            If Controller.CaseSensitive Then
                options = options Or DevExpress.XtraRichEdit.API.Native.SearchOptions.CaseSensitive
            End If
            Dim ranges() As DocumentRange = Control.Document.FindAll(text, options)
            If ranges IsNot Nothing AndAlso ranges.Length > 0 Then
                For Each range As DocumentRange In ranges
                    Control.Document.CustomMarks.Create(range.Start, range)
                    Control.Document.CustomMarks.Create(range.End, range)
                Next range
            End If
        End Sub
        Private Sub ClearCustomMarks()
            For i As Integer = Control.Document.CustomMarks.Count - 1 To 0 Step -1
                Dim mark As DevExpress.XtraRichEdit.API.Native.CustomMark = Control.Document.CustomMarks(i)
                Control.Document.CustomMarks.Remove(mark)
            Next i
        End Sub
    End Class
End Namespace
