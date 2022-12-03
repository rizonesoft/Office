Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Layout
Imports DevExpress.XtraRichEdit.API.Native
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms

Namespace RichEditControl_CheckBox
    Partial Public Class Form1
        Inherits DevExpress.XtraEditors.XtraForm

        Private Shared ReadOnly checkedCheckBox As String = ChrW(&H2612).ToString()
        Private Shared ReadOnly uncheckedCheckBox As String = ChrW(&H2610).ToString()
        Public Sub New()
            InitializeComponent()
        End Sub
        Private Sub barButtonItem1_ItemClick(ByVal sender As Object, ByVal e As DevExpress.XtraBars.ItemClickEventArgs) Handles barButtonItem1.ItemClick
            Dim caretPosition As DocumentPosition = richEditControl1.Document.CaretPosition
            Dim document As SubDocument = caretPosition.BeginUpdateDocument()
            Dim checkBox As DocumentRange = document.InsertText(caretPosition, uncheckedCheckBox)
            Dim cp As CharacterProperties = document.BeginUpdateCharacters(checkBox)
            cp.FontName = "MS Gothic"
            document.EndUpdateCharacters(cp)
            caretPosition.EndUpdateDocument(document)
        End Sub
        Private Sub richEditControl1_MouseClick(ByVal sender As Object, ByVal e As MouseEventArgs) Handles richEditControl1.MouseClick
            Dim pageLayoutPosition As PageLayoutPosition = richEditControl1.ActiveView.GetDocumentLayoutPosition(e.Location)
            If pageLayoutPosition Is Nothing Then
                Return
            End If
            Dim pageIndex As Integer = pageLayoutPosition.PageIndex
            Dim point As Point = pageLayoutPosition.Position
            Dim layoutPage As LayoutPage = richEditControl1.DocumentLayout.GetPage(pageIndex)
            Dim hitTest As New HitTestManager(richEditControl1.DocumentLayout)
            Dim result As RichEditHitTestResult = hitTest.HitTest(layoutPage, point)
            If TypeOf result.LayoutElement Is CharacterBox AndAlso richEditControl1.Document.Selection.Length = 0 Then
                Dim character As CharacterBox = CType(result.LayoutElement, CharacterBox)
                Dim caretPosition As DocumentPosition = richEditControl1.Document.CaretPosition
                Dim document As SubDocument = caretPosition.BeginUpdateDocument()
                If document.GetSubDocumentType() = GetLocation(character.Parent) Then
                    Dim characterRange As DocumentRange = document.CreateRange(character.Range.Start, 1)
                    UpdateCheckState(document, characterRange, character.Text)
                End If
                caretPosition.EndUpdateDocument(document)
            End If
        End Sub
        Public Sub UpdateCheckState(ByVal document As SubDocument, ByVal range As DocumentRange, ByVal prevState As String)
            If prevState.Equals(checkedCheckBox) Then
                document.Replace(range, uncheckedCheckBox)
            ElseIf prevState.Equals(uncheckedCheckBox) Then
                document.Replace(range, checkedCheckBox)
            End If
        End Sub
        Public Function GetLocation(ByVal element As LayoutElement) As SubDocumentType
            Do While element IsNot Nothing
                Select Case element.Type
                    Case LayoutType.CommentsArea
                        Return SubDocumentType.Comment
                    Case LayoutType.Header
                        Return SubDocumentType.Header
                    Case LayoutType.Footer
                        Return SubDocumentType.Footer
                    Case LayoutType.TextBox
                        Return SubDocumentType.TextBox
                End Select
                element = element.Parent
            Loop
            Return SubDocumentType.Main
        End Function
    End Class
End Namespace
