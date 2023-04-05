Imports DevExpress.XtraBars.Helpers
Imports DevExpress.Spreadsheet
Imports DevExpress.XtraSpreadsheet.Menu
Public Class Form1
    Sub New()
        InitSkins()
        InitializeComponent()
        Me.InitSkinGallery()
        Dim worksheet As Worksheet = spreadsheetControl.ActiveWorksheet
        Dim richText As New RichTextString()

        richText.AddTextRun("Rich ", New RichTextRunFont("Arial", 14, System.Drawing.Color.FromArgb(&HC5, &H9F, &HC9)))
        richText.AddTextRun("text ", New RichTextRunFont("Tahoma", 14, System.Drawing.Color.FromArgb(&H2C, &H60, &H8E)))
        richText.AddTextRun("formatting", New RichTextRunFont("Castellar", 14, System.Drawing.Color.FromArgb(&H2F, &H24, &H4F)))
        worksheet("B2").SetRichText(richText)
        worksheet("B5").SetValueFromText("This is the plain text" & vbLf & "Use the context menu to set rich text formatting")
        worksheet("B5").Alignment.WrapText = True
        worksheet.Columns(1).WidthInCharacters = 50
    End Sub
    Sub InitSkins()
        DevExpress.Skins.SkinManager.EnableFormSkins()
        DevExpress.UserSkins.BonusSkins.Register()
    End Sub
    Private Sub InitSkinGallery()
        SkinHelper.InitSkinGallery(rgbiSkins, True)
    End Sub

    Private Sub spreadsheetControl_CellBeginEdit(sender As Object, e As DevExpress.XtraSpreadsheet.SpreadsheetCellCancelEventArgs) Handles spreadsheetControl.CellBeginEdit
        If e.Cell.HasRichText Then
            e.Cancel = True
            Using richEditForm As New RichTextEditForm(e.Cell)
                richEditForm.ShowDialog()
            End Using
        End If
    End Sub

    Private Sub spreadsheetControl_PopupMenuShowing(sender As Object, e As DevExpress.XtraSpreadsheet.PopupMenuShowingEventArgs) Handles spreadsheetControl.PopupMenuShowing
        If e.MenuType = DevExpress.XtraSpreadsheet.SpreadsheetMenuType.Cell Then
            Dim activeCell As Cell = spreadsheetControl.ActiveCell
            If activeCell.Value.IsEmpty OrElse (Not activeCell.HasFormula AndAlso activeCell.Value.IsText) Then
                Dim setRichTextItem As New SpreadsheetMenuItem("Set Rich Text", New EventHandler(AddressOf SetRichTextItemClick))
                e.Menu.Items.Add(setRichTextItem)
            End If
        End If
    End Sub

    Private Sub SetRichTextItemClick(ByVal sender As Object, ByVal e As EventArgs)
        Using richEditForm As New RichTextEditForm(spreadsheetControl.ActiveCell)
            richEditForm.ShowDialog()
        End Using
    End Sub
End Class
