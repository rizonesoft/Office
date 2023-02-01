Imports DevExpress.Xpf.Core
Imports DevExpress.XtraRichEdit.API.Native
Imports System.Reflection
Imports System.Globalization

Namespace DXRichEdit
	Partial Public Class MainWindow
		Inherits ThemedWindow

		Public Sub New()
			InitializeComponent()

			richEditControl1.LoadDocument("Multimodal.docx")
			Dim openOfficePatternStream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("hyphen.dic")
			Dim customDictionaryStream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("hyphen_exc.dic")

			'Create dictionary objects
			Dim hyphenationDictionary As New OpenOfficeHyphenationDictionary(openOfficePatternStream, New CultureInfo("EN-US"))
			Dim exceptionsDictionary As New CustomHyphenationDictionary(customDictionaryStream, New CultureInfo("EN-US"))

			'Add them to the word processor's collection
			richEditControl1.HyphenationDictionaries.Add(hyphenationDictionary)
			richEditControl1.HyphenationDictionaries.Add(exceptionsDictionary)

			richEditControl1.Document.Hyphenation = True
		End Sub
	End Class
End Namespace
