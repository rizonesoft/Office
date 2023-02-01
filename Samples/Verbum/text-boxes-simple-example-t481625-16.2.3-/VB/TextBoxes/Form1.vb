Imports DevExpress.XtraBars.Ribbon
Imports System
Imports System.Drawing
Imports DevExpress.XtraRichEdit.API.Native

Namespace TextBoxes
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            richEditControl1.LoadDocument("FloatingObjects.docx")

        End Sub
        Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
            CreateTextBox(richEditControl1.Document)
            ResizeTextBox(richEditControl1.Document)
            ColorTextBox(richEditControl1.Document)
            EditTextBoxContent(richEditControl1.Document)
        End Sub

        Private Sub CreateTextBox(ByVal document As Document)
'            #Region "#create"
            Dim myPosition As DocumentPosition = document.Paragraphs(0).Range.Start

            'Insert a text box to a given position
            Dim myTextBox As Shape = document.Shapes.InsertTextBox(myPosition)
'            #End Region ' #create
        End Sub

        Private Sub EditTextBoxContent(ByVal document As Document)
'            #Region "#editcontent"
            'Access the text box content
            Dim textBoxDocument As SubDocument = document.Shapes(0).TextBox.Document

            'Insert text to the text box
            textBoxDocument.AppendText("Multimodal, Stochastic Symmetries for E-Commerce")

            'Apply formatting to the text box content
            Dim cp As CharacterProperties = textBoxDocument.BeginUpdateCharacters(textBoxDocument.Range)
            cp.ForeColor = Color.DarkSlateGray
            cp.FontName = "Times New Roman"
            cp.FontSize = 18
            textBoxDocument.EndUpdateCharacters(cp)
'            #End Region ' #editcontent
        End Sub

        Private Sub ColorTextBox(ByVal document As Document)
'            #Region "#changecolor"
            Dim myTextBox As Shape = document.Shapes(0)

            'Specify the background color
            myTextBox.Fill.Color = Color.MistyRose

            'Draw a border around the text box
            myTextBox.Line.Color = Color.DarkGray
            myTextBox.Line.Thickness = 1.5F
'            #End Region ' #changecolor
        End Sub

        Private Sub ResizeTextBox(ByVal document As Document)
'            #Region "#resize"
            Dim myTextBox As Shape = document.Shapes(0)

            'Resize the text box
            myTextBox.ScaleX = 5F
            myTextBox.ScaleY = 1F

            'Set the horizontal alignment
            myTextBox.HorizontalAlignment = ShapeHorizontalAlignment.Center
            myTextBox.RelativeHorizontalPosition = ShapeRelativeHorizontalPosition.Margin

            'Change the vertical alignment
            myTextBox.VerticalAlignment = ShapeVerticalAlignment.Top
            myTextBox.RelativeVerticalPosition = ShapeRelativeVerticalPosition.Margin
'            #End Region ' #resize
        End Sub
    End Class
End Namespace
