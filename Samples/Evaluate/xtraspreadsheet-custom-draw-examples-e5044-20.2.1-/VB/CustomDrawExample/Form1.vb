#Region "#using"
Imports System
Imports System.Drawing
Imports DevExpress.Spreadsheet
Imports DevExpress.XtraSpreadsheet
#End Region ' #using
Imports System.Windows.Forms

Namespace CustomDrawExample
	Partial Public Class Form1
		Inherits DevExpress.XtraBars.Ribbon.RibbonForm

		Public Sub New()
			InitializeComponent()
			spreadsheetControl1.LoadDocument("Products.xlsx")
			spreadsheetControl1.Options.Behavior.Column.Delete = DocumentCapability.Disabled
			spreadsheetControl1.Options.Behavior.Column.Insert = DocumentCapability.Disabled

			AddHandler spreadsheetControl1.CustomDrawColumnHeader, AddressOf spreadsheetControl1_CustomDrawColumnHeader
			AddHandler spreadsheetControl1.CustomDrawColumnHeaderBackground, AddressOf spreadsheetControl1_CustomDrawColumnHeaderBackground
			AddHandler spreadsheetControl1.CustomDrawRowHeader, AddressOf spreadsheetControl1_CustomDrawRowHeader
			AddHandler spreadsheetControl1.CustomDrawRowHeaderBackground, AddressOf spreadsheetControl1_CustomDrawRowHeaderBackground
			AddHandler spreadsheetControl1.CustomDrawCell, AddressOf spreadsheetControl1_CustomDrawCell
			AddHandler spreadsheetControl1.CustomDrawCellBackground, AddressOf spreadsheetControl1_CustomDrawCellBackground
		End Sub
#Region "#CustomDrawColumnHeader"
		Private Sub spreadsheetControl1_CustomDrawColumnHeader(ByVal sender As Object,
			ByVal e As CustomDrawColumnHeaderEventArgs)
			' Cancel default painting for the column header.
			e.Handled = True

			If e.ColumnIndex > 4 Then
				Return
			End If

			' Specify the list of new column header names.
			Dim headers() As String = {"Category", "Product Name", "Quantity per Unit",
				"Unit Price", "Units in Stock"}

			' Specify font attributes for the column header.
			Dim defaultFont As SpreadsheetFont = spreadsheetControl1.Document.Styles.DefaultStyle.Font
			Using font As New Font(defaultFont.Name, CSng(defaultFont.Size), FontStyle.Bold)
				' Specify layout settings for the column header.
				Using stringFormat As New StringFormat()
					stringFormat.LineAlignment = StringAlignment.Center
					stringFormat.Alignment = If(e.ColumnIndex < 3, StringAlignment.Near, StringAlignment.Far)
					stringFormat.Trimming = StringTrimming.EllipsisCharacter

					' Draw the column header.
					e.Graphics.DrawString(headers(e.ColumnIndex), font,
				e.Cache.GetSolidBrush(Color.White), e.Bounds, stringFormat)
				End Using
			End Using
		End Sub
#End Region ' #CustomDrawColumnHeader

#Region "#CustomDrawColumnHeaderBackground"
		Private Sub spreadsheetControl1_CustomDrawColumnHeaderBackground(ByVal sender As Object,
			ByVal e As CustomDrawColumnHeaderBackgroundEventArgs)
			' Cancel default painting for the column header background.
			e.Handled = True

			' If the column header is under the mouse pointer or the column contains the active cell,
			' paint the column header background in Color 1.
			' Otherwise, use Color 2.
			If e.ColumnIndex <= 4 Then
				Dim backColor = If(e.IsHovered OrElse (e.ColumnIndex = spreadsheetControl1.ActiveCell.ColumnIndex),
					Color.FromArgb(200, 44, 74), 'Color 1
					Color.FromArgb(91, 155, 213)) ' Color 2
				e.Cache.FillRectangle(e.Cache.GetSolidBrush(backColor), e.Bounds)
			End If
		End Sub
#End Region ' #CustomDrawColumnHeaderBackground

#Region "#CustomDrawRowHeader"
		Private Sub spreadsheetControl1_CustomDrawRowHeader(ByVal sender As Object,
			ByVal e As CustomDrawRowHeaderEventArgs)
			' Cancel default painting for the row header.
			e.Handled = True

			' Display a row number for every fifth row.
			If (e.RowIndex + 1) Mod 5 = 0 Then
				' Specify font style.
				e.Appearance.FontStyleDelta = FontStyle.Bold

				' Return the row header bounds.
				Dim textBounds As Rectangle = e.Bounds

				' Specify row header text.
				Dim text As String = (e.RowIndex + 1).ToString()

				' Specify text alignment. 
				Dim format As New StringFormat With {
					.LineAlignment = StringAlignment.Center,
					.Alignment = StringAlignment.Center
				}

				' Draw row header text.
				e.Graphics.DrawString(text, e.Font,
			e.Cache.GetSolidBrush(Color.FromArgb(91, 155, 213)), textBounds, format)
			End If
		End Sub
#End Region ' #CustomDrawRowHeader

#Region "#CustomDrawRowHeaderBackground"
		Private Sub spreadsheetControl1_CustomDrawRowHeaderBackground(ByVal sender As Object,
			ByVal e As CustomDrawRowHeaderBackgroundEventArgs)
			' Cancel default painting for the row header background.
			e.Handled = True

			' If the row header is under the mouse pointer or the row contains the active cell,
			' paint the row header background in Color 1.
			' Otherwise, paint the row header in white.
			Dim backColor As Color = If(e.IsHovered OrElse (e.RowIndex = spreadsheetControl1.ActiveCell.RowIndex),
				Color.FromArgb(200, 44, 74), ' Color 1
				Color.White)
			e.Cache.FillRectangle(e.Cache.GetSolidBrush(backColor), e.Bounds)
		End Sub
#End Region ' #CustomDrawRowHeaderBackground

#Region "#CustomDrawCell"
		Private Sub spreadsheetControl1_CustomDrawCell(ByVal sender As Object, ByVal e As CustomDrawCellEventArgs)
			' Check whether a cell belongs to the "Category" column.
			If e.Cell.ColumnIndex = 1 Then

				' Obtain the category name. 
				Dim categoryName As String = e.Cell.Value.ToString()

				' Return the image that corresponds to the category name. 
				Dim categoryImage As Image = ChooseImage(categoryName)

				' Specify the image location (the upper-right corner of the cell).
				Dim point As New Point(e.Bounds.Right - 50, e.Bounds.Top)

				' Draw the category image over the cell.
				If categoryImage IsNot Nothing Then
					e.Graphics.DrawImage(categoryImage, point)
				End If
			End If

			' If a cell belongs to the "Units In Stock" column and the cell value is "0",
			' draw a callout to the right of this cell.
			If e.Cell.ColumnIndex = 4 AndAlso e.Cell.Value.IsNumeric AndAlso e.Cell.Value.NumericValue = 0 Then
				' Specify callout text.
				Dim text As String = "OUT OF STOCK"

				Using font As New Font(e.Font.Name, 9.0F, FontStyle.Bold)
					Using format As New StringFormat()
						' Align callout text.
						format.LineAlignment = StringAlignment.Center
						format.Alignment = StringAlignment.Center

						' Calculate the callout bounds.
						Dim size As SizeF = e.Graphics.MeasureString(text, font, Integer.MaxValue, format)
						Dim textBounds As New Rectangle(
							e.Bounds.Right + 15,
							CInt(Math.Truncate(Math.Round(e.Bounds.Top + (e.Bounds.Height - size.Height) / 2))),
							CInt(Math.Truncate(size.Width + 8)),
							CInt(Math.Truncate(Math.Round(size.Height))))

						Dim middle As Integer = CInt(Math.Truncate(Math.Round(textBounds.Height / 2.0)))

						Dim points() As Point = {
							New Point(textBounds.Left, textBounds.Top),
							New Point(textBounds.Left - middle, textBounds.Top + middle),
							New Point(textBounds.Left, textBounds.Bottom)
						}

						' Draw the callout.
						Dim brush As Brush = e.Cache.GetSolidBrush(Color.FromArgb(200, 44, 74))
						e.Graphics.FillPolygon(brush, points)
						e.Cache.FillRectangle(brush, textBounds)
						e.Graphics.DrawString(text, font, e.Cache.GetSolidBrush(Color.White), textBounds, format)
					End Using
				End Using
			End If
		End Sub

		Private Function ChooseImage(categoryName As String) As Image
			Select Case categoryName
				Case "Beverages"
					Return Image.FromFile("images/beverages.png")
				Case "Condiments"
					Return Image.FromFile("images/condiments.png")
				Case "Confections"
					Return Image.FromFile("images/confections.png")
				Case "Dairy Products"
					Return Image.FromFile("images/dairy.png")
				Case "Grains/Cereals"
					Return Image.FromFile("images/cereals.png")
				Case "Meat/Poultry"
					Return Image.FromFile("images/meat.png")
				Case "Produce"
					Return Image.FromFile("images/produce.png")
				Case "Seafood"
					Return Image.FromFile("images/seafood.png")
			End Select

			Return Nothing
		End Function
#End Region ' #CustomDrawCell

#Region "#CustomDrawCellBackground"
		Private Sub spreadsheetControl1_CustomDrawCellBackground(ByVal sender As Object,
			ByVal e As CustomDrawCellBackgroundEventArgs)
			' Specify the background color for the active cell. 
			If e.Cell Is spreadsheetControl1.ActiveCell Then
				e.BackColor = Color.FromArgb(50, 200, 44, 74)
				Return
			End If

			' Specify the background color for cells that contain data and belong to odd rows.
			Dim dataRange = e.Cell.Worksheet.GetDataRange()
			If e.Cell.IsIntersecting(dataRange) AndAlso e.Cell.RowIndex Mod 2 <> 0 Then
				e.BackColor = Color.FromArgb(50, 91, 155, 213)
			End If
		End Sub
#End Region ' #CustomDrawCellBackground
	End Class
End Namespace
