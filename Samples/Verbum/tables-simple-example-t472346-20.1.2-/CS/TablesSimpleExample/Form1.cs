using System.Drawing;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.Office.Utils;
using DevExpress.XtraBars.Ribbon;
using System;

namespace TablesSimpleExample
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();

            CreateTable(richEditControl1.Document);
            SetColumnWidth(richEditControl1.Document.Tables[0]);
            MergeAndSplit(richEditControl1.Document);
            FillData(richEditControl1.Document);
            FormatData(richEditControl1.Document);
            CustomizeTable(richEditControl1.Document);
            TableStyle(richEditControl1.Document);
            //WrapText(richEditControl1.Document);
            //DeleteElements(richEditControl1.Document);
        }
        private void CreateTable(Document document)
        {
            #region #CreateTable
            //Create a new table and specify its layout type
            Table table = document.Tables.Create(document.Range.End, 2, 2);

            //Add new rows to the table
            TableRow newRowBefore = table.Rows.InsertBefore(0);
            TableRow newRowAfter = table.Rows.InsertAfter(0);

            //Add a new column to the table
            TableCell newLastColumn = table.Rows[0].Cells.Append();

            #endregion #CreateTable
        }

        private void SetColumnWidth(Table table)
        {
            #region #ResizeTable
            //Set the width of the first column
            table.Rows[0].FirstCell.PreferredWidthType = WidthType.Fixed;
            table.Rows[0].FirstCell.PreferredWidth = Units.InchesToDocumentsF(0.8f);


            //Set the second column width and cell height
            table[0, 1].PreferredWidthType = WidthType.Fixed;
            table[0, 1].PreferredWidth = Units.InchesToDocumentsF(5f);
            table[0, 1].HeightType = HeightType.Exact;
            table[0, 1].Height = Units.InchesToDocumentsF(0.5f);

            //Set the third column width 
            table.Rows[0].LastCell.PreferredWidthType = WidthType.Fixed;
            table.Rows[0].LastCell.PreferredWidth = Units.InchesToDocumentsF(0.8f);
            #endregion #ResizeTable
        }

        private void MergeAndSplit(Document document)
        {
            #region #SplitAndMerge
            Table table = document.Tables[0];
            table.BeginUpdate();

            //Split cell into 8
            table[3, 1].Split(4, 2);

            //Merge cells
            table.MergeCells(table[4, 1], table[4, 2]);
            table.MergeCells(table[6, 1], table[6, 2]);
            table.EndUpdate();
            #endregion #SplitAndMerge
        }
        private void FillData(Document document)
        {
            #region #DataInserting
            Table table = document.Tables[0];

            //Insert the header data
            document.InsertSingleLineText(table.Rows[0].Cells[1].Range.Start, "Active Customers");
            document.InsertSingleLineText(table[2, 0].Range.Start, "Photo");
            document.InsertSingleLineText(table[2, 1].Range.Start, "Customer Info");
            document.InsertSingleLineText(table[2, 2].Range.Start, "Rentals");

            //Insert the customer photo
            document.Images.Insert(table[3, 0].Range.Start, DocumentImageSource.FromFile("photo.png"));

            //Insert the customer info
            document.InsertText(table[3, 1].Range.Start, "Ryan Anita W");
            document.InsertText(table[3, 2].Range.Start, "Intermediate");
            document.InsertText(table[4, 1].Range.Start, "3/28/1984");
            document.InsertText(table[5, 1].Range.Start, "anita_ryan@dxvideorent.com");
            document.InsertText(table[5, 2].Range.Start, "(555)421-0059");
            document.InsertText(table[6, 1].Range.Start, "5119 Beryl Dr, San Antonio, TX 78212");

            document.InsertSingleLineText(table[3, 3].Range.Start, "18");

            #endregion #DataInserting
        }
        private void FormatData(Document document)
        {
            #region #FormatData
            Table table = document.Tables[0];

            //Apply formatting to the "Active Customers" cell
            CharacterProperties properties = document.BeginUpdateCharacters(table[0, 1].ContentRange);
            properties.FontName = "Segoe UI";
            properties.FontSize = 16;
            document.EndUpdateCharacters(properties);
            ParagraphProperties alignment = document.BeginUpdateParagraphs(table[0, 1].ContentRange);
            alignment.Alignment = ParagraphAlignment.Center;
            document.EndUpdateParagraphs(alignment);
            table[0, 1].VerticalAlignment = TableCellVerticalAlignment.Center;

            //Apply formatting to the header cells
            CharacterProperties headerRowProperties = document.BeginUpdateCharacters(table.Rows[2].Range);
            headerRowProperties.FontName = "Segoe UI";
            headerRowProperties.FontSize = 11;
            headerRowProperties.ForeColor = Color.FromArgb(212, 236, 183);
            document.EndUpdateCharacters(headerRowProperties);

            ParagraphProperties headerRowParagraphProperties = document.BeginUpdateParagraphs(table.Rows[2].Range);
            headerRowParagraphProperties.Alignment = ParagraphAlignment.Center;
            document.EndUpdateParagraphs(headerRowParagraphProperties);

            //Apply formatting to the customer info cells
            DocumentRange targetRange = document.CreateRange(table[3, 1].Range.Start, table[6, 2].Range.Start.ToInt() - table[3, 1].Range.Start.ToInt());
            CharacterProperties infoProperties = document.BeginUpdateCharacters(targetRange);
            infoProperties.FontSize = 8;
            infoProperties.FontName = "Segoe UI";
            infoProperties.ForeColor = Color.FromArgb(111, 116, 106);
            document.EndUpdateCharacters(infoProperties);

            //Format "Rentals" cells
            CharacterProperties rentalFormat = document.BeginUpdateCharacters(table[3, 3].Range);
            rentalFormat.FontSize = 28;
            rentalFormat.Bold = true;
            document.EndUpdateCharacters(rentalFormat);

            ParagraphProperties rentalAlignment = document.BeginUpdateParagraphs(table[3, 3].Range);
            rentalAlignment.Alignment = ParagraphAlignment.Center;
            document.EndUpdateParagraphs(rentalAlignment);
            table[3, 3].VerticalAlignment = TableCellVerticalAlignment.Center;
            #endregion #FormatData

        }

        private void TableStyle(Document document)
        {
            #region #CreateNewTableStyle
            document.BeginUpdate();
            //Create a new table style
            TableStyle tStyleMain = document.TableStyles.CreateNew();

            //Specify style options
            TableBorder insideHorizontalBorder = tStyleMain.TableBorders.InsideHorizontalBorder;
            insideHorizontalBorder.LineStyle = TableBorderLineStyle.Single;
            insideHorizontalBorder.LineColor = Color.White;

            TableBorder insideVerticalBorder = tStyleMain.TableBorders.InsideVerticalBorder;
            insideVerticalBorder.LineStyle = TableBorderLineStyle.Single;
            insideVerticalBorder.LineColor = Color.White;
            tStyleMain.CellBackgroundColor = Color.FromArgb(227, 238, 220);
            tStyleMain.Name = "MyTableStyle";

            //Add the style to the document collection
            document.TableStyles.Add(tStyleMain);

            //Create conditional styles (styles for specific table elements)         
            TableConditionalStyle myNewStyleForOddRows = tStyleMain.ConditionalStyleProperties.CreateConditionalStyle(ConditionalTableStyleFormattingTypes.OddRowBanding);
            myNewStyleForOddRows.CellBackgroundColor = Color.FromArgb(196, 220, 182);

            TableConditionalStyle myNewStyleForBottomRightCell = tStyleMain.ConditionalStyleProperties.CreateConditionalStyle(ConditionalTableStyleFormattingTypes.BottomRightCell);
            myNewStyleForBottomRightCell.CellBackgroundColor = Color.FromArgb(188, 214, 201);
            document.EndUpdate();

            document.BeginUpdate();

            // Apply a previously defined style to the table
            document.Tables[0].Style = tStyleMain;
            document.EndUpdate();
            #endregion #CreateNewTableStyle
        }

        private void CustomizeTable(Document document)
        {
            #region #FirstRowTransparency
            Table table = document.Tables[0];
            table.BeginUpdate();

            //Call the ChangeCellBorderColor method for every cell in the first two rows
            for (int i = 0; i < 2; i++)
            {
                for (int j = 0; j < table.Rows[i].Cells.Count; j++)
                {
                    ChangeCellBorderColor(table[i, j]);
                }
            }
            #endregion #FirstRowTransparency
                        
            #region #ColorForHeader
            //Specify the background color for the third row
            TableRow targetRow = table.Rows[2];
            targetRow.Cells[0].BackgroundColor = Color.FromArgb(99, 122, 110);
            targetRow.Cells[1].BackgroundColor = Color.FromArgb(99, 122, 110);
            targetRow.Cells[2].BackgroundColor = Color.FromArgb(99, 122, 110);
            table.EndUpdate();
            #endregion #ColorForHeader
        }

        #region #CustomizeTable
        public static void ChangeCellBorderColor(TableCell cell)
        {
            //Specify the border style and the background color for the header cells 
            cell.Borders.Bottom.LineStyle = TableBorderLineStyle.None;
            cell.Borders.Left.LineStyle = TableBorderLineStyle.None;
            cell.Borders.Right.LineStyle = TableBorderLineStyle.None;
            cell.Borders.Top.LineStyle = TableBorderLineStyle.None;
            cell.BackgroundColor = Color.Transparent;
        }
        #endregion #CustomizeTable

        private void WrapText(Document document)
        {
            Table table = document.Tables[0];
            table.BeginUpdate();
            //Wrap text around the table
            table.TextWrappingType = TableTextWrappingType.Around;

            //Specify vertical alignment:
            table.RelativeVerticalPosition = TableRelativeVerticalPosition.Paragraph;
            table.VerticalAlignment = TableVerticalAlignment.None;
            table.OffsetYRelative = Units.InchesToDocumentsF(2f);

            //Specify horizontal alignment:
            table.RelativeHorizontalPosition = TableRelativeHorizontalPosition.Margin;
            table.HorizontalAlignment = TableHorizontalAlignment.Center;

            //Set distance between the text and the table:
            table.MarginBottom = Units.InchesToDocumentsF(0.3f);
            table.MarginLeft = Units.InchesToDocumentsF(0.3f);
            table.MarginTop = Units.InchesToDocumentsF(0.3f);
            table.MarginRight = Units.InchesToDocumentsF(0.3f);
            table.EndUpdate();
        }

        #region #DeleteColumns
        //Declare a method that deletes the second cell in every table row
        public static void DeleteCells(TableRow row, int i)
        {
            row.Cells[1].Delete();
        }
        #endregion #DeleteColumns
        private void DeleteElements(Document document)
        {
            #region #DeleteCells
            Table tbl = document.Tables[0];
            tbl.BeginUpdate();

            //Delete a cell
            tbl.Cell(1, 1).Delete();

            //Delete a row
            tbl.Rows[0].Delete();
            tbl.EndUpdate();

            //Delete the entire table
            //document.Tables.Remove(tbl);
            #endregion #DeleteCells

            #region #CallDeleteColumns
            //Call the declared method using ForEachRow method and the corresponding delegate
            tbl.ForEachRow(new TableRowProcessorDelegate(DeleteCells));
            #endregion #CallDeleteColumns

        }
    }
}



