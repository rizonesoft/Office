#region #using
using System;
using System.Drawing;
using DevExpress.Spreadsheet;
using DevExpress.XtraSpreadsheet;
#endregion #using

namespace WindowsFormsApp1
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        public Form1()
        {
            InitializeComponent();

            // Load a document.
            spreadsheetControl1.LoadDocument("Products.xlsx");
        }

        #region #CustomDrawCell
        private void spreadsheetControl1_CustomDrawCell(object sender, CustomDrawCellEventArgs e)
        {

            // Check whether a cell belongs to the "Category" column.
            if (e.Cell.ColumnIndex == 1) { 
                
                // Obtain the category name. 
                String categoryName = e.Cell.Value.ToString();

                // Return the image that corresponds to the category name. 
                Image categoryImage = ChooseImage(categoryName);

                // Specify the image location (the upper-right corner of the cell).
                Point point = new Point(e.Bounds.Right - 50, e.Bounds.Top);

                // Draw the category image over the cell.
                if (categoryImage != null)
                    e.Graphics.DrawImage(categoryImage, point);
            }

            // If a cell belongs to the "Units In Stock" column and the cell value is "0",
            // draw a callout to the right of this cell.
            if (e.Cell.ColumnIndex == 4 && e.Cell.Value.IsNumeric && e.Cell.Value.NumericValue == 0)
            {
                // Specify callout text.
                string text = "OUT OF STOCK";

                using (Font font = new Font(e.Font.Name, 9f, FontStyle.Bold))
                {
                    using (StringFormat format = new StringFormat())
                    {
                        // Align callout text.
                        format.LineAlignment = StringAlignment.Center;
                        format.Alignment = StringAlignment.Center;

                        // Calculate the callout bounds.
                        SizeF size = e.Graphics.MeasureString(text, font, int.MaxValue, format);
                        Rectangle textBounds = new Rectangle(
                            e.Bounds.Right + 15,
                            (int)Math.Round(e.Bounds.Top + (e.Bounds.Height - size.Height) / 2),
                            (int)(size.Width + 8),
                            (int)Math.Round(size.Height));

                        int middle = (int)Math.Round(textBounds.Height / 2.0);

                        Point[] points = new Point[] {
                            new Point(textBounds.Left, textBounds.Top),
                            new Point(textBounds.Left - middle, textBounds.Top + middle),
                            new Point(textBounds.Left, textBounds.Bottom)
                        };

                        // Draw the callout.
                        Brush brush = e.Cache.GetSolidBrush(Color.FromArgb(200, 44, 74));
                        e.Graphics.FillPolygon(brush, points);
                        e.Cache.FillRectangle(brush, textBounds);
                        e.Graphics.DrawString(text, font, e.Cache.GetSolidBrush(Color.White), textBounds, format);
                    }
                }
            }
        }

        private Image ChooseImage(string categoryName)
        {
            switch (categoryName)
            {
                case "Beverages":
                    return Image.FromFile("images/beverages.png");
                case "Condiments":
                    return Image.FromFile("images/condiments.png");
                case "Confections":
                    return Image.FromFile("images/confections.png");
                case "Dairy Products":
                    return Image.FromFile("images/dairy.png");
                case "Grains/Cereals":
                    return Image.FromFile("images/cereals.png");
                case "Meat/Poultry":
                    return Image.FromFile("images/meat.png");
                case "Produce":
                    return Image.FromFile("images/produce.png");
                case "Seafood":
                    return Image.FromFile("images/seafood.png");
            }

            return null;
        }
        #endregion #CustomDrawCell

        #region #CustomDrawCellBackground
        private void spreadsheetControl1_CustomDrawCellBackground(object sender, 
            CustomDrawCellBackgroundEventArgs e)
        {
            // Specify the background color for the active cell. 
            if (e.Cell == spreadsheetControl1.ActiveCell)
            {
                e.BackColor = Color.FromArgb(50, 200, 44, 74);
                return;
            }

            // Specify the background color for cells that contain data and belong to odd rows.
            var dataRange = e.Cell.Worksheet.GetDataRange();
            if (e.Cell.IsIntersecting(dataRange) && e.Cell.RowIndex % 2 != 0) 
            {             
                e.BackColor = Color.FromArgb(50, 91, 155, 213);
            }
        }
        #endregion #CustomDrawCellBackground

        #region #CustomDrawColumnHeader
        private void spreadsheetControl1_CustomDrawColumnHeader(object sender, 
            CustomDrawColumnHeaderEventArgs e)
        {           
            // Cancel default painting for the column header.
            e.Handled = true;

            if (e.ColumnIndex > 4) 
                return;

            // Specify the list of new column header names.
            string[] headers = new string[] { "Category", "Product Name", 
                "Quantity per Unit", "Unit Price", "Units in Stock" };

            // Specify font attributes for the column header.
            SpreadsheetFont defaultFont = spreadsheetControl1.Document.Styles.DefaultStyle.Font;
            using (Font font = new Font(defaultFont.Name, (float)defaultFont.Size, FontStyle.Bold))
            {
                // Specify layout settings for the column header.
                using (StringFormat stringFormat = new StringFormat())
                {
                    stringFormat.LineAlignment = StringAlignment.Center;
                    stringFormat.Alignment = e.ColumnIndex < 3 ? StringAlignment.Near : StringAlignment.Far;
                    stringFormat.Trimming = StringTrimming.EllipsisCharacter;
                    
                    // Draw the column header.
                    e.Graphics.DrawString(headers[e.ColumnIndex], font, 
                        e.Cache.GetSolidBrush(Color.White), e.Bounds, stringFormat);
                }
            }
        }
        #endregion #CustomDrawColumnHeader

        #region #CustomDrawColumnHeaderBackground
        private void spreadsheetControl1_CustomDrawColumnHeaderBackground(object sender, 
            CustomDrawColumnHeaderBackgroundEventArgs e)
        {
            // Cancel default painting for the column header background.
            e.Handled = true;

            // If the column header is under the mouse pointer or the column contains the active cell,
            // paint the column header background in Color 1.
            // Otherwise, use Color 2.
            if (e.ColumnIndex <= 4) {
                var backColor = e.IsHovered || (e.ColumnIndex == spreadsheetControl1.ActiveCell.ColumnIndex) ?
                    //Color 1
                    Color.FromArgb(200, 44, 74) :
                    //Color 2
                    Color.FromArgb(91, 155, 213);
                e.Cache.FillRectangle(e.Cache.GetSolidBrush(backColor), e.Bounds);
            }
        }
        #endregion #CustomDrawColumnHeaderBackground

        #region #CustomDrawRowHeader
        private void spreadsheetControl1_CustomDrawRowHeader(object sender, CustomDrawRowHeaderEventArgs e)
        {
            // Cancel default painting for the row header.
            e.Handled = true;

            // Display a row number for every fifth row.
            if ((e.RowIndex + 1) % 5 == 0)
            {
                // Specify font style.
                e.Appearance.FontStyleDelta = FontStyle.Bold;

                // Return the row header bounds.
                Rectangle textBounds = e.Bounds;

                // Specify row header text.
                string text = (e.RowIndex + 1).ToString();

                // Specify text alignment. 
                StringFormat format = new StringFormat {
                    LineAlignment = StringAlignment.Center,
                    Alignment = StringAlignment.Center
                };

                // Draw row header text.
                e.Graphics.DrawString(text, e.Font, 
                    e.Cache.GetSolidBrush(Color.FromArgb(91, 155, 213)), textBounds, format);
            }
        }
        #endregion #CustomDrawRowHeader

        #region #CustomDrawRowHeaderBackground
        private void spreadsheetControl1_CustomDrawRowHeaderBackground(object sender, 
            CustomDrawRowHeaderBackgroundEventArgs e)
        {
            // Cancel default painting for the row header background.
            e.Handled = true;

            // If the row header is under the mouse pointer or the row contains the active cell,
            // paint the row header background in Color 1.
            // Otherwise, paint the row header in white.
            Color backColor = e.IsHovered || (e.RowIndex == spreadsheetControl1.ActiveCell.RowIndex) ? 
                Color.FromArgb(200, 44, 74) : // Color 1
                Color.White;
            e.Cache.FillRectangle(e.Cache.GetSolidBrush(backColor), e.Bounds);
        }
        #endregion #CustomDrawRowHeaderBackground
    }
}
