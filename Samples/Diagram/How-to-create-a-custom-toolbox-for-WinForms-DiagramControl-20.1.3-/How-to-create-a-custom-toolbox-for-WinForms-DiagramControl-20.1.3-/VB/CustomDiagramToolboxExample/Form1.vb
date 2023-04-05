Imports DevExpress.Diagram.Core
Imports DevExpress.XtraDiagram
Imports DevExpress.XtraDiagram.Extensions
Imports DevExpress.XtraGrid.Views.Grid.ViewInfo
Imports System
Imports System.Collections.Generic
Imports System.Collections.ObjectModel
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Windows.Forms

Namespace CustomDiagramToolboxExample
	Partial Public Class Form1
		Inherits Form

		Public Sub New()
			InitializeComponent()
			Dim toolboxItems = New ObservableCollection(Of DiagramShape)()
			For Each shape In BasicShapes.Stencil.Shapes
				toolboxItems.Add(New DiagramShape() With {.Shape = shape})
			Next shape
			gridControl1.DataSource = toolboxItems
		End Sub
		Private shapeTextOffset As Integer = 60
		Private mouseDownLocation As Point
		Private gridHitInfo As GridHitInfo
		Private Sub GridView1_CustomDrawCell(ByVal sender As Object, ByVal e As DevExpress.XtraGrid.Views.Base.RowCellCustomDrawEventArgs) Handles gridView1.CustomDrawCell
			Dim shapeItem As DiagramShape = TryCast(gridView1.GetRow(e.RowHandle), DiagramShape)
			If shapeItem Is Nothing Then
				Return
			End If
			Dim transState As GraphicsState = e.Graphics.Save()
			Try
				e.Appearance.DrawString(e.Cache, e.DisplayText, New Rectangle(e.Bounds.X + shapeTextOffset, e.Bounds.Y, e.Bounds.Width - shapeTextOffset, e.Bounds.Height))
				e.Cache.TranslateTransform(e.Bounds.X, e.Bounds.Y)
				shapeItem.Width = 40
				shapeItem.Height = e.Bounds.Height
				diagramControl1.DrawDetachedItem(shapeItem, e.Cache)
				e.Handled = True
			Finally
				e.Graphics.Restore(transState)
			End Try
		End Sub
		Private Sub gridControl1_MouseDown(ByVal sender As Object, ByVal e As MouseEventArgs) Handles gridControl1.MouseDown
			gridHitInfo = gridView1.CalcHitInfo(e.Location)
			mouseDownLocation = e.Location
		End Sub
		Private Sub gridControl1_MouseMove(ByVal sender As Object, ByVal e As MouseEventArgs) Handles gridControl1.MouseMove
			If e.Button = MouseButtons.Left AndAlso CanStartDragDrop(e.Location) Then
				StartDragDrop()
			End If
		End Sub
		Private Sub gridControl1_MouseLeave(ByVal sender As Object, ByVal e As EventArgs) Handles gridControl1.MouseLeave
			If gridHitInfo IsNot Nothing Then
				gridHitInfo.View.ResetCursor()
			End If
			gridHitInfo = Nothing
		End Sub
'INSTANT VB NOTE: The variable location was renamed since Visual Basic does not handle local variables named the same as class members well:
		Private Function CanStartDragDrop(ByVal location_Conflict As Point) As Boolean
			Return gridHitInfo.InDataRow AndAlso (Math.Abs(location_Conflict.X - mouseDownLocation.X) > 2 OrElse Math.Abs(location_Conflict.Y - mouseDownLocation.Y) > 2)
		End Function
		Public Sub StartDragDrop()
			Dim draggedItem = CType(gridHitInfo.View.GetRow(gridHitInfo.RowHandle), DiagramShape)
			Dim tool = New FactoryItemTool("", Function() "", Function(diagram) New DiagramShape(draggedItem.Shape), New System.Windows.Size(150, 100))
			diagramControl1.Commands.Execute(DiagramCommandsBase.StartDragToolCommand, tool, Nothing)
		End Sub
	End Class
End Namespace
