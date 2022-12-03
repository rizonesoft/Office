Namespace Expander
    Partial Public Class Form1
        ''' <summary>
        ''' Required designer variable.
        ''' </summary>
        Private components As System.ComponentModel.IContainer = Nothing

        ''' <summary>
        ''' Clean up any resources being used.
        ''' </summary>
        ''' <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        Protected Overrides Sub Dispose(ByVal disposing As Boolean)
            If disposing AndAlso (components IsNot Nothing) Then
                components.Dispose()
            End If
            MyBase.Dispose(disposing)
        End Sub

        #Region "Windows Form Designer generated code"

        ''' <summary>
        ''' Required method for Designer support - do not modify
        ''' the contents of this method with the code editor.
        ''' </summary>
        Private Sub InitializeComponent()
            Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
            Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
            Me.ribbonControl1 = New DevExpress.XtraBars.Ribbon.RibbonControl()
            Me.fileNewItem1 = New DevExpress.XtraRichEdit.UI.FileNewItem()
            Me.fileOpenItem1 = New DevExpress.XtraRichEdit.UI.FileOpenItem()
            Me.fileSaveItem1 = New DevExpress.XtraRichEdit.UI.FileSaveItem()
            Me.fileSaveAsItem1 = New DevExpress.XtraRichEdit.UI.FileSaveAsItem()
            Me.quickPrintItem1 = New DevExpress.XtraRichEdit.UI.QuickPrintItem()
            Me.printItem1 = New DevExpress.XtraRichEdit.UI.PrintItem()
            Me.printPreviewItem1 = New DevExpress.XtraRichEdit.UI.PrintPreviewItem()
            Me.undoItem1 = New DevExpress.XtraRichEdit.UI.UndoItem()
            Me.redoItem1 = New DevExpress.XtraRichEdit.UI.RedoItem()
            Me.cutItem1 = New DevExpress.XtraRichEdit.UI.CutItem()
            Me.copyItem1 = New DevExpress.XtraRichEdit.UI.CopyItem()
            Me.pasteItem1 = New DevExpress.XtraRichEdit.UI.PasteItem()
            Me.pasteSpecialItem1 = New DevExpress.XtraRichEdit.UI.PasteSpecialItem()
            Me.changeFontNameItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontNameItem()
            Me.repositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
            Me.changeFontSizeItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontSizeItem()
            Me.repositoryItemRichEditFontSizeEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit()
            Me.changeFontColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontColorItem()
            Me.changeFontBackColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem()
            Me.toggleFontSuperscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem()
            Me.toggleFontSubscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem()
            Me.changeTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ChangeTextCaseItem()
            Me.makeTextUpperCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem()
            Me.makeTextLowerCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem()
            Me.toggleTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ToggleTextCaseItem()
            Me.fontSizeIncreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem()
            Me.fontSizeDecreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem()
            Me.clearFormattingItem1 = New DevExpress.XtraRichEdit.UI.ClearFormattingItem()
            Me.showFontFormItem1 = New DevExpress.XtraRichEdit.UI.ShowFontFormItem()
            Me.toggleParagraphAlignmentLeftItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem()
            Me.toggleParagraphAlignmentCenterItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem()
            Me.toggleParagraphAlignmentRightItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem()
            Me.toggleParagraphAlignmentJustifyItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem()
            Me.changeParagraphLineSpacingItem1 = New DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem()
            Me.setSingleParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem()
            Me.setSesquialteralParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem()
            Me.setDoubleParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem()
            Me.showLineSpacingFormItem1 = New DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem()
            Me.addSpacingBeforeParagraphItem1 = New DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem()
            Me.removeSpacingBeforeParagraphItem1 = New DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem()
            Me.addSpacingAfterParagraphItem1 = New DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem()
            Me.removeSpacingAfterParagraphItem1 = New DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem()
            Me.toggleBulletedListItem1 = New DevExpress.XtraRichEdit.UI.ToggleBulletedListItem()
            Me.toggleNumberingListItem1 = New DevExpress.XtraRichEdit.UI.ToggleNumberingListItem()
            Me.toggleMultiLevelListItem1 = New DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem()
            Me.decreaseIndentItem1 = New DevExpress.XtraRichEdit.UI.DecreaseIndentItem()
            Me.increaseIndentItem1 = New DevExpress.XtraRichEdit.UI.IncreaseIndentItem()
            Me.toggleShowWhitespaceItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem()
            Me.showParagraphFormItem1 = New DevExpress.XtraRichEdit.UI.ShowParagraphFormItem()
            Me.changeStyleItem1 = New DevExpress.XtraRichEdit.UI.ChangeStyleItem()
            Me.repositoryItemRichEditStyleEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditStyleEdit()
            Me.findItem1 = New DevExpress.XtraRichEdit.UI.FindItem()
            Me.replaceItem1 = New DevExpress.XtraRichEdit.UI.ReplaceItem()
            Me.barButtonGroup1 = New DevExpress.XtraBars.BarButtonGroup()
            Me.toggleFontBoldItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontBoldItem()
            Me.toggleFontItalicItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontItalicItem()
            Me.toggleFontUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem()
            Me.toggleFontDoubleUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem()
            Me.toggleFontStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem()
            Me.toggleFontDoubleStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem()
            Me.barButtonGroup2 = New DevExpress.XtraBars.BarButtonGroup()
            Me.barButtonGroup3 = New DevExpress.XtraBars.BarButtonGroup()
            Me.barButtonGroup4 = New DevExpress.XtraBars.BarButtonGroup()
            Me.barButtonGroup5 = New DevExpress.XtraBars.BarButtonGroup()
            Me.barButtonGroup6 = New DevExpress.XtraBars.BarButtonGroup()
            Me.barButtonGroup7 = New DevExpress.XtraBars.BarButtonGroup()
            Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
            Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
            Me.homeRibbonPage1 = New DevExpress.XtraRichEdit.UI.HomeRibbonPage()
            Me.clipboardRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup()
            Me.fontRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.FontRibbonPageGroup()
            Me.paragraphRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup()
            Me.stylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup()
            Me.editingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup()
            Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
            Me.pagesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup()
            Me.insertRibbonPage1 = New DevExpress.XtraRichEdit.UI.InsertRibbonPage()
            Me.insertPageBreakItem1 = New DevExpress.XtraRichEdit.UI.InsertPageBreakItem()
            Me.tablesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup()
            Me.insertTableItem1 = New DevExpress.XtraRichEdit.UI.InsertTableItem()
            Me.illustrationsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup()
            Me.insertPictureItem1 = New DevExpress.XtraRichEdit.UI.InsertPictureItem()
            Me.linksRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup()
            Me.insertBookmarkItem1 = New DevExpress.XtraRichEdit.UI.InsertBookmarkItem()
            Me.insertHyperlinkItem1 = New DevExpress.XtraRichEdit.UI.InsertHyperlinkItem()
            Me.headerFooterRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup()
            Me.editPageHeaderItem1 = New DevExpress.XtraRichEdit.UI.EditPageHeaderItem()
            Me.editPageFooterItem1 = New DevExpress.XtraRichEdit.UI.EditPageFooterItem()
            Me.insertPageNumberItem1 = New DevExpress.XtraRichEdit.UI.InsertPageNumberItem()
            Me.insertPageCountItem1 = New DevExpress.XtraRichEdit.UI.InsertPageCountItem()
            Me.symbolsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup()
            Me.insertSymbolItem1 = New DevExpress.XtraRichEdit.UI.InsertSymbolItem()
            DirectCast(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.repositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
            Me.SuspendLayout()
            ' 
            ' richEditControl1
            ' 
            Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
            Me.richEditControl1.Location = New System.Drawing.Point(0, 143)
            Me.richEditControl1.MenuManager = Me.ribbonControl1
            Me.richEditControl1.Name = "richEditControl1"
            Me.richEditControl1.Size = New System.Drawing.Size(784, 419)
            Me.richEditControl1.TabIndex = 0
            Me.richEditControl1.Text = "richEditControl1"
            ' 
            ' ribbonControl1
            ' 
            Me.ribbonControl1.ApplicationButtonText = Nothing
            ' 
            ' 
            ' 
            Me.ribbonControl1.ExpandCollapseItem.Id = 0
            Me.ribbonControl1.ExpandCollapseItem.Name = ""
            Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.undoItem1, Me.redoItem1, Me.cutItem1, Me.copyItem1, Me.pasteItem1, Me.pasteSpecialItem1, Me.changeFontNameItem1, Me.changeFontSizeItem1, Me.changeFontColorItem1, Me.changeFontBackColorItem1, Me.toggleFontSuperscriptItem1, Me.toggleFontSubscriptItem1, Me.changeTextCaseItem1, Me.makeTextUpperCaseItem1, Me.makeTextLowerCaseItem1, Me.toggleTextCaseItem1, Me.fontSizeIncreaseItem1, Me.fontSizeDecreaseItem1, Me.clearFormattingItem1, Me.showFontFormItem1, Me.toggleParagraphAlignmentLeftItem1, Me.toggleParagraphAlignmentCenterItem1, Me.toggleParagraphAlignmentRightItem1, Me.toggleParagraphAlignmentJustifyItem1, Me.changeParagraphLineSpacingItem1, Me.setSingleParagraphSpacingItem1, Me.setSesquialteralParagraphSpacingItem1, Me.setDoubleParagraphSpacingItem1, Me.showLineSpacingFormItem1, Me.addSpacingBeforeParagraphItem1, Me.removeSpacingBeforeParagraphItem1, Me.addSpacingAfterParagraphItem1, Me.removeSpacingAfterParagraphItem1, Me.toggleBulletedListItem1, Me.toggleNumberingListItem1, Me.toggleMultiLevelListItem1, Me.decreaseIndentItem1, Me.increaseIndentItem1, Me.toggleShowWhitespaceItem1, Me.showParagraphFormItem1, Me.changeStyleItem1, Me.findItem1, Me.replaceItem1, Me.barButtonGroup1, Me.barButtonGroup2, Me.barButtonGroup3, Me.barButtonGroup4, Me.barButtonGroup5, Me.barButtonGroup6, Me.barButtonGroup7, Me.toggleFontBoldItem1, Me.toggleFontItalicItem1, Me.toggleFontUnderlineItem1, Me.toggleFontDoubleUnderlineItem1, Me.toggleFontStrikeoutItem1, Me.toggleFontDoubleStrikeoutItem1, Me.insertPageBreakItem1, Me.insertTableItem1, Me.insertPictureItem1, Me.insertBookmarkItem1, Me.insertHyperlinkItem1, Me.editPageHeaderItem1, Me.editPageFooterItem1, Me.insertPageNumberItem1, Me.insertPageCountItem1, Me.insertSymbolItem1})
            Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
            Me.ribbonControl1.MaxItemId = 84
            Me.ribbonControl1.Name = "ribbonControl1"
            Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1, Me.homeRibbonPage1, Me.insertRibbonPage1})
            Me.ribbonControl1.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() { Me.repositoryItemFontEdit1, Me.repositoryItemRichEditFontSizeEdit1, Me.repositoryItemRichEditStyleEdit1})
            Me.ribbonControl1.SelectedPage = Me.homeRibbonPage1
            Me.ribbonControl1.Size = New System.Drawing.Size(784, 143)
            ' 
            ' fileNewItem1
            ' 
            Me.fileNewItem1.Glyph = (DirectCast(resources.GetObject("fileNewItem1.Glyph"), System.Drawing.Image))
            Me.fileNewItem1.Id = 6
            Me.fileNewItem1.LargeGlyph = (DirectCast(resources.GetObject("fileNewItem1.LargeGlyph"), System.Drawing.Image))
            Me.fileNewItem1.Name = "fileNewItem1"
            ' 
            ' fileOpenItem1
            ' 
            Me.fileOpenItem1.Glyph = (DirectCast(resources.GetObject("fileOpenItem1.Glyph"), System.Drawing.Image))
            Me.fileOpenItem1.Id = 7
            Me.fileOpenItem1.LargeGlyph = (DirectCast(resources.GetObject("fileOpenItem1.LargeGlyph"), System.Drawing.Image))
            Me.fileOpenItem1.Name = "fileOpenItem1"
            ' 
            ' fileSaveItem1
            ' 
            Me.fileSaveItem1.Glyph = (DirectCast(resources.GetObject("fileSaveItem1.Glyph"), System.Drawing.Image))
            Me.fileSaveItem1.Id = 8
            Me.fileSaveItem1.LargeGlyph = (DirectCast(resources.GetObject("fileSaveItem1.LargeGlyph"), System.Drawing.Image))
            Me.fileSaveItem1.Name = "fileSaveItem1"
            ' 
            ' fileSaveAsItem1
            ' 
            Me.fileSaveAsItem1.Glyph = (DirectCast(resources.GetObject("fileSaveAsItem1.Glyph"), System.Drawing.Image))
            Me.fileSaveAsItem1.Id = 9
            Me.fileSaveAsItem1.LargeGlyph = (DirectCast(resources.GetObject("fileSaveAsItem1.LargeGlyph"), System.Drawing.Image))
            Me.fileSaveAsItem1.Name = "fileSaveAsItem1"
            ' 
            ' quickPrintItem1
            ' 
            Me.quickPrintItem1.Glyph = (DirectCast(resources.GetObject("quickPrintItem1.Glyph"), System.Drawing.Image))
            Me.quickPrintItem1.Id = 10
            Me.quickPrintItem1.LargeGlyph = (DirectCast(resources.GetObject("quickPrintItem1.LargeGlyph"), System.Drawing.Image))
            Me.quickPrintItem1.Name = "quickPrintItem1"
            ' 
            ' printItem1
            ' 
            Me.printItem1.Glyph = (DirectCast(resources.GetObject("printItem1.Glyph"), System.Drawing.Image))
            Me.printItem1.Id = 11
            Me.printItem1.LargeGlyph = (DirectCast(resources.GetObject("printItem1.LargeGlyph"), System.Drawing.Image))
            Me.printItem1.Name = "printItem1"
            ' 
            ' printPreviewItem1
            ' 
            Me.printPreviewItem1.Glyph = (DirectCast(resources.GetObject("printPreviewItem1.Glyph"), System.Drawing.Image))
            Me.printPreviewItem1.Id = 12
            Me.printPreviewItem1.LargeGlyph = (DirectCast(resources.GetObject("printPreviewItem1.LargeGlyph"), System.Drawing.Image))
            Me.printPreviewItem1.Name = "printPreviewItem1"
            ' 
            ' undoItem1
            ' 
            Me.undoItem1.Glyph = (DirectCast(resources.GetObject("undoItem1.Glyph"), System.Drawing.Image))
            Me.undoItem1.Id = 13
            Me.undoItem1.LargeGlyph = (DirectCast(resources.GetObject("undoItem1.LargeGlyph"), System.Drawing.Image))
            Me.undoItem1.Name = "undoItem1"
            ' 
            ' redoItem1
            ' 
            Me.redoItem1.Glyph = (DirectCast(resources.GetObject("redoItem1.Glyph"), System.Drawing.Image))
            Me.redoItem1.Id = 14
            Me.redoItem1.LargeGlyph = (DirectCast(resources.GetObject("redoItem1.LargeGlyph"), System.Drawing.Image))
            Me.redoItem1.Name = "redoItem1"
            ' 
            ' cutItem1
            ' 
            Me.cutItem1.Glyph = (DirectCast(resources.GetObject("cutItem1.Glyph"), System.Drawing.Image))
            Me.cutItem1.Id = 15
            Me.cutItem1.LargeGlyph = (DirectCast(resources.GetObject("cutItem1.LargeGlyph"), System.Drawing.Image))
            Me.cutItem1.Name = "cutItem1"
            Me.cutItem1.RibbonStyle = (CType((DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText Or DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText), DevExpress.XtraBars.Ribbon.RibbonItemStyles))
            ' 
            ' copyItem1
            ' 
            Me.copyItem1.Glyph = (DirectCast(resources.GetObject("copyItem1.Glyph"), System.Drawing.Image))
            Me.copyItem1.Id = 16
            Me.copyItem1.LargeGlyph = (DirectCast(resources.GetObject("copyItem1.LargeGlyph"), System.Drawing.Image))
            Me.copyItem1.Name = "copyItem1"
            Me.copyItem1.RibbonStyle = (CType((DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText Or DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText), DevExpress.XtraBars.Ribbon.RibbonItemStyles))
            ' 
            ' pasteItem1
            ' 
            Me.pasteItem1.Glyph = (DirectCast(resources.GetObject("pasteItem1.Glyph"), System.Drawing.Image))
            Me.pasteItem1.Id = 17
            Me.pasteItem1.LargeGlyph = (DirectCast(resources.GetObject("pasteItem1.LargeGlyph"), System.Drawing.Image))
            Me.pasteItem1.Name = "pasteItem1"
            Me.pasteItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
            ' 
            ' pasteSpecialItem1
            ' 
            Me.pasteSpecialItem1.Glyph = (DirectCast(resources.GetObject("pasteSpecialItem1.Glyph"), System.Drawing.Image))
            Me.pasteSpecialItem1.Id = 18
            Me.pasteSpecialItem1.LargeGlyph = (DirectCast(resources.GetObject("pasteSpecialItem1.LargeGlyph"), System.Drawing.Image))
            Me.pasteSpecialItem1.Name = "pasteSpecialItem1"
            Me.pasteSpecialItem1.RibbonStyle = (CType((DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText Or DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText), DevExpress.XtraBars.Ribbon.RibbonItemStyles))
            ' 
            ' changeFontNameItem1
            ' 
            Me.changeFontNameItem1.Edit = Me.repositoryItemFontEdit1
            Me.changeFontNameItem1.Id = 19
            Me.changeFontNameItem1.Name = "changeFontNameItem1"
            Me.changeFontNameItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
            Me.changeFontNameItem1.Width = 150
            ' 
            ' repositoryItemFontEdit1
            ' 
            Me.repositoryItemFontEdit1.AutoHeight = False
            Me.repositoryItemFontEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
            Me.repositoryItemFontEdit1.Name = "repositoryItemFontEdit1"
            ' 
            ' changeFontSizeItem1
            ' 
            Me.changeFontSizeItem1.Edit = Me.repositoryItemRichEditFontSizeEdit1
            Me.changeFontSizeItem1.Id = 20
            Me.changeFontSizeItem1.Name = "changeFontSizeItem1"
            Me.changeFontSizeItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
            ' 
            ' repositoryItemRichEditFontSizeEdit1
            ' 
            Me.repositoryItemRichEditFontSizeEdit1.AutoHeight = False
            Me.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
            Me.repositoryItemRichEditFontSizeEdit1.Control = Me.richEditControl1
            Me.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1"
            ' 
            ' changeFontColorItem1
            ' 
            Me.changeFontColorItem1.Glyph = (DirectCast(resources.GetObject("changeFontColorItem1.Glyph"), System.Drawing.Image))
            Me.changeFontColorItem1.Id = 21
            Me.changeFontColorItem1.LargeGlyph = (DirectCast(resources.GetObject("changeFontColorItem1.LargeGlyph"), System.Drawing.Image))
            Me.changeFontColorItem1.Name = "changeFontColorItem1"
            Me.changeFontColorItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' changeFontBackColorItem1
            ' 
            Me.changeFontBackColorItem1.Glyph = (DirectCast(resources.GetObject("changeFontBackColorItem1.Glyph"), System.Drawing.Image))
            Me.changeFontBackColorItem1.Id = 22
            Me.changeFontBackColorItem1.LargeGlyph = (DirectCast(resources.GetObject("changeFontBackColorItem1.LargeGlyph"), System.Drawing.Image))
            Me.changeFontBackColorItem1.Name = "changeFontBackColorItem1"
            Me.changeFontBackColorItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontSuperscriptItem1
            ' 
            Me.toggleFontSuperscriptItem1.Glyph = (DirectCast(resources.GetObject("toggleFontSuperscriptItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontSuperscriptItem1.Id = 29
            Me.toggleFontSuperscriptItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontSuperscriptItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1"
            Me.toggleFontSuperscriptItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Default
            ' 
            ' toggleFontSubscriptItem1
            ' 
            Me.toggleFontSubscriptItem1.Glyph = (DirectCast(resources.GetObject("toggleFontSubscriptItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontSubscriptItem1.Id = 30
            Me.toggleFontSubscriptItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontSubscriptItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1"
            Me.toggleFontSubscriptItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Default
            ' 
            ' changeTextCaseItem1
            ' 
            Me.changeTextCaseItem1.Glyph = (DirectCast(resources.GetObject("changeTextCaseItem1.Glyph"), System.Drawing.Image))
            Me.changeTextCaseItem1.Id = 31
            Me.changeTextCaseItem1.LargeGlyph = (DirectCast(resources.GetObject("changeTextCaseItem1.LargeGlyph"), System.Drawing.Image))
            Me.changeTextCaseItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextUpperCaseItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextLowerCaseItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTextCaseItem1) _
            })
            Me.changeTextCaseItem1.Name = "changeTextCaseItem1"
            Me.changeTextCaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Default
            ' 
            ' makeTextUpperCaseItem1
            ' 
            Me.makeTextUpperCaseItem1.Id = 32
            Me.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1"
            ' 
            ' makeTextLowerCaseItem1
            ' 
            Me.makeTextLowerCaseItem1.Id = 33
            Me.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1"
            ' 
            ' toggleTextCaseItem1
            ' 
            Me.toggleTextCaseItem1.Id = 34
            Me.toggleTextCaseItem1.Name = "toggleTextCaseItem1"
            ' 
            ' fontSizeIncreaseItem1
            ' 
            Me.fontSizeIncreaseItem1.Glyph = (DirectCast(resources.GetObject("fontSizeIncreaseItem1.Glyph"), System.Drawing.Image))
            Me.fontSizeIncreaseItem1.Id = 35
            Me.fontSizeIncreaseItem1.LargeGlyph = (DirectCast(resources.GetObject("fontSizeIncreaseItem1.LargeGlyph"), System.Drawing.Image))
            Me.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1"
            Me.fontSizeIncreaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Default
            ' 
            ' fontSizeDecreaseItem1
            ' 
            Me.fontSizeDecreaseItem1.Glyph = (DirectCast(resources.GetObject("fontSizeDecreaseItem1.Glyph"), System.Drawing.Image))
            Me.fontSizeDecreaseItem1.Id = 36
            Me.fontSizeDecreaseItem1.LargeGlyph = (DirectCast(resources.GetObject("fontSizeDecreaseItem1.LargeGlyph"), System.Drawing.Image))
            Me.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1"
            Me.fontSizeDecreaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Default
            ' 
            ' clearFormattingItem1
            ' 
            Me.clearFormattingItem1.Glyph = (DirectCast(resources.GetObject("clearFormattingItem1.Glyph"), System.Drawing.Image))
            Me.clearFormattingItem1.Id = 37
            Me.clearFormattingItem1.LargeGlyph = (DirectCast(resources.GetObject("clearFormattingItem1.LargeGlyph"), System.Drawing.Image))
            Me.clearFormattingItem1.Name = "clearFormattingItem1"
            Me.clearFormattingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' showFontFormItem1
            ' 
            Me.showFontFormItem1.Glyph = (DirectCast(resources.GetObject("showFontFormItem1.Glyph"), System.Drawing.Image))
            Me.showFontFormItem1.Id = 38
            Me.showFontFormItem1.LargeGlyph = (DirectCast(resources.GetObject("showFontFormItem1.LargeGlyph"), System.Drawing.Image))
            Me.showFontFormItem1.Name = "showFontFormItem1"
            Me.showFontFormItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleParagraphAlignmentLeftItem1
            ' 
            Me.toggleParagraphAlignmentLeftItem1.Glyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentLeftItem1.Glyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentLeftItem1.Id = 39
            Me.toggleParagraphAlignmentLeftItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentLeftItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1"
            Me.toggleParagraphAlignmentLeftItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleParagraphAlignmentCenterItem1
            ' 
            Me.toggleParagraphAlignmentCenterItem1.Glyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentCenterItem1.Glyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentCenterItem1.Id = 40
            Me.toggleParagraphAlignmentCenterItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentCenterItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1"
            Me.toggleParagraphAlignmentCenterItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleParagraphAlignmentRightItem1
            ' 
            Me.toggleParagraphAlignmentRightItem1.Glyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentRightItem1.Glyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentRightItem1.Id = 41
            Me.toggleParagraphAlignmentRightItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentRightItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1"
            Me.toggleParagraphAlignmentRightItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleParagraphAlignmentJustifyItem1
            ' 
            Me.toggleParagraphAlignmentJustifyItem1.Glyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentJustifyItem1.Glyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentJustifyItem1.Id = 42
            Me.toggleParagraphAlignmentJustifyItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleParagraphAlignmentJustifyItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1"
            Me.toggleParagraphAlignmentJustifyItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' changeParagraphLineSpacingItem1
            ' 
            Me.changeParagraphLineSpacingItem1.Glyph = (DirectCast(resources.GetObject("changeParagraphLineSpacingItem1.Glyph"), System.Drawing.Image))
            Me.changeParagraphLineSpacingItem1.Id = 43
            Me.changeParagraphLineSpacingItem1.LargeGlyph = (DirectCast(resources.GetObject("changeParagraphLineSpacingItem1.LargeGlyph"), System.Drawing.Image))
            Me.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSingleParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSesquialteralParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setDoubleParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.showLineSpacingFormItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingBeforeParagraphItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingBeforeParagraphItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingAfterParagraphItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingAfterParagraphItem1) _
            })
            Me.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1"
            ' 
            ' setSingleParagraphSpacingItem1
            ' 
            Me.setSingleParagraphSpacingItem1.Id = 44
            Me.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1"
            Me.setSingleParagraphSpacingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' setSesquialteralParagraphSpacingItem1
            ' 
            Me.setSesquialteralParagraphSpacingItem1.Id = 45
            Me.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1"
            Me.setSesquialteralParagraphSpacingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' setDoubleParagraphSpacingItem1
            ' 
            Me.setDoubleParagraphSpacingItem1.Id = 46
            Me.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1"
            Me.setDoubleParagraphSpacingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' showLineSpacingFormItem1
            ' 
            Me.showLineSpacingFormItem1.Id = 47
            Me.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1"
            Me.showLineSpacingFormItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' addSpacingBeforeParagraphItem1
            ' 
            Me.addSpacingBeforeParagraphItem1.Id = 48
            Me.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1"
            Me.addSpacingBeforeParagraphItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' removeSpacingBeforeParagraphItem1
            ' 
            Me.removeSpacingBeforeParagraphItem1.Id = 49
            Me.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1"
            Me.removeSpacingBeforeParagraphItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' addSpacingAfterParagraphItem1
            ' 
            Me.addSpacingAfterParagraphItem1.Id = 50
            Me.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1"
            Me.addSpacingAfterParagraphItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' removeSpacingAfterParagraphItem1
            ' 
            Me.removeSpacingAfterParagraphItem1.Id = 51
            Me.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1"
            Me.removeSpacingAfterParagraphItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleBulletedListItem1
            ' 
            Me.toggleBulletedListItem1.Glyph = (DirectCast(resources.GetObject("toggleBulletedListItem1.Glyph"), System.Drawing.Image))
            Me.toggleBulletedListItem1.Id = 52
            Me.toggleBulletedListItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleBulletedListItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleBulletedListItem1.Name = "toggleBulletedListItem1"
            Me.toggleBulletedListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleNumberingListItem1
            ' 
            Me.toggleNumberingListItem1.Glyph = (DirectCast(resources.GetObject("toggleNumberingListItem1.Glyph"), System.Drawing.Image))
            Me.toggleNumberingListItem1.Id = 53
            Me.toggleNumberingListItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleNumberingListItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleNumberingListItem1.Name = "toggleNumberingListItem1"
            Me.toggleNumberingListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleMultiLevelListItem1
            ' 
            Me.toggleMultiLevelListItem1.Glyph = (DirectCast(resources.GetObject("toggleMultiLevelListItem1.Glyph"), System.Drawing.Image))
            Me.toggleMultiLevelListItem1.Id = 54
            Me.toggleMultiLevelListItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleMultiLevelListItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1"
            Me.toggleMultiLevelListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' decreaseIndentItem1
            ' 
            Me.decreaseIndentItem1.Glyph = (DirectCast(resources.GetObject("decreaseIndentItem1.Glyph"), System.Drawing.Image))
            Me.decreaseIndentItem1.Id = 55
            Me.decreaseIndentItem1.LargeGlyph = (DirectCast(resources.GetObject("decreaseIndentItem1.LargeGlyph"), System.Drawing.Image))
            Me.decreaseIndentItem1.Name = "decreaseIndentItem1"
            Me.decreaseIndentItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' increaseIndentItem1
            ' 
            Me.increaseIndentItem1.Glyph = (DirectCast(resources.GetObject("increaseIndentItem1.Glyph"), System.Drawing.Image))
            Me.increaseIndentItem1.Id = 56
            Me.increaseIndentItem1.LargeGlyph = (DirectCast(resources.GetObject("increaseIndentItem1.LargeGlyph"), System.Drawing.Image))
            Me.increaseIndentItem1.Name = "increaseIndentItem1"
            Me.increaseIndentItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleShowWhitespaceItem1
            ' 
            Me.toggleShowWhitespaceItem1.Glyph = (DirectCast(resources.GetObject("toggleShowWhitespaceItem1.Glyph"), System.Drawing.Image))
            Me.toggleShowWhitespaceItem1.Id = 57
            Me.toggleShowWhitespaceItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleShowWhitespaceItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1"
            Me.toggleShowWhitespaceItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' showParagraphFormItem1
            ' 
            Me.showParagraphFormItem1.Glyph = (DirectCast(resources.GetObject("showParagraphFormItem1.Glyph"), System.Drawing.Image))
            Me.showParagraphFormItem1.Id = 58
            Me.showParagraphFormItem1.LargeGlyph = (DirectCast(resources.GetObject("showParagraphFormItem1.LargeGlyph"), System.Drawing.Image))
            Me.showParagraphFormItem1.Name = "showParagraphFormItem1"
            Me.showParagraphFormItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' changeStyleItem1
            ' 
            Me.changeStyleItem1.Edit = Me.repositoryItemRichEditStyleEdit1
            Me.changeStyleItem1.Id = 59
            Me.changeStyleItem1.Name = "changeStyleItem1"
            Me.changeStyleItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' repositoryItemRichEditStyleEdit1
            ' 
            Me.repositoryItemRichEditStyleEdit1.AutoHeight = False
            Me.repositoryItemRichEditStyleEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
            Me.repositoryItemRichEditStyleEdit1.Control = Me.richEditControl1
            Me.repositoryItemRichEditStyleEdit1.Name = "repositoryItemRichEditStyleEdit1"
            ' 
            ' findItem1
            ' 
            Me.findItem1.Glyph = (DirectCast(resources.GetObject("findItem1.Glyph"), System.Drawing.Image))
            Me.findItem1.Id = 60
            Me.findItem1.LargeGlyph = (DirectCast(resources.GetObject("findItem1.LargeGlyph"), System.Drawing.Image))
            Me.findItem1.Name = "findItem1"
            ' 
            ' replaceItem1
            ' 
            Me.replaceItem1.Glyph = (DirectCast(resources.GetObject("replaceItem1.Glyph"), System.Drawing.Image))
            Me.replaceItem1.Id = 61
            Me.replaceItem1.LargeGlyph = (DirectCast(resources.GetObject("replaceItem1.LargeGlyph"), System.Drawing.Image))
            Me.replaceItem1.Name = "replaceItem1"
            ' 
            ' barButtonGroup1
            ' 
            Me.barButtonGroup1.Caption = "barButtonGroup1"
            Me.barButtonGroup1.Id = 40
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontBoldItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontItalicItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontUnderlineItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontDoubleUnderlineItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontStrikeoutItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontDoubleStrikeoutItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontSubscriptItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.toggleFontSuperscriptItem1)
            Me.barButtonGroup1.Name = "barButtonGroup1"
            ' 
            ' toggleFontBoldItem1
            ' 
            Me.toggleFontBoldItem1.Glyph = (DirectCast(resources.GetObject("toggleFontBoldItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontBoldItem1.Id = 23
            Me.toggleFontBoldItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontBoldItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontBoldItem1.Name = "toggleFontBoldItem1"
            Me.toggleFontBoldItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontItalicItem1
            ' 
            Me.toggleFontItalicItem1.Glyph = (DirectCast(resources.GetObject("toggleFontItalicItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontItalicItem1.Id = 24
            Me.toggleFontItalicItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontItalicItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontItalicItem1.Name = "toggleFontItalicItem1"
            Me.toggleFontItalicItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontUnderlineItem1
            ' 
            Me.toggleFontUnderlineItem1.Glyph = (DirectCast(resources.GetObject("toggleFontUnderlineItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontUnderlineItem1.Id = 25
            Me.toggleFontUnderlineItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontUnderlineItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1"
            Me.toggleFontUnderlineItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontDoubleUnderlineItem1
            ' 
            Me.toggleFontDoubleUnderlineItem1.Glyph = (DirectCast(resources.GetObject("toggleFontDoubleUnderlineItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontDoubleUnderlineItem1.Id = 26
            Me.toggleFontDoubleUnderlineItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontDoubleUnderlineItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1"
            Me.toggleFontDoubleUnderlineItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontStrikeoutItem1
            ' 
            Me.toggleFontStrikeoutItem1.Glyph = (DirectCast(resources.GetObject("toggleFontStrikeoutItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontStrikeoutItem1.Id = 27
            Me.toggleFontStrikeoutItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontStrikeoutItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1"
            Me.toggleFontStrikeoutItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' toggleFontDoubleStrikeoutItem1
            ' 
            Me.toggleFontDoubleStrikeoutItem1.Glyph = (DirectCast(resources.GetObject("toggleFontDoubleStrikeoutItem1.Glyph"), System.Drawing.Image))
            Me.toggleFontDoubleStrikeoutItem1.Id = 28
            Me.toggleFontDoubleStrikeoutItem1.LargeGlyph = (DirectCast(resources.GetObject("toggleFontDoubleStrikeoutItem1.LargeGlyph"), System.Drawing.Image))
            Me.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1"
            Me.toggleFontDoubleStrikeoutItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
            ' 
            ' barButtonGroup2
            ' 
            Me.barButtonGroup2.Caption = "barButtonGroup2"
            Me.barButtonGroup2.Id = 42
            Me.barButtonGroup2.ItemLinks.Add(Me.changeFontColorItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.changeFontBackColorItem1)
            Me.barButtonGroup2.Name = "barButtonGroup2"
            ' 
            ' barButtonGroup3
            ' 
            Me.barButtonGroup3.Caption = "barButtonGroup3"
            Me.barButtonGroup3.Id = 43
            Me.barButtonGroup3.ItemLinks.Add(Me.fontSizeDecreaseItem1)
            Me.barButtonGroup3.ItemLinks.Add(Me.fontSizeIncreaseItem1)
            Me.barButtonGroup3.Name = "barButtonGroup3"
            ' 
            ' barButtonGroup4
            ' 
            Me.barButtonGroup4.Caption = "barButtonGroup4"
            Me.barButtonGroup4.Id = 44
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleBulletedListItem1)
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleNumberingListItem1)
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleMultiLevelListItem1)
            Me.barButtonGroup4.Name = "barButtonGroup4"
            ' 
            ' barButtonGroup5
            ' 
            Me.barButtonGroup5.Caption = "barButtonGroup5"
            Me.barButtonGroup5.Id = 46
            Me.barButtonGroup5.ItemLinks.Add(Me.decreaseIndentItem1)
            Me.barButtonGroup5.ItemLinks.Add(Me.increaseIndentItem1)
            Me.barButtonGroup5.Name = "barButtonGroup5"
            ' 
            ' barButtonGroup6
            ' 
            Me.barButtonGroup6.Caption = "barButtonGroup6"
            Me.barButtonGroup6.Id = 47
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentLeftItem1)
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentCenterItem1)
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentRightItem1)
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentJustifyItem1)
            Me.barButtonGroup6.Name = "barButtonGroup6"
            ' 
            ' barButtonGroup7
            ' 
            Me.barButtonGroup7.Caption = "barButtonGroup7"
            Me.barButtonGroup7.Id = 143
            Me.barButtonGroup7.ItemLinks.Add(Me.clearFormattingItem1)
            Me.barButtonGroup7.Name = "barButtonGroup7"
            ' 
            ' fileRibbonPage1
            ' 
            Me.fileRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.commonRibbonPageGroup1})
            Me.fileRibbonPage1.Name = "fileRibbonPage1"
            ' 
            ' commonRibbonPageGroup1
            ' 
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileNewItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileOpenItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveAsItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.quickPrintItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printPreviewItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.undoItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.redoItem1)
            Me.commonRibbonPageGroup1.Name = "commonRibbonPageGroup1"
            Me.commonRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' homeRibbonPage1
            ' 
            Me.homeRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.clipboardRibbonPageGroup1, Me.fontRibbonPageGroup1, Me.paragraphRibbonPageGroup1, Me.stylesRibbonPageGroup1, Me.editingRibbonPageGroup1})
            Me.homeRibbonPage1.Name = "homeRibbonPage1"
            ' 
            ' clipboardRibbonPageGroup1
            ' 
            Me.clipboardRibbonPageGroup1.AllowMinimize = False
            Me.clipboardRibbonPageGroup1.AllowTextClipping = False
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteItem1)
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.copyItem1)
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.cutItem1)
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteSpecialItem1)
            Me.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1"
            Me.clipboardRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' fontRibbonPageGroup1
            ' 
            Me.fontRibbonPageGroup1.AllowMinimize = False
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.changeFontNameItem1)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.changeFontSizeItem1)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup1)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup2)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup7)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup3)
            Me.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1"
            Me.fontRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' paragraphRibbonPageGroup1
            ' 
            Me.paragraphRibbonPageGroup1.AllowMinimize = False
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup4)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup5)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup6)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.toggleShowWhitespaceItem1, False, "", "", True)
            Me.paragraphRibbonPageGroup1.Name = "paragraphRibbonPageGroup1"
            Me.paragraphRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' stylesRibbonPageGroup1
            ' 
            Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.changeStyleItem1)
            Me.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1"
            Me.stylesRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' editingRibbonPageGroup1
            ' 
            Me.editingRibbonPageGroup1.ItemLinks.Add(Me.findItem1)
            Me.editingRibbonPageGroup1.ItemLinks.Add(Me.replaceItem1)
            Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
            Me.editingRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' richEditBarController1
            ' 
            Me.richEditBarController1.BarItems.Add(Me.fileNewItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileOpenItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileSaveItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileSaveAsItem1)
            Me.richEditBarController1.BarItems.Add(Me.quickPrintItem1)
            Me.richEditBarController1.BarItems.Add(Me.printItem1)
            Me.richEditBarController1.BarItems.Add(Me.printPreviewItem1)
            Me.richEditBarController1.BarItems.Add(Me.undoItem1)
            Me.richEditBarController1.BarItems.Add(Me.redoItem1)
            Me.richEditBarController1.BarItems.Add(Me.cutItem1)
            Me.richEditBarController1.BarItems.Add(Me.copyItem1)
            Me.richEditBarController1.BarItems.Add(Me.pasteItem1)
            Me.richEditBarController1.BarItems.Add(Me.pasteSpecialItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontNameItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontSizeItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontBackColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontSuperscriptItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontSubscriptItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeTextCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.makeTextUpperCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.makeTextLowerCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleTextCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.fontSizeIncreaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.fontSizeDecreaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.clearFormattingItem1)
            Me.richEditBarController1.BarItems.Add(Me.showFontFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentLeftItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentCenterItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentRightItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentJustifyItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeParagraphLineSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSingleParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSesquialteralParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setDoubleParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.showLineSpacingFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.addSpacingBeforeParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.removeSpacingBeforeParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.addSpacingAfterParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.removeSpacingAfterParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleBulletedListItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleNumberingListItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleMultiLevelListItem1)
            Me.richEditBarController1.BarItems.Add(Me.decreaseIndentItem1)
            Me.richEditBarController1.BarItems.Add(Me.increaseIndentItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleShowWhitespaceItem1)
            Me.richEditBarController1.BarItems.Add(Me.showParagraphFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeStyleItem1)
            Me.richEditBarController1.BarItems.Add(Me.findItem1)
            Me.richEditBarController1.BarItems.Add(Me.replaceItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageBreakItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertTableItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPictureItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertBookmarkItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertHyperlinkItem1)
            Me.richEditBarController1.BarItems.Add(Me.editPageHeaderItem1)
            Me.richEditBarController1.BarItems.Add(Me.editPageFooterItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageNumberItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageCountItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertSymbolItem1)
            Me.richEditBarController1.RichEditControl = Me.richEditControl1
            ' 
            ' pagesRibbonPageGroup1
            ' 
            Me.pagesRibbonPageGroup1.ItemLinks.Add(Me.insertPageBreakItem1)
            Me.pagesRibbonPageGroup1.Name = "pagesRibbonPageGroup1"
            Me.pagesRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' insertRibbonPage1
            ' 
            Me.insertRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.pagesRibbonPageGroup1, Me.tablesRibbonPageGroup1, Me.illustrationsRibbonPageGroup1, Me.linksRibbonPageGroup1, Me.headerFooterRibbonPageGroup1, Me.symbolsRibbonPageGroup1})
            Me.insertRibbonPage1.Name = "insertRibbonPage1"
            ' 
            ' insertPageBreakItem1
            ' 
            Me.insertPageBreakItem1.Glyph = (DirectCast(resources.GetObject("insertPageBreakItem1.Glyph"), System.Drawing.Image))
            Me.insertPageBreakItem1.Id = 74
            Me.insertPageBreakItem1.LargeGlyph = (DirectCast(resources.GetObject("insertPageBreakItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertPageBreakItem1.Name = "insertPageBreakItem1"
            ' 
            ' tablesRibbonPageGroup1
            ' 
            Me.tablesRibbonPageGroup1.ItemLinks.Add(Me.insertTableItem1)
            Me.tablesRibbonPageGroup1.Name = "tablesRibbonPageGroup1"
            Me.tablesRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' insertTableItem1
            ' 
            Me.insertTableItem1.Glyph = (DirectCast(resources.GetObject("insertTableItem1.Glyph"), System.Drawing.Image))
            Me.insertTableItem1.Id = 75
            Me.insertTableItem1.LargeGlyph = (DirectCast(resources.GetObject("insertTableItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertTableItem1.Name = "insertTableItem1"
            ' 
            ' illustrationsRibbonPageGroup1
            ' 
            Me.illustrationsRibbonPageGroup1.ItemLinks.Add(Me.insertPictureItem1)
            Me.illustrationsRibbonPageGroup1.Name = "illustrationsRibbonPageGroup1"
            Me.illustrationsRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' insertPictureItem1
            ' 
            Me.insertPictureItem1.Glyph = (DirectCast(resources.GetObject("insertPictureItem1.Glyph"), System.Drawing.Image))
            Me.insertPictureItem1.Id = 76
            Me.insertPictureItem1.LargeGlyph = (DirectCast(resources.GetObject("insertPictureItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertPictureItem1.Name = "insertPictureItem1"
            ' 
            ' linksRibbonPageGroup1
            ' 
            Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertBookmarkItem1)
            Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertHyperlinkItem1)
            Me.linksRibbonPageGroup1.Name = "linksRibbonPageGroup1"
            Me.linksRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' insertBookmarkItem1
            ' 
            Me.insertBookmarkItem1.Glyph = (DirectCast(resources.GetObject("insertBookmarkItem1.Glyph"), System.Drawing.Image))
            Me.insertBookmarkItem1.Id = 77
            Me.insertBookmarkItem1.LargeGlyph = (DirectCast(resources.GetObject("insertBookmarkItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertBookmarkItem1.Name = "insertBookmarkItem1"
            ' 
            ' insertHyperlinkItem1
            ' 
            Me.insertHyperlinkItem1.Glyph = (DirectCast(resources.GetObject("insertHyperlinkItem1.Glyph"), System.Drawing.Image))
            Me.insertHyperlinkItem1.Id = 78
            Me.insertHyperlinkItem1.LargeGlyph = (DirectCast(resources.GetObject("insertHyperlinkItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertHyperlinkItem1.Name = "insertHyperlinkItem1"
            ' 
            ' headerFooterRibbonPageGroup1
            ' 
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageHeaderItem1)
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageFooterItem1)
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageNumberItem1)
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageCountItem1)
            Me.headerFooterRibbonPageGroup1.Name = "headerFooterRibbonPageGroup1"
            Me.headerFooterRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' editPageHeaderItem1
            ' 
            Me.editPageHeaderItem1.Glyph = (DirectCast(resources.GetObject("editPageHeaderItem1.Glyph"), System.Drawing.Image))
            Me.editPageHeaderItem1.Id = 79
            Me.editPageHeaderItem1.LargeGlyph = (DirectCast(resources.GetObject("editPageHeaderItem1.LargeGlyph"), System.Drawing.Image))
            Me.editPageHeaderItem1.Name = "editPageHeaderItem1"
            ' 
            ' editPageFooterItem1
            ' 
            Me.editPageFooterItem1.Glyph = (DirectCast(resources.GetObject("editPageFooterItem1.Glyph"), System.Drawing.Image))
            Me.editPageFooterItem1.Id = 80
            Me.editPageFooterItem1.LargeGlyph = (DirectCast(resources.GetObject("editPageFooterItem1.LargeGlyph"), System.Drawing.Image))
            Me.editPageFooterItem1.Name = "editPageFooterItem1"
            ' 
            ' insertPageNumberItem1
            ' 
            Me.insertPageNumberItem1.Glyph = (DirectCast(resources.GetObject("insertPageNumberItem1.Glyph"), System.Drawing.Image))
            Me.insertPageNumberItem1.Id = 81
            Me.insertPageNumberItem1.LargeGlyph = (DirectCast(resources.GetObject("insertPageNumberItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertPageNumberItem1.Name = "insertPageNumberItem1"
            ' 
            ' insertPageCountItem1
            ' 
            Me.insertPageCountItem1.Glyph = (DirectCast(resources.GetObject("insertPageCountItem1.Glyph"), System.Drawing.Image))
            Me.insertPageCountItem1.Id = 82
            Me.insertPageCountItem1.LargeGlyph = (DirectCast(resources.GetObject("insertPageCountItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertPageCountItem1.Name = "insertPageCountItem1"
            ' 
            ' symbolsRibbonPageGroup1
            ' 
            Me.symbolsRibbonPageGroup1.ItemLinks.Add(Me.insertSymbolItem1)
            Me.symbolsRibbonPageGroup1.Name = "symbolsRibbonPageGroup1"
            Me.symbolsRibbonPageGroup1.RichEditControl = Me.richEditControl1
            ' 
            ' insertSymbolItem1
            ' 
            Me.insertSymbolItem1.Glyph = (DirectCast(resources.GetObject("insertSymbolItem1.Glyph"), System.Drawing.Image))
            Me.insertSymbolItem1.Id = 83
            Me.insertSymbolItem1.LargeGlyph = (DirectCast(resources.GetObject("insertSymbolItem1.LargeGlyph"), System.Drawing.Image))
            Me.insertSymbolItem1.Name = "insertSymbolItem1"
            ' 
            ' Form1
            ' 
            Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
            Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
            Me.ClientSize = New System.Drawing.Size(784, 562)
            Me.Controls.Add(Me.richEditControl1)
            Me.Controls.Add(Me.ribbonControl1)
            Me.Name = "Form1"
            Me.Text = "Form1"
            DirectCast(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.repositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
            Me.ResumeLayout(False)

        End Sub

        #End Region

        Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
        Private ribbonControl1 As DevExpress.XtraBars.Ribbon.RibbonControl
        Private fileNewItem1 As DevExpress.XtraRichEdit.UI.FileNewItem
        Private fileOpenItem1 As DevExpress.XtraRichEdit.UI.FileOpenItem
        Private fileSaveItem1 As DevExpress.XtraRichEdit.UI.FileSaveItem
        Private fileSaveAsItem1 As DevExpress.XtraRichEdit.UI.FileSaveAsItem
        Private quickPrintItem1 As DevExpress.XtraRichEdit.UI.QuickPrintItem
        Private printItem1 As DevExpress.XtraRichEdit.UI.PrintItem
        Private printPreviewItem1 As DevExpress.XtraRichEdit.UI.PrintPreviewItem
        Private undoItem1 As DevExpress.XtraRichEdit.UI.UndoItem
        Private redoItem1 As DevExpress.XtraRichEdit.UI.RedoItem
        Private cutItem1 As DevExpress.XtraRichEdit.UI.CutItem
        Private copyItem1 As DevExpress.XtraRichEdit.UI.CopyItem
        Private pasteItem1 As DevExpress.XtraRichEdit.UI.PasteItem
        Private pasteSpecialItem1 As DevExpress.XtraRichEdit.UI.PasteSpecialItem
        Private changeFontNameItem1 As DevExpress.XtraRichEdit.UI.ChangeFontNameItem
        Private repositoryItemFontEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemFontEdit
        Private changeFontSizeItem1 As DevExpress.XtraRichEdit.UI.ChangeFontSizeItem
        Private repositoryItemRichEditFontSizeEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit
        Private changeFontColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontColorItem
        Private changeFontBackColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem
        Private toggleFontSuperscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem
        Private toggleFontSubscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem
        Private changeTextCaseItem1 As DevExpress.XtraRichEdit.UI.ChangeTextCaseItem
        Private makeTextUpperCaseItem1 As DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem
        Private makeTextLowerCaseItem1 As DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem
        Private toggleTextCaseItem1 As DevExpress.XtraRichEdit.UI.ToggleTextCaseItem
        Private fontSizeIncreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem
        Private fontSizeDecreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem
        Private clearFormattingItem1 As DevExpress.XtraRichEdit.UI.ClearFormattingItem
        Private showFontFormItem1 As DevExpress.XtraRichEdit.UI.ShowFontFormItem
        Private toggleParagraphAlignmentLeftItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem
        Private toggleParagraphAlignmentCenterItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem
        Private toggleParagraphAlignmentRightItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem
        Private toggleParagraphAlignmentJustifyItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem
        Private changeParagraphLineSpacingItem1 As DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem
        Private setSingleParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem
        Private setSesquialteralParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem
        Private setDoubleParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem
        Private showLineSpacingFormItem1 As DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem
        Private addSpacingBeforeParagraphItem1 As DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem
        Private removeSpacingBeforeParagraphItem1 As DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem
        Private addSpacingAfterParagraphItem1 As DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem
        Private removeSpacingAfterParagraphItem1 As DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem
        Private toggleBulletedListItem1 As DevExpress.XtraRichEdit.UI.ToggleBulletedListItem
        Private toggleNumberingListItem1 As DevExpress.XtraRichEdit.UI.ToggleNumberingListItem
        Private toggleMultiLevelListItem1 As DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem
        Private decreaseIndentItem1 As DevExpress.XtraRichEdit.UI.DecreaseIndentItem
        Private increaseIndentItem1 As DevExpress.XtraRichEdit.UI.IncreaseIndentItem
        Private toggleShowWhitespaceItem1 As DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem
        Private showParagraphFormItem1 As DevExpress.XtraRichEdit.UI.ShowParagraphFormItem
        Private changeStyleItem1 As DevExpress.XtraRichEdit.UI.ChangeStyleItem
        Private repositoryItemRichEditStyleEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditStyleEdit
        Private findItem1 As DevExpress.XtraRichEdit.UI.FindItem
        Private replaceItem1 As DevExpress.XtraRichEdit.UI.ReplaceItem
        Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
        Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
        Private homeRibbonPage1 As DevExpress.XtraRichEdit.UI.HomeRibbonPage
        Private clipboardRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup
        Private fontRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.FontRibbonPageGroup
        Private paragraphRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup
        Private stylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup
        Private editingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup
        Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
        Private barButtonGroup1 As DevExpress.XtraBars.BarButtonGroup
        'private DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup stylesRibbonPageGroup1;
        Private barButtonGroup2 As DevExpress.XtraBars.BarButtonGroup
        Private barButtonGroup3 As DevExpress.XtraBars.BarButtonGroup
        Private barButtonGroup4 As DevExpress.XtraBars.BarButtonGroup
        Private barButtonGroup5 As DevExpress.XtraBars.BarButtonGroup
        Private barButtonGroup6 As DevExpress.XtraBars.BarButtonGroup
        Private barButtonGroup7 As DevExpress.XtraBars.BarButtonGroup
        Private toggleFontBoldItem1 As DevExpress.XtraRichEdit.UI.ToggleFontBoldItem
        Private toggleFontItalicItem1 As DevExpress.XtraRichEdit.UI.ToggleFontItalicItem
        Private toggleFontUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem
        Private toggleFontDoubleUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem
        Private toggleFontStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem
        Private toggleFontDoubleStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem
        Private insertPageBreakItem1 As DevExpress.XtraRichEdit.UI.InsertPageBreakItem
        Private insertTableItem1 As DevExpress.XtraRichEdit.UI.InsertTableItem
        Private insertPictureItem1 As DevExpress.XtraRichEdit.UI.InsertPictureItem
        Private insertBookmarkItem1 As DevExpress.XtraRichEdit.UI.InsertBookmarkItem
        Private insertHyperlinkItem1 As DevExpress.XtraRichEdit.UI.InsertHyperlinkItem
        Private editPageHeaderItem1 As DevExpress.XtraRichEdit.UI.EditPageHeaderItem
        Private editPageFooterItem1 As DevExpress.XtraRichEdit.UI.EditPageFooterItem
        Private insertPageNumberItem1 As DevExpress.XtraRichEdit.UI.InsertPageNumberItem
        Private insertPageCountItem1 As DevExpress.XtraRichEdit.UI.InsertPageCountItem
        Private insertSymbolItem1 As DevExpress.XtraRichEdit.UI.InsertSymbolItem
        Private insertRibbonPage1 As DevExpress.XtraRichEdit.UI.InsertRibbonPage
        Private pagesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup
        Private tablesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup
        Private illustrationsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup
        Private linksRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup
        Private headerFooterRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup
        Private symbolsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup
    End Class
End Namespace

