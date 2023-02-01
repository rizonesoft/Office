Imports DevExpress.XtraRichEdit.API.Layout
Imports DevExpress.XtraRichEdit.API.Native
Imports System

Namespace LineNumberingExample
	#Region "#MyLayoutVisitor"
	Public Class MyLayoutVisitor
		Inherits LayoutVisitor

		Private document As Document

		Private privateRowIndex As Integer
		Public Property RowIndex() As Integer
			Get
				Return privateRowIndex
			End Get
			Private Set(ByVal value As Integer)
				privateRowIndex = value
			End Set
		End Property

		Public Sub New(ByVal doc As Document)
			Me.document = doc
			RowIndex = 0
		End Sub

		Protected Overrides Sub VisitRow(ByVal row As LayoutRow)
			RowIndex += 1
			MyBase.VisitRow(row)
		End Sub
	End Class
	#End Region ' #MyLayoutVisitor
End Namespace