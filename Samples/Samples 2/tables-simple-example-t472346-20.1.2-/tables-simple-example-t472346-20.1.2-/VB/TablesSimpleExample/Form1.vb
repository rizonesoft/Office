Imports System.Drawing
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.Office.Utils
Imports DevExpress.XtraBars.Ribbon
Imports System

Namespace TablesSimpleExample
	Partial Public Class Form1
		Inherits RibbonForm

		Public Sub New()
			InitializeComponent()

			CreateTable(richEditControl1.Document)
			SetColumnWidth(richEditControl1.Document.Tables(0))
			MergeAndSplit(richEditControl1.Document)
			FillData(richEditControl1.Document)
			FormatData(richEditControl1.Document)
			CustomizeTable(richEditControl1.Document)
			TableStyle(richEditControl1.Document)
			'WrapText(richEditControl1.Document);
			'DeleteElements(richEditControl1.Document);
		End Sub
		Private Sub CreateTable(ByVal document As Document)
'			#Region "#CreateTable"
			'Create a new table and specify its layout type
			Dim table As Table = document.Tables.Create(document.Range.End, 2, 2)

			'Add new rows to the table
			Dim newRowBefore As TableRow = table.Rows.InsertBefore(0)
			Dim newRowAfter As TableRow = table.Rows.InsertAfter(0)

			'Add a new column to the table
			Dim newLastColumn As TableCell = table.Rows(0).Cells.Append()

'			#End Region ' #CreateTable
		End Sub

		Private Sub SetColumnWidth(ByVal table As Table)
'			#Region "#ResizeTable"
			'Set the width of the first column
			table.Rows(0).FirstCell.PreferredWidthType = WidthType.Fixed
			table.Rows(0).FirstCell.PreferredWidth = Units.InchesToDocumentsF(0.8F)


			'Set the second column width and cell height
			table(0, 1).PreferredWidthType = WidthType.Fixed
			table(0, 1).PreferredWidth = Units.InchesToDocumentsF(5F)
			table(0, 1).HeightType = HeightType.Exact
			table(0, 1).Height = Units.InchesToDocumentsF(0.5F)

			'Set the third column width 
			table.Rows(0).LastCell.PreferredWidthType = WidthType.Fixed
			table.Rows(0).LastCell.PreferredWidth = Units.InchesToDocumentsF(0.8F)
'			#End Region ' #ResizeTable
		End Sub

		Private Sub MergeAndSplit(ByVal document As Document)
'			#Region "#SplitAndMerge"
			Dim table As Table = document.Tables(0)
			table.BeginUpdate()

			'Split cell into 8
			table(3, 1).Split(4, 2)

			'Merge cells
			table.MergeCells(table(4, 1), table(4, 2))
			table.MergeCells(table(6, 1), table(6, 2))
			table.EndUpdate()
'			#End Region ' #SplitAndMerge
		End Sub
		Private Sub FillData(ByVal document As Document)
'			#Region "#DataInserting"
			Dim table As Table = document.Tables(0)

			'Insert the header data
			document.InsertSingleLineText(table.Rows(0).Cells(1).Range.Start, "Active Customers")
			document.InsertSingleLineText(table(2, 0).Range.Start, "Photo")
			document.InsertSingleLineText(table(2, 1).Range.Start, "Customer Info")
			document.InsertSingleLineText(table(2, 2).Range.Start, "Rentals")

			'Insert the customer photo
			document.Images.Insert(table(3, 0).Range.Start, DocumentImageSource.FromFile("photo.png"))

			'Insert the customer info
			document.InsertText(table(3, 1).Range.Start, "Ryan Anita W")
			document.InsertText(table(3, 2).Range.Start, "Intermediate")
			document.InsertText(table(4, 1).Range.Start, "3/28/1984")
			document.InsertText(table(5, 1).Range.Start, "anita_ryan@dxvideorent.com")
			document.InsertText(table(5, 2).Range.Start, "(555)421-0059")
			document.InsertText(table(6, 1).Range.Start, "5119 Beryl Dr, San Antonio, TX 78212")

			document.InsertSingleLineText(table(3, 3).Range.Start, "18")

'			#End Region ' #DataInserting
		End Sub
		Private Sub FormatData(ByVal document As Document)
'			#Region "#FormatData"
			Dim table As Table = document.Tables(0)

			'Apply formatting to the "Active Customers" cell
			Dim properties As CharacterProperties = document.BeginUpdateCharacters(table(0, 1).ContentRange)
			properties.FontName = "Segoe UI"
			properties.FontSize = 16
			document.EndUpdateCharacters(properties)
			Dim alignment As ParagraphProperties = document.BeginUpdateParagraphs(table(0, 1).ContentRange)
			alignment.Alignment = ParagraphAlignment.Center
			document.EndUpdateParagraphs(alignment)
			table(0, 1).VerticalAlignment = TableCellVerticalAlignment.Center

			'Apply formatting to the header cells
			Dim headerRowProperties As CharacterProperties = document.BeginUpdateCharacters(table.Rows(2).Range)
			headerRowProperties.FontName = "Segoe UI"
			headerRowProperties.FontSize = 11
			headerRowProperties.ForeColor = Color.FromArgb(212, 236, 183)
			document.EndUpdateCharacters(headerRowProperties)

			Dim headerRowParagraphProperties As ParagraphProperties = document.BeginUpdateParagraphs(table.Rows(2).Range)
			headerRowParagraphProperties.Alignment = ParagraphAlignment.Center
			document.EndUpdateParagraphs(headerRowParagraphProperties)

			'Apply formatting to the customer info cells
			Dim targetRange As DocumentRange = document.CreateRange(table(3, 1).Range.Start, table(6, 2).Range.Start.ToInt() - table(3, 1).Range.Start.ToInt())
			Dim infoProperties As CharacterProperties = document.BeginUpdateCharacters(targetRange)
			infoProperties.FontSize = 8
			infoProperties.FontName = "Segoe UI"
			infoProperties.ForeColor = Color.FromArgb(111, 116, 106)
			document.EndUpdateCharacters(infoProperties)

			'Format "Rentals" cells
			Dim rentalFormat As CharacterProperties = document.BeginUpdateCharacters(table(3, 3).Range)
			rentalFormat.FontSize = 28
			rentalFormat.Bold = True
			document.EndUpdateCharacters(rentalFormat)

			Dim rentalAlignment As ParagraphProperties = document.BeginUpdateParagraphs(table(3, 3).Range)
			rentalAlignment.Alignment = ParagraphAlignment.Center
			document.EndUpdateParagraphs(rentalAlignment)
			table(3, 3).VerticalAlignment = TableCellVerticalAlignment.Center
'			#End Region ' #FormatData

		End Sub

		Private Sub TableStyle(ByVal document As Document)
'			#Region "#CreateNewTableStyle"
			document.BeginUpdate()
			'Create a new table style
			Dim tStyleMain As TableStyle = document.TableStyles.CreateNew()

			'Specify style options
			Dim insideHorizontalBorder As TableBorder = tStyleMain.TableBorders.InsideHorizontalBorder
			insideHorizontalBorder.LineStyle = TableBorderLineStyle.Single
			insideHorizontalBorder.LineColor = Color.White

			Dim insideVerticalBorder As TableBorder = tStyleMain.TableBorders.InsideVerticalBorder
			insideVerticalBorder.LineStyle = TableBorderLineStyle.Single
			insideVerticalBorder.LineColor = Color.White
			tStyleMain.CellBackgroundColor = Color.FromArgb(227, 238, 220)
			tStyleMain.Name = "MyTableStyle"

			'Add the style to the document collection
			document.TableStyles.Add(tStyleMain)

			'Create conditional styles (styles for specific table elements)         
			Dim myNewStyleForOddRows As TableConditionalStyle = tStyleMain.ConditionalStyleProperties.CreateConditionalStyle(ConditionalTableStyleFormattingTypes.OddRowBanding)
			myNewStyleForOddRows.CellBackgroundColor = Color.FromArgb(196, 220, 182)

			Dim myNewStyleForBottomRightCell As TableConditionalStyle = tStyleMain.ConditionalStyleProperties.CreateConditionalStyle(ConditionalTableStyleFormattingTypes.BottomRightCell)
			myNewStyleForBottomRightCell.CellBackgroundColor = Color.FromArgb(188, 214, 201)
			document.EndUpdate()

			document.BeginUpdate()

			' Apply a previously defined style to the table
			document.Tables(0).Style = tStyleMain
			document.EndUpdate()
'			#End Region ' #CreateNewTableStyle
		End Sub

		Private Sub CustomizeTable(ByVal document As Document)
'			#Region "#FirstRowTransparency"
			Dim table As Table = document.Tables(0)
			table.BeginUpdate()

			'Call the ChangeCellBorderColor method for every cell in the first two rows
			For i As Integer = 0 To 1
				Dim j As Integer = 0
				Do While j < table.Rows(i).Cells.Count
					ChangeCellBorderColor(table(i, j))
					j += 1
				Loop
			Next i
'			#End Region ' #FirstRowTransparency

'			#Region "#ColorForHeader"
			'Specify the background color for the third row
			Dim targetRow As TableRow = table.Rows(2)
			targetRow.Cells(0).BackgroundColor = Color.FromArgb(99, 122, 110)
			targetRow.Cells(1).BackgroundColor = Color.FromArgb(99, 122, 110)
			targetRow.Cells(2).BackgroundColor = Color.FromArgb(99, 122, 110)
			table.EndUpdate()
'			#End Region ' #ColorForHeader
		End Sub

		#Region "#CustomizeTable"
		Public Shared Sub ChangeCellBorderColor(ByVal cell As TableCell)
			'Specify the border style and the background color for the header cells 
			cell.Borders.Bottom.LineStyle = TableBorderLineStyle.None
			cell.Borders.Left.LineStyle = TableBorderLineStyle.None
			cell.Borders.Right.LineStyle = TableBorderLineStyle.None
			cell.Borders.Top.LineStyle = TableBorderLineStyle.None
			cell.BackgroundColor = Color.Transparent
		End Sub
		#End Region ' #CustomizeTable

		Private Sub WrapText(ByVal document As Document)
			Dim table As Table = document.Tables(0)
			table.BeginUpdate()
			'Wrap text around the table
			table.TextWrappingType = TableTextWrappingType.Around

			'Specify vertical alignment:
			table.RelativeVerticalPosition = TableRelativeVerticalPosition.Paragraph
			table.VerticalAlignment = TableVerticalAlignment.None
			table.OffsetYRelative = Units.InchesToDocumentsF(2F)

			'Specify horizontal alignment:
			table.RelativeHorizontalPosition = TableRelativeHorizontalPosition.Margin
			table.HorizontalAlignment = TableHorizontalAlignment.Center

			'Set distance between the text and the table:
			table.MarginBottom = Units.InchesToDocumentsF(0.3F)
			table.MarginLeft = Units.InchesToDocumentsF(0.3F)
			table.MarginTop = Units.InchesToDocumentsF(0.3F)
			table.MarginRight = Units.InchesToDocumentsF(0.3F)
			table.EndUpdate()
		End Sub

		#Region "#DeleteColumns"
		'Declare a method that deletes the second cell in every table row
		Public Shared Sub DeleteCells(ByVal row As TableRow, ByVal i As Integer)
			row.Cells(1).Delete()
		End Sub
		#End Region ' #DeleteColumns
		Private Sub DeleteElements(ByVal document As Document)
'			#Region "#DeleteCells"
			Dim tbl As Table = document.Tables(0)
			tbl.BeginUpdate()

			'Delete a cell
			tbl.Cell(1, 1).Delete()

			'Delete a row
			tbl.Rows(0).Delete()
			tbl.EndUpdate()

			'Delete the entire table
			'document.Tables.Remove(tbl);
'			#End Region ' #DeleteCells

'			#Region "#CallDeleteColumns"
			'Call the declared method using ForEachRow method and the corresponding delegate
			tbl.ForEachRow(New TableRowProcessorDelegate(AddressOf DeleteCells))
'			#End Region ' #CallDeleteColumns

		End Sub
	End Class
End Namespace



