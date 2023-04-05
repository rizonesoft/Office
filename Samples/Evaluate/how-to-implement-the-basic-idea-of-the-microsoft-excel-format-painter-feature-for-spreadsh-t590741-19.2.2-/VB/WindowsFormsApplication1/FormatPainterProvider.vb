Imports DevExpress.Spreadsheet
Imports DevExpress.XtraBars
Imports DevExpress.XtraSpreadsheet
Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms

Namespace WindowsFormsApplication1
	Public Class FormatPainterProvider
		Private spreadsheetControl As SpreadsheetControl
		Private biFormatPainter As BarCheckItem
		Private sourceCell As CellRange = Nothing
'INSTANT VB NOTE: The field formatPainterMode was renamed since Visual Basic does not allow fields to have the same name as other class members:
		Private formatPainterMode_Renamed As FormatPainterMode = WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.None
		Private Enum FormatPainterMode
			SingleAction
			MultipleActions
			None
		End Enum
		Public Sub RegisterFormatPainter(ByVal spreadsheet As SpreadsheetControl, ByVal biFormatPainter As BarCheckItem)
			spreadsheetControl = spreadsheet
			Me.biFormatPainter = biFormatPainter
			AddHandler spreadsheet.MouseUp, AddressOf spreadsheetControl1_MouseUp
			AddHandler spreadsheet.PreviewKeyDown, AddressOf spreadsheetControl1_PreviewKeyDown
			AddHandler spreadsheet.SelectionChanged, AddressOf spreadsheetControl1_SelectionChanged
			AddHandler spreadsheet.CellBeginEdit, AddressOf spreadsheetControl1_CellBeginEdit
			AddHandler spreadsheet.SheetRemoving, AddressOf Spreadsheet_SheetRemoving
			AddHandler biFormatPainter.CheckedChanged, AddressOf barCheckItem1_CheckedChanged
			AddHandler biFormatPainter.ItemDoubleClick, AddressOf barCheckItem1_ItemDoubleClick

		End Sub
		Private Sub Spreadsheet_SheetRemoving(ByVal sender As Object, ByVal e As SheetRemovingEventArgs)
			If sourceCell IsNot Nothing AndAlso e.SheetName = sourceCell.Worksheet.Name Then
				biFormatPainter.Checked = False
			End If
		End Sub
		Private Sub barCheckItem1_CheckedChanged(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs)
			Dim shouldCopyFormat As Boolean = biFormatPainter.Checked
			sourceCell = If(shouldCopyFormat, spreadsheetControl.SelectedCell, Nothing)

			formatPainterMode_Renamed = If(shouldCopyFormat, WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.SingleAction, WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.None)
		End Sub

		Private Sub spreadsheetControl1_MouseUp(ByVal sender As Object, ByVal e As MouseEventArgs)
			If IsFormatPainterActivated() Then
				ApplyFormat()
			End If
		End Sub

		Private Function IsFormatPainterActivated() As Boolean
			If formatPainterMode_Renamed = WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.None OrElse sourceCell Is Nothing Then
				Return False
			End If

			Return True
		End Function
		Private Sub ApplyFormat()
			spreadsheetControl.Selection.CopyFrom(sourceCell, PasteSpecial.Formats)
			If formatPainterMode_Renamed = WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.SingleAction Then
				biFormatPainter.Checked = False
			End If
		End Sub

		Private Sub barCheckItem1_ItemDoubleClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs)
			biFormatPainter.Checked = True
			formatPainterMode_Renamed = WindowsFormsApplication1.FormatPainterProvider.FormatPainterMode.MultipleActions
		End Sub

		Private Sub spreadsheetControl1_PreviewKeyDown(ByVal sender As Object, ByVal e As PreviewKeyDownEventArgs)
			If Not IsFormatPainterActivated() Then
				Return
			End If

			If e.KeyCode = Keys.Escape Then
				biFormatPainter.Checked = False
			End If
		End Sub

		Private Sub spreadsheetControl1_SelectionChanged(ByVal sender As Object, ByVal e As EventArgs)
			If spreadsheetControl.SelectedShape IsNot Nothing OrElse spreadsheetControl.SelectedComment IsNot Nothing Then
				biFormatPainter.Enabled = False
				biFormatPainter.Checked = False
			Else
				biFormatPainter.Enabled = True
			End If
		End Sub

		Private Sub spreadsheetControl1_CellBeginEdit(ByVal sender As Object, ByVal e As DevExpress.XtraSpreadsheet.SpreadsheetCellCancelEventArgs)
			If IsFormatPainterActivated() Then
				ApplyFormat()
				e.Cancel = True
			Else
				biFormatPainter.Enabled = False
			End If
		End Sub

	End Class

End Namespace
