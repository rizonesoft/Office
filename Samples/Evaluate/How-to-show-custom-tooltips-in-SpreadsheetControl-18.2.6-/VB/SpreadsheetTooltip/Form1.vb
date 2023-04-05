Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms
Imports DevExpress.Spreadsheet
Imports DevExpress.Utils

Namespace SpreadsheetTooltip
	Partial Public Class Form1
		Inherits DevExpress.XtraEditors.XtraForm

		Public Sub New()
			InitializeComponent()
			spreadsheetControl1.ToolTipController = toolTipController1
			AddHandler toolTipController1.GetActiveObjectInfo, AddressOf ToolTipController1_GetActiveObjectInfo

			spreadsheetControl1.LoadDocument("template.xlsx")
		End Sub

		Private Sub ToolTipController1_GetActiveObjectInfo(ByVal sender As Object, ByVal e As DevExpress.Utils.ToolTipControllerGetActiveObjectInfoEventArgs)
			If e.SelectedControl IsNot spreadsheetControl1 Then
				Return
			End If
			Dim cell As Cell = spreadsheetControl1.GetCellFromPoint(New PointF(e.ControlMousePosition.X, e.ControlMousePosition.Y))
			If cell Is Nothing Then
				Return
			End If

			If cell.IsMerged Then
				cell = cell.GetMergedRanges().First()(0)
			End If
			If Not cell.Value.IsEmpty Then
				Dim info As New ToolTipControlInfo(cell, String.Empty)
				info.ToolTipType = ToolTipType.SuperTip
				Dim sToolTip As New SuperToolTip()
				Dim item As New ToolTipItem()
				item.Font = New Font("Arial", 10)
				item.ImageOptions.SvgImage = svgImageCollection1(cell.Value.Type.ToString().ToLower())
				item.Text = PrepareCellTooltip(cell)
				sToolTip.Items.Add(item)
				info.SuperTip = sToolTip
				e.Info = info
			End If
		End Sub
		Private Function PrepareCellTooltip(ByVal cell As Cell) As String
			Dim cellReference As String = cell.GetReferenceA1()
			Dim cellDataType As String = cell.Value.Type.ToString()
			Dim cellDisplayText As String = cell.DisplayText
			Return String.Format("Cell reference: {0}" & vbCrLf & "Data type: {1}" & vbCrLf & "Value: {2}", cellReference, cellDataType, cellDisplayText)
		End Function
	End Class
End Namespace
