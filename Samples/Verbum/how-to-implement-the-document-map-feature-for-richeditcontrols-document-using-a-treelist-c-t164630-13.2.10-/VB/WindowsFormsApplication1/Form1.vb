Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.XtraTreeList.Columns
Imports DevExpress.XtraTreeList.Nodes
Imports DevExpress.XtraRichEdit.API.Native
Imports System.Diagnostics
Imports DevExpress.XtraBars.Ribbon

Namespace WindowsFormsApplication1
	Partial Public Class Form1
		Inherits RibbonForm
		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub richEditControl1_DocumentLoaded(ByVal sender As Object, ByVal e As EventArgs)
			treeList1.Nodes.Clear()
			Dim parents As New Dictionary(Of Integer, TreeListNode)()
			For Each item As Paragraph In richEditControl1.Document.Paragraphs
				If item.OutlineLevel = 0 Then
					Continue For
				End If
				Dim description As String = richEditControl1.Document.GetText(item.Range)
				Dim level As Integer = item.OutlineLevel

				Dim newNode As TreeListNode
				If parents.ContainsKey(level - 1) Then
					newNode = treeList1.AppendNode(New Object() { description }, parents(level - 1))
				Else
                    newNode = treeList1.AppendNode(New Object() {description}, -1)
				End If
				parents(level) = newNode
				newNode.Tag = item.Range
			Next item
			treeList1.ExpandAll()
		End Sub

		Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
			Dim descriptionColumn As TreeListColumn = treeList1.Columns.Add()
			descriptionColumn.FieldName = "Description"
			descriptionColumn.VisibleIndex = 0

			treeList1.OptionsBehavior.Editable = False
			AddHandler treeList1.FocusedNodeChanged, AddressOf treeList1_FocusedNodeChanged

			AddHandler richEditControl1.DocumentLoaded, AddressOf richEditControl1_DocumentLoaded
			richEditControl1.LoadDocument("BookmarkTemplate.docx")
		End Sub

		Private Sub treeList1_FocusedNodeChanged(ByVal sender As Object, ByVal e As DevExpress.XtraTreeList.FocusedNodeChangedEventArgs)
            BeginInvoke(New MethodInvoker(Function() AnonymousMethod1(e)))
		End Sub
		
        Private Function AnonymousMethod1(ByVal e As DevExpress.XtraTreeList.FocusedNodeChangedEventArgs) As Boolean
            If e.Node IsNot Nothing Then
                richEditControl1.Document.CaretPosition = (TryCast(e.Node.Tag, DocumentRange)).Start
                richEditControl1.Document.Selection = (TryCast(e.Node.Tag, DocumentRange))
                richEditControl1.ScrollToCaret()
            End If
            Return True
        End Function
	End Class
End Namespace
