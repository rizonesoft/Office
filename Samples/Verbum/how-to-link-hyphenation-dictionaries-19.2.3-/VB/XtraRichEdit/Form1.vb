Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Export
Imports System
Imports System.IO
Imports DevExpress.Office.Services
Imports DevExpress.Office.Utils
Imports DevExpress.BarCodes
Imports System.Drawing
Imports System.Windows.Forms
Imports DevExpress.Pdf
Imports DevExpress.XtraBars
Imports System.Data
Imports System.Runtime.Serialization.Formatters.Binary
Imports DevExpress.XtraRichEdit.Forms
Imports System.Reflection
Imports System.Globalization

Namespace XtraRichEdit
	Partial Public Class Form1
		Inherits RibbonForm

		Public Sub New()
			InitializeComponent()
			Me.Controls.Add(richEditControl.CreateRibbon())

			richEditControl.LoadDocument("Multimodal.docx")

			HyphenateDocument(richEditControl.Document)

		End Sub

		Private Sub HyphenateDocument(ByVal document As Document)
			'Load embedded dictionaries
			Dim openOfficePatternStream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("hyphen.dic")
			Dim customDictionaryStream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("hyphen_exc.dic")


			'Create dictionary objects
			Dim hyphenationDictionary As New OpenOfficeHyphenationDictionary(openOfficePatternStream, New CultureInfo("EN-US"))
			Dim exceptionsDictionary As New CustomHyphenationDictionary(customDictionaryStream, New CultureInfo("EN-US"))

			'Add them to the word processor's collection
			richEditControl.HyphenationDictionaries.Add(hyphenationDictionary)
			richEditControl.HyphenationDictionaries.Add(exceptionsDictionary)

			'Enable automatic hyphenation
			document.Hyphenation = True
		End Sub
	End Class
End Namespace
