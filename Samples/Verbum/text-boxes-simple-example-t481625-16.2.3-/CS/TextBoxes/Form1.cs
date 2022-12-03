using DevExpress.XtraBars.Ribbon;
using System;
using System.Drawing;
using DevExpress.XtraRichEdit.API.Native;

namespace TextBoxes
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("FloatingObjects.docx");

        }
        private void Form1_Load(object sender, EventArgs e)
        {
            CreateTextBox(richEditControl1.Document);
            ResizeTextBox(richEditControl1.Document);
            ColorTextBox(richEditControl1.Document);
            EditTextBoxContent(richEditControl1.Document);
        }

        private void CreateTextBox(Document document)
        {
            #region #create
            DocumentPosition myPosition = document.Paragraphs[0].Range.Start;

            //Insert a text box to a given position
            Shape myTextBox = document.Shapes.InsertTextBox(myPosition);
            #endregion #create
        }

        private void EditTextBoxContent(Document document)
        {
            #region #editcontent
            //Access the text box content
            SubDocument textBoxDocument = document.Shapes[0].TextBox.Document;

            //Insert text to the text box
            textBoxDocument.AppendText("Multimodal, Stochastic Symmetries for E-Commerce");

            //Apply formatting to the text box content
            CharacterProperties cp = textBoxDocument.BeginUpdateCharacters(textBoxDocument.Range);
            cp.ForeColor = Color.DarkSlateGray;
            cp.FontName = "Times New Roman";
            cp.FontSize = 18;
            textBoxDocument.EndUpdateCharacters(cp);
            #endregion #editcontent
        }

        private void ColorTextBox(Document document)
        {
            #region #changecolor
            Shape myTextBox = document.Shapes[0];

            //Specify the background color
            myTextBox.Fill.Color = Color.MistyRose;

            //Draw a border around the text box
            myTextBox.Line.Color = Color.DarkGray;
            myTextBox.Line.Thickness = 1.5f;
            #endregion #changecolor
        }

        private void ResizeTextBox(Document document)
        {
            #region #resize
            Shape myTextBox = document.Shapes[0];

            //Resize the text box
            myTextBox.ScaleX = 5f;
            myTextBox.ScaleY = 1f;

            //Set the horizontal alignment
            myTextBox.HorizontalAlignment = ShapeHorizontalAlignment.Center;
            myTextBox.RelativeHorizontalPosition = ShapeRelativeHorizontalPosition.Margin;

            //Change the vertical alignment
            myTextBox.VerticalAlignment = ShapeVerticalAlignment.Top;
            myTextBox.RelativeVerticalPosition = ShapeRelativeVerticalPosition.Margin;
            #endregion #resize
        }
    }
}
