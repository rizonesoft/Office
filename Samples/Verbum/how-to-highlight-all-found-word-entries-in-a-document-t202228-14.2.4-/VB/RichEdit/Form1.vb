Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Layout.Export

Namespace RichEdit
    Partial Public Class Form1
        Inherits Form

        Shared Sub New()
        End Sub
        Public Sub New()
            InitializeComponent()

            AddHandler Me.richEditControl1.CustomMarkDraw, AddressOf richEditControl1_CustomMarkDraw
            AddHandler Me.richEditControl1.SearchFormShowing, AddressOf richEditControl1_SearchFormShowing
        End Sub

        Private Sub richEditControl1_SearchFormShowing(ByVal sender As Object, ByVal e As SearchFormShowingEventArgs)
            e.Handled = True
            Dim form As New CustomSearchForm(e.ControllerParameters)
            e.DialogResult = form.ShowDialog()
        End Sub




        Private Sub richEditControl1_CustomMarkDraw(ByVal sender As Object, ByVal e As RichEditCustomMarkDrawEventArgs)
            If e.VisualInfoCollection IsNot Nothing Then
                Dim table As New Dictionary(Of DocumentRange, Rectangle)()
                For Each viewInfo As CustomMarkVisualInfo In e.VisualInfoCollection
                    Dim range As DocumentRange = TryCast(viewInfo.UserData, DocumentRange)
                    If Not table.ContainsKey(range) Then
                        table.Add(range, Rectangle.Empty)
                    End If

                    Dim mark As DevExpress.XtraRichEdit.API.Native.CustomMark = Me.richEditControl1.Document.CustomMarks.GetByVisualInfo(viewInfo)

                    Dim bounds_Renamed As Rectangle = table(range)
                    Dim newBounds As Rectangle
                    If mark.Position = range.Start Then
                        newBounds = Rectangle.FromLTRB(viewInfo.Bounds.Left, viewInfo.Bounds.Top, bounds_Renamed.Right, bounds_Renamed.Bottom)
                    Else
                        newBounds = Rectangle.FromLTRB(bounds_Renamed.Left, bounds_Renamed.Top, viewInfo.Bounds.Right, viewInfo.Bounds.Bottom)
                    End If
                    table(range) = newBounds
                Next viewInfo
                Using brush As Brush = New SolidBrush(Color.FromArgb(100, Color.Yellow))
                    For Each rect As Rectangle In table.Values
                        e.Graphics.FillRectangle(brush, rect)
                    Next rect
                End Using
            End If
        End Sub


        Private Sub barButtonItem1_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles doAction.ItemClick


            Dim ranges() As DocumentRange = Me.richEditControl1.Document.FindAll("test", DevExpress.XtraRichEdit.API.Native.SearchOptions.WholeWord)
            If ranges IsNot Nothing AndAlso ranges.Length > 0 Then
                For Each range As DocumentRange In ranges
                    Me.richEditControl1.Document.CustomMarks.Create(range.Start, range)
                    Me.richEditControl1.Document.CustomMarks.Create(range.End, range)
                Next range
            End If

        End Sub
    End Class



End Namespace
