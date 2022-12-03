Namespace PageLayout
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
            Me.components = New System.ComponentModel.Container()
            Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
            Dim galleryItemGroup1 As New DevExpress.XtraBars.Ribbon.GalleryItemGroup()
            Dim reduceOperation1 As New DevExpress.XtraBars.Ribbon.ReduceOperation()
            Me.stylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup()
            Me.galleryChangeStyleItem1 = New DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem()
            Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
            Me.ribbonControl1 = New DevExpress.XtraBars.Ribbon.RibbonControl()
            Me.undoItem1 = New DevExpress.XtraRichEdit.UI.UndoItem()
            Me.redoItem1 = New DevExpress.XtraRichEdit.UI.RedoItem()
            Me.fileNewItem1 = New DevExpress.XtraRichEdit.UI.FileNewItem()
            Me.fileOpenItem1 = New DevExpress.XtraRichEdit.UI.FileOpenItem()
            Me.fileSaveItem1 = New DevExpress.XtraRichEdit.UI.FileSaveItem()
            Me.fileSaveAsItem1 = New DevExpress.XtraRichEdit.UI.FileSaveAsItem()
            Me.quickPrintItem1 = New DevExpress.XtraRichEdit.UI.QuickPrintItem()
            Me.printItem1 = New DevExpress.XtraRichEdit.UI.PrintItem()
            Me.printPreviewItem1 = New DevExpress.XtraRichEdit.UI.PrintPreviewItem()
            Me.showDocumentPropertiesFormItem1 = New DevExpress.XtraRichEdit.UI.ShowDocumentPropertiesFormItem()
            Me.insertPageBreakItem21 = New DevExpress.XtraRichEdit.UI.InsertPageBreakItem2()
            Me.insertTableItem1 = New DevExpress.XtraRichEdit.UI.InsertTableItem()
            Me.insertPictureItem1 = New DevExpress.XtraRichEdit.UI.InsertPictureItem()
            Me.insertFloatingPictureItem1 = New DevExpress.XtraRichEdit.UI.InsertFloatingPictureItem()
            Me.insertBookmarkItem1 = New DevExpress.XtraRichEdit.UI.InsertBookmarkItem()
            Me.insertHyperlinkItem1 = New DevExpress.XtraRichEdit.UI.InsertHyperlinkItem()
            Me.editPageHeaderItem1 = New DevExpress.XtraRichEdit.UI.EditPageHeaderItem()
            Me.editPageFooterItem1 = New DevExpress.XtraRichEdit.UI.EditPageFooterItem()
            Me.insertPageNumberItem1 = New DevExpress.XtraRichEdit.UI.InsertPageNumberItem()
            Me.insertPageCountItem1 = New DevExpress.XtraRichEdit.UI.InsertPageCountItem()
            Me.insertTextBoxItem1 = New DevExpress.XtraRichEdit.UI.InsertTextBoxItem()
            Me.insertSymbolItem1 = New DevExpress.XtraRichEdit.UI.InsertSymbolItem()
            Me.changeSectionPageMarginsItem1 = New DevExpress.XtraRichEdit.UI.ChangeSectionPageMarginsItem()
            Me.setNormalSectionPageMarginsItem1 = New DevExpress.XtraRichEdit.UI.SetNormalSectionPageMarginsItem()
            Me.setNarrowSectionPageMarginsItem1 = New DevExpress.XtraRichEdit.UI.SetNarrowSectionPageMarginsItem()
            Me.setModerateSectionPageMarginsItem1 = New DevExpress.XtraRichEdit.UI.SetModerateSectionPageMarginsItem()
            Me.setWideSectionPageMarginsItem1 = New DevExpress.XtraRichEdit.UI.SetWideSectionPageMarginsItem()
            Me.showPageMarginsSetupFormItem1 = New DevExpress.XtraRichEdit.UI.ShowPageMarginsSetupFormItem()
            Me.changeSectionPageOrientationItem1 = New DevExpress.XtraRichEdit.UI.ChangeSectionPageOrientationItem()
            Me.setPortraitPageOrientationItem1 = New DevExpress.XtraRichEdit.UI.SetPortraitPageOrientationItem()
            Me.setLandscapePageOrientationItem1 = New DevExpress.XtraRichEdit.UI.SetLandscapePageOrientationItem()
            Me.changeSectionPaperKindItem1 = New DevExpress.XtraRichEdit.UI.ChangeSectionPaperKindItem()
            Me.changeSectionColumnsItem1 = New DevExpress.XtraRichEdit.UI.ChangeSectionColumnsItem()
            Me.setSectionOneColumnItem1 = New DevExpress.XtraRichEdit.UI.SetSectionOneColumnItem()
            Me.setSectionTwoColumnsItem1 = New DevExpress.XtraRichEdit.UI.SetSectionTwoColumnsItem()
            Me.setSectionThreeColumnsItem1 = New DevExpress.XtraRichEdit.UI.SetSectionThreeColumnsItem()
            Me.showColumnsSetupFormItem1 = New DevExpress.XtraRichEdit.UI.ShowColumnsSetupFormItem()
            Me.insertBreakItem1 = New DevExpress.XtraRichEdit.UI.InsertBreakItem()
            Me.insertPageBreakItem1 = New DevExpress.XtraRichEdit.UI.InsertPageBreakItem()
            Me.insertColumnBreakItem1 = New DevExpress.XtraRichEdit.UI.InsertColumnBreakItem()
            Me.insertSectionBreakNextPageItem1 = New DevExpress.XtraRichEdit.UI.InsertSectionBreakNextPageItem()
            Me.insertSectionBreakEvenPageItem1 = New DevExpress.XtraRichEdit.UI.InsertSectionBreakEvenPageItem()
            Me.insertSectionBreakOddPageItem1 = New DevExpress.XtraRichEdit.UI.InsertSectionBreakOddPageItem()
            Me.changeSectionLineNumberingItem1 = New DevExpress.XtraRichEdit.UI.ChangeSectionLineNumberingItem()
            Me.setSectionLineNumberingNoneItem1 = New DevExpress.XtraRichEdit.UI.SetSectionLineNumberingNoneItem()
            Me.setSectionLineNumberingContinuousItem1 = New DevExpress.XtraRichEdit.UI.SetSectionLineNumberingContinuousItem()
            Me.setSectionLineNumberingRestartNewPageItem1 = New DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewPageItem()
            Me.setSectionLineNumberingRestartNewSectionItem1 = New DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewSectionItem()
            Me.toggleParagraphSuppressLineNumbersItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphSuppressLineNumbersItem()
            Me.showLineNumberingFormItem1 = New DevExpress.XtraRichEdit.UI.ShowLineNumberingFormItem()
            Me.changePageColorItem1 = New DevExpress.XtraRichEdit.UI.ChangePageColorItem()
            Me.pasteItem1 = New DevExpress.XtraRichEdit.UI.PasteItem()
            Me.cutItem1 = New DevExpress.XtraRichEdit.UI.CutItem()
            Me.copyItem1 = New DevExpress.XtraRichEdit.UI.CopyItem()
            Me.pasteSpecialItem1 = New DevExpress.XtraRichEdit.UI.PasteSpecialItem()
            Me.barButtonGroup1 = New DevExpress.XtraBars.BarButtonGroup()
            Me.changeFontNameItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontNameItem()
            Me.repositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
            Me.changeFontSizeItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontSizeItem()
            Me.repositoryItemRichEditFontSizeEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit()
            Me.fontSizeIncreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem()
            Me.fontSizeDecreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem()
            Me.barButtonGroup2 = New DevExpress.XtraBars.BarButtonGroup()
            Me.toggleFontBoldItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontBoldItem()
            Me.toggleFontItalicItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontItalicItem()
            Me.toggleFontUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem()
            Me.toggleFontDoubleUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem()
            Me.toggleFontStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem()
            Me.toggleFontDoubleStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem()
            Me.toggleFontSuperscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem()
            Me.toggleFontSubscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem()
            Me.barButtonGroup3 = New DevExpress.XtraBars.BarButtonGroup()
            Me.changeFontColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontColorItem()
            Me.changeFontHighlightColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontHighlightColorItem()
            Me.changeTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ChangeTextCaseItem()
            Me.makeTextUpperCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem()
            Me.makeTextLowerCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem()
            Me.capitalizeEachWordCaseItem1 = New DevExpress.XtraRichEdit.UI.CapitalizeEachWordCaseItem()
            Me.toggleTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ToggleTextCaseItem()
            Me.clearFormattingItem1 = New DevExpress.XtraRichEdit.UI.ClearFormattingItem()
            Me.barButtonGroup4 = New DevExpress.XtraBars.BarButtonGroup()
            Me.toggleBulletedListItem1 = New DevExpress.XtraRichEdit.UI.ToggleBulletedListItem()
            Me.toggleNumberingListItem1 = New DevExpress.XtraRichEdit.UI.ToggleNumberingListItem()
            Me.toggleMultiLevelListItem1 = New DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem()
            Me.barButtonGroup5 = New DevExpress.XtraBars.BarButtonGroup()
            Me.decreaseIndentItem1 = New DevExpress.XtraRichEdit.UI.DecreaseIndentItem()
            Me.increaseIndentItem1 = New DevExpress.XtraRichEdit.UI.IncreaseIndentItem()
            Me.toggleShowWhitespaceItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem()
            Me.barButtonGroup6 = New DevExpress.XtraBars.BarButtonGroup()
            Me.toggleParagraphAlignmentLeftItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem()
            Me.toggleParagraphAlignmentCenterItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem()
            Me.toggleParagraphAlignmentRightItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem()
            Me.toggleParagraphAlignmentJustifyItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem()
            Me.barButtonGroup7 = New DevExpress.XtraBars.BarButtonGroup()
            Me.changeParagraphLineSpacingItem1 = New DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem()
            Me.setSingleParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem()
            Me.setSesquialteralParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem()
            Me.setDoubleParagraphSpacingItem1 = New DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem()
            Me.showLineSpacingFormItem1 = New DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem()
            Me.addSpacingBeforeParagraphItem1 = New DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem()
            Me.removeSpacingBeforeParagraphItem1 = New DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem()
            Me.addSpacingAfterParagraphItem1 = New DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem()
            Me.removeSpacingAfterParagraphItem1 = New DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem()
            Me.changeParagraphBackColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeParagraphBackColorItem()
            Me.findItem1 = New DevExpress.XtraRichEdit.UI.FindItem()
            Me.replaceItem1 = New DevExpress.XtraRichEdit.UI.ReplaceItem()
            Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
            Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
            Me.infoRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.InfoRibbonPageGroup()
            Me.homeRibbonPage1 = New DevExpress.XtraRichEdit.UI.HomeRibbonPage()
            Me.clipboardRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup()
            Me.fontRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.FontRibbonPageGroup()
            Me.paragraphRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup()
            Me.editingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup()
            Me.insertRibbonPage1 = New DevExpress.XtraRichEdit.UI.InsertRibbonPage()
            Me.pagesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup()
            Me.tablesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup()
            Me.illustrationsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup()
            Me.linksRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup()
            Me.headerFooterRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup()
            Me.textRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TextRibbonPageGroup()
            Me.symbolsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup()
            Me.pageLayoutRibbonPage1 = New DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage()
            Me.pageSetupRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup()
            Me.pageBackgroundRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup()
            Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
            Me.defaultLookAndFeel1 = New DevExpress.LookAndFeel.DefaultLookAndFeel(Me.components)
            CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
            CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
            CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
            CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
            Me.SuspendLayout()
            ' 
            ' stylesRibbonPageGroup1
            ' 
            Me.stylesRibbonPageGroup1.ImageOptions.Image = (CType(resources.GetObject("stylesRibbonPageGroup1.ImageOptions.Image"), System.Drawing.Image))
            Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.galleryChangeStyleItem1)
            Me.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1"
            ' 
            ' galleryChangeStyleItem1
            ' 
            ' 
            ' 
            ' 
            Me.galleryChangeStyleItem1.Gallery.ColumnCount = 10
            Me.galleryChangeStyleItem1.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { galleryItemGroup1})
            Me.galleryChangeStyleItem1.Gallery.ImageSize = New System.Drawing.Size(65, 46)
            Me.galleryChangeStyleItem1.Id = 103
            Me.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1"
            ' 
            ' richEditControl1
            ' 
            Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
            Me.richEditControl1.Location = New System.Drawing.Point(0, 146)
            Me.richEditControl1.MenuManager = Me.ribbonControl1
            Me.richEditControl1.Name = "richEditControl1"
            Me.richEditControl1.Size = New System.Drawing.Size(610, 288)
            Me.richEditControl1.TabIndex = 0
            ' 
            ' ribbonControl1
            ' 
            Me.ribbonControl1.ExpandCollapseItem.Id = 0
            Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.undoItem1, Me.redoItem1, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.showDocumentPropertiesFormItem1, Me.insertPageBreakItem21, Me.insertTableItem1, Me.insertPictureItem1, Me.insertFloatingPictureItem1, Me.insertBookmarkItem1, Me.insertHyperlinkItem1, Me.editPageHeaderItem1, Me.editPageFooterItem1, Me.insertPageNumberItem1, Me.insertPageCountItem1, Me.insertTextBoxItem1, Me.insertSymbolItem1, Me.changeSectionPageMarginsItem1, Me.setNormalSectionPageMarginsItem1, Me.setNarrowSectionPageMarginsItem1, Me.setModerateSectionPageMarginsItem1, Me.setWideSectionPageMarginsItem1, Me.showPageMarginsSetupFormItem1, Me.changeSectionPageOrientationItem1, Me.setPortraitPageOrientationItem1, Me.setLandscapePageOrientationItem1, Me.changeSectionPaperKindItem1, Me.changeSectionColumnsItem1, Me.setSectionOneColumnItem1, Me.setSectionTwoColumnsItem1, Me.setSectionThreeColumnsItem1, Me.showColumnsSetupFormItem1, Me.insertBreakItem1, Me.insertPageBreakItem1, Me.insertColumnBreakItem1, Me.insertSectionBreakNextPageItem1, Me.insertSectionBreakEvenPageItem1, Me.insertSectionBreakOddPageItem1, Me.changeSectionLineNumberingItem1, Me.setSectionLineNumberingNoneItem1, Me.setSectionLineNumberingContinuousItem1, Me.setSectionLineNumberingRestartNewPageItem1, Me.setSectionLineNumberingRestartNewSectionItem1, Me.toggleParagraphSuppressLineNumbersItem1, Me.showLineNumberingFormItem1, Me.changePageColorItem1, Me.pasteItem1, Me.cutItem1, Me.copyItem1, Me.pasteSpecialItem1, Me.barButtonGroup1, Me.changeFontNameItem1, Me.changeFontSizeItem1, Me.fontSizeIncreaseItem1, Me.fontSizeDecreaseItem1, Me.barButtonGroup2, Me.toggleFontBoldItem1, Me.toggleFontItalicItem1, Me.toggleFontUnderlineItem1, Me.toggleFontDoubleUnderlineItem1, Me.toggleFontStrikeoutItem1, Me.toggleFontDoubleStrikeoutItem1, Me.toggleFontSuperscriptItem1, Me.toggleFontSubscriptItem1, Me.barButtonGroup3, Me.changeFontColorItem1, Me.changeFontHighlightColorItem1, Me.changeTextCaseItem1, Me.makeTextUpperCaseItem1, Me.makeTextLowerCaseItem1, Me.capitalizeEachWordCaseItem1, Me.toggleTextCaseItem1, Me.clearFormattingItem1, Me.barButtonGroup4, Me.toggleBulletedListItem1, Me.toggleNumberingListItem1, Me.toggleMultiLevelListItem1, Me.barButtonGroup5, Me.decreaseIndentItem1, Me.increaseIndentItem1, Me.barButtonGroup6, Me.toggleParagraphAlignmentLeftItem1, Me.toggleParagraphAlignmentCenterItem1, Me.toggleParagraphAlignmentRightItem1, Me.toggleParagraphAlignmentJustifyItem1, Me.toggleShowWhitespaceItem1, Me.barButtonGroup7, Me.changeParagraphLineSpacingItem1, Me.setSingleParagraphSpacingItem1, Me.setSesquialteralParagraphSpacingItem1, Me.setDoubleParagraphSpacingItem1, Me.showLineSpacingFormItem1, Me.addSpacingBeforeParagraphItem1, Me.removeSpacingBeforeParagraphItem1, Me.addSpacingAfterParagraphItem1, Me.removeSpacingAfterParagraphItem1, Me.changeParagraphBackColorItem1, Me.galleryChangeStyleItem1, Me.findItem1, Me.replaceItem1})
            Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
            Me.ribbonControl1.MaxItemId = 106
            Me.ribbonControl1.Name = "ribbonControl1"
            Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1, Me.homeRibbonPage1, Me.insertRibbonPage1, Me.pageLayoutRibbonPage1})
            Me.ribbonControl1.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() { Me.repositoryItemFontEdit1, Me.repositoryItemRichEditFontSizeEdit1})
            Me.ribbonControl1.Size = New System.Drawing.Size(610, 146)
            ' 
            ' undoItem1
            ' 
            Me.undoItem1.Id = 1
            Me.undoItem1.Name = "undoItem1"
            ' 
            ' redoItem1
            ' 
            Me.redoItem1.Id = 2
            Me.redoItem1.Name = "redoItem1"
            ' 
            ' fileNewItem1
            ' 
            Me.fileNewItem1.Id = 3
            Me.fileNewItem1.Name = "fileNewItem1"
            ' 
            ' fileOpenItem1
            ' 
            Me.fileOpenItem1.Id = 4
            Me.fileOpenItem1.Name = "fileOpenItem1"
            ' 
            ' fileSaveItem1
            ' 
            Me.fileSaveItem1.Id = 5
            Me.fileSaveItem1.Name = "fileSaveItem1"
            ' 
            ' fileSaveAsItem1
            ' 
            Me.fileSaveAsItem1.Id = 6
            Me.fileSaveAsItem1.Name = "fileSaveAsItem1"
            ' 
            ' quickPrintItem1
            ' 
            Me.quickPrintItem1.Id = 7
            Me.quickPrintItem1.Name = "quickPrintItem1"
            ' 
            ' printItem1
            ' 
            Me.printItem1.Id = 8
            Me.printItem1.Name = "printItem1"
            ' 
            ' printPreviewItem1
            ' 
            Me.printPreviewItem1.Id = 9
            Me.printPreviewItem1.Name = "printPreviewItem1"
            ' 
            ' showDocumentPropertiesFormItem1
            ' 
            Me.showDocumentPropertiesFormItem1.Id = 10
            Me.showDocumentPropertiesFormItem1.Name = "showDocumentPropertiesFormItem1"
            ' 
            ' insertPageBreakItem21
            ' 
            Me.insertPageBreakItem21.Id = 11
            Me.insertPageBreakItem21.Name = "insertPageBreakItem21"
            ' 
            ' insertTableItem1
            ' 
            Me.insertTableItem1.Id = 12
            Me.insertTableItem1.Name = "insertTableItem1"
            ' 
            ' insertPictureItem1
            ' 
            Me.insertPictureItem1.Id = 13
            Me.insertPictureItem1.Name = "insertPictureItem1"
            ' 
            ' insertFloatingPictureItem1
            ' 
            Me.insertFloatingPictureItem1.Id = 14
            Me.insertFloatingPictureItem1.Name = "insertFloatingPictureItem1"
            ' 
            ' insertBookmarkItem1
            ' 
            Me.insertBookmarkItem1.Id = 15
            Me.insertBookmarkItem1.Name = "insertBookmarkItem1"
            ' 
            ' insertHyperlinkItem1
            ' 
            Me.insertHyperlinkItem1.Id = 16
            Me.insertHyperlinkItem1.Name = "insertHyperlinkItem1"
            ' 
            ' editPageHeaderItem1
            ' 
            Me.editPageHeaderItem1.Id = 17
            Me.editPageHeaderItem1.Name = "editPageHeaderItem1"
            ' 
            ' editPageFooterItem1
            ' 
            Me.editPageFooterItem1.Id = 18
            Me.editPageFooterItem1.Name = "editPageFooterItem1"
            ' 
            ' insertPageNumberItem1
            ' 
            Me.insertPageNumberItem1.Id = 19
            Me.insertPageNumberItem1.Name = "insertPageNumberItem1"
            ' 
            ' insertPageCountItem1
            ' 
            Me.insertPageCountItem1.Id = 20
            Me.insertPageCountItem1.Name = "insertPageCountItem1"
            ' 
            ' insertTextBoxItem1
            ' 
            Me.insertTextBoxItem1.Id = 21
            Me.insertTextBoxItem1.Name = "insertTextBoxItem1"
            ' 
            ' insertSymbolItem1
            ' 
            Me.insertSymbolItem1.Id = 22
            Me.insertSymbolItem1.Name = "insertSymbolItem1"
            ' 
            ' changeSectionPageMarginsItem1
            ' 
            Me.changeSectionPageMarginsItem1.Id = 23
            Me.changeSectionPageMarginsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setNormalSectionPageMarginsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setNarrowSectionPageMarginsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setModerateSectionPageMarginsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setWideSectionPageMarginsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.showPageMarginsSetupFormItem1, True) _
            })
            Me.changeSectionPageMarginsItem1.Name = "changeSectionPageMarginsItem1"
            ' 
            ' setNormalSectionPageMarginsItem1
            ' 
            Me.setNormalSectionPageMarginsItem1.Id = 24
            Me.setNormalSectionPageMarginsItem1.Name = "setNormalSectionPageMarginsItem1"
            ' 
            ' setNarrowSectionPageMarginsItem1
            ' 
            Me.setNarrowSectionPageMarginsItem1.Id = 25
            Me.setNarrowSectionPageMarginsItem1.Name = "setNarrowSectionPageMarginsItem1"
            ' 
            ' setModerateSectionPageMarginsItem1
            ' 
            Me.setModerateSectionPageMarginsItem1.Id = 26
            Me.setModerateSectionPageMarginsItem1.Name = "setModerateSectionPageMarginsItem1"
            ' 
            ' setWideSectionPageMarginsItem1
            ' 
            Me.setWideSectionPageMarginsItem1.Id = 27
            Me.setWideSectionPageMarginsItem1.Name = "setWideSectionPageMarginsItem1"
            ' 
            ' showPageMarginsSetupFormItem1
            ' 
            Me.showPageMarginsSetupFormItem1.Id = 28
            Me.showPageMarginsSetupFormItem1.Name = "showPageMarginsSetupFormItem1"
            ' 
            ' changeSectionPageOrientationItem1
            ' 
            Me.changeSectionPageOrientationItem1.Id = 29
            Me.changeSectionPageOrientationItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setPortraitPageOrientationItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setLandscapePageOrientationItem1) _
            })
            Me.changeSectionPageOrientationItem1.Name = "changeSectionPageOrientationItem1"
            ' 
            ' setPortraitPageOrientationItem1
            ' 
            Me.setPortraitPageOrientationItem1.Id = 30
            Me.setPortraitPageOrientationItem1.Name = "setPortraitPageOrientationItem1"
            ' 
            ' setLandscapePageOrientationItem1
            ' 
            Me.setLandscapePageOrientationItem1.Id = 31
            Me.setLandscapePageOrientationItem1.Name = "setLandscapePageOrientationItem1"
            ' 
            ' changeSectionPaperKindItem1
            ' 
            Me.changeSectionPaperKindItem1.Id = 32
            Me.changeSectionPaperKindItem1.Name = "changeSectionPaperKindItem1"
            ' 
            ' changeSectionColumnsItem1
            ' 
            Me.changeSectionColumnsItem1.Id = 33
            Me.changeSectionColumnsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionOneColumnItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionTwoColumnsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionThreeColumnsItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.showColumnsSetupFormItem1, True) _
            })
            Me.changeSectionColumnsItem1.Name = "changeSectionColumnsItem1"
            ' 
            ' setSectionOneColumnItem1
            ' 
            Me.setSectionOneColumnItem1.Id = 34
            Me.setSectionOneColumnItem1.Name = "setSectionOneColumnItem1"
            ' 
            ' setSectionTwoColumnsItem1
            ' 
            Me.setSectionTwoColumnsItem1.Id = 35
            Me.setSectionTwoColumnsItem1.Name = "setSectionTwoColumnsItem1"
            ' 
            ' setSectionThreeColumnsItem1
            ' 
            Me.setSectionThreeColumnsItem1.Id = 36
            Me.setSectionThreeColumnsItem1.Name = "setSectionThreeColumnsItem1"
            ' 
            ' showColumnsSetupFormItem1
            ' 
            Me.showColumnsSetupFormItem1.Id = 37
            Me.showColumnsSetupFormItem1.Name = "showColumnsSetupFormItem1"
            ' 
            ' insertBreakItem1
            ' 
            Me.insertBreakItem1.Id = 38
            Me.insertBreakItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.insertPageBreakItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "B", ""), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.insertColumnBreakItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakNextPageItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakEvenPageItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakOddPageItem1) _
            })
            Me.insertBreakItem1.Name = "insertBreakItem1"
            ' 
            ' insertPageBreakItem1
            ' 
            Me.insertPageBreakItem1.Id = 39
            Me.insertPageBreakItem1.Name = "insertPageBreakItem1"
            ' 
            ' insertColumnBreakItem1
            ' 
            Me.insertColumnBreakItem1.Id = 40
            Me.insertColumnBreakItem1.Name = "insertColumnBreakItem1"
            ' 
            ' insertSectionBreakNextPageItem1
            ' 
            Me.insertSectionBreakNextPageItem1.Id = 41
            Me.insertSectionBreakNextPageItem1.Name = "insertSectionBreakNextPageItem1"
            ' 
            ' insertSectionBreakEvenPageItem1
            ' 
            Me.insertSectionBreakEvenPageItem1.Id = 42
            Me.insertSectionBreakEvenPageItem1.Name = "insertSectionBreakEvenPageItem1"
            ' 
            ' insertSectionBreakOddPageItem1
            ' 
            Me.insertSectionBreakOddPageItem1.Id = 43
            Me.insertSectionBreakOddPageItem1.Name = "insertSectionBreakOddPageItem1"
            ' 
            ' changeSectionLineNumberingItem1
            ' 
            Me.changeSectionLineNumberingItem1.Id = 44
            Me.changeSectionLineNumberingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingNoneItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingContinuousItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingRestartNewPageItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingRestartNewSectionItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.toggleParagraphSuppressLineNumbersItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.showLineNumberingFormItem1, True) _
            })
            Me.changeSectionLineNumberingItem1.Name = "changeSectionLineNumberingItem1"
            ' 
            ' setSectionLineNumberingNoneItem1
            ' 
            Me.setSectionLineNumberingNoneItem1.Id = 45
            Me.setSectionLineNumberingNoneItem1.Name = "setSectionLineNumberingNoneItem1"
            ' 
            ' setSectionLineNumberingContinuousItem1
            ' 
            Me.setSectionLineNumberingContinuousItem1.Id = 46
            Me.setSectionLineNumberingContinuousItem1.Name = "setSectionLineNumberingContinuousItem1"
            ' 
            ' setSectionLineNumberingRestartNewPageItem1
            ' 
            Me.setSectionLineNumberingRestartNewPageItem1.Id = 47
            Me.setSectionLineNumberingRestartNewPageItem1.Name = "setSectionLineNumberingRestartNewPageItem1"
            ' 
            ' setSectionLineNumberingRestartNewSectionItem1
            ' 
            Me.setSectionLineNumberingRestartNewSectionItem1.Id = 48
            Me.setSectionLineNumberingRestartNewSectionItem1.Name = "setSectionLineNumberingRestartNewSectionItem1"
            ' 
            ' toggleParagraphSuppressLineNumbersItem1
            ' 
            Me.toggleParagraphSuppressLineNumbersItem1.Id = 49
            Me.toggleParagraphSuppressLineNumbersItem1.Name = "toggleParagraphSuppressLineNumbersItem1"
            ' 
            ' showLineNumberingFormItem1
            ' 
            Me.showLineNumberingFormItem1.Id = 50
            Me.showLineNumberingFormItem1.Name = "showLineNumberingFormItem1"
            ' 
            ' changePageColorItem1
            ' 
            Me.changePageColorItem1.Id = 51
            Me.changePageColorItem1.Name = "changePageColorItem1"
            ' 
            ' pasteItem1
            ' 
            Me.pasteItem1.Id = 59
            Me.pasteItem1.Name = "pasteItem1"
            ' 
            ' cutItem1
            ' 
            Me.cutItem1.Id = 60
            Me.cutItem1.Name = "cutItem1"
            ' 
            ' copyItem1
            ' 
            Me.copyItem1.Id = 61
            Me.copyItem1.Name = "copyItem1"
            ' 
            ' pasteSpecialItem1
            ' 
            Me.pasteSpecialItem1.Id = 62
            Me.pasteSpecialItem1.Name = "pasteSpecialItem1"
            ' 
            ' barButtonGroup1
            ' 
            Me.barButtonGroup1.Id = 52
            Me.barButtonGroup1.ItemLinks.Add(Me.changeFontNameItem1, "FF")
            Me.barButtonGroup1.ItemLinks.Add(Me.changeFontSizeItem1)
            Me.barButtonGroup1.ItemLinks.Add(Me.fontSizeIncreaseItem1, "FG")
            Me.barButtonGroup1.ItemLinks.Add(Me.fontSizeDecreaseItem1, "FK")
            Me.barButtonGroup1.Name = "barButtonGroup1"
            Me.barButtonGroup1.Tag = "{97BBE334-159B-44d9-A168-0411957565E8}"
            ' 
            ' changeFontNameItem1
            ' 
            Me.changeFontNameItem1.Edit = Me.repositoryItemFontEdit1
            Me.changeFontNameItem1.Id = 63
            Me.changeFontNameItem1.Name = "changeFontNameItem1"
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
            Me.changeFontSizeItem1.Id = 64
            Me.changeFontSizeItem1.Name = "changeFontSizeItem1"
            ' 
            ' repositoryItemRichEditFontSizeEdit1
            ' 
            Me.repositoryItemRichEditFontSizeEdit1.AutoHeight = False
            Me.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
            Me.repositoryItemRichEditFontSizeEdit1.Control = Me.richEditControl1
            Me.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1"
            ' 
            ' fontSizeIncreaseItem1
            ' 
            Me.fontSizeIncreaseItem1.Id = 65
            Me.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1"
            ' 
            ' fontSizeDecreaseItem1
            ' 
            Me.fontSizeDecreaseItem1.Id = 66
            Me.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1"
            ' 
            ' barButtonGroup2
            ' 
            Me.barButtonGroup2.Id = 53
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontBoldItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontItalicItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontUnderlineItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontDoubleUnderlineItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontStrikeoutItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontDoubleStrikeoutItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontSuperscriptItem1)
            Me.barButtonGroup2.ItemLinks.Add(Me.toggleFontSubscriptItem1)
            Me.barButtonGroup2.Name = "barButtonGroup2"
            Me.barButtonGroup2.Tag = "{433DA7F0-03E2-4650-9DB5-66DD92D16E39}"
            ' 
            ' toggleFontBoldItem1
            ' 
            Me.toggleFontBoldItem1.Id = 67
            Me.toggleFontBoldItem1.Name = "toggleFontBoldItem1"
            ' 
            ' toggleFontItalicItem1
            ' 
            Me.toggleFontItalicItem1.Id = 68
            Me.toggleFontItalicItem1.Name = "toggleFontItalicItem1"
            ' 
            ' toggleFontUnderlineItem1
            ' 
            Me.toggleFontUnderlineItem1.Id = 69
            Me.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1"
            ' 
            ' toggleFontDoubleUnderlineItem1
            ' 
            Me.toggleFontDoubleUnderlineItem1.Id = 70
            Me.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1"
            ' 
            ' toggleFontStrikeoutItem1
            ' 
            Me.toggleFontStrikeoutItem1.Id = 71
            Me.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1"
            ' 
            ' toggleFontDoubleStrikeoutItem1
            ' 
            Me.toggleFontDoubleStrikeoutItem1.Id = 72
            Me.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1"
            ' 
            ' toggleFontSuperscriptItem1
            ' 
            Me.toggleFontSuperscriptItem1.Id = 73
            Me.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1"
            ' 
            ' toggleFontSubscriptItem1
            ' 
            Me.toggleFontSubscriptItem1.Id = 74
            Me.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1"
            ' 
            ' barButtonGroup3
            ' 
            Me.barButtonGroup3.Id = 54
            Me.barButtonGroup3.ItemLinks.Add(Me.changeFontColorItem1, "FC")
            Me.barButtonGroup3.ItemLinks.Add(Me.changeFontHighlightColorItem1, "I")
            Me.barButtonGroup3.Name = "barButtonGroup3"
            Me.barButtonGroup3.Tag = "{DF8C5334-EDE3-47c9-A42C-FE9A9247E180}"
            ' 
            ' changeFontColorItem1
            ' 
            Me.changeFontColorItem1.Id = 75
            Me.changeFontColorItem1.Name = "changeFontColorItem1"
            ' 
            ' changeFontHighlightColorItem1
            ' 
            Me.changeFontHighlightColorItem1.Id = 76
            Me.changeFontHighlightColorItem1.Name = "changeFontHighlightColorItem1"
            ' 
            ' changeTextCaseItem1
            ' 
            Me.changeTextCaseItem1.Id = 77
            Me.changeTextCaseItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextUpperCaseItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextLowerCaseItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.capitalizeEachWordCaseItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTextCaseItem1) _
            })
            Me.changeTextCaseItem1.Name = "changeTextCaseItem1"
            ' 
            ' makeTextUpperCaseItem1
            ' 
            Me.makeTextUpperCaseItem1.Id = 78
            Me.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1"
            ' 
            ' makeTextLowerCaseItem1
            ' 
            Me.makeTextLowerCaseItem1.Id = 79
            Me.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1"
            ' 
            ' capitalizeEachWordCaseItem1
            ' 
            Me.capitalizeEachWordCaseItem1.Id = 80
            Me.capitalizeEachWordCaseItem1.Name = "capitalizeEachWordCaseItem1"
            ' 
            ' toggleTextCaseItem1
            ' 
            Me.toggleTextCaseItem1.Id = 81
            Me.toggleTextCaseItem1.Name = "toggleTextCaseItem1"
            ' 
            ' clearFormattingItem1
            ' 
            Me.clearFormattingItem1.Id = 82
            Me.clearFormattingItem1.Name = "clearFormattingItem1"
            ' 
            ' barButtonGroup4
            ' 
            Me.barButtonGroup4.Id = 55
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleBulletedListItem1, "U")
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleNumberingListItem1, "N")
            Me.barButtonGroup4.ItemLinks.Add(Me.toggleMultiLevelListItem1, "M")
            Me.barButtonGroup4.Name = "barButtonGroup4"
            Me.barButtonGroup4.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}"
            ' 
            ' toggleBulletedListItem1
            ' 
            Me.toggleBulletedListItem1.Id = 83
            Me.toggleBulletedListItem1.Name = "toggleBulletedListItem1"
            ' 
            ' toggleNumberingListItem1
            ' 
            Me.toggleNumberingListItem1.Id = 84
            Me.toggleNumberingListItem1.Name = "toggleNumberingListItem1"
            ' 
            ' toggleMultiLevelListItem1
            ' 
            Me.toggleMultiLevelListItem1.Id = 85
            Me.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1"
            ' 
            ' barButtonGroup5
            ' 
            Me.barButtonGroup5.Id = 56
            Me.barButtonGroup5.ItemLinks.Add(Me.decreaseIndentItem1, "AO")
            Me.barButtonGroup5.ItemLinks.Add(Me.increaseIndentItem1, "AI")
            Me.barButtonGroup5.ItemLinks.Add(Me.toggleShowWhitespaceItem1)
            Me.barButtonGroup5.Name = "barButtonGroup5"
            Me.barButtonGroup5.Tag = "{4747D5AB-2BEB-4ea6-9A1D-8E4FB36F1B40}"
            ' 
            ' decreaseIndentItem1
            ' 
            Me.decreaseIndentItem1.Id = 86
            Me.decreaseIndentItem1.Name = "decreaseIndentItem1"
            ' 
            ' increaseIndentItem1
            ' 
            Me.increaseIndentItem1.Id = 87
            Me.increaseIndentItem1.Name = "increaseIndentItem1"
            ' 
            ' toggleShowWhitespaceItem1
            ' 
            Me.toggleShowWhitespaceItem1.Id = 92
            Me.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1"
            ' 
            ' barButtonGroup6
            ' 
            Me.barButtonGroup6.Id = 57
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentLeftItem1, "AL")
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentCenterItem1, "AC")
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentRightItem1, "AR")
            Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentJustifyItem1, "AJ")
            Me.barButtonGroup6.Name = "barButtonGroup6"
            Me.barButtonGroup6.Tag = "{8E89E775-996E-49a0-AADA-DE338E34732E}"
            ' 
            ' toggleParagraphAlignmentLeftItem1
            ' 
            Me.toggleParagraphAlignmentLeftItem1.Id = 88
            Me.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1"
            ' 
            ' toggleParagraphAlignmentCenterItem1
            ' 
            Me.toggleParagraphAlignmentCenterItem1.Id = 89
            Me.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1"
            ' 
            ' toggleParagraphAlignmentRightItem1
            ' 
            Me.toggleParagraphAlignmentRightItem1.Id = 90
            Me.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1"
            ' 
            ' toggleParagraphAlignmentJustifyItem1
            ' 
            Me.toggleParagraphAlignmentJustifyItem1.Id = 91
            Me.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1"
            ' 
            ' barButtonGroup7
            ' 
            Me.barButtonGroup7.Id = 58
            Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphLineSpacingItem1, "K")
            Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphBackColorItem1, "H")
            Me.barButtonGroup7.Name = "barButtonGroup7"
            Me.barButtonGroup7.Tag = "{9A8DEAD8-3890-4857-A395-EC625FD02217}"
            ' 
            ' changeParagraphLineSpacingItem1
            ' 
            Me.changeParagraphLineSpacingItem1.Id = 93
            Me.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSingleParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setSesquialteralParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.setDoubleParagraphSpacingItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.showLineSpacingFormItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.addSpacingBeforeParagraphItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "B", ""), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingBeforeParagraphItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingAfterParagraphItem1), _
                New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingAfterParagraphItem1) _
            })
            Me.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1"
            ' 
            ' setSingleParagraphSpacingItem1
            ' 
            Me.setSingleParagraphSpacingItem1.Id = 94
            Me.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1"
            ' 
            ' setSesquialteralParagraphSpacingItem1
            ' 
            Me.setSesquialteralParagraphSpacingItem1.Id = 95
            Me.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1"
            ' 
            ' setDoubleParagraphSpacingItem1
            ' 
            Me.setDoubleParagraphSpacingItem1.Id = 96
            Me.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1"
            ' 
            ' showLineSpacingFormItem1
            ' 
            Me.showLineSpacingFormItem1.Id = 97
            Me.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1"
            ' 
            ' addSpacingBeforeParagraphItem1
            ' 
            Me.addSpacingBeforeParagraphItem1.Id = 98
            Me.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1"
            ' 
            ' removeSpacingBeforeParagraphItem1
            ' 
            Me.removeSpacingBeforeParagraphItem1.Id = 99
            Me.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1"
            ' 
            ' addSpacingAfterParagraphItem1
            ' 
            Me.addSpacingAfterParagraphItem1.Id = 100
            Me.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1"
            ' 
            ' removeSpacingAfterParagraphItem1
            ' 
            Me.removeSpacingAfterParagraphItem1.Id = 101
            Me.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1"
            ' 
            ' changeParagraphBackColorItem1
            ' 
            Me.changeParagraphBackColorItem1.Id = 102
            Me.changeParagraphBackColorItem1.Name = "changeParagraphBackColorItem1"
            ' 
            ' findItem1
            ' 
            Me.findItem1.Id = 104
            Me.findItem1.Name = "findItem1"
            ' 
            ' replaceItem1
            ' 
            Me.replaceItem1.Id = 105
            Me.replaceItem1.Name = "replaceItem1"
            ' 
            ' fileRibbonPage1
            ' 
            Me.fileRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.commonRibbonPageGroup1, Me.infoRibbonPageGroup1})
            Me.fileRibbonPage1.Name = "fileRibbonPage1"
            ' 
            ' commonRibbonPageGroup1
            ' 
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.undoItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.redoItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileNewItem1, "N")
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileOpenItem1, "O")
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveItem1, "S")
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveAsItem1, "A")
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.quickPrintItem1)
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printItem1, "P")
            Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printPreviewItem1)
            Me.commonRibbonPageGroup1.Name = "commonRibbonPageGroup1"
            ' 
            ' infoRibbonPageGroup1
            ' 
            Me.infoRibbonPageGroup1.ItemLinks.Add(Me.showDocumentPropertiesFormItem1)
            Me.infoRibbonPageGroup1.Name = "infoRibbonPageGroup1"
            ' 
            ' homeRibbonPage1
            ' 
            Me.homeRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.clipboardRibbonPageGroup1, Me.fontRibbonPageGroup1, Me.paragraphRibbonPageGroup1, Me.stylesRibbonPageGroup1, Me.editingRibbonPageGroup1})
            Me.homeRibbonPage1.Name = "homeRibbonPage1"
            reduceOperation1.Behavior = DevExpress.XtraBars.Ribbon.ReduceOperationBehavior.UntilAvailable
            reduceOperation1.Group = Me.stylesRibbonPageGroup1
            reduceOperation1.ItemLinkIndex = 0
            reduceOperation1.ItemLinksCount = 0
            reduceOperation1.Operation = DevExpress.XtraBars.Ribbon.ReduceOperationType.Gallery
            Me.homeRibbonPage1.ReduceOperations.Add(reduceOperation1)
            ' 
            ' clipboardRibbonPageGroup1
            ' 
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteItem1, "V")
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.cutItem1, "X")
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.copyItem1, "C")
            Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteSpecialItem1)
            Me.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1"
            ' 
            ' fontRibbonPageGroup1
            ' 
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup1)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup2)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup3)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.changeTextCaseItem1)
            Me.fontRibbonPageGroup1.ItemLinks.Add(Me.clearFormattingItem1, "E")
            Me.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1"
            ' 
            ' paragraphRibbonPageGroup1
            ' 
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup4)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup5)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup6)
            Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup7)
            Me.paragraphRibbonPageGroup1.Name = "paragraphRibbonPageGroup1"
            ' 
            ' editingRibbonPageGroup1
            ' 
            Me.editingRibbonPageGroup1.ItemLinks.Add(Me.findItem1, "FD")
            Me.editingRibbonPageGroup1.ItemLinks.Add(Me.replaceItem1, "R")
            Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
            ' 
            ' insertRibbonPage1
            ' 
            Me.insertRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.pagesRibbonPageGroup1, Me.tablesRibbonPageGroup1, Me.illustrationsRibbonPageGroup1, Me.linksRibbonPageGroup1, Me.headerFooterRibbonPageGroup1, Me.textRibbonPageGroup1, Me.symbolsRibbonPageGroup1})
            Me.insertRibbonPage1.Name = "insertRibbonPage1"
            ' 
            ' pagesRibbonPageGroup1
            ' 
            Me.pagesRibbonPageGroup1.AllowTextClipping = False
            Me.pagesRibbonPageGroup1.ItemLinks.Add(Me.insertPageBreakItem21, "B")
            Me.pagesRibbonPageGroup1.Name = "pagesRibbonPageGroup1"
            ' 
            ' tablesRibbonPageGroup1
            ' 
            Me.tablesRibbonPageGroup1.AllowTextClipping = False
            Me.tablesRibbonPageGroup1.ItemLinks.Add(Me.insertTableItem1, "T")
            Me.tablesRibbonPageGroup1.Name = "tablesRibbonPageGroup1"
            ' 
            ' illustrationsRibbonPageGroup1
            ' 
            Me.illustrationsRibbonPageGroup1.ItemLinks.Add(Me.insertPictureItem1, "P")
            Me.illustrationsRibbonPageGroup1.ItemLinks.Add(Me.insertFloatingPictureItem1)
            Me.illustrationsRibbonPageGroup1.Name = "illustrationsRibbonPageGroup1"
            ' 
            ' linksRibbonPageGroup1
            ' 
            Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertBookmarkItem1, "K")
            Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertHyperlinkItem1, "I")
            Me.linksRibbonPageGroup1.Name = "linksRibbonPageGroup1"
            ' 
            ' headerFooterRibbonPageGroup1
            ' 
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageHeaderItem1, "H")
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageFooterItem1, "O")
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageNumberItem1, "NU")
            Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageCountItem1)
            Me.headerFooterRibbonPageGroup1.Name = "headerFooterRibbonPageGroup1"
            ' 
            ' textRibbonPageGroup1
            ' 
            Me.textRibbonPageGroup1.ImageOptions.Image = (CType(resources.GetObject("textRibbonPageGroup1.ImageOptions.Image"), System.Drawing.Image))
            Me.textRibbonPageGroup1.ItemLinks.Add(Me.insertTextBoxItem1, "X")
            Me.textRibbonPageGroup1.Name = "textRibbonPageGroup1"
            ' 
            ' symbolsRibbonPageGroup1
            ' 
            Me.symbolsRibbonPageGroup1.AllowTextClipping = False
            Me.symbolsRibbonPageGroup1.ItemLinks.Add(Me.insertSymbolItem1, "U")
            Me.symbolsRibbonPageGroup1.Name = "symbolsRibbonPageGroup1"
            ' 
            ' pageLayoutRibbonPage1
            ' 
            Me.pageLayoutRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.pageSetupRibbonPageGroup1, Me.pageBackgroundRibbonPageGroup1})
            Me.pageLayoutRibbonPage1.Name = "pageLayoutRibbonPage1"
            ' 
            ' pageSetupRibbonPageGroup1
            ' 
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.changeSectionPageMarginsItem1, "M")
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.changeSectionPageOrientationItem1, "O")
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.changeSectionPaperKindItem1, "SZ")
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.changeSectionColumnsItem1, "J")
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.insertBreakItem1, "B")
            Me.pageSetupRibbonPageGroup1.ItemLinks.Add(Me.changeSectionLineNumberingItem1, "LN")
            Me.pageSetupRibbonPageGroup1.Name = "pageSetupRibbonPageGroup1"
            ' 
            ' pageBackgroundRibbonPageGroup1
            ' 
            Me.pageBackgroundRibbonPageGroup1.AllowTextClipping = False
            Me.pageBackgroundRibbonPageGroup1.ItemLinks.Add(Me.changePageColorItem1, "PC")
            Me.pageBackgroundRibbonPageGroup1.Name = "pageBackgroundRibbonPageGroup1"
            ' 
            ' richEditBarController1
            ' 
            Me.richEditBarController1.BarItems.Add(Me.undoItem1)
            Me.richEditBarController1.BarItems.Add(Me.redoItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileNewItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileOpenItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileSaveItem1)
            Me.richEditBarController1.BarItems.Add(Me.fileSaveAsItem1)
            Me.richEditBarController1.BarItems.Add(Me.quickPrintItem1)
            Me.richEditBarController1.BarItems.Add(Me.printItem1)
            Me.richEditBarController1.BarItems.Add(Me.printPreviewItem1)
            Me.richEditBarController1.BarItems.Add(Me.showDocumentPropertiesFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageBreakItem21)
            Me.richEditBarController1.BarItems.Add(Me.insertTableItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPictureItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertFloatingPictureItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertBookmarkItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertHyperlinkItem1)
            Me.richEditBarController1.BarItems.Add(Me.editPageHeaderItem1)
            Me.richEditBarController1.BarItems.Add(Me.editPageFooterItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageNumberItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageCountItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertTextBoxItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertSymbolItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeSectionPageMarginsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setNormalSectionPageMarginsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setNarrowSectionPageMarginsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setModerateSectionPageMarginsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setWideSectionPageMarginsItem1)
            Me.richEditBarController1.BarItems.Add(Me.showPageMarginsSetupFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeSectionPageOrientationItem1)
            Me.richEditBarController1.BarItems.Add(Me.setPortraitPageOrientationItem1)
            Me.richEditBarController1.BarItems.Add(Me.setLandscapePageOrientationItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeSectionPaperKindItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeSectionColumnsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionOneColumnItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionTwoColumnsItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionThreeColumnsItem1)
            Me.richEditBarController1.BarItems.Add(Me.showColumnsSetupFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertBreakItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertPageBreakItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertColumnBreakItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertSectionBreakNextPageItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertSectionBreakEvenPageItem1)
            Me.richEditBarController1.BarItems.Add(Me.insertSectionBreakOddPageItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeSectionLineNumberingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionLineNumberingNoneItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionLineNumberingContinuousItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionLineNumberingRestartNewPageItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSectionLineNumberingRestartNewSectionItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphSuppressLineNumbersItem1)
            Me.richEditBarController1.BarItems.Add(Me.showLineNumberingFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.changePageColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.pasteItem1)
            Me.richEditBarController1.BarItems.Add(Me.cutItem1)
            Me.richEditBarController1.BarItems.Add(Me.copyItem1)
            Me.richEditBarController1.BarItems.Add(Me.pasteSpecialItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontNameItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontSizeItem1)
            Me.richEditBarController1.BarItems.Add(Me.fontSizeIncreaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.fontSizeDecreaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontBoldItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontItalicItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontUnderlineItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontDoubleUnderlineItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontStrikeoutItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontDoubleStrikeoutItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontSuperscriptItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleFontSubscriptItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeFontHighlightColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeTextCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.makeTextUpperCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.makeTextLowerCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.capitalizeEachWordCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleTextCaseItem1)
            Me.richEditBarController1.BarItems.Add(Me.clearFormattingItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleBulletedListItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleNumberingListItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleMultiLevelListItem1)
            Me.richEditBarController1.BarItems.Add(Me.decreaseIndentItem1)
            Me.richEditBarController1.BarItems.Add(Me.increaseIndentItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentLeftItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentCenterItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentRightItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleParagraphAlignmentJustifyItem1)
            Me.richEditBarController1.BarItems.Add(Me.toggleShowWhitespaceItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeParagraphLineSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSingleParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setSesquialteralParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.setDoubleParagraphSpacingItem1)
            Me.richEditBarController1.BarItems.Add(Me.showLineSpacingFormItem1)
            Me.richEditBarController1.BarItems.Add(Me.addSpacingBeforeParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.removeSpacingBeforeParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.addSpacingAfterParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.removeSpacingAfterParagraphItem1)
            Me.richEditBarController1.BarItems.Add(Me.changeParagraphBackColorItem1)
            Me.richEditBarController1.BarItems.Add(Me.galleryChangeStyleItem1)
            Me.richEditBarController1.BarItems.Add(Me.findItem1)
            Me.richEditBarController1.BarItems.Add(Me.replaceItem1)
            Me.richEditBarController1.Control = Me.richEditControl1
            ' 
            ' defaultLookAndFeel1
            ' 
            Me.defaultLookAndFeel1.LookAndFeel.SkinName = "Office 2016 Colorful"
            ' 
            ' Form1
            ' 
            Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
            Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
            Me.ClientSize = New System.Drawing.Size(610, 434)
            Me.Controls.Add(Me.richEditControl1)
            Me.Controls.Add(Me.ribbonControl1)
            Me.Icon = (CType(resources.GetObject("$this.Icon"), System.Drawing.Icon))
            Me.Name = "Form1"
            Me.Ribbon = Me.ribbonControl1
            Me.Text = "RichEditControl"
            CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
            CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
            CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
            CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
            Me.ResumeLayout(False)
            Me.PerformLayout()

        End Sub

        #End Region

        Private richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
        Private ribbonControl1 As DevExpress.XtraBars.Ribbon.RibbonControl
        Private undoItem1 As DevExpress.XtraRichEdit.UI.UndoItem
        Private redoItem1 As DevExpress.XtraRichEdit.UI.RedoItem
        Private fileNewItem1 As DevExpress.XtraRichEdit.UI.FileNewItem
        Private fileOpenItem1 As DevExpress.XtraRichEdit.UI.FileOpenItem
        Private fileSaveItem1 As DevExpress.XtraRichEdit.UI.FileSaveItem
        Private fileSaveAsItem1 As DevExpress.XtraRichEdit.UI.FileSaveAsItem
        Private quickPrintItem1 As DevExpress.XtraRichEdit.UI.QuickPrintItem
        Private printItem1 As DevExpress.XtraRichEdit.UI.PrintItem
        Private printPreviewItem1 As DevExpress.XtraRichEdit.UI.PrintPreviewItem
        Private showDocumentPropertiesFormItem1 As DevExpress.XtraRichEdit.UI.ShowDocumentPropertiesFormItem
        Private insertPageBreakItem21 As DevExpress.XtraRichEdit.UI.InsertPageBreakItem2
        Private insertTableItem1 As DevExpress.XtraRichEdit.UI.InsertTableItem
        Private insertPictureItem1 As DevExpress.XtraRichEdit.UI.InsertPictureItem
        Private insertFloatingPictureItem1 As DevExpress.XtraRichEdit.UI.InsertFloatingPictureItem
        Private insertBookmarkItem1 As DevExpress.XtraRichEdit.UI.InsertBookmarkItem
        Private insertHyperlinkItem1 As DevExpress.XtraRichEdit.UI.InsertHyperlinkItem
        Private editPageHeaderItem1 As DevExpress.XtraRichEdit.UI.EditPageHeaderItem
        Private editPageFooterItem1 As DevExpress.XtraRichEdit.UI.EditPageFooterItem
        Private insertPageNumberItem1 As DevExpress.XtraRichEdit.UI.InsertPageNumberItem
        Private insertPageCountItem1 As DevExpress.XtraRichEdit.UI.InsertPageCountItem
        Private insertTextBoxItem1 As DevExpress.XtraRichEdit.UI.InsertTextBoxItem
        Private insertSymbolItem1 As DevExpress.XtraRichEdit.UI.InsertSymbolItem
        Private changeSectionPageMarginsItem1 As DevExpress.XtraRichEdit.UI.ChangeSectionPageMarginsItem
        Private setNormalSectionPageMarginsItem1 As DevExpress.XtraRichEdit.UI.SetNormalSectionPageMarginsItem
        Private setNarrowSectionPageMarginsItem1 As DevExpress.XtraRichEdit.UI.SetNarrowSectionPageMarginsItem
        Private setModerateSectionPageMarginsItem1 As DevExpress.XtraRichEdit.UI.SetModerateSectionPageMarginsItem
        Private setWideSectionPageMarginsItem1 As DevExpress.XtraRichEdit.UI.SetWideSectionPageMarginsItem
        Private showPageMarginsSetupFormItem1 As DevExpress.XtraRichEdit.UI.ShowPageMarginsSetupFormItem
        Private changeSectionPageOrientationItem1 As DevExpress.XtraRichEdit.UI.ChangeSectionPageOrientationItem
        Private setPortraitPageOrientationItem1 As DevExpress.XtraRichEdit.UI.SetPortraitPageOrientationItem
        Private setLandscapePageOrientationItem1 As DevExpress.XtraRichEdit.UI.SetLandscapePageOrientationItem
        Private changeSectionPaperKindItem1 As DevExpress.XtraRichEdit.UI.ChangeSectionPaperKindItem
        Private changeSectionColumnsItem1 As DevExpress.XtraRichEdit.UI.ChangeSectionColumnsItem
        Private setSectionOneColumnItem1 As DevExpress.XtraRichEdit.UI.SetSectionOneColumnItem
        Private setSectionTwoColumnsItem1 As DevExpress.XtraRichEdit.UI.SetSectionTwoColumnsItem
        Private setSectionThreeColumnsItem1 As DevExpress.XtraRichEdit.UI.SetSectionThreeColumnsItem
        Private showColumnsSetupFormItem1 As DevExpress.XtraRichEdit.UI.ShowColumnsSetupFormItem
        Private insertBreakItem1 As DevExpress.XtraRichEdit.UI.InsertBreakItem
        Private insertPageBreakItem1 As DevExpress.XtraRichEdit.UI.InsertPageBreakItem
        Private insertColumnBreakItem1 As DevExpress.XtraRichEdit.UI.InsertColumnBreakItem
        Private insertSectionBreakNextPageItem1 As DevExpress.XtraRichEdit.UI.InsertSectionBreakNextPageItem
        Private insertSectionBreakEvenPageItem1 As DevExpress.XtraRichEdit.UI.InsertSectionBreakEvenPageItem
        Private insertSectionBreakOddPageItem1 As DevExpress.XtraRichEdit.UI.InsertSectionBreakOddPageItem
        Private changeSectionLineNumberingItem1 As DevExpress.XtraRichEdit.UI.ChangeSectionLineNumberingItem
        Private setSectionLineNumberingNoneItem1 As DevExpress.XtraRichEdit.UI.SetSectionLineNumberingNoneItem
        Private setSectionLineNumberingContinuousItem1 As DevExpress.XtraRichEdit.UI.SetSectionLineNumberingContinuousItem
        Private setSectionLineNumberingRestartNewPageItem1 As DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewPageItem
        Private setSectionLineNumberingRestartNewSectionItem1 As DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewSectionItem
        Private toggleParagraphSuppressLineNumbersItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphSuppressLineNumbersItem
        Private showLineNumberingFormItem1 As DevExpress.XtraRichEdit.UI.ShowLineNumberingFormItem
        Private changePageColorItem1 As DevExpress.XtraRichEdit.UI.ChangePageColorItem
        Private pasteItem1 As DevExpress.XtraRichEdit.UI.PasteItem
        Private cutItem1 As DevExpress.XtraRichEdit.UI.CutItem
        Private copyItem1 As DevExpress.XtraRichEdit.UI.CopyItem
        Private pasteSpecialItem1 As DevExpress.XtraRichEdit.UI.PasteSpecialItem
        Private barButtonGroup1 As DevExpress.XtraBars.BarButtonGroup
        Private changeFontNameItem1 As DevExpress.XtraRichEdit.UI.ChangeFontNameItem
        Private repositoryItemFontEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemFontEdit
        Private changeFontSizeItem1 As DevExpress.XtraRichEdit.UI.ChangeFontSizeItem
        Private repositoryItemRichEditFontSizeEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit
        Private fontSizeIncreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem
        Private fontSizeDecreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem
        Private barButtonGroup2 As DevExpress.XtraBars.BarButtonGroup
        Private toggleFontBoldItem1 As DevExpress.XtraRichEdit.UI.ToggleFontBoldItem
        Private toggleFontItalicItem1 As DevExpress.XtraRichEdit.UI.ToggleFontItalicItem
        Private toggleFontUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem
        Private toggleFontDoubleUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem
        Private toggleFontStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem
        Private toggleFontDoubleStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem
        Private toggleFontSuperscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem
        Private toggleFontSubscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem
        Private barButtonGroup3 As DevExpress.XtraBars.BarButtonGroup
        Private changeFontColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontColorItem
        Private changeFontHighlightColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontHighlightColorItem
        Private changeTextCaseItem1 As DevExpress.XtraRichEdit.UI.ChangeTextCaseItem
        Private makeTextUpperCaseItem1 As DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem
        Private makeTextLowerCaseItem1 As DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem
        Private capitalizeEachWordCaseItem1 As DevExpress.XtraRichEdit.UI.CapitalizeEachWordCaseItem
        Private toggleTextCaseItem1 As DevExpress.XtraRichEdit.UI.ToggleTextCaseItem
        Private clearFormattingItem1 As DevExpress.XtraRichEdit.UI.ClearFormattingItem
        Private barButtonGroup4 As DevExpress.XtraBars.BarButtonGroup
        Private toggleBulletedListItem1 As DevExpress.XtraRichEdit.UI.ToggleBulletedListItem
        Private toggleNumberingListItem1 As DevExpress.XtraRichEdit.UI.ToggleNumberingListItem
        Private toggleMultiLevelListItem1 As DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem
        Private barButtonGroup5 As DevExpress.XtraBars.BarButtonGroup
        Private decreaseIndentItem1 As DevExpress.XtraRichEdit.UI.DecreaseIndentItem
        Private increaseIndentItem1 As DevExpress.XtraRichEdit.UI.IncreaseIndentItem
        Private toggleShowWhitespaceItem1 As DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem
        Private barButtonGroup6 As DevExpress.XtraBars.BarButtonGroup
        Private toggleParagraphAlignmentLeftItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem
        Private toggleParagraphAlignmentCenterItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem
        Private toggleParagraphAlignmentRightItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem
        Private toggleParagraphAlignmentJustifyItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem
        Private barButtonGroup7 As DevExpress.XtraBars.BarButtonGroup
        Private changeParagraphLineSpacingItem1 As DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem
        Private setSingleParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem
        Private setSesquialteralParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem
        Private setDoubleParagraphSpacingItem1 As DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem
        Private showLineSpacingFormItem1 As DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem
        Private addSpacingBeforeParagraphItem1 As DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem
        Private removeSpacingBeforeParagraphItem1 As DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem
        Private addSpacingAfterParagraphItem1 As DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem
        Private removeSpacingAfterParagraphItem1 As DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem
        Private changeParagraphBackColorItem1 As DevExpress.XtraRichEdit.UI.ChangeParagraphBackColorItem
        Private galleryChangeStyleItem1 As DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem
        Private findItem1 As DevExpress.XtraRichEdit.UI.FindItem
        Private replaceItem1 As DevExpress.XtraRichEdit.UI.ReplaceItem
        Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
        Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
        Private infoRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.InfoRibbonPageGroup
        Private homeRibbonPage1 As DevExpress.XtraRichEdit.UI.HomeRibbonPage
        Private clipboardRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup
        Private fontRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.FontRibbonPageGroup
        Private paragraphRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup
        Private stylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup
        Private editingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup
        Private insertRibbonPage1 As DevExpress.XtraRichEdit.UI.InsertRibbonPage
        Private pagesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup
        Private tablesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup
        Private illustrationsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup
        Private linksRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup
        Private headerFooterRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup
        Private textRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TextRibbonPageGroup
        Private symbolsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup
        Private pageLayoutRibbonPage1 As DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage
        Private pageSetupRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup
        Private pageBackgroundRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup
        Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
        Private defaultLookAndFeel1 As DevExpress.LookAndFeel.DefaultLookAndFeel
    End Class
End Namespace

