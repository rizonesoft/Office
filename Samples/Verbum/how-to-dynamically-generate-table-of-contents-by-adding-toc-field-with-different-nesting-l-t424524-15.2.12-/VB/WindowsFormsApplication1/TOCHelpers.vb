Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports DevExpress.Office
Imports DevExpress.XtraRichEdit.API.Native

Namespace WindowsFormsApplication1
	Public NotInheritable Class TOCContentHelper

		Private Sub New()
		End Sub
		Public Shared Sub AppendNewDocumentFragment(ByVal headerText As String, ByVal fragmentText As String, ByVal doc As Document, ByVal headerLevel As Integer, ByVal isPageBreakRequired As Boolean)
			If headerLevel = 1 AndAlso isPageBreakRequired Then
				doc.AppendText(Characters.PageBreak.ToString())
			End If

			Dim headerParagraph As Paragraph = doc.Paragraphs.Append()
			SetParagraphStyleSettings(doc, headerParagraph, headerLevel)
			Dim headerRange As DocumentRange = doc.AppendText(headerText)
			Dim singleParagraph As Paragraph = doc.Paragraphs.Append()
			SetParagraphStyleSettings(doc, singleParagraph, 0)
			ChangeHeaderCharacterProperties(doc, headerRange, headerLevel)
			doc.AppendText(fragmentText)
		End Sub

		Private Shared Sub ChangeHeaderCharacterProperties(ByVal doc As Document, ByVal headerRange As DocumentRange, ByVal headerLevel As Integer)
			Dim cp As CharacterProperties = doc.BeginUpdateCharacters(headerRange)
			cp.ForeColor = Color.Blue

			If headerLevel = 1 Then
				cp.Bold = True
				cp.FontSize = 16
			End If
			If headerLevel = 2 Then
				cp.Bold = True
				cp.FontSize = 12
			End If
			If headerLevel = 3 Then
				cp.Bold = False
				cp.FontSize = 12
			End If
			doc.EndUpdateCharacters(cp)
		End Sub

		Private Shared Sub SetParagraphStyleSettings(ByVal doc As Document, ByVal currentParagraph As Paragraph, ByVal level As Integer)
			If level > 0 Then
				Dim styleName As String = "Paragraph Level " & level.ToString()
				Dim paragraphStyle As ParagraphStyle = doc.ParagraphStyles(styleName)

				If paragraphStyle Is Nothing Then
					paragraphStyle = doc.ParagraphStyles.CreateNew()
					paragraphStyle.Name = styleName
					paragraphStyle.Parent = doc.ParagraphStyles("Normal")
					paragraphStyle.OutlineLevel = level
					doc.ParagraphStyles.Add(paragraphStyle)
				End If
				currentParagraph.Style = paragraphStyle
			Else
				currentParagraph.Style = doc.ParagraphStyles("Normal")
			End If
		End Sub

		Public Shared Sub InsertPageNumber(ByVal someDocument As Document)
			For i As Integer = 1 To someDocument.Sections.Count - 1
				Dim currentSection As Section = someDocument.Sections(i)

				Dim myFooter As SubDocument = currentSection.BeginUpdateFooter()
				Dim range As DocumentRange = myFooter.InsertText(myFooter.CreatePosition(0), " PAGE NUMBER ")
				Dim fld As Field = myFooter.Fields.Create(range.End, "PAGE")
				myFooter.Fields.Update()

				Dim pp As ParagraphProperties = myFooter.BeginUpdateParagraphs(myFooter.Range)
				pp.Alignment = ParagraphAlignment.Right
				myFooter.EndUpdateParagraphs(pp)

				currentSection.EndUpdateFooter(myFooter)
			Next i
		End Sub

		Public Shared Sub InsertTOC(ByVal switches As String, ByVal doc As Document)
			Dim documentHeader As DocumentRange = doc.InsertText(doc.Range.End, "INSTALL GUIDE" & Constants.vbCrLf)
			Dim pp As ParagraphProperties = doc.BeginUpdateParagraphs(documentHeader)
			pp.Reset()
			pp.Alignment = ParagraphAlignment.Center
			doc.EndUpdateParagraphs(pp)

			Dim cp As CharacterProperties = doc.BeginUpdateCharacters(documentHeader)
			cp.ForeColor = Color.Red
			cp.Bold = True
			cp.FontSize = 16
			doc.EndUpdateCharacters(cp)


			Dim field As Field = doc.Fields.Create(documentHeader.End, "TOC " & switches)
			doc.InsertSection(field.Range.End)
			field.Update()
		End Sub

		Public Shared Sub UpdateTOCFieldFormatting(ByVal doc As Document)
			If doc.ParagraphStyles("TOC 1") IsNot Nothing Then
				doc.ParagraphStyles("TOC 1").Bold = True
				doc.ParagraphStyles("TOC 1").FontSize = 16
				doc.ParagraphStyles("TOC 1").LeftIndent = 0f
			End If
			If doc.ParagraphStyles("TOC 2") IsNot Nothing Then
				doc.ParagraphStyles("TOC 2").Bold = True
				doc.ParagraphStyles("TOC 2").FontSize = 12
				doc.ParagraphStyles("TOC 2").LeftIndent = 0f
			End If
			If doc.ParagraphStyles("TOC 3") IsNot Nothing Then
				doc.ParagraphStyles("TOC 3").Bold = False
				doc.ParagraphStyles("TOC 3").FontSize = 12
				doc.ParagraphStyles("TOC 3").LeftIndent = 0f
			End If
		End Sub
	End Class
End Namespace
