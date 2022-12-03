' Developer Express Code Central Example:
' How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
' 
' This example demonstrates how to copy the characters and paragraphs properties
' and apply formatting to the selected text. Try the Format Painter button on the
' ribbon Home tab.
' 
' To obtain the selected text range, the
' RichEditDocument.Document.Selection property is used. The characters and
' paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
' handler. Then, they are stored in the CharacterPropertiesObject and
' ParagraphPropertiesObject object containers.
' 
' In order to change the current
' RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
' the custom MouseCursorCalculator class Calculate method for clarification.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E5223

Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Windows.Forms
Imports DevExpress.XtraBars.Helpers
Imports DevExpress.XtraBars
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native


Namespace DXApplication9
	Partial Public Class Form1
		Inherits RibbonForm

		Public Sub New()
			InitializeComponent()
			InitSkinGallery()
			InitializeRichEditControl()
			ribbonControl.SelectedPage = homeRibbonPage1
			Dim path As String = "DemoDoc.docx"

			richEditControl.LoadDocument(path,DocumentFormat.OpenXml)
		End Sub

		Private Sub richEditControl_MouseUp(ByVal sender As Object, ByVal e As MouseEventArgs) Handles richEditControl.MouseUp
			If barCheckItem1.Checked Then
				ApplyFormatToSelectedText()
				barCheckItem1.Checked = False
			End If
		End Sub

		Private Sub InitSkinGallery()
			SkinHelper.InitSkinGallery(rgbiSkins, True)
		End Sub
		Private Sub InitializeRichEditControl()
			AddHandler richEditControl.StartHeaderFooterEditing, AddressOf richEditControl_StartHeaderFooterEditing
			AddHandler richEditControl.SelectionChanged, AddressOf richEditControl_SelectionChanged
			AddHandler richEditControl.FinishHeaderFooterEditing, AddressOf richEditControl_FinishHeaderFooterEditing
		End Sub

		Private Sub richEditControl_StartHeaderFooterEditing(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.HeaderFooterEditingEventArgs)
			headerFooterToolsRibbonPageCategory1.Visible = True
			ribbonControl.SelectedPage = headerFooterToolsDesignRibbonPage1
		End Sub
		Private Sub richEditControl_FinishHeaderFooterEditing(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.HeaderFooterEditingEventArgs)
			headerFooterToolsRibbonPageCategory1.Visible = False
		End Sub
		Private Sub richEditControl_SelectionChanged(ByVal sender As Object, ByVal e As EventArgs)
			tableToolsRibbonPageCategory1.Visible = richEditControl.IsSelectionInTable()
			floatingPictureToolsRibbonPageCategory1.Visible = richEditControl.IsFloatingObjectSelected
		End Sub

		Private sourceSelectedRange As DocumentRange
		Private Sub SaveSelectedRange()
			Dim selection As DocumentRange = richEditControl.Document.Selection
			Dim subDocument As SubDocument = selection.BeginUpdateDocument()
			sourceSelectedRange = subDocument.CreateRange(selection.Start, richEditControl.Document.Selection.Length)
			selection.EndUpdateDocument(subDocument)
		End Sub
		Private Sub barCheckItem1_CheckedChanged(ByVal sender As Object, ByVal e As ItemClickEventArgs) Handles barCheckItem1.CheckedChanged
			If barCheckItem1.Checked Then
				SaveSelectedRange()
				richEditControl.FormatCalculatorEnabled = True
			Else
				richEditControl.FormatCalculatorEnabled = False
			End If

		End Sub

		Private Sub ApplyFormatToSelectedText()
			Dim targetSelectedRange As DocumentRange = richEditControl.Document.Selection

			richEditControl.BeginUpdate()
			Dim targetSubDocument As SubDocument = targetSelectedRange.BeginUpdateDocument()
			Dim subDocument As SubDocument = sourceSelectedRange.BeginUpdateDocument()

			Dim targetCharactersProperties As DevExpress.XtraRichEdit.API.Native.CharacterProperties = targetSubDocument.BeginUpdateCharacters(targetSelectedRange)
			Dim sourceCharactersProperties As DevExpress.XtraRichEdit.API.Native.CharacterProperties = subDocument.BeginUpdateCharacters(sourceSelectedRange)
			targetCharactersProperties.Assign(sourceCharactersProperties)
			subDocument.EndUpdateCharacters(sourceCharactersProperties)
			targetSubDocument.EndUpdateCharacters(targetCharactersProperties)

			Dim targetParagraphProperties As DevExpress.XtraRichEdit.API.Native.ParagraphProperties = targetSubDocument.BeginUpdateParagraphs(targetSelectedRange)
			Dim sourceParagraphProperties As DevExpress.XtraRichEdit.API.Native.ParagraphProperties = subDocument.BeginUpdateParagraphs(sourceSelectedRange)
			targetParagraphProperties.Assign(sourceParagraphProperties)
			subDocument.EndUpdateParagraphs(sourceParagraphProperties)
			targetSubDocument.EndUpdateParagraphs(targetParagraphProperties)

			sourceSelectedRange.EndUpdateDocument(subDocument)
			targetSelectedRange.EndUpdateDocument(targetSubDocument)
			richEditControl.EndUpdate()
		End Sub



	End Class

End Namespace