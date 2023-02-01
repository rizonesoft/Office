Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Layout

Namespace WindowsFormsApplication1
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        Public Sub New()
            InitializeComponent()
            AddHandler richEditControl1.SelectionChanged, AddressOf richEditControl1_SelectionChanged
            AddHandler richEditControl1.DocumentLayout.DocumentFormatted, AddressOf DocumentLayout_DocumentFormatted
        End Sub

        Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
            richEditControl1.LoadDocument("SampleDocument.rtf")
        End Sub

        Private Sub DocumentLayout_DocumentFormatted(ByVal sender As Object, ByVal e As EventArgs)
            Me.BeginInvoke((Sub()
                                If Me.Visible Then
                                    Dim visitor As New CustomLayoutVisitor(richEditControl1.Document)
                                    Dim list As List(Of PageLayoutInfo) = richEditControl1.ActiveView.GetVisiblePageLayoutInfos()
                                    For i As Integer = 0 To list.Count - 1
                                        visitor.Reset()
                                        visitor.Visit(richEditControl1.DocumentLayout.GetPage(list(i).PageIndex))
                                    Next i
                                    UpdateStaticItems(richEditControl1)
                                End If
                            End Sub))
        End Sub

        Private Sub richEditControl1_SelectionChanged(ByVal sender As Object, ByVal e As EventArgs)
            Dim richEdit As RichEditControl = TryCast(sender, RichEditControl)

            If richEdit.DocumentLayout.IsDocumentFormattingCompleted Then
                Dim currentPageIndex As Integer = richEdit.Views.PrintLayoutView.CurrentPageIndex
                barStaticItem3.Caption = String.Format("Current page: {0}", currentPageIndex + 1)

                Dim visitor As New CustomLayoutVisitor(richEdit.Document)

                For i As Integer = 0 To richEdit.DocumentLayout.GetPageCount() - 1
                    visitor.Reset()
                    Dim page As LayoutPage = richEdit.DocumentLayout.GetPage(i)
                    visitor.Visit(page)

                    If visitor.IsFound Then
                        Exit For
                    End If
                Next i

                If visitor.IsFound Then
                    barStaticItem4.Caption = String.Format("Current line: {0}", visitor.RowIndex)
                    barStaticItem5.Caption = String.Format("Current column: {0}", visitor.ColIndex)
                End If
            End If
        End Sub

        Private Function GetWordCount(ByVal richEdit As RichEditControl) As Integer
            Dim [iterator] As New DocumentIterator(richEdit.Document, True)
            Dim visitor As New StaticsticsVisitor()
            Do While [iterator].MoveNext()
                [iterator].Current.Accept(visitor)
            Loop

            Return visitor.WordCount
        End Function

        Private Function GetPageCount(ByVal richEdit As RichEditControl) As Integer
            Return richEdit.DocumentLayout.GetPageCount()
        End Function

        Private Sub UpdateStaticItems(ByVal richEdit As RichEditControl)
            barStaticItem1.Caption = String.Format("Page count: {0}", GetPageCount(richEdit))
            barStaticItem2.Caption = String.Format("Word count: {0}", GetWordCount(richEdit))
        End Sub

    End Class
End Namespace
