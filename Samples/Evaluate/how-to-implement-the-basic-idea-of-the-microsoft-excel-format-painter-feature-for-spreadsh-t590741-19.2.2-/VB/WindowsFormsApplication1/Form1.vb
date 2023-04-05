Imports DevExpress.Spreadsheet
Imports System
Imports System.Linq
Imports System.Windows.Forms

Namespace WindowsFormsApplication1
	Partial Public Class Form1
		Inherits Form

		Public Sub New()
			InitializeComponent()
			Dim formatPainterProvider As New FormatPainterProvider()
			formatPainterProvider.RegisterFormatPainter(spreadsheetControl1, biFormatPainter)
		End Sub
	End Class


End Namespace
