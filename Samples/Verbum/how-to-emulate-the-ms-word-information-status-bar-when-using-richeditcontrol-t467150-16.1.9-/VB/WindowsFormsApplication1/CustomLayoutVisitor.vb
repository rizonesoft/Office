Imports DevExpress.XtraRichEdit.API.Layout
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Layout
Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports System.Reflection
Imports System.Text

Namespace WindowsFormsApplication1
    Public Class StaticsticsVisitor
        Inherits DocumentVisitorBase

        Private ReadOnly _buffer As StringBuilder

        Public Sub New()
            WordCount = 0
            Me._buffer = New StringBuilder()
        End Sub

        Public Overrides Sub Visit(ByVal text As DocumentText)
            _buffer.Append(text.Text)
        End Sub

        Public Overrides Sub Visit(ByVal paragraphEnd As DocumentParagraphEnd)
            FinishParagraph()
        End Sub

        Private Sub FinishParagraph()
            Dim text As String = _buffer.ToString()
            Me.WordCount += text.Split(New Char() { " "c, "."c, "!"c, "?"c }, StringSplitOptions.RemoveEmptyEntries).Length
            _buffer.Length = 0
        End Sub

        Private privateWordCount As Integer
        Public Property WordCount() As Integer
            Get
                Return privateWordCount
            End Get
            Private Set(ByVal value As Integer)
                privateWordCount = value
            End Set
        End Property
        Protected ReadOnly Property Buffer() As StringBuilder
            Get
                Return _buffer
            End Get
        End Property
    End Class

    Public Class CustomLayoutVisitor
        Inherits LayoutVisitor

        Private document As Document

        Public Sub New(ByVal doc As Document)
            Me.document = doc
            RowIndex = 0
            ColIndex = 0
            IsFound = False
        End Sub

        Protected Overrides Sub VisitRow(ByVal row As LayoutRow)
            If Not IsFound Then
                RowIndex += 1
                If row.Range.Contains(document.CaretPosition.ToInt()) Then
                    IsFound = True
                    ColIndex = document.CaretPosition.ToInt() - row.Range.Start
                End If
            End If
            MyBase.VisitRow(row)
        End Sub

        Public Sub Reset()
            RowIndex = 0
            ColIndex = 0
        End Sub

        Private privateColIndex As Integer
        Public Property ColIndex() As Integer
            Get
                Return privateColIndex
            End Get
            Private Set(ByVal value As Integer)
                privateColIndex = value
            End Set
        End Property
        Private privateRowIndex As Integer
        Public Property RowIndex() As Integer
            Get
                Return privateRowIndex
            End Get
            Private Set(ByVal value As Integer)
                privateRowIndex = value
            End Set
        End Property
        Private privateIsFound As Boolean
        Public Property IsFound() As Boolean
            Get
                Return privateIsFound
            End Get
            Private Set(ByVal value As Boolean)
                privateIsFound = value
            End Set
        End Property
    End Class
End Namespace
