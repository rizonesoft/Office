Namespace XtraRichEdit
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
			Dim optionsSpelling1 As New DevExpress.XtraSpellChecker.OptionsSpelling()
			Dim galleryItemGroup2 As New DevExpress.XtraBars.Ribbon.GalleryItemGroup()
			Dim reduceOperation1 As New DevExpress.XtraBars.Ribbon.ReduceOperation()
			Me.stylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup()
			Me.galleryChangeStyleItem1 = New DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem()
			Me.appMenu = New DevExpress.XtraBars.Ribbon.ApplicationMenu(Me.components)
			Me.ribbonImageCollection = New DevExpress.Utils.ImageCollection(Me.components)
			Me.richEditControl = New DevExpress.XtraRichEdit.RichEditControl()
			Me.spellChecker = New DevExpress.XtraSpellChecker.SpellChecker(Me.components)
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
			Me.toggleParagraphLeftToRightItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphLeftToRightItem()
			Me.toggleParagraphRightToLeftItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphRightToLeftItem()
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
			Me.insertPageBreakItem21 = New DevExpress.XtraRichEdit.UI.InsertPageBreakItem2()
			Me.insertTableItem1 = New DevExpress.XtraRichEdit.UI.InsertTableItem()
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
			Me.insertSectionBreakContinuousItem1 = New DevExpress.XtraRichEdit.UI.InsertSectionBreakContinuousItem()
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
			Me.insertTableOfContentsItem1 = New DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem()
			Me.updateTableOfContentsItem1 = New DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem()
			Me.addParagraphsToTableOfContentItem1 = New DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem()
			Me.setParagraphHeadingLevelItem1 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem2 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem3 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem4 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem5 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem6 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem7 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem8 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem9 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem10 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.insertCaptionPlaceholderItem1 = New DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem()
			Me.insertFiguresCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems()
			Me.insertTablesCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems()
			Me.insertEquationsCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems()
			Me.insertTableOfFiguresPlaceholderItem1 = New DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem()
			Me.insertTableOfFiguresItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems()
			Me.insertTableOfTablesItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems()
			Me.insertTableOfEquationsItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems()
			Me.updateTableOfFiguresItem1 = New DevExpress.XtraRichEdit.UI.UpdateTableOfFiguresItem()
			Me.insertMergeFieldItem1 = New DevExpress.XtraRichEdit.UI.InsertMergeFieldItem()
			Me.showAllFieldCodesItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem()
			Me.showAllFieldResultsItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem()
			Me.toggleViewMergedDataItem1 = New DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem()
			Me.checkSpellingItem1 = New DevExpress.XtraRichEdit.UI.CheckSpellingItem()
			Me.changeLanguageItem1 = New DevExpress.XtraRichEdit.UI.ChangeLanguageItem()
			Me.protectDocumentItem1 = New DevExpress.XtraRichEdit.UI.ProtectDocumentItem()
			Me.changeRangeEditingPermissionsItem1 = New DevExpress.XtraRichEdit.UI.ChangeRangeEditingPermissionsItem()
			Me.unprotectDocumentItem1 = New DevExpress.XtraRichEdit.UI.UnprotectDocumentItem()
			Me.newCommentItem1 = New DevExpress.XtraRichEdit.UI.NewCommentItem()
			Me.deleteCommentsItem1 = New DevExpress.XtraRichEdit.UI.DeleteCommentsItem()
			Me.deleteOneCommentItem1 = New DevExpress.XtraRichEdit.UI.DeleteOneCommentItem()
			Me.deleteAllCommentsShownItem1 = New DevExpress.XtraRichEdit.UI.DeleteAllCommentsShownItem()
			Me.deleteAllCommentsItem1 = New DevExpress.XtraRichEdit.UI.DeleteAllCommentsItem()
			Me.previousCommentItem1 = New DevExpress.XtraRichEdit.UI.PreviousCommentItem()
			Me.nextCommentItem1 = New DevExpress.XtraRichEdit.UI.NextCommentItem()
			Me.changeCommentItem1 = New DevExpress.XtraRichEdit.UI.ChangeCommentItem()
			Me.reviewersItem1 = New DevExpress.XtraRichEdit.UI.ReviewersItem()
			Me.reviewingPaneItem1 = New DevExpress.XtraRichEdit.UI.ReviewingPaneItem()
			Me.switchToSimpleViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem()
			Me.switchToDraftViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem()
			Me.switchToPrintLayoutViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem()
			Me.toggleShowHorizontalRulerItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem()
			Me.toggleShowVerticalRulerItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem()
			Me.zoomOutItem1 = New DevExpress.XtraRichEdit.UI.ZoomOutItem()
			Me.zoomInItem1 = New DevExpress.XtraRichEdit.UI.ZoomInItem()
			Me.goToPageHeaderItem1 = New DevExpress.XtraRichEdit.UI.GoToPageHeaderItem()
			Me.goToPageFooterItem1 = New DevExpress.XtraRichEdit.UI.GoToPageFooterItem()
			Me.goToNextHeaderFooterItem1 = New DevExpress.XtraRichEdit.UI.GoToNextHeaderFooterItem()
			Me.goToPreviousHeaderFooterItem1 = New DevExpress.XtraRichEdit.UI.GoToPreviousHeaderFooterItem()
			Me.toggleLinkToPreviousItem1 = New DevExpress.XtraRichEdit.UI.ToggleLinkToPreviousItem()
			Me.toggleDifferentFirstPageItem1 = New DevExpress.XtraRichEdit.UI.ToggleDifferentFirstPageItem()
			Me.toggleDifferentOddAndEvenPagesItem1 = New DevExpress.XtraRichEdit.UI.ToggleDifferentOddAndEvenPagesItem()
			Me.closePageHeaderFooterItem1 = New DevExpress.XtraRichEdit.UI.ClosePageHeaderFooterItem()
			Me.toggleFirstRowItem1 = New DevExpress.XtraRichEdit.UI.ToggleFirstRowItem()
			Me.toggleLastRowItem1 = New DevExpress.XtraRichEdit.UI.ToggleLastRowItem()
			Me.toggleBandedRowsItem1 = New DevExpress.XtraRichEdit.UI.ToggleBandedRowsItem()
			Me.toggleFirstColumnItem1 = New DevExpress.XtraRichEdit.UI.ToggleFirstColumnItem()
			Me.toggleLastColumnItem1 = New DevExpress.XtraRichEdit.UI.ToggleLastColumnItem()
			Me.toggleBandedColumnsItem1 = New DevExpress.XtraRichEdit.UI.ToggleBandedColumnsItem()
			Me.galleryChangeTableStyleItem1 = New DevExpress.XtraRichEdit.UI.GalleryChangeTableStyleItem()
			Me.changeTableBorderLineStyleItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem()
			Me.repositoryItemBorderLineStyle1 = New DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle()
			Me.changeTableBorderLineWeightItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem()
			Me.repositoryItemBorderLineWeight1 = New DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight()
			Me.changeTableBorderColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem()
			Me.changeTableBordersItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBordersItem()
			Me.toggleTableCellsBottomBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomBorderItem()
			Me.toggleTableCellsTopBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopBorderItem()
			Me.toggleTableCellsLeftBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsLeftBorderItem()
			Me.toggleTableCellsRightBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsRightBorderItem()
			Me.resetTableCellsAllBordersItem1 = New DevExpress.XtraRichEdit.UI.ResetTableCellsAllBordersItem()
			Me.toggleTableCellsAllBordersItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsAllBordersItem()
			Me.toggleTableCellsOutsideBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsOutsideBorderItem()
			Me.toggleTableCellsInsideBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideBorderItem()
			Me.toggleTableCellsInsideHorizontalBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideHorizontalBorderItem()
			Me.toggleTableCellsInsideVerticalBorderItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideVerticalBorderItem()
			Me.toggleShowTableGridLinesItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowTableGridLinesItem()
			Me.changeTableCellsShadingItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem()
			Me.selectTableElementsItem1 = New DevExpress.XtraRichEdit.UI.SelectTableElementsItem()
			Me.selectTableCellItem1 = New DevExpress.XtraRichEdit.UI.SelectTableCellItem()
			Me.selectTableColumnItem1 = New DevExpress.XtraRichEdit.UI.SelectTableColumnItem()
			Me.selectTableRowItem1 = New DevExpress.XtraRichEdit.UI.SelectTableRowItem()
			Me.selectTableItem1 = New DevExpress.XtraRichEdit.UI.SelectTableItem()
			Me.showTablePropertiesFormItem1 = New DevExpress.XtraRichEdit.UI.ShowTablePropertiesFormItem()
			Me.deleteTableElementsItem1 = New DevExpress.XtraRichEdit.UI.DeleteTableElementsItem()
			Me.showDeleteTableCellsFormItem1 = New DevExpress.XtraRichEdit.UI.ShowDeleteTableCellsFormItem()
			Me.deleteTableColumnsItem1 = New DevExpress.XtraRichEdit.UI.DeleteTableColumnsItem()
			Me.deleteTableRowsItem1 = New DevExpress.XtraRichEdit.UI.DeleteTableRowsItem()
			Me.deleteTableItem1 = New DevExpress.XtraRichEdit.UI.DeleteTableItem()
			Me.insertTableRowAboveItem1 = New DevExpress.XtraRichEdit.UI.InsertTableRowAboveItem()
			Me.insertTableRowBelowItem1 = New DevExpress.XtraRichEdit.UI.InsertTableRowBelowItem()
			Me.insertTableColumnToLeftItem1 = New DevExpress.XtraRichEdit.UI.InsertTableColumnToLeftItem()
			Me.insertTableColumnToRightItem1 = New DevExpress.XtraRichEdit.UI.InsertTableColumnToRightItem()
			Me.mergeTableCellsItem1 = New DevExpress.XtraRichEdit.UI.MergeTableCellsItem()
			Me.showSplitTableCellsForm1 = New DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm()
			Me.splitTableItem1 = New DevExpress.XtraRichEdit.UI.SplitTableItem()
			Me.toggleTableAutoFitItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem()
			Me.toggleTableAutoFitContentsItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem()
			Me.toggleTableAutoFitWindowItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem()
			Me.toggleTableFixedColumnWidthItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem()
			Me.toggleTableCellsTopLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem()
			Me.toggleTableCellsMiddleLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem()
			Me.toggleTableCellsBottomLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem()
			Me.toggleTableCellsTopCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem()
			Me.toggleTableCellsMiddleCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem()
			Me.toggleTableCellsBottomCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem()
			Me.toggleTableCellsTopRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem()
			Me.toggleTableCellsMiddleRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem()
			Me.toggleTableCellsBottomRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem()
			Me.showTableOptionsFormItem1 = New DevExpress.XtraRichEdit.UI.ShowTableOptionsFormItem()
			Me.changeFloatingObjectFillColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFloatingObjectFillColorItem()
			Me.changeFloatingObjectOutlineColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineColorItem()
			Me.changeFloatingObjectOutlineWeightItem1 = New DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineWeightItem()
			Me.repositoryItemFloatingObjectOutlineWeight1 = New DevExpress.XtraRichEdit.Forms.Design.RepositoryItemFloatingObjectOutlineWeight()
			Me.changeFloatingObjectTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.ChangeFloatingObjectTextWrapTypeItem()
			Me.setFloatingObjectInlineTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectInlineTextWrapTypeItem()
			Me.setFloatingObjectSquareTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectSquareTextWrapTypeItem()
			Me.setFloatingObjectTightTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectTightTextWrapTypeItem()
			Me.setFloatingObjectThroughTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectThroughTextWrapTypeItem()
			Me.setFloatingObjectTopAndBottomTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectTopAndBottomTextWrapTypeItem()
			Me.setFloatingObjectBehindTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectBehindTextWrapTypeItem()
			Me.setFloatingObjectInFrontOfTextWrapTypeItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectInFrontOfTextWrapTypeItem()
			Me.changeFloatingObjectAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ChangeFloatingObjectAlignmentItem()
			Me.setFloatingObjectTopLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectTopLeftAlignmentItem()
			Me.setFloatingObjectTopCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectTopCenterAlignmentItem()
			Me.setFloatingObjectTopRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectTopRightAlignmentItem()
			Me.setFloatingObjectMiddleLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleLeftAlignmentItem()
			Me.setFloatingObjectMiddleCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleCenterAlignmentItem()
			Me.setFloatingObjectMiddleRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleRightAlignmentItem()
			Me.setFloatingObjectBottomLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomLeftAlignmentItem()
			Me.setFloatingObjectBottomCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomCenterAlignmentItem()
			Me.setFloatingObjectBottomRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomRightAlignmentItem()
			Me.floatingObjectBringForwardSubItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardSubItem()
			Me.floatingObjectBringForwardItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardItem()
			Me.floatingObjectBringToFrontItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectBringToFrontItem()
			Me.floatingObjectBringInFrontOfTextItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectBringInFrontOfTextItem()
			Me.floatingObjectSendBackwardSubItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardSubItem()
			Me.floatingObjectSendBackwardItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardItem()
			Me.floatingObjectSendToBackItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectSendToBackItem()
			Me.floatingObjectSendBehindTextItem1 = New DevExpress.XtraRichEdit.UI.FloatingObjectSendBehindTextItem()
			Me.headerFooterToolsRibbonPageCategory1 = New DevExpress.XtraRichEdit.UI.HeaderFooterToolsRibbonPageCategory()
			Me.headerFooterToolsDesignRibbonPage1 = New DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignRibbonPage()
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignNavigationRibbonPageGroup()
			Me.headerFooterToolsDesignOptionsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignOptionsRibbonPageGroup()
			Me.headerFooterToolsDesignCloseRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignCloseRibbonPageGroup()
			Me.tableToolsRibbonPageCategory1 = New DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory()
			Me.tableDesignRibbonPage1 = New DevExpress.XtraRichEdit.UI.TableDesignRibbonPage()
			Me.tableStyleOptionsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableStyleOptionsRibbonPageGroup()
			Me.tableStylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup()
			Me.tableDrawBordersRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup()
			Me.tableLayoutRibbonPage1 = New DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage()
			Me.tableTableRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup()
			Me.tableRowsAndColumnsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup()
			Me.tableMergeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup()
			Me.tableCellSizeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup()
			Me.tableAlignmentRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup()
			Me.floatingPictureToolsRibbonPageCategory1 = New DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory()
			Me.floatingPictureToolsFormatPage1 = New DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage()
			Me.floatingPictureToolsShapeStylesPageGroup1 = New DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup()
			Me.floatingPictureToolsArrangePageGroup1 = New DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup()
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
			Me.referencesRibbonPage1 = New DevExpress.XtraRichEdit.UI.ReferencesRibbonPage()
			Me.tableOfContentsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup()
			Me.captionsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup()
			Me.mailingsRibbonPage1 = New DevExpress.XtraRichEdit.UI.MailingsRibbonPage()
			Me.mailMergeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup()
			Me.reviewRibbonPage1 = New DevExpress.XtraRichEdit.UI.ReviewRibbonPage()
			Me.documentProofingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentProofingRibbonPageGroup()
			Me.documentProtectionRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentProtectionRibbonPageGroup()
			Me.documentCommentRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentCommentRibbonPageGroup()
			Me.documentTrackingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentTrackingRibbonPageGroup()
			Me.viewRibbonPage1 = New DevExpress.XtraRichEdit.UI.ViewRibbonPage()
			Me.documentViewsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup()
			Me.showRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup()
			Me.zoomRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup()
			Me.ribbonImageCollectionLarge = New DevExpress.Utils.ImageCollection(Me.components)
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController(Me.components)
			Me.dockManager1 = New DevExpress.XtraBars.Docking.DockManager(Me.components)
			Me.dockPanel1 = New DevExpress.XtraBars.Docking.DockPanel()
			Me.dockPanel1_Container = New DevExpress.XtraBars.Docking.ControlContainer()
			Me.richEditCommentControl1 = New DevExpress.XtraRichEdit.RichEditCommentControl()
			Me.ribbonPage2 = New DevExpress.XtraBars.Ribbon.RibbonPage()
			DirectCast(Me.appMenu, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.ribbonImageCollection, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.repositoryItemBorderLineStyle1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.repositoryItemBorderLineWeight1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.repositoryItemFloatingObjectOutlineWeight1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.ribbonImageCollectionLarge, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.dockManager1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.dockPanel1.SuspendLayout()
			Me.dockPanel1_Container.SuspendLayout()
			Me.SuspendLayout()
			' 
			' stylesRibbonPageGroup1
			' 
			Me.stylesRibbonPageGroup1.ImageOptions.Image = (DirectCast(resources.GetObject("stylesRibbonPageGroup1.ImageOptions.Image"), System.Drawing.Image))
			Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.galleryChangeStyleItem1)
			Me.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1"
			Me.stylesRibbonPageGroup1.Text = ""
			' 
			' galleryChangeStyleItem1
			' 
			' 
			' 
			' 
			Me.galleryChangeStyleItem1.Gallery.ColumnCount = 10
			Me.galleryChangeStyleItem1.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { galleryItemGroup1})
			Me.galleryChangeStyleItem1.Gallery.ImageSize = New System.Drawing.Size(65, 46)
			Me.galleryChangeStyleItem1.Id = 64
			Me.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1"
			' 
			' appMenu
			' 
			Me.appMenu.Name = "appMenu"
			Me.appMenu.ShowRightPane = True
			' 
			' ribbonImageCollection
			' 
			Me.ribbonImageCollection.ImageStream = (DirectCast(resources.GetObject("ribbonImageCollection.ImageStream"), DevExpress.Utils.ImageCollectionStreamer))
			Me.ribbonImageCollection.Images.SetKeyName(0, "Ribbon_Exit_16x16.png")
			Me.ribbonImageCollection.Images.SetKeyName(1, "Ribbon_Content_16x16.png")
			Me.ribbonImageCollection.Images.SetKeyName(2, "Ribbon_Info_16x16.png")
			' 
			' richEditControl
			' 
			Me.richEditControl.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder
			Me.richEditControl.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl.Location = New System.Drawing.Point(0, 0)
			Me.richEditControl.Name = "richEditControl"
			Me.richEditControl.Size = New System.Drawing.Size(941, 610)
			Me.richEditControl.SpellChecker = Me.spellChecker
			Me.spellChecker.SetSpellCheckerOptions(Me.richEditControl, optionsSpelling1)
			Me.richEditControl.TabIndex = 1
			Me.richEditControl.Views.PrintLayoutView.AdjustColorsToSkins = True
			' 
			' spellChecker
			' 
			Me.spellChecker.Culture = New System.Globalization.CultureInfo("ru-RU")
			Me.spellChecker.ParentContainer = Nothing
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
			' pasteItem1
			' 
			Me.pasteItem1.Id = 18
			Me.pasteItem1.Name = "pasteItem1"
			' 
			' cutItem1
			' 
			Me.cutItem1.Id = 19
			Me.cutItem1.Name = "cutItem1"
			' 
			' copyItem1
			' 
			Me.copyItem1.Id = 20
			Me.copyItem1.Name = "copyItem1"
			' 
			' pasteSpecialItem1
			' 
			Me.pasteSpecialItem1.Id = 21
			Me.pasteSpecialItem1.Name = "pasteSpecialItem1"
			' 
			' barButtonGroup1
			' 
			Me.barButtonGroup1.Id = 11
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
			Me.changeFontNameItem1.Id = 22
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
			Me.changeFontSizeItem1.Id = 23
			Me.changeFontSizeItem1.Name = "changeFontSizeItem1"
			' 
			' repositoryItemRichEditFontSizeEdit1
			' 
			Me.repositoryItemRichEditFontSizeEdit1.AutoHeight = False
			Me.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemRichEditFontSizeEdit1.Control = Me.richEditControl
			Me.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1"
			' 
			' fontSizeIncreaseItem1
			' 
			Me.fontSizeIncreaseItem1.Id = 24
			Me.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1"
			' 
			' fontSizeDecreaseItem1
			' 
			Me.fontSizeDecreaseItem1.Id = 25
			Me.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1"
			' 
			' barButtonGroup2
			' 
			Me.barButtonGroup2.Id = 12
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
			Me.toggleFontBoldItem1.Id = 26
			Me.toggleFontBoldItem1.Name = "toggleFontBoldItem1"
			' 
			' toggleFontItalicItem1
			' 
			Me.toggleFontItalicItem1.Id = 27
			Me.toggleFontItalicItem1.Name = "toggleFontItalicItem1"
			' 
			' toggleFontUnderlineItem1
			' 
			Me.toggleFontUnderlineItem1.Id = 28
			Me.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1"
			' 
			' toggleFontDoubleUnderlineItem1
			' 
			Me.toggleFontDoubleUnderlineItem1.Id = 29
			Me.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1"
			' 
			' toggleFontStrikeoutItem1
			' 
			Me.toggleFontStrikeoutItem1.Id = 30
			Me.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1"
			' 
			' toggleFontDoubleStrikeoutItem1
			' 
			Me.toggleFontDoubleStrikeoutItem1.Id = 31
			Me.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1"
			' 
			' toggleFontSuperscriptItem1
			' 
			Me.toggleFontSuperscriptItem1.Id = 32
			Me.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1"
			' 
			' toggleFontSubscriptItem1
			' 
			Me.toggleFontSubscriptItem1.Id = 33
			Me.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1"
			' 
			' barButtonGroup3
			' 
			Me.barButtonGroup3.Id = 13
			Me.barButtonGroup3.ItemLinks.Add(Me.changeFontColorItem1, "FC")
			Me.barButtonGroup3.ItemLinks.Add(Me.changeFontHighlightColorItem1, "I")
			Me.barButtonGroup3.Name = "barButtonGroup3"
			Me.barButtonGroup3.Tag = "{DF8C5334-EDE3-47c9-A42C-FE9A9247E180}"
			' 
			' changeFontColorItem1
			' 
			Me.changeFontColorItem1.Id = 34
			Me.changeFontColorItem1.Name = "changeFontColorItem1"
			' 
			' changeFontHighlightColorItem1
			' 
			Me.changeFontHighlightColorItem1.Id = 35
			Me.changeFontHighlightColorItem1.Name = "changeFontHighlightColorItem1"
			' 
			' changeTextCaseItem1
			' 
			Me.changeTextCaseItem1.Id = 36
			Me.changeTextCaseItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextUpperCaseItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextLowerCaseItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.capitalizeEachWordCaseItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTextCaseItem1)
			})
			Me.changeTextCaseItem1.Name = "changeTextCaseItem1"
			' 
			' makeTextUpperCaseItem1
			' 
			Me.makeTextUpperCaseItem1.Id = 37
			Me.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1"
			' 
			' makeTextLowerCaseItem1
			' 
			Me.makeTextLowerCaseItem1.Id = 38
			Me.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1"
			' 
			' capitalizeEachWordCaseItem1
			' 
			Me.capitalizeEachWordCaseItem1.Id = 39
			Me.capitalizeEachWordCaseItem1.Name = "capitalizeEachWordCaseItem1"
			' 
			' toggleTextCaseItem1
			' 
			Me.toggleTextCaseItem1.Id = 40
			Me.toggleTextCaseItem1.Name = "toggleTextCaseItem1"
			' 
			' clearFormattingItem1
			' 
			Me.clearFormattingItem1.Id = 41
			Me.clearFormattingItem1.Name = "clearFormattingItem1"
			' 
			' barButtonGroup4
			' 
			Me.barButtonGroup4.Id = 14
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleBulletedListItem1, "U")
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleNumberingListItem1, "N")
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleMultiLevelListItem1, "M")
			Me.barButtonGroup4.Name = "barButtonGroup4"
			Me.barButtonGroup4.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}"
			' 
			' toggleBulletedListItem1
			' 
			Me.toggleBulletedListItem1.Id = 42
			Me.toggleBulletedListItem1.Name = "toggleBulletedListItem1"
			' 
			' toggleNumberingListItem1
			' 
			Me.toggleNumberingListItem1.Id = 43
			Me.toggleNumberingListItem1.Name = "toggleNumberingListItem1"
			' 
			' toggleMultiLevelListItem1
			' 
			Me.toggleMultiLevelListItem1.Id = 44
			Me.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1"
			' 
			' barButtonGroup5
			' 
			Me.barButtonGroup5.Id = 15
			Me.barButtonGroup5.ItemLinks.Add(Me.decreaseIndentItem1, "AO")
			Me.barButtonGroup5.ItemLinks.Add(Me.increaseIndentItem1, "AI")
			Me.barButtonGroup5.ItemLinks.Add(Me.toggleParagraphLeftToRightItem1)
			Me.barButtonGroup5.ItemLinks.Add(Me.toggleParagraphRightToLeftItem1)
			Me.barButtonGroup5.ItemLinks.Add(Me.toggleShowWhitespaceItem1)
			Me.barButtonGroup5.Name = "barButtonGroup5"
			Me.barButtonGroup5.Tag = "{4747D5AB-2BEB-4ea6-9A1D-8E4FB36F1B40}"
			' 
			' decreaseIndentItem1
			' 
			Me.decreaseIndentItem1.Id = 45
			Me.decreaseIndentItem1.Name = "decreaseIndentItem1"
			' 
			' increaseIndentItem1
			' 
			Me.increaseIndentItem1.Id = 46
			Me.increaseIndentItem1.Name = "increaseIndentItem1"
			' 
			' toggleParagraphLeftToRightItem1
			' 
			Me.toggleParagraphLeftToRightItem1.Id = 47
			Me.toggleParagraphLeftToRightItem1.Name = "toggleParagraphLeftToRightItem1"
			' 
			' toggleParagraphRightToLeftItem1
			' 
			Me.toggleParagraphRightToLeftItem1.Id = 48
			Me.toggleParagraphRightToLeftItem1.Name = "toggleParagraphRightToLeftItem1"
			' 
			' toggleShowWhitespaceItem1
			' 
			Me.toggleShowWhitespaceItem1.Id = 53
			Me.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1"
			' 
			' barButtonGroup6
			' 
			Me.barButtonGroup6.Id = 16
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentLeftItem1, "AL")
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentCenterItem1, "AC")
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentRightItem1, "AR")
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentJustifyItem1, "AJ")
			Me.barButtonGroup6.Name = "barButtonGroup6"
			Me.barButtonGroup6.Tag = "{8E89E775-996E-49a0-AADA-DE338E34732E}"
			' 
			' toggleParagraphAlignmentLeftItem1
			' 
			Me.toggleParagraphAlignmentLeftItem1.Id = 49
			Me.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1"
			' 
			' toggleParagraphAlignmentCenterItem1
			' 
			Me.toggleParagraphAlignmentCenterItem1.Id = 50
			Me.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1"
			' 
			' toggleParagraphAlignmentRightItem1
			' 
			Me.toggleParagraphAlignmentRightItem1.Id = 51
			Me.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1"
			' 
			' toggleParagraphAlignmentJustifyItem1
			' 
			Me.toggleParagraphAlignmentJustifyItem1.Id = 52
			Me.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1"
			' 
			' barButtonGroup7
			' 
			Me.barButtonGroup7.Id = 17
			Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphLineSpacingItem1, "K")
			Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphBackColorItem1, "H")
			Me.barButtonGroup7.Name = "barButtonGroup7"
			Me.barButtonGroup7.Tag = "{9A8DEAD8-3890-4857-A395-EC625FD02217}"
			' 
			' changeParagraphLineSpacingItem1
			' 
			Me.changeParagraphLineSpacingItem1.Id = 54
			Me.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSingleParagraphSpacingItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSesquialteralParagraphSpacingItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setDoubleParagraphSpacingItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.showLineSpacingFormItem1),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.addSpacingBeforeParagraphItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "B", ""),
				New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingBeforeParagraphItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingAfterParagraphItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingAfterParagraphItem1)
			})
			Me.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1"
			' 
			' setSingleParagraphSpacingItem1
			' 
			Me.setSingleParagraphSpacingItem1.Id = 55
			Me.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1"
			' 
			' setSesquialteralParagraphSpacingItem1
			' 
			Me.setSesquialteralParagraphSpacingItem1.Id = 56
			Me.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1"
			' 
			' setDoubleParagraphSpacingItem1
			' 
			Me.setDoubleParagraphSpacingItem1.Id = 57
			Me.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1"
			' 
			' showLineSpacingFormItem1
			' 
			Me.showLineSpacingFormItem1.Id = 58
			Me.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1"
			' 
			' addSpacingBeforeParagraphItem1
			' 
			Me.addSpacingBeforeParagraphItem1.Id = 59
			Me.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1"
			' 
			' removeSpacingBeforeParagraphItem1
			' 
			Me.removeSpacingBeforeParagraphItem1.Id = 60
			Me.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1"
			' 
			' addSpacingAfterParagraphItem1
			' 
			Me.addSpacingAfterParagraphItem1.Id = 61
			Me.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1"
			' 
			' removeSpacingAfterParagraphItem1
			' 
			Me.removeSpacingAfterParagraphItem1.Id = 62
			Me.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1"
			' 
			' changeParagraphBackColorItem1
			' 
			Me.changeParagraphBackColorItem1.Id = 63
			Me.changeParagraphBackColorItem1.Name = "changeParagraphBackColorItem1"
			' 
			' findItem1
			' 
			Me.findItem1.Id = 65
			Me.findItem1.Name = "findItem1"
			' 
			' replaceItem1
			' 
			Me.replaceItem1.Id = 66
			Me.replaceItem1.Name = "replaceItem1"
			' 
			' insertPageBreakItem21
			' 
			Me.insertPageBreakItem21.Id = 67
			Me.insertPageBreakItem21.Name = "insertPageBreakItem21"
			' 
			' insertTableItem1
			' 
			Me.insertTableItem1.Id = 68
			Me.insertTableItem1.Name = "insertTableItem1"
			' 
			' insertFloatingPictureItem1
			' 
			Me.insertFloatingPictureItem1.Id = 69
			Me.insertFloatingPictureItem1.Name = "insertFloatingPictureItem1"
			' 
			' insertBookmarkItem1
			' 
			Me.insertBookmarkItem1.Id = 70
			Me.insertBookmarkItem1.Name = "insertBookmarkItem1"
			' 
			' insertHyperlinkItem1
			' 
			Me.insertHyperlinkItem1.Id = 71
			Me.insertHyperlinkItem1.Name = "insertHyperlinkItem1"
			' 
			' editPageHeaderItem1
			' 
			Me.editPageHeaderItem1.Id = 72
			Me.editPageHeaderItem1.Name = "editPageHeaderItem1"
			' 
			' editPageFooterItem1
			' 
			Me.editPageFooterItem1.Id = 73
			Me.editPageFooterItem1.Name = "editPageFooterItem1"
			' 
			' insertPageNumberItem1
			' 
			Me.insertPageNumberItem1.Id = 74
			Me.insertPageNumberItem1.Name = "insertPageNumberItem1"
			' 
			' insertPageCountItem1
			' 
			Me.insertPageCountItem1.Id = 75
			Me.insertPageCountItem1.Name = "insertPageCountItem1"
			' 
			' insertTextBoxItem1
			' 
			Me.insertTextBoxItem1.Id = 76
			Me.insertTextBoxItem1.Name = "insertTextBoxItem1"
			' 
			' insertSymbolItem1
			' 
			Me.insertSymbolItem1.Id = 77
			Me.insertSymbolItem1.Name = "insertSymbolItem1"
			' 
			' changeSectionPageMarginsItem1
			' 
			Me.changeSectionPageMarginsItem1.Id = 78
			Me.changeSectionPageMarginsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setNormalSectionPageMarginsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setNarrowSectionPageMarginsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setModerateSectionPageMarginsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setWideSectionPageMarginsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.showPageMarginsSetupFormItem1, True)
			})
			Me.changeSectionPageMarginsItem1.Name = "changeSectionPageMarginsItem1"
			' 
			' setNormalSectionPageMarginsItem1
			' 
			Me.setNormalSectionPageMarginsItem1.Id = 79
			Me.setNormalSectionPageMarginsItem1.Name = "setNormalSectionPageMarginsItem1"
			' 
			' setNarrowSectionPageMarginsItem1
			' 
			Me.setNarrowSectionPageMarginsItem1.Id = 80
			Me.setNarrowSectionPageMarginsItem1.Name = "setNarrowSectionPageMarginsItem1"
			' 
			' setModerateSectionPageMarginsItem1
			' 
			Me.setModerateSectionPageMarginsItem1.Id = 81
			Me.setModerateSectionPageMarginsItem1.Name = "setModerateSectionPageMarginsItem1"
			' 
			' setWideSectionPageMarginsItem1
			' 
			Me.setWideSectionPageMarginsItem1.Id = 82
			Me.setWideSectionPageMarginsItem1.Name = "setWideSectionPageMarginsItem1"
			' 
			' showPageMarginsSetupFormItem1
			' 
			Me.showPageMarginsSetupFormItem1.Id = 83
			Me.showPageMarginsSetupFormItem1.Name = "showPageMarginsSetupFormItem1"
			' 
			' changeSectionPageOrientationItem1
			' 
			Me.changeSectionPageOrientationItem1.Id = 84
			Me.changeSectionPageOrientationItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setPortraitPageOrientationItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setLandscapePageOrientationItem1)
			})
			Me.changeSectionPageOrientationItem1.Name = "changeSectionPageOrientationItem1"
			' 
			' setPortraitPageOrientationItem1
			' 
			Me.setPortraitPageOrientationItem1.Id = 85
			Me.setPortraitPageOrientationItem1.Name = "setPortraitPageOrientationItem1"
			' 
			' setLandscapePageOrientationItem1
			' 
			Me.setLandscapePageOrientationItem1.Id = 86
			Me.setLandscapePageOrientationItem1.Name = "setLandscapePageOrientationItem1"
			' 
			' changeSectionPaperKindItem1
			' 
			Me.changeSectionPaperKindItem1.Id = 87
			Me.changeSectionPaperKindItem1.Name = "changeSectionPaperKindItem1"
			' 
			' changeSectionColumnsItem1
			' 
			Me.changeSectionColumnsItem1.Id = 88
			Me.changeSectionColumnsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionOneColumnItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionTwoColumnsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionThreeColumnsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.showColumnsSetupFormItem1, True)
			})
			Me.changeSectionColumnsItem1.Name = "changeSectionColumnsItem1"
			' 
			' setSectionOneColumnItem1
			' 
			Me.setSectionOneColumnItem1.Id = 89
			Me.setSectionOneColumnItem1.Name = "setSectionOneColumnItem1"
			' 
			' setSectionTwoColumnsItem1
			' 
			Me.setSectionTwoColumnsItem1.Id = 90
			Me.setSectionTwoColumnsItem1.Name = "setSectionTwoColumnsItem1"
			' 
			' setSectionThreeColumnsItem1
			' 
			Me.setSectionThreeColumnsItem1.Id = 91
			Me.setSectionThreeColumnsItem1.Name = "setSectionThreeColumnsItem1"
			' 
			' showColumnsSetupFormItem1
			' 
			Me.showColumnsSetupFormItem1.Id = 92
			Me.showColumnsSetupFormItem1.Name = "showColumnsSetupFormItem1"
			' 
			' insertBreakItem1
			' 
			Me.insertBreakItem1.Id = 93
			Me.insertBreakItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.insertPageBreakItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "B", ""),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertColumnBreakItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakNextPageItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakContinuousItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakEvenPageItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakOddPageItem1)
			})
			Me.insertBreakItem1.Name = "insertBreakItem1"
			' 
			' insertPageBreakItem1
			' 
			Me.insertPageBreakItem1.Id = 94
			Me.insertPageBreakItem1.Name = "insertPageBreakItem1"
			' 
			' insertColumnBreakItem1
			' 
			Me.insertColumnBreakItem1.Id = 95
			Me.insertColumnBreakItem1.Name = "insertColumnBreakItem1"
			' 
			' insertSectionBreakNextPageItem1
			' 
			Me.insertSectionBreakNextPageItem1.Id = 96
			Me.insertSectionBreakNextPageItem1.Name = "insertSectionBreakNextPageItem1"
			' 
			' insertSectionBreakContinuousItem1
			' 
			Me.insertSectionBreakContinuousItem1.Id = 97
			Me.insertSectionBreakContinuousItem1.Name = "insertSectionBreakContinuousItem1"
			' 
			' insertSectionBreakEvenPageItem1
			' 
			Me.insertSectionBreakEvenPageItem1.Id = 98
			Me.insertSectionBreakEvenPageItem1.Name = "insertSectionBreakEvenPageItem1"
			' 
			' insertSectionBreakOddPageItem1
			' 
			Me.insertSectionBreakOddPageItem1.Id = 99
			Me.insertSectionBreakOddPageItem1.Name = "insertSectionBreakOddPageItem1"
			' 
			' changeSectionLineNumberingItem1
			' 
			Me.changeSectionLineNumberingItem1.Id = 100
			Me.changeSectionLineNumberingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingNoneItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingContinuousItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingRestartNewPageItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setSectionLineNumberingRestartNewSectionItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleParagraphSuppressLineNumbersItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.showLineNumberingFormItem1, True)
			})
			Me.changeSectionLineNumberingItem1.Name = "changeSectionLineNumberingItem1"
			' 
			' setSectionLineNumberingNoneItem1
			' 
			Me.setSectionLineNumberingNoneItem1.Id = 101
			Me.setSectionLineNumberingNoneItem1.Name = "setSectionLineNumberingNoneItem1"
			' 
			' setSectionLineNumberingContinuousItem1
			' 
			Me.setSectionLineNumberingContinuousItem1.Id = 102
			Me.setSectionLineNumberingContinuousItem1.Name = "setSectionLineNumberingContinuousItem1"
			' 
			' setSectionLineNumberingRestartNewPageItem1
			' 
			Me.setSectionLineNumberingRestartNewPageItem1.Id = 103
			Me.setSectionLineNumberingRestartNewPageItem1.Name = "setSectionLineNumberingRestartNewPageItem1"
			' 
			' setSectionLineNumberingRestartNewSectionItem1
			' 
			Me.setSectionLineNumberingRestartNewSectionItem1.Id = 104
			Me.setSectionLineNumberingRestartNewSectionItem1.Name = "setSectionLineNumberingRestartNewSectionItem1"
			' 
			' toggleParagraphSuppressLineNumbersItem1
			' 
			Me.toggleParagraphSuppressLineNumbersItem1.Id = 105
			Me.toggleParagraphSuppressLineNumbersItem1.Name = "toggleParagraphSuppressLineNumbersItem1"
			' 
			' showLineNumberingFormItem1
			' 
			Me.showLineNumberingFormItem1.Id = 106
			Me.showLineNumberingFormItem1.Name = "showLineNumberingFormItem1"
			' 
			' changePageColorItem1
			' 
			Me.changePageColorItem1.Id = 107
			Me.changePageColorItem1.Name = "changePageColorItem1"
			' 
			' insertTableOfContentsItem1
			' 
			Me.insertTableOfContentsItem1.Id = 108
			Me.insertTableOfContentsItem1.Name = "insertTableOfContentsItem1"
			' 
			' updateTableOfContentsItem1
			' 
			Me.updateTableOfContentsItem1.Id = 109
			Me.updateTableOfContentsItem1.Name = "updateTableOfContentsItem1"
			' 
			' addParagraphsToTableOfContentItem1
			' 
			Me.addParagraphsToTableOfContentItem1.Id = 110
			Me.addParagraphsToTableOfContentItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem2),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem3),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem4),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem5),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem6),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem7),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem8),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem9),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem10)
			})
			Me.addParagraphsToTableOfContentItem1.Name = "addParagraphsToTableOfContentItem1"
			' 
			' setParagraphHeadingLevelItem1
			' 
			Me.setParagraphHeadingLevelItem1.Id = 111
			Me.setParagraphHeadingLevelItem1.Name = "setParagraphHeadingLevelItem1"
			Me.setParagraphHeadingLevelItem1.OutlineLevel = 0
			' 
			' setParagraphHeadingLevelItem2
			' 
			Me.setParagraphHeadingLevelItem2.Id = 112
			Me.setParagraphHeadingLevelItem2.Name = "setParagraphHeadingLevelItem2"
			Me.setParagraphHeadingLevelItem2.OutlineLevel = 1
			' 
			' setParagraphHeadingLevelItem3
			' 
			Me.setParagraphHeadingLevelItem3.Id = 113
			Me.setParagraphHeadingLevelItem3.Name = "setParagraphHeadingLevelItem3"
			Me.setParagraphHeadingLevelItem3.OutlineLevel = 2
			' 
			' setParagraphHeadingLevelItem4
			' 
			Me.setParagraphHeadingLevelItem4.Id = 114
			Me.setParagraphHeadingLevelItem4.Name = "setParagraphHeadingLevelItem4"
			Me.setParagraphHeadingLevelItem4.OutlineLevel = 3
			' 
			' setParagraphHeadingLevelItem5
			' 
			Me.setParagraphHeadingLevelItem5.Id = 115
			Me.setParagraphHeadingLevelItem5.Name = "setParagraphHeadingLevelItem5"
			Me.setParagraphHeadingLevelItem5.OutlineLevel = 4
			' 
			' setParagraphHeadingLevelItem6
			' 
			Me.setParagraphHeadingLevelItem6.Id = 116
			Me.setParagraphHeadingLevelItem6.Name = "setParagraphHeadingLevelItem6"
			Me.setParagraphHeadingLevelItem6.OutlineLevel = 5
			' 
			' setParagraphHeadingLevelItem7
			' 
			Me.setParagraphHeadingLevelItem7.Id = 117
			Me.setParagraphHeadingLevelItem7.Name = "setParagraphHeadingLevelItem7"
			Me.setParagraphHeadingLevelItem7.OutlineLevel = 6
			' 
			' setParagraphHeadingLevelItem8
			' 
			Me.setParagraphHeadingLevelItem8.Id = 118
			Me.setParagraphHeadingLevelItem8.Name = "setParagraphHeadingLevelItem8"
			Me.setParagraphHeadingLevelItem8.OutlineLevel = 7
			' 
			' setParagraphHeadingLevelItem9
			' 
			Me.setParagraphHeadingLevelItem9.Id = 119
			Me.setParagraphHeadingLevelItem9.Name = "setParagraphHeadingLevelItem9"
			Me.setParagraphHeadingLevelItem9.OutlineLevel = 8
			' 
			' setParagraphHeadingLevelItem10
			' 
			Me.setParagraphHeadingLevelItem10.Id = 120
			Me.setParagraphHeadingLevelItem10.Name = "setParagraphHeadingLevelItem10"
			Me.setParagraphHeadingLevelItem10.OutlineLevel = 9
			' 
			' insertCaptionPlaceholderItem1
			' 
			Me.insertCaptionPlaceholderItem1.Id = 121
			Me.insertCaptionPlaceholderItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertFiguresCaptionItems1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertTablesCaptionItems1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertEquationsCaptionItems1)
			})
			Me.insertCaptionPlaceholderItem1.Name = "insertCaptionPlaceholderItem1"
			' 
			' insertFiguresCaptionItems1
			' 
			Me.insertFiguresCaptionItems1.Id = 122
			Me.insertFiguresCaptionItems1.Name = "insertFiguresCaptionItems1"
			' 
			' insertTablesCaptionItems1
			' 
			Me.insertTablesCaptionItems1.Id = 123
			Me.insertTablesCaptionItems1.Name = "insertTablesCaptionItems1"
			' 
			' insertEquationsCaptionItems1
			' 
			Me.insertEquationsCaptionItems1.Id = 124
			Me.insertEquationsCaptionItems1.Name = "insertEquationsCaptionItems1"
			' 
			' insertTableOfFiguresPlaceholderItem1
			' 
			Me.insertTableOfFiguresPlaceholderItem1.Id = 125
			Me.insertTableOfFiguresPlaceholderItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfFiguresItems1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfTablesItems1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfEquationsItems1)
			})
			Me.insertTableOfFiguresPlaceholderItem1.Name = "insertTableOfFiguresPlaceholderItem1"
			' 
			' insertTableOfFiguresItems1
			' 
			Me.insertTableOfFiguresItems1.Id = 126
			Me.insertTableOfFiguresItems1.Name = "insertTableOfFiguresItems1"
			' 
			' insertTableOfTablesItems1
			' 
			Me.insertTableOfTablesItems1.Id = 127
			Me.insertTableOfTablesItems1.Name = "insertTableOfTablesItems1"
			' 
			' insertTableOfEquationsItems1
			' 
			Me.insertTableOfEquationsItems1.Id = 128
			Me.insertTableOfEquationsItems1.Name = "insertTableOfEquationsItems1"
			' 
			' updateTableOfFiguresItem1
			' 
			Me.updateTableOfFiguresItem1.Id = 129
			Me.updateTableOfFiguresItem1.Name = "updateTableOfFiguresItem1"
			' 
			' insertMergeFieldItem1
			' 
			Me.insertMergeFieldItem1.Id = 130
			Me.insertMergeFieldItem1.Name = "insertMergeFieldItem1"
			' 
			' showAllFieldCodesItem1
			' 
			Me.showAllFieldCodesItem1.Id = 131
			Me.showAllFieldCodesItem1.Name = "showAllFieldCodesItem1"
			' 
			' showAllFieldResultsItem1
			' 
			Me.showAllFieldResultsItem1.Id = 132
			Me.showAllFieldResultsItem1.Name = "showAllFieldResultsItem1"
			' 
			' toggleViewMergedDataItem1
			' 
			Me.toggleViewMergedDataItem1.Id = 133
			Me.toggleViewMergedDataItem1.Name = "toggleViewMergedDataItem1"
			' 
			' checkSpellingItem1
			' 
			Me.checkSpellingItem1.Id = 134
			Me.checkSpellingItem1.Name = "checkSpellingItem1"
			' 
			' changeLanguageItem1
			' 
			Me.changeLanguageItem1.Id = 135
			Me.changeLanguageItem1.Name = "changeLanguageItem1"
			' 
			' protectDocumentItem1
			' 
			Me.protectDocumentItem1.Id = 136
			Me.protectDocumentItem1.Name = "protectDocumentItem1"
			' 
			' changeRangeEditingPermissionsItem1
			' 
			Me.changeRangeEditingPermissionsItem1.Id = 137
			Me.changeRangeEditingPermissionsItem1.Name = "changeRangeEditingPermissionsItem1"
			' 
			' unprotectDocumentItem1
			' 
			Me.unprotectDocumentItem1.Id = 138
			Me.unprotectDocumentItem1.Name = "unprotectDocumentItem1"
			' 
			' newCommentItem1
			' 
			Me.newCommentItem1.Id = 139
			Me.newCommentItem1.Name = "newCommentItem1"
			' 
			' deleteCommentsItem1
			' 
			Me.deleteCommentsItem1.Id = 140
			Me.deleteCommentsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteOneCommentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteAllCommentsShownItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteAllCommentsItem1)
			})
			Me.deleteCommentsItem1.Name = "deleteCommentsItem1"
			' 
			' deleteOneCommentItem1
			' 
			Me.deleteOneCommentItem1.Id = 141
			Me.deleteOneCommentItem1.Name = "deleteOneCommentItem1"
			' 
			' deleteAllCommentsShownItem1
			' 
			Me.deleteAllCommentsShownItem1.Id = 142
			Me.deleteAllCommentsShownItem1.Name = "deleteAllCommentsShownItem1"
			' 
			' deleteAllCommentsItem1
			' 
			Me.deleteAllCommentsItem1.Id = 143
			Me.deleteAllCommentsItem1.Name = "deleteAllCommentsItem1"
			' 
			' previousCommentItem1
			' 
			Me.previousCommentItem1.Id = 144
			Me.previousCommentItem1.Name = "previousCommentItem1"
			' 
			' nextCommentItem1
			' 
			Me.nextCommentItem1.Id = 145
			Me.nextCommentItem1.Name = "nextCommentItem1"
			' 
			' changeCommentItem1
			' 
			Me.changeCommentItem1.Id = 146
			Me.changeCommentItem1.Name = "changeCommentItem1"
			' 
			' reviewersItem1
			' 
			Me.reviewersItem1.Id = 147
			Me.reviewersItem1.Name = "reviewersItem1"
			' 
			' reviewingPaneItem1
			' 
			Me.reviewingPaneItem1.Id = 148
			Me.reviewingPaneItem1.Name = "reviewingPaneItem1"
			' 
			' switchToSimpleViewItem1
			' 
			Me.switchToSimpleViewItem1.Id = 149
			Me.switchToSimpleViewItem1.Name = "switchToSimpleViewItem1"
			' 
			' switchToDraftViewItem1
			' 
			Me.switchToDraftViewItem1.Id = 150
			Me.switchToDraftViewItem1.Name = "switchToDraftViewItem1"
			' 
			' switchToPrintLayoutViewItem1
			' 
			Me.switchToPrintLayoutViewItem1.Id = 151
			Me.switchToPrintLayoutViewItem1.Name = "switchToPrintLayoutViewItem1"
			' 
			' toggleShowHorizontalRulerItem1
			' 
			Me.toggleShowHorizontalRulerItem1.Id = 152
			Me.toggleShowHorizontalRulerItem1.Name = "toggleShowHorizontalRulerItem1"
			' 
			' toggleShowVerticalRulerItem1
			' 
			Me.toggleShowVerticalRulerItem1.Id = 153
			Me.toggleShowVerticalRulerItem1.Name = "toggleShowVerticalRulerItem1"
			' 
			' zoomOutItem1
			' 
			Me.zoomOutItem1.Id = 154
			Me.zoomOutItem1.Name = "zoomOutItem1"
			' 
			' zoomInItem1
			' 
			Me.zoomInItem1.Id = 155
			Me.zoomInItem1.Name = "zoomInItem1"
			' 
			' goToPageHeaderItem1
			' 
			Me.goToPageHeaderItem1.Id = 156
			Me.goToPageHeaderItem1.Name = "goToPageHeaderItem1"
			' 
			' goToPageFooterItem1
			' 
			Me.goToPageFooterItem1.Id = 157
			Me.goToPageFooterItem1.Name = "goToPageFooterItem1"
			' 
			' goToNextHeaderFooterItem1
			' 
			Me.goToNextHeaderFooterItem1.Id = 158
			Me.goToNextHeaderFooterItem1.Name = "goToNextHeaderFooterItem1"
			' 
			' goToPreviousHeaderFooterItem1
			' 
			Me.goToPreviousHeaderFooterItem1.Id = 159
			Me.goToPreviousHeaderFooterItem1.Name = "goToPreviousHeaderFooterItem1"
			' 
			' toggleLinkToPreviousItem1
			' 
			Me.toggleLinkToPreviousItem1.Id = 160
			Me.toggleLinkToPreviousItem1.Name = "toggleLinkToPreviousItem1"
			' 
			' toggleDifferentFirstPageItem1
			' 
			Me.toggleDifferentFirstPageItem1.Id = 161
			Me.toggleDifferentFirstPageItem1.Name = "toggleDifferentFirstPageItem1"
			' 
			' toggleDifferentOddAndEvenPagesItem1
			' 
			Me.toggleDifferentOddAndEvenPagesItem1.Id = 162
			Me.toggleDifferentOddAndEvenPagesItem1.Name = "toggleDifferentOddAndEvenPagesItem1"
			' 
			' closePageHeaderFooterItem1
			' 
			Me.closePageHeaderFooterItem1.Id = 163
			Me.closePageHeaderFooterItem1.Name = "closePageHeaderFooterItem1"
			' 
			' toggleFirstRowItem1
			' 
			Me.toggleFirstRowItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleFirstRowItem1.Id = 164
			Me.toggleFirstRowItem1.Name = "toggleFirstRowItem1"
			' 
			' toggleLastRowItem1
			' 
			Me.toggleLastRowItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleLastRowItem1.Id = 165
			Me.toggleLastRowItem1.Name = "toggleLastRowItem1"
			' 
			' toggleBandedRowsItem1
			' 
			Me.toggleBandedRowsItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleBandedRowsItem1.Id = 166
			Me.toggleBandedRowsItem1.Name = "toggleBandedRowsItem1"
			' 
			' toggleFirstColumnItem1
			' 
			Me.toggleFirstColumnItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleFirstColumnItem1.Id = 167
			Me.toggleFirstColumnItem1.Name = "toggleFirstColumnItem1"
			' 
			' toggleLastColumnItem1
			' 
			Me.toggleLastColumnItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleLastColumnItem1.Id = 168
			Me.toggleLastColumnItem1.Name = "toggleLastColumnItem1"
			' 
			' toggleBandedColumnsItem1
			' 
			Me.toggleBandedColumnsItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText
			Me.toggleBandedColumnsItem1.Id = 169
			Me.toggleBandedColumnsItem1.Name = "toggleBandedColumnsItem1"
			' 
			' galleryChangeTableStyleItem1
			' 
			Me.galleryChangeTableStyleItem1.CurrentItem = Nothing
			Me.galleryChangeTableStyleItem1.DeleteItemLink = Nothing
			' 
			' 
			' 
			Me.galleryChangeTableStyleItem1.Gallery.ColumnCount = 3
			Me.galleryChangeTableStyleItem1.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { galleryItemGroup2})
			Me.galleryChangeTableStyleItem1.Gallery.ImageSize = New System.Drawing.Size(65, 46)
			Me.galleryChangeTableStyleItem1.Id = 170
			Me.galleryChangeTableStyleItem1.ModifyItemLink = Nothing
			Me.galleryChangeTableStyleItem1.Name = "galleryChangeTableStyleItem1"
			Me.galleryChangeTableStyleItem1.NewItemLink = Nothing
			Me.galleryChangeTableStyleItem1.PopupGallery = Nothing
			' 
			' changeTableBorderLineStyleItem1
			' 
			Me.changeTableBorderLineStyleItem1.Edit = Me.repositoryItemBorderLineStyle1
			Me.changeTableBorderLineStyleItem1.EditWidth = 130
			Me.changeTableBorderLineStyleItem1.Id = 171
			Me.changeTableBorderLineStyleItem1.Name = "changeTableBorderLineStyleItem1"
			' 
			' repositoryItemBorderLineStyle1
			' 
			Me.repositoryItemBorderLineStyle1.AutoHeight = False
			Me.repositoryItemBorderLineStyle1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemBorderLineStyle1.Control = Me.richEditControl
			Me.repositoryItemBorderLineStyle1.Name = "repositoryItemBorderLineStyle1"
			' 
			' changeTableBorderLineWeightItem1
			' 
			Me.changeTableBorderLineWeightItem1.Edit = Me.repositoryItemBorderLineWeight1
			Me.changeTableBorderLineWeightItem1.EditValue = 20
			Me.changeTableBorderLineWeightItem1.EditWidth = 130
			Me.changeTableBorderLineWeightItem1.Id = 172
			Me.changeTableBorderLineWeightItem1.Name = "changeTableBorderLineWeightItem1"
			' 
			' repositoryItemBorderLineWeight1
			' 
			Me.repositoryItemBorderLineWeight1.AutoHeight = False
			Me.repositoryItemBorderLineWeight1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemBorderLineWeight1.Control = Me.richEditControl
			Me.repositoryItemBorderLineWeight1.Name = "repositoryItemBorderLineWeight1"
			' 
			' changeTableBorderColorItem1
			' 
			Me.changeTableBorderColorItem1.Id = 173
			Me.changeTableBorderColorItem1.Name = "changeTableBorderColorItem1"
			' 
			' changeTableBordersItem1
			' 
			Me.changeTableBordersItem1.Id = 174
			Me.changeTableBordersItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsBottomBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsTopBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsLeftBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsRightBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.resetTableCellsAllBordersItem1, True),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsAllBordersItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsOutsideBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideHorizontalBorderItem1, True),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideVerticalBorderItem1),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.toggleShowTableGridLinesItem1, "", True, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "TG", "")
			})
			Me.changeTableBordersItem1.Name = "changeTableBordersItem1"
			' 
			' toggleTableCellsBottomBorderItem1
			' 
			Me.toggleTableCellsBottomBorderItem1.Id = 175
			Me.toggleTableCellsBottomBorderItem1.Name = "toggleTableCellsBottomBorderItem1"
			' 
			' toggleTableCellsTopBorderItem1
			' 
			Me.toggleTableCellsTopBorderItem1.Id = 176
			Me.toggleTableCellsTopBorderItem1.Name = "toggleTableCellsTopBorderItem1"
			' 
			' toggleTableCellsLeftBorderItem1
			' 
			Me.toggleTableCellsLeftBorderItem1.Id = 177
			Me.toggleTableCellsLeftBorderItem1.Name = "toggleTableCellsLeftBorderItem1"
			' 
			' toggleTableCellsRightBorderItem1
			' 
			Me.toggleTableCellsRightBorderItem1.Id = 178
			Me.toggleTableCellsRightBorderItem1.Name = "toggleTableCellsRightBorderItem1"
			' 
			' resetTableCellsAllBordersItem1
			' 
			Me.resetTableCellsAllBordersItem1.Id = 179
			Me.resetTableCellsAllBordersItem1.Name = "resetTableCellsAllBordersItem1"
			' 
			' toggleTableCellsAllBordersItem1
			' 
			Me.toggleTableCellsAllBordersItem1.Id = 180
			Me.toggleTableCellsAllBordersItem1.Name = "toggleTableCellsAllBordersItem1"
			' 
			' toggleTableCellsOutsideBorderItem1
			' 
			Me.toggleTableCellsOutsideBorderItem1.Id = 181
			Me.toggleTableCellsOutsideBorderItem1.Name = "toggleTableCellsOutsideBorderItem1"
			' 
			' toggleTableCellsInsideBorderItem1
			' 
			Me.toggleTableCellsInsideBorderItem1.Id = 182
			Me.toggleTableCellsInsideBorderItem1.Name = "toggleTableCellsInsideBorderItem1"
			' 
			' toggleTableCellsInsideHorizontalBorderItem1
			' 
			Me.toggleTableCellsInsideHorizontalBorderItem1.Id = 183
			Me.toggleTableCellsInsideHorizontalBorderItem1.Name = "toggleTableCellsInsideHorizontalBorderItem1"
			' 
			' toggleTableCellsInsideVerticalBorderItem1
			' 
			Me.toggleTableCellsInsideVerticalBorderItem1.Id = 184
			Me.toggleTableCellsInsideVerticalBorderItem1.Name = "toggleTableCellsInsideVerticalBorderItem1"
			' 
			' toggleShowTableGridLinesItem1
			' 
			Me.toggleShowTableGridLinesItem1.Id = 185
			Me.toggleShowTableGridLinesItem1.Name = "toggleShowTableGridLinesItem1"
			' 
			' changeTableCellsShadingItem1
			' 
			Me.changeTableCellsShadingItem1.Id = 186
			Me.changeTableCellsShadingItem1.Name = "changeTableCellsShadingItem1"
			' 
			' selectTableElementsItem1
			' 
			Me.selectTableElementsItem1.Id = 187
			Me.selectTableElementsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableCellItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableColumnItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableRowItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableItem1)
			})
			Me.selectTableElementsItem1.Name = "selectTableElementsItem1"
			' 
			' selectTableCellItem1
			' 
			Me.selectTableCellItem1.Id = 188
			Me.selectTableCellItem1.Name = "selectTableCellItem1"
			' 
			' selectTableColumnItem1
			' 
			Me.selectTableColumnItem1.Id = 189
			Me.selectTableColumnItem1.Name = "selectTableColumnItem1"
			' 
			' selectTableRowItem1
			' 
			Me.selectTableRowItem1.Id = 190
			Me.selectTableRowItem1.Name = "selectTableRowItem1"
			' 
			' selectTableItem1
			' 
			Me.selectTableItem1.Id = 191
			Me.selectTableItem1.Name = "selectTableItem1"
			' 
			' showTablePropertiesFormItem1
			' 
			Me.showTablePropertiesFormItem1.Id = 192
			Me.showTablePropertiesFormItem1.Name = "showTablePropertiesFormItem1"
			' 
			' deleteTableElementsItem1
			' 
			Me.deleteTableElementsItem1.Id = 193
			Me.deleteTableElementsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.showDeleteTableCellsFormItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableColumnsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableRowsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableItem1)
			})
			Me.deleteTableElementsItem1.Name = "deleteTableElementsItem1"
			' 
			' showDeleteTableCellsFormItem1
			' 
			Me.showDeleteTableCellsFormItem1.Id = 194
			Me.showDeleteTableCellsFormItem1.Name = "showDeleteTableCellsFormItem1"
			' 
			' deleteTableColumnsItem1
			' 
			Me.deleteTableColumnsItem1.Id = 195
			Me.deleteTableColumnsItem1.Name = "deleteTableColumnsItem1"
			' 
			' deleteTableRowsItem1
			' 
			Me.deleteTableRowsItem1.Id = 196
			Me.deleteTableRowsItem1.Name = "deleteTableRowsItem1"
			' 
			' deleteTableItem1
			' 
			Me.deleteTableItem1.Id = 197
			Me.deleteTableItem1.Name = "deleteTableItem1"
			' 
			' insertTableRowAboveItem1
			' 
			Me.insertTableRowAboveItem1.Id = 198
			Me.insertTableRowAboveItem1.Name = "insertTableRowAboveItem1"
			' 
			' insertTableRowBelowItem1
			' 
			Me.insertTableRowBelowItem1.Id = 199
			Me.insertTableRowBelowItem1.Name = "insertTableRowBelowItem1"
			' 
			' insertTableColumnToLeftItem1
			' 
			Me.insertTableColumnToLeftItem1.Id = 200
			Me.insertTableColumnToLeftItem1.Name = "insertTableColumnToLeftItem1"
			' 
			' insertTableColumnToRightItem1
			' 
			Me.insertTableColumnToRightItem1.Id = 201
			Me.insertTableColumnToRightItem1.Name = "insertTableColumnToRightItem1"
			' 
			' mergeTableCellsItem1
			' 
			Me.mergeTableCellsItem1.Id = 202
			Me.mergeTableCellsItem1.Name = "mergeTableCellsItem1"
			' 
			' showSplitTableCellsForm1
			' 
			Me.showSplitTableCellsForm1.Id = 203
			Me.showSplitTableCellsForm1.Name = "showSplitTableCellsForm1"
			' 
			' splitTableItem1
			' 
			Me.splitTableItem1.Id = 204
			Me.splitTableItem1.Name = "splitTableItem1"
			' 
			' toggleTableAutoFitItem1
			' 
			Me.toggleTableAutoFitItem1.Id = 205
			Me.toggleTableAutoFitItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableAutoFitContentsItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableAutoFitWindowItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableFixedColumnWidthItem1)
			})
			Me.toggleTableAutoFitItem1.Name = "toggleTableAutoFitItem1"
			' 
			' toggleTableAutoFitContentsItem1
			' 
			Me.toggleTableAutoFitContentsItem1.Id = 206
			Me.toggleTableAutoFitContentsItem1.Name = "toggleTableAutoFitContentsItem1"
			' 
			' toggleTableAutoFitWindowItem1
			' 
			Me.toggleTableAutoFitWindowItem1.Id = 207
			Me.toggleTableAutoFitWindowItem1.Name = "toggleTableAutoFitWindowItem1"
			' 
			' toggleTableFixedColumnWidthItem1
			' 
			Me.toggleTableFixedColumnWidthItem1.Id = 208
			Me.toggleTableFixedColumnWidthItem1.Name = "toggleTableFixedColumnWidthItem1"
			' 
			' toggleTableCellsTopLeftAlignmentItem1
			' 
			Me.toggleTableCellsTopLeftAlignmentItem1.Id = 209
			Me.toggleTableCellsTopLeftAlignmentItem1.Name = "toggleTableCellsTopLeftAlignmentItem1"
			' 
			' toggleTableCellsMiddleLeftAlignmentItem1
			' 
			Me.toggleTableCellsMiddleLeftAlignmentItem1.Id = 210
			Me.toggleTableCellsMiddleLeftAlignmentItem1.Name = "toggleTableCellsMiddleLeftAlignmentItem1"
			' 
			' toggleTableCellsBottomLeftAlignmentItem1
			' 
			Me.toggleTableCellsBottomLeftAlignmentItem1.Id = 211
			Me.toggleTableCellsBottomLeftAlignmentItem1.Name = "toggleTableCellsBottomLeftAlignmentItem1"
			' 
			' toggleTableCellsTopCenterAlignmentItem1
			' 
			Me.toggleTableCellsTopCenterAlignmentItem1.Id = 212
			Me.toggleTableCellsTopCenterAlignmentItem1.Name = "toggleTableCellsTopCenterAlignmentItem1"
			' 
			' toggleTableCellsMiddleCenterAlignmentItem1
			' 
			Me.toggleTableCellsMiddleCenterAlignmentItem1.Id = 213
			Me.toggleTableCellsMiddleCenterAlignmentItem1.Name = "toggleTableCellsMiddleCenterAlignmentItem1"
			' 
			' toggleTableCellsBottomCenterAlignmentItem1
			' 
			Me.toggleTableCellsBottomCenterAlignmentItem1.Id = 214
			Me.toggleTableCellsBottomCenterAlignmentItem1.Name = "toggleTableCellsBottomCenterAlignmentItem1"
			' 
			' toggleTableCellsTopRightAlignmentItem1
			' 
			Me.toggleTableCellsTopRightAlignmentItem1.Id = 215
			Me.toggleTableCellsTopRightAlignmentItem1.Name = "toggleTableCellsTopRightAlignmentItem1"
			' 
			' toggleTableCellsMiddleRightAlignmentItem1
			' 
			Me.toggleTableCellsMiddleRightAlignmentItem1.Id = 216
			Me.toggleTableCellsMiddleRightAlignmentItem1.Name = "toggleTableCellsMiddleRightAlignmentItem1"
			' 
			' toggleTableCellsBottomRightAlignmentItem1
			' 
			Me.toggleTableCellsBottomRightAlignmentItem1.Id = 217
			Me.toggleTableCellsBottomRightAlignmentItem1.Name = "toggleTableCellsBottomRightAlignmentItem1"
			' 
			' showTableOptionsFormItem1
			' 
			Me.showTableOptionsFormItem1.Id = 218
			Me.showTableOptionsFormItem1.Name = "showTableOptionsFormItem1"
			' 
			' changeFloatingObjectFillColorItem1
			' 
			Me.changeFloatingObjectFillColorItem1.Id = 219
			Me.changeFloatingObjectFillColorItem1.Name = "changeFloatingObjectFillColorItem1"
			' 
			' changeFloatingObjectOutlineColorItem1
			' 
			Me.changeFloatingObjectOutlineColorItem1.Id = 220
			Me.changeFloatingObjectOutlineColorItem1.Name = "changeFloatingObjectOutlineColorItem1"
			' 
			' changeFloatingObjectOutlineWeightItem1
			' 
			Me.changeFloatingObjectOutlineWeightItem1.Edit = Me.repositoryItemFloatingObjectOutlineWeight1
			Me.changeFloatingObjectOutlineWeightItem1.EditValue = 20
			Me.changeFloatingObjectOutlineWeightItem1.Id = 221
			Me.changeFloatingObjectOutlineWeightItem1.Name = "changeFloatingObjectOutlineWeightItem1"
			' 
			' repositoryItemFloatingObjectOutlineWeight1
			' 
			Me.repositoryItemFloatingObjectOutlineWeight1.AutoHeight = False
			Me.repositoryItemFloatingObjectOutlineWeight1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemFloatingObjectOutlineWeight1.Control = Me.richEditControl
			Me.repositoryItemFloatingObjectOutlineWeight1.Name = "repositoryItemFloatingObjectOutlineWeight1"
			' 
			' changeFloatingObjectTextWrapTypeItem1
			' 
			Me.changeFloatingObjectTextWrapTypeItem1.Id = 222
			Me.changeFloatingObjectTextWrapTypeItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectInlineTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectSquareTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectTightTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectThroughTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectTopAndBottomTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectBehindTextWrapTypeItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectInFrontOfTextWrapTypeItem1)
			})
			Me.changeFloatingObjectTextWrapTypeItem1.Name = "changeFloatingObjectTextWrapTypeItem1"
			' 
			' setFloatingObjectInlineTextWrapTypeItem1
			' 
			Me.setFloatingObjectInlineTextWrapTypeItem1.Id = 223
			Me.setFloatingObjectInlineTextWrapTypeItem1.Name = "setFloatingObjectInlineTextWrapTypeItem1"
			' 
			' setFloatingObjectSquareTextWrapTypeItem1
			' 
			Me.setFloatingObjectSquareTextWrapTypeItem1.Id = 224
			Me.setFloatingObjectSquareTextWrapTypeItem1.Name = "setFloatingObjectSquareTextWrapTypeItem1"
			' 
			' setFloatingObjectTightTextWrapTypeItem1
			' 
			Me.setFloatingObjectTightTextWrapTypeItem1.Id = 225
			Me.setFloatingObjectTightTextWrapTypeItem1.Name = "setFloatingObjectTightTextWrapTypeItem1"
			' 
			' setFloatingObjectThroughTextWrapTypeItem1
			' 
			Me.setFloatingObjectThroughTextWrapTypeItem1.Id = 226
			Me.setFloatingObjectThroughTextWrapTypeItem1.Name = "setFloatingObjectThroughTextWrapTypeItem1"
			' 
			' setFloatingObjectTopAndBottomTextWrapTypeItem1
			' 
			Me.setFloatingObjectTopAndBottomTextWrapTypeItem1.Id = 227
			Me.setFloatingObjectTopAndBottomTextWrapTypeItem1.Name = "setFloatingObjectTopAndBottomTextWrapTypeItem1"
			' 
			' setFloatingObjectBehindTextWrapTypeItem1
			' 
			Me.setFloatingObjectBehindTextWrapTypeItem1.Id = 228
			Me.setFloatingObjectBehindTextWrapTypeItem1.Name = "setFloatingObjectBehindTextWrapTypeItem1"
			' 
			' setFloatingObjectInFrontOfTextWrapTypeItem1
			' 
			Me.setFloatingObjectInFrontOfTextWrapTypeItem1.Id = 229
			Me.setFloatingObjectInFrontOfTextWrapTypeItem1.Name = "setFloatingObjectInFrontOfTextWrapTypeItem1"
			' 
			' changeFloatingObjectAlignmentItem1
			' 
			Me.changeFloatingObjectAlignmentItem1.Id = 230
			Me.changeFloatingObjectAlignmentItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectTopLeftAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectTopCenterAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectTopRightAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectMiddleLeftAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectMiddleCenterAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectMiddleRightAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectBottomLeftAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectBottomCenterAlignmentItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setFloatingObjectBottomRightAlignmentItem1)
			})
			Me.changeFloatingObjectAlignmentItem1.Name = "changeFloatingObjectAlignmentItem1"
			' 
			' setFloatingObjectTopLeftAlignmentItem1
			' 
			Me.setFloatingObjectTopLeftAlignmentItem1.Id = 231
			Me.setFloatingObjectTopLeftAlignmentItem1.Name = "setFloatingObjectTopLeftAlignmentItem1"
			' 
			' setFloatingObjectTopCenterAlignmentItem1
			' 
			Me.setFloatingObjectTopCenterAlignmentItem1.Id = 232
			Me.setFloatingObjectTopCenterAlignmentItem1.Name = "setFloatingObjectTopCenterAlignmentItem1"
			' 
			' setFloatingObjectTopRightAlignmentItem1
			' 
			Me.setFloatingObjectTopRightAlignmentItem1.Id = 233
			Me.setFloatingObjectTopRightAlignmentItem1.Name = "setFloatingObjectTopRightAlignmentItem1"
			' 
			' setFloatingObjectMiddleLeftAlignmentItem1
			' 
			Me.setFloatingObjectMiddleLeftAlignmentItem1.Id = 234
			Me.setFloatingObjectMiddleLeftAlignmentItem1.Name = "setFloatingObjectMiddleLeftAlignmentItem1"
			' 
			' setFloatingObjectMiddleCenterAlignmentItem1
			' 
			Me.setFloatingObjectMiddleCenterAlignmentItem1.Id = 235
			Me.setFloatingObjectMiddleCenterAlignmentItem1.Name = "setFloatingObjectMiddleCenterAlignmentItem1"
			' 
			' setFloatingObjectMiddleRightAlignmentItem1
			' 
			Me.setFloatingObjectMiddleRightAlignmentItem1.Id = 236
			Me.setFloatingObjectMiddleRightAlignmentItem1.Name = "setFloatingObjectMiddleRightAlignmentItem1"
			' 
			' setFloatingObjectBottomLeftAlignmentItem1
			' 
			Me.setFloatingObjectBottomLeftAlignmentItem1.Id = 237
			Me.setFloatingObjectBottomLeftAlignmentItem1.Name = "setFloatingObjectBottomLeftAlignmentItem1"
			' 
			' setFloatingObjectBottomCenterAlignmentItem1
			' 
			Me.setFloatingObjectBottomCenterAlignmentItem1.Id = 238
			Me.setFloatingObjectBottomCenterAlignmentItem1.Name = "setFloatingObjectBottomCenterAlignmentItem1"
			' 
			' setFloatingObjectBottomRightAlignmentItem1
			' 
			Me.setFloatingObjectBottomRightAlignmentItem1.Id = 239
			Me.setFloatingObjectBottomRightAlignmentItem1.Name = "setFloatingObjectBottomRightAlignmentItem1"
			' 
			' floatingObjectBringForwardSubItem1
			' 
			Me.floatingObjectBringForwardSubItem1.Id = 240
			Me.floatingObjectBringForwardSubItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectBringForwardItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectBringToFrontItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectBringInFrontOfTextItem1)
			})
			Me.floatingObjectBringForwardSubItem1.Name = "floatingObjectBringForwardSubItem1"
			' 
			' floatingObjectBringForwardItem1
			' 
			Me.floatingObjectBringForwardItem1.Id = 241
			Me.floatingObjectBringForwardItem1.Name = "floatingObjectBringForwardItem1"
			' 
			' floatingObjectBringToFrontItem1
			' 
			Me.floatingObjectBringToFrontItem1.Id = 242
			Me.floatingObjectBringToFrontItem1.Name = "floatingObjectBringToFrontItem1"
			' 
			' floatingObjectBringInFrontOfTextItem1
			' 
			Me.floatingObjectBringInFrontOfTextItem1.Id = 243
			Me.floatingObjectBringInFrontOfTextItem1.Name = "floatingObjectBringInFrontOfTextItem1"
			' 
			' floatingObjectSendBackwardSubItem1
			' 
			Me.floatingObjectSendBackwardSubItem1.Id = 244
			Me.floatingObjectSendBackwardSubItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectSendBackwardItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectSendToBackItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.floatingObjectSendBehindTextItem1)
			})
			Me.floatingObjectSendBackwardSubItem1.Name = "floatingObjectSendBackwardSubItem1"
			' 
			' floatingObjectSendBackwardItem1
			' 
			Me.floatingObjectSendBackwardItem1.Id = 245
			Me.floatingObjectSendBackwardItem1.Name = "floatingObjectSendBackwardItem1"
			' 
			' floatingObjectSendToBackItem1
			' 
			Me.floatingObjectSendToBackItem1.Id = 246
			Me.floatingObjectSendToBackItem1.Name = "floatingObjectSendToBackItem1"
			' 
			' floatingObjectSendBehindTextItem1
			' 
			Me.floatingObjectSendBehindTextItem1.Id = 247
			Me.floatingObjectSendBehindTextItem1.Name = "floatingObjectSendBehindTextItem1"
			' 
			' headerFooterToolsRibbonPageCategory1
			' 
			Me.headerFooterToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb((CInt((CByte(38)))), (CInt((CByte(176)))), (CInt((CByte(35)))))
			Me.headerFooterToolsRibbonPageCategory1.Control = Me.richEditControl
			Me.headerFooterToolsRibbonPageCategory1.Name = "headerFooterToolsRibbonPageCategory1"
			Me.headerFooterToolsRibbonPageCategory1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.headerFooterToolsDesignRibbonPage1})
			' 
			' headerFooterToolsDesignRibbonPage1
			' 
			Me.headerFooterToolsDesignRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.headerFooterToolsDesignNavigationRibbonPageGroup1, Me.headerFooterToolsDesignOptionsRibbonPageGroup1, Me.headerFooterToolsDesignCloseRibbonPageGroup1})
			Me.headerFooterToolsDesignRibbonPage1.Name = "headerFooterToolsDesignRibbonPage1"
			' 
			' headerFooterToolsDesignNavigationRibbonPageGroup1
			' 
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(Me.goToPageHeaderItem1, "E")
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(Me.goToPageFooterItem1, "G")
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(Me.goToNextHeaderFooterItem1, "X")
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(Me.goToPreviousHeaderFooterItem1, "R")
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(Me.toggleLinkToPreviousItem1, "K")
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.Name = "headerFooterToolsDesignNavigationRibbonPageGroup1"
			Me.headerFooterToolsDesignNavigationRibbonPageGroup1.Text = ""
			' 
			' headerFooterToolsDesignOptionsRibbonPageGroup1
			' 
			Me.headerFooterToolsDesignOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleDifferentFirstPageItem1, "A")
			Me.headerFooterToolsDesignOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleDifferentOddAndEvenPagesItem1, "V")
			Me.headerFooterToolsDesignOptionsRibbonPageGroup1.Name = "headerFooterToolsDesignOptionsRibbonPageGroup1"
			Me.headerFooterToolsDesignOptionsRibbonPageGroup1.Text = ""
			' 
			' headerFooterToolsDesignCloseRibbonPageGroup1
			' 
			Me.headerFooterToolsDesignCloseRibbonPageGroup1.ItemLinks.Add(Me.closePageHeaderFooterItem1, "C")
			Me.headerFooterToolsDesignCloseRibbonPageGroup1.Name = "headerFooterToolsDesignCloseRibbonPageGroup1"
			Me.headerFooterToolsDesignCloseRibbonPageGroup1.Text = ""
			' 
			' tableToolsRibbonPageCategory1
			' 
			Me.tableToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb((CInt((CByte(252)))), (CInt((CByte(233)))), (CInt((CByte(20)))))
			Me.tableToolsRibbonPageCategory1.Control = Me.richEditControl
			Me.tableToolsRibbonPageCategory1.Name = "tableToolsRibbonPageCategory1"
			Me.tableToolsRibbonPageCategory1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.tableDesignRibbonPage1, Me.tableLayoutRibbonPage1})
			' 
			' tableDesignRibbonPage1
			' 
			Me.tableDesignRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableStyleOptionsRibbonPageGroup1, Me.tableStylesRibbonPageGroup1, Me.tableDrawBordersRibbonPageGroup1})
			Me.tableDesignRibbonPage1.Name = "tableDesignRibbonPage1"
			' 
			' tableStyleOptionsRibbonPageGroup1
			' 
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleFirstRowItem1)
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleLastRowItem1)
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleBandedRowsItem1)
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleFirstColumnItem1)
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleLastColumnItem1)
			Me.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(Me.toggleBandedColumnsItem1)
			Me.tableStyleOptionsRibbonPageGroup1.Name = "tableStyleOptionsRibbonPageGroup1"
			Me.tableStyleOptionsRibbonPageGroup1.Text = ""
			' 
			' tableStylesRibbonPageGroup1
			' 
			Me.tableStylesRibbonPageGroup1.ItemLinks.Add(Me.galleryChangeTableStyleItem1)
			Me.tableStylesRibbonPageGroup1.Name = "tableStylesRibbonPageGroup1"
			Me.tableStylesRibbonPageGroup1.Text = ""
			' 
			' tableDrawBordersRibbonPageGroup1
			' 
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderLineStyleItem1)
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderLineWeightItem1)
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderColorItem1, "C")
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBordersItem1, "B")
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableCellsShadingItem1, "H")
			Me.tableDrawBordersRibbonPageGroup1.Name = "tableDrawBordersRibbonPageGroup1"
			Me.tableDrawBordersRibbonPageGroup1.Text = ""
			' 
			' tableLayoutRibbonPage1
			' 
			Me.tableLayoutRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableTableRibbonPageGroup1, Me.tableRowsAndColumnsRibbonPageGroup1, Me.tableMergeRibbonPageGroup1, Me.tableCellSizeRibbonPageGroup1, Me.tableAlignmentRibbonPageGroup1})
			Me.tableLayoutRibbonPage1.Name = "tableLayoutRibbonPage1"
			' 
			' tableTableRibbonPageGroup1
			' 
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.selectTableElementsItem1, "K")
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.toggleShowTableGridLinesItem1, "TG")
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.showTablePropertiesFormItem1, "O")
			Me.tableTableRibbonPageGroup1.Name = "tableTableRibbonPageGroup1"
			Me.tableTableRibbonPageGroup1.Text = ""
			' 
			' tableRowsAndColumnsRibbonPageGroup1
			' 
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.deleteTableElementsItem1, "D")
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableRowAboveItem1, "A")
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableRowBelowItem1, "E")
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableColumnToLeftItem1, "L")
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableColumnToRightItem1, "R")
			Me.tableRowsAndColumnsRibbonPageGroup1.Name = "tableRowsAndColumnsRibbonPageGroup1"
			Me.tableRowsAndColumnsRibbonPageGroup1.Text = ""
			' 
			' tableMergeRibbonPageGroup1
			' 
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.mergeTableCellsItem1, "M")
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.showSplitTableCellsForm1, "P")
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.splitTableItem1, "Q")
			Me.tableMergeRibbonPageGroup1.Name = "tableMergeRibbonPageGroup1"
			Me.tableMergeRibbonPageGroup1.Text = ""
			' 
			' tableCellSizeRibbonPageGroup1
			' 
			Me.tableCellSizeRibbonPageGroup1.AllowTextClipping = False
			Me.tableCellSizeRibbonPageGroup1.ItemLinks.Add(Me.toggleTableAutoFitItem1, "F")
			Me.tableCellSizeRibbonPageGroup1.Name = "tableCellSizeRibbonPageGroup1"
			Me.tableCellSizeRibbonPageGroup1.Text = ""
			' 
			' tableAlignmentRibbonPageGroup1
			' 
			Me.tableAlignmentRibbonPageGroup1.ImageOptions.Image = (DirectCast(resources.GetObject("tableAlignmentRibbonPageGroup1.ImageOptions.Image"), System.Drawing.Image))
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopLeftAlignmentItem1, "TL")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleLeftAlignmentItem1, "CL")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomLeftAlignmentItem1, "BL")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopCenterAlignmentItem1, "TC")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleCenterAlignmentItem1, "CC")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomCenterAlignmentItem1, "BC")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopRightAlignmentItem1, "TR")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleRightAlignmentItem1, "CR")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomRightAlignmentItem1, "BR")
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.showTableOptionsFormItem1, "N")
			Me.tableAlignmentRibbonPageGroup1.Name = "tableAlignmentRibbonPageGroup1"
			Me.tableAlignmentRibbonPageGroup1.Text = ""
			' 
			' floatingPictureToolsRibbonPageCategory1
			' 
			Me.floatingPictureToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb((CInt((CByte(201)))), (CInt((CByte(0)))), (CInt((CByte(119)))))
			Me.floatingPictureToolsRibbonPageCategory1.Control = Me.richEditControl
			Me.floatingPictureToolsRibbonPageCategory1.Name = "floatingPictureToolsRibbonPageCategory1"
			Me.floatingPictureToolsRibbonPageCategory1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.floatingPictureToolsFormatPage1})
			' 
			' floatingPictureToolsFormatPage1
			' 
			Me.floatingPictureToolsFormatPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.floatingPictureToolsShapeStylesPageGroup1, Me.floatingPictureToolsArrangePageGroup1})
			Me.floatingPictureToolsFormatPage1.Name = "floatingPictureToolsFormatPage1"
			' 
			' floatingPictureToolsShapeStylesPageGroup1
			' 
			Me.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(Me.changeFloatingObjectFillColorItem1)
			Me.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(Me.changeFloatingObjectOutlineColorItem1)
			Me.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(Me.changeFloatingObjectOutlineWeightItem1)
			Me.floatingPictureToolsShapeStylesPageGroup1.Name = "floatingPictureToolsShapeStylesPageGroup1"
			Me.floatingPictureToolsShapeStylesPageGroup1.Text = ""
			' 
			' floatingPictureToolsArrangePageGroup1
			' 
			Me.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(Me.changeFloatingObjectTextWrapTypeItem1, "TW")
			Me.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(Me.changeFloatingObjectAlignmentItem1, "PO")
			Me.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(Me.floatingObjectBringForwardSubItem1, "AF")
			Me.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(Me.floatingObjectSendBackwardSubItem1, "AE")
			Me.floatingPictureToolsArrangePageGroup1.Name = "floatingPictureToolsArrangePageGroup1"
			Me.floatingPictureToolsArrangePageGroup1.Text = ""
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
			Me.commonRibbonPageGroup1.Text = ""
			' 
			' infoRibbonPageGroup1
			' 
			Me.infoRibbonPageGroup1.ItemLinks.Add(Me.showDocumentPropertiesFormItem1)
			Me.infoRibbonPageGroup1.Name = "infoRibbonPageGroup1"
			Me.infoRibbonPageGroup1.Text = ""
			' 
			' homeRibbonPage1
			' 
			Me.homeRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.clipboardRibbonPageGroup1, Me.fontRibbonPageGroup1, Me.paragraphRibbonPageGroup1, Me.stylesRibbonPageGroup1, Me.editingRibbonPageGroup1})
			Me.homeRibbonPage1.Name = "homeRibbonPage1"
			reduceOperation1.Behavior = DevExpress.XtraBars.Ribbon.ReduceOperationBehavior.UntilAvailable
			reduceOperation1.GroupName = Nothing
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
			Me.clipboardRibbonPageGroup1.Text = ""
			' 
			' fontRibbonPageGroup1
			' 
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup1)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup2)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup3)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.changeTextCaseItem1)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.clearFormattingItem1, "E")
			Me.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1"
			Me.fontRibbonPageGroup1.Text = ""
			' 
			' paragraphRibbonPageGroup1
			' 
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup4)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup5)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup6)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup7)
			Me.paragraphRibbonPageGroup1.Name = "paragraphRibbonPageGroup1"
			Me.paragraphRibbonPageGroup1.Text = ""
			' 
			' editingRibbonPageGroup1
			' 
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.findItem1, "FD")
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.replaceItem1, "R")
			Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
			Me.editingRibbonPageGroup1.Text = ""
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
			Me.pagesRibbonPageGroup1.Text = ""
			' 
			' tablesRibbonPageGroup1
			' 
			Me.tablesRibbonPageGroup1.AllowTextClipping = False
			Me.tablesRibbonPageGroup1.ItemLinks.Add(Me.insertTableItem1, "T")
			Me.tablesRibbonPageGroup1.Name = "tablesRibbonPageGroup1"
			Me.tablesRibbonPageGroup1.Text = ""
			' 
			' illustrationsRibbonPageGroup1
			' 
			Me.illustrationsRibbonPageGroup1.ItemLinks.Add(Me.insertFloatingPictureItem1)
			Me.illustrationsRibbonPageGroup1.Name = "illustrationsRibbonPageGroup1"
			Me.illustrationsRibbonPageGroup1.Text = ""
			' 
			' linksRibbonPageGroup1
			' 
			Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertBookmarkItem1, "K")
			Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertHyperlinkItem1, "I")
			Me.linksRibbonPageGroup1.Name = "linksRibbonPageGroup1"
			Me.linksRibbonPageGroup1.Text = ""
			' 
			' headerFooterRibbonPageGroup1
			' 
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageHeaderItem1, "H")
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageFooterItem1, "O")
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageNumberItem1, "NU")
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageCountItem1)
			Me.headerFooterRibbonPageGroup1.Name = "headerFooterRibbonPageGroup1"
			Me.headerFooterRibbonPageGroup1.Text = ""
			' 
			' textRibbonPageGroup1
			' 
			Me.textRibbonPageGroup1.ImageOptions.Image = (DirectCast(resources.GetObject("textRibbonPageGroup1.ImageOptions.Image"), System.Drawing.Image))
			Me.textRibbonPageGroup1.ItemLinks.Add(Me.insertTextBoxItem1, "X")
			Me.textRibbonPageGroup1.Name = "textRibbonPageGroup1"
			Me.textRibbonPageGroup1.Text = ""
			' 
			' symbolsRibbonPageGroup1
			' 
			Me.symbolsRibbonPageGroup1.AllowTextClipping = False
			Me.symbolsRibbonPageGroup1.ItemLinks.Add(Me.insertSymbolItem1, "U")
			Me.symbolsRibbonPageGroup1.Name = "symbolsRibbonPageGroup1"
			Me.symbolsRibbonPageGroup1.Text = ""
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
			Me.pageSetupRibbonPageGroup1.Text = ""
			' 
			' pageBackgroundRibbonPageGroup1
			' 
			Me.pageBackgroundRibbonPageGroup1.AllowTextClipping = False
			Me.pageBackgroundRibbonPageGroup1.ItemLinks.Add(Me.changePageColorItem1, "PC")
			Me.pageBackgroundRibbonPageGroup1.Name = "pageBackgroundRibbonPageGroup1"
			Me.pageBackgroundRibbonPageGroup1.Text = ""
			' 
			' referencesRibbonPage1
			' 
			Me.referencesRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableOfContentsRibbonPageGroup1, Me.captionsRibbonPageGroup1})
			Me.referencesRibbonPage1.Name = "referencesRibbonPage1"
			' 
			' tableOfContentsRibbonPageGroup1
			' 
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.insertTableOfContentsItem1, "T")
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.updateTableOfContentsItem1, "U")
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.addParagraphsToTableOfContentItem1, "A")
			Me.tableOfContentsRibbonPageGroup1.Name = "tableOfContentsRibbonPageGroup1"
			Me.tableOfContentsRibbonPageGroup1.Text = ""
			' 
			' captionsRibbonPageGroup1
			' 
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.insertCaptionPlaceholderItem1, "C")
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.insertTableOfFiguresPlaceholderItem1, "G")
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.updateTableOfFiguresItem1, "V")
			Me.captionsRibbonPageGroup1.Name = "captionsRibbonPageGroup1"
			Me.captionsRibbonPageGroup1.Text = ""
			' 
			' mailingsRibbonPage1
			' 
			Me.mailingsRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.mailMergeRibbonPageGroup1})
			Me.mailingsRibbonPage1.Name = "mailingsRibbonPage1"
			' 
			' mailMergeRibbonPageGroup1
			' 
			Me.mailMergeRibbonPageGroup1.ItemLinks.Add(Me.insertMergeFieldItem1)
			Me.mailMergeRibbonPageGroup1.ItemLinks.Add(Me.showAllFieldCodesItem1)
			Me.mailMergeRibbonPageGroup1.ItemLinks.Add(Me.showAllFieldResultsItem1)
			Me.mailMergeRibbonPageGroup1.ItemLinks.Add(Me.toggleViewMergedDataItem1, "P")
			Me.mailMergeRibbonPageGroup1.Name = "mailMergeRibbonPageGroup1"
			Me.mailMergeRibbonPageGroup1.Text = ""
			' 
			' reviewRibbonPage1
			' 
			Me.reviewRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.documentProofingRibbonPageGroup1, Me.documentProtectionRibbonPageGroup1, Me.documentCommentRibbonPageGroup1, Me.documentTrackingRibbonPageGroup1})
			Me.reviewRibbonPage1.Name = "reviewRibbonPage1"
			' 
			' documentProofingRibbonPageGroup1
			' 
			Me.documentProofingRibbonPageGroup1.ItemLinks.Add(Me.checkSpellingItem1, "S")
			Me.documentProofingRibbonPageGroup1.ItemLinks.Add(Me.changeLanguageItem1)
			Me.documentProofingRibbonPageGroup1.Name = "documentProofingRibbonPageGroup1"
			Me.documentProofingRibbonPageGroup1.Text = ""
			' 
			' documentProtectionRibbonPageGroup1
			' 
			Me.documentProtectionRibbonPageGroup1.ItemLinks.Add(Me.protectDocumentItem1)
			Me.documentProtectionRibbonPageGroup1.ItemLinks.Add(Me.changeRangeEditingPermissionsItem1)
			Me.documentProtectionRibbonPageGroup1.ItemLinks.Add(Me.unprotectDocumentItem1)
			Me.documentProtectionRibbonPageGroup1.Name = "documentProtectionRibbonPageGroup1"
			Me.documentProtectionRibbonPageGroup1.Text = ""
			' 
			' documentCommentRibbonPageGroup1
			' 
			Me.documentCommentRibbonPageGroup1.ItemLinks.Add(Me.newCommentItem1, "C")
			Me.documentCommentRibbonPageGroup1.ItemLinks.Add(Me.deleteCommentsItem1, "D")
			Me.documentCommentRibbonPageGroup1.ItemLinks.Add(Me.previousCommentItem1, "V")
			Me.documentCommentRibbonPageGroup1.ItemLinks.Add(Me.nextCommentItem1, "N")
			Me.documentCommentRibbonPageGroup1.Name = "documentCommentRibbonPageGroup1"
			Me.documentCommentRibbonPageGroup1.Text = ""
			' 
			' documentTrackingRibbonPageGroup1
			' 
			Me.documentTrackingRibbonPageGroup1.ItemLinks.Add(Me.changeCommentItem1)
			Me.documentTrackingRibbonPageGroup1.ItemLinks.Add(Me.reviewersItem1)
			Me.documentTrackingRibbonPageGroup1.ItemLinks.Add(Me.reviewingPaneItem1)
			Me.documentTrackingRibbonPageGroup1.Name = "documentTrackingRibbonPageGroup1"
			Me.documentTrackingRibbonPageGroup1.Text = ""
			' 
			' viewRibbonPage1
			' 
			Me.viewRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.documentViewsRibbonPageGroup1, Me.showRibbonPageGroup1, Me.zoomRibbonPageGroup1})
			Me.viewRibbonPage1.Name = "viewRibbonPage1"
			' 
			' documentViewsRibbonPageGroup1
			' 
			Me.documentViewsRibbonPageGroup1.ItemLinks.Add(Me.switchToSimpleViewItem1, "L")
			Me.documentViewsRibbonPageGroup1.ItemLinks.Add(Me.switchToDraftViewItem1, "E")
			Me.documentViewsRibbonPageGroup1.ItemLinks.Add(Me.switchToPrintLayoutViewItem1, "P")
			Me.documentViewsRibbonPageGroup1.Name = "documentViewsRibbonPageGroup1"
			Me.documentViewsRibbonPageGroup1.Text = ""
			' 
			' showRibbonPageGroup1
			' 
			Me.showRibbonPageGroup1.ItemLinks.Add(Me.toggleShowHorizontalRulerItem1)
			Me.showRibbonPageGroup1.ItemLinks.Add(Me.toggleShowVerticalRulerItem1)
			Me.showRibbonPageGroup1.Name = "showRibbonPageGroup1"
			Me.showRibbonPageGroup1.Text = ""
			' 
			' zoomRibbonPageGroup1
			' 
			Me.zoomRibbonPageGroup1.ItemLinks.Add(Me.zoomOutItem1)
			Me.zoomRibbonPageGroup1.ItemLinks.Add(Me.zoomInItem1)
			Me.zoomRibbonPageGroup1.Name = "zoomRibbonPageGroup1"
			Me.zoomRibbonPageGroup1.Text = ""
			' 
			' ribbonImageCollectionLarge
			' 
			Me.ribbonImageCollectionLarge.ImageSize = New System.Drawing.Size(32, 32)
			Me.ribbonImageCollectionLarge.ImageStream = (DirectCast(resources.GetObject("ribbonImageCollectionLarge.ImageStream"), DevExpress.Utils.ImageCollectionStreamer))
			Me.ribbonImageCollectionLarge.Images.SetKeyName(0, "Ribbon_Exit_32x32.png")
			Me.ribbonImageCollectionLarge.Images.SetKeyName(1, "Ribbon_Content_32x32.png")
			Me.ribbonImageCollectionLarge.Images.SetKeyName(2, "Ribbon_Info_32x32.png")
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
			Me.richEditBarController1.BarItems.Add(Me.toggleParagraphLeftToRightItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleParagraphRightToLeftItem1)
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
			Me.richEditBarController1.BarItems.Add(Me.insertPageBreakItem21)
			Me.richEditBarController1.BarItems.Add(Me.insertTableItem1)
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
			Me.richEditBarController1.BarItems.Add(Me.insertSectionBreakContinuousItem1)
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
			Me.richEditBarController1.BarItems.Add(Me.insertTableOfContentsItem1)
			Me.richEditBarController1.BarItems.Add(Me.updateTableOfContentsItem1)
			Me.richEditBarController1.BarItems.Add(Me.addParagraphsToTableOfContentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem1)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem2)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem3)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem4)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem5)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem6)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem7)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem8)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem9)
			Me.richEditBarController1.BarItems.Add(Me.setParagraphHeadingLevelItem10)
			Me.richEditBarController1.BarItems.Add(Me.insertCaptionPlaceholderItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertFiguresCaptionItems1)
			Me.richEditBarController1.BarItems.Add(Me.insertTablesCaptionItems1)
			Me.richEditBarController1.BarItems.Add(Me.insertEquationsCaptionItems1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableOfFiguresPlaceholderItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableOfFiguresItems1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableOfTablesItems1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableOfEquationsItems1)
			Me.richEditBarController1.BarItems.Add(Me.updateTableOfFiguresItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertMergeFieldItem1)
			Me.richEditBarController1.BarItems.Add(Me.showAllFieldCodesItem1)
			Me.richEditBarController1.BarItems.Add(Me.showAllFieldResultsItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleViewMergedDataItem1)
			Me.richEditBarController1.BarItems.Add(Me.checkSpellingItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeLanguageItem1)
			Me.richEditBarController1.BarItems.Add(Me.protectDocumentItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeRangeEditingPermissionsItem1)
			Me.richEditBarController1.BarItems.Add(Me.unprotectDocumentItem1)
			Me.richEditBarController1.BarItems.Add(Me.newCommentItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteCommentsItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteOneCommentItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteAllCommentsShownItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteAllCommentsItem1)
			Me.richEditBarController1.BarItems.Add(Me.previousCommentItem1)
			Me.richEditBarController1.BarItems.Add(Me.nextCommentItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeCommentItem1)
			Me.richEditBarController1.BarItems.Add(Me.reviewersItem1)
			Me.richEditBarController1.BarItems.Add(Me.reviewingPaneItem1)
			Me.richEditBarController1.BarItems.Add(Me.switchToSimpleViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.switchToDraftViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.switchToPrintLayoutViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleShowHorizontalRulerItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleShowVerticalRulerItem1)
			Me.richEditBarController1.BarItems.Add(Me.zoomOutItem1)
			Me.richEditBarController1.BarItems.Add(Me.zoomInItem1)
			Me.richEditBarController1.BarItems.Add(Me.goToPageHeaderItem1)
			Me.richEditBarController1.BarItems.Add(Me.goToPageFooterItem1)
			Me.richEditBarController1.BarItems.Add(Me.goToNextHeaderFooterItem1)
			Me.richEditBarController1.BarItems.Add(Me.goToPreviousHeaderFooterItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleLinkToPreviousItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleDifferentFirstPageItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleDifferentOddAndEvenPagesItem1)
			Me.richEditBarController1.BarItems.Add(Me.closePageHeaderFooterItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleFirstRowItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleLastRowItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleBandedRowsItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleFirstColumnItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleLastColumnItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleBandedColumnsItem1)
			Me.richEditBarController1.BarItems.Add(Me.galleryChangeTableStyleItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeTableBorderLineStyleItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeTableBorderLineWeightItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeTableBorderColorItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeTableBordersItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsBottomBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsTopBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsLeftBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsRightBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.resetTableCellsAllBordersItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsAllBordersItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsOutsideBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsInsideBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsInsideHorizontalBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsInsideVerticalBorderItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleShowTableGridLinesItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeTableCellsShadingItem1)
			Me.richEditBarController1.BarItems.Add(Me.selectTableElementsItem1)
			Me.richEditBarController1.BarItems.Add(Me.selectTableCellItem1)
			Me.richEditBarController1.BarItems.Add(Me.selectTableColumnItem1)
			Me.richEditBarController1.BarItems.Add(Me.selectTableRowItem1)
			Me.richEditBarController1.BarItems.Add(Me.selectTableItem1)
			Me.richEditBarController1.BarItems.Add(Me.showTablePropertiesFormItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteTableElementsItem1)
			Me.richEditBarController1.BarItems.Add(Me.showDeleteTableCellsFormItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteTableColumnsItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteTableRowsItem1)
			Me.richEditBarController1.BarItems.Add(Me.deleteTableItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableRowAboveItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableRowBelowItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableColumnToLeftItem1)
			Me.richEditBarController1.BarItems.Add(Me.insertTableColumnToRightItem1)
			Me.richEditBarController1.BarItems.Add(Me.mergeTableCellsItem1)
			Me.richEditBarController1.BarItems.Add(Me.showSplitTableCellsForm1)
			Me.richEditBarController1.BarItems.Add(Me.splitTableItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableAutoFitItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableAutoFitContentsItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableAutoFitWindowItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableFixedColumnWidthItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsTopLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsMiddleLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsBottomLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsTopCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsMiddleCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsBottomCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsTopRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsMiddleRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleTableCellsBottomRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.showTableOptionsFormItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeFloatingObjectFillColorItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeFloatingObjectOutlineColorItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeFloatingObjectOutlineWeightItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeFloatingObjectTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectInlineTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectSquareTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectTightTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectThroughTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectTopAndBottomTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectBehindTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectInFrontOfTextWrapTypeItem1)
			Me.richEditBarController1.BarItems.Add(Me.changeFloatingObjectAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectTopLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectTopCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectTopRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectMiddleLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectMiddleCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectMiddleRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectBottomLeftAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectBottomCenterAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.setFloatingObjectBottomRightAlignmentItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectBringForwardSubItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectBringForwardItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectBringToFrontItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectBringInFrontOfTextItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectSendBackwardSubItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectSendBackwardItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectSendToBackItem1)
			Me.richEditBarController1.BarItems.Add(Me.floatingObjectSendBehindTextItem1)
			Me.richEditBarController1.Control = Me.richEditControl
			' 
			' dockManager1
			' 
			Me.dockManager1.Form = Me
			Me.dockManager1.HiddenPanels.AddRange(New DevExpress.XtraBars.Docking.DockPanel() { Me.dockPanel1})
			Me.dockManager1.TopZIndexControls.AddRange(New String() { "DevExpress.XtraBars.BarDockControl", "DevExpress.XtraBars.StandaloneBarDockControl", "System.Windows.Forms.StatusBar", "System.Windows.Forms.MenuStrip", "System.Windows.Forms.StatusStrip", "DevExpress.XtraBars.Ribbon.RibbonStatusBar", "DevExpress.XtraBars.Ribbon.RibbonControl", "DevExpress.XtraBars.Navigation.OfficeNavigationBar", "DevExpress.XtraBars.Navigation.TileNavPane", "DevExpress.XtraBars.TabFormControl", "DevExpress.XtraBars.FluentDesignSystem.FluentDesignFormControl"})
			' 
			' dockPanel1
			' 
			Me.dockPanel1.Controls.Add(Me.dockPanel1_Container)
			Me.dockPanel1.Dock = DevExpress.XtraBars.Docking.DockingStyle.Left
			Me.dockPanel1.ID = New System.Guid("9004d178-e773-4916-b7be-b77e77b186bb")
			Me.dockPanel1.Location = New System.Drawing.Point(0, 0)
			Me.dockPanel1.Name = "dockPanel1"
			Me.dockPanel1.OriginalSize = New System.Drawing.Size(328, 200)
			Me.dockPanel1.SavedDock = DevExpress.XtraBars.Docking.DockingStyle.Left
			Me.dockPanel1.SavedIndex = 0
			Me.dockPanel1.Size = New System.Drawing.Size(328, 472)
			Me.dockPanel1.Text = "Main document comments"
			Me.dockPanel1.Visibility = DevExpress.XtraBars.Docking.DockVisibility.Hidden
			' 
			' dockPanel1_Container
			' 
			Me.dockPanel1_Container.Controls.Add(Me.richEditCommentControl1)
			Me.dockPanel1_Container.Location = New System.Drawing.Point(3, 46)
			Me.dockPanel1_Container.Name = "dockPanel1_Container"
			Me.dockPanel1_Container.Size = New System.Drawing.Size(321, 423)
			Me.dockPanel1_Container.TabIndex = 0
			' 
			' richEditCommentControl1
			' 
			Me.richEditCommentControl1.ActiveViewType = DevExpress.XtraRichEdit.RichEditViewType.Simple
			Me.richEditCommentControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditCommentControl1.Location = New System.Drawing.Point(0, 0)
			Me.richEditCommentControl1.Name = "richEditCommentControl1"
			Me.richEditCommentControl1.ReadOnly = False
			Me.richEditCommentControl1.RichEditControl = Me.richEditControl
			Me.richEditCommentControl1.Size = New System.Drawing.Size(321, 423)
			Me.richEditCommentControl1.TabIndex = 0
			' 
			' ribbonPage2
			' 
			Me.ribbonPage2.Name = "ribbonPage2"
			Me.ribbonPage2.Text = "ribbonPage2"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(941, 610)
			Me.Controls.Add(Me.richEditControl)
			Me.Name = "Form1"
			Me.ShowIcon = False
			Me.Text = "Rich Text Editor"
			DirectCast(Me.appMenu, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.ribbonImageCollection, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.repositoryItemBorderLineStyle1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.repositoryItemBorderLineWeight1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.repositoryItemFloatingObjectOutlineWeight1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.ribbonImageCollectionLarge, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.dockManager1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.dockPanel1.ResumeLayout(False)
			Me.dockPanel1_Container.ResumeLayout(False)
			Me.ResumeLayout(False)

		End Sub

		#End Region
		Private appMenu As DevExpress.XtraBars.Ribbon.ApplicationMenu
		Private ribbonImageCollection As DevExpress.Utils.ImageCollection
		Private ribbonImageCollectionLarge As DevExpress.Utils.ImageCollection
		Private richEditControl As DevExpress.XtraRichEdit.RichEditControl
		Private spellChecker As DevExpress.XtraSpellChecker.SpellChecker
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
		Private dockManager1 As DevExpress.XtraBars.Docking.DockManager
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
		Private toggleParagraphLeftToRightItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphLeftToRightItem
		Private toggleParagraphRightToLeftItem1 As DevExpress.XtraRichEdit.UI.ToggleParagraphRightToLeftItem
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
		Private insertPageBreakItem21 As DevExpress.XtraRichEdit.UI.InsertPageBreakItem2
		Private insertTableItem1 As DevExpress.XtraRichEdit.UI.InsertTableItem
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
		Private insertSectionBreakContinuousItem1 As DevExpress.XtraRichEdit.UI.InsertSectionBreakContinuousItem
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
		Private insertTableOfContentsItem1 As DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem
		Private updateTableOfContentsItem1 As DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem
		Private addParagraphsToTableOfContentItem1 As DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem
		Private setParagraphHeadingLevelItem1 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem2 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem3 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem4 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem5 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem6 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem7 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem8 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem9 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem10 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private insertCaptionPlaceholderItem1 As DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem
		Private insertFiguresCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems
		Private insertTablesCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems
		Private insertEquationsCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems
		Private insertTableOfFiguresPlaceholderItem1 As DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem
		Private insertTableOfFiguresItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems
		Private insertTableOfTablesItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems
		Private insertTableOfEquationsItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems
		Private updateTableOfFiguresItem1 As DevExpress.XtraRichEdit.UI.UpdateTableOfFiguresItem
		Private insertMergeFieldItem1 As DevExpress.XtraRichEdit.UI.InsertMergeFieldItem
		Private showAllFieldCodesItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem
		Private showAllFieldResultsItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem
		Private toggleViewMergedDataItem1 As DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem
		Private checkSpellingItem1 As DevExpress.XtraRichEdit.UI.CheckSpellingItem
		Private changeLanguageItem1 As DevExpress.XtraRichEdit.UI.ChangeLanguageItem
		Private protectDocumentItem1 As DevExpress.XtraRichEdit.UI.ProtectDocumentItem
		Private changeRangeEditingPermissionsItem1 As DevExpress.XtraRichEdit.UI.ChangeRangeEditingPermissionsItem
		Private unprotectDocumentItem1 As DevExpress.XtraRichEdit.UI.UnprotectDocumentItem
		Private newCommentItem1 As DevExpress.XtraRichEdit.UI.NewCommentItem
		Private deleteCommentsItem1 As DevExpress.XtraRichEdit.UI.DeleteCommentsItem
		Private deleteOneCommentItem1 As DevExpress.XtraRichEdit.UI.DeleteOneCommentItem
		Private deleteAllCommentsShownItem1 As DevExpress.XtraRichEdit.UI.DeleteAllCommentsShownItem
		Private deleteAllCommentsItem1 As DevExpress.XtraRichEdit.UI.DeleteAllCommentsItem
		Private previousCommentItem1 As DevExpress.XtraRichEdit.UI.PreviousCommentItem
		Private nextCommentItem1 As DevExpress.XtraRichEdit.UI.NextCommentItem
		Private changeCommentItem1 As DevExpress.XtraRichEdit.UI.ChangeCommentItem
		Private reviewersItem1 As DevExpress.XtraRichEdit.UI.ReviewersItem
		Private reviewingPaneItem1 As DevExpress.XtraRichEdit.UI.ReviewingPaneItem
		Private switchToSimpleViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem
		Private switchToDraftViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem
		Private switchToPrintLayoutViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem
		Private toggleShowHorizontalRulerItem1 As DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem
		Private toggleShowVerticalRulerItem1 As DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem
		Private zoomOutItem1 As DevExpress.XtraRichEdit.UI.ZoomOutItem
		Private zoomInItem1 As DevExpress.XtraRichEdit.UI.ZoomInItem
		Private goToPageHeaderItem1 As DevExpress.XtraRichEdit.UI.GoToPageHeaderItem
		Private goToPageFooterItem1 As DevExpress.XtraRichEdit.UI.GoToPageFooterItem
		Private goToNextHeaderFooterItem1 As DevExpress.XtraRichEdit.UI.GoToNextHeaderFooterItem
		Private goToPreviousHeaderFooterItem1 As DevExpress.XtraRichEdit.UI.GoToPreviousHeaderFooterItem
		Private toggleLinkToPreviousItem1 As DevExpress.XtraRichEdit.UI.ToggleLinkToPreviousItem
		Private toggleDifferentFirstPageItem1 As DevExpress.XtraRichEdit.UI.ToggleDifferentFirstPageItem
		Private toggleDifferentOddAndEvenPagesItem1 As DevExpress.XtraRichEdit.UI.ToggleDifferentOddAndEvenPagesItem
		Private closePageHeaderFooterItem1 As DevExpress.XtraRichEdit.UI.ClosePageHeaderFooterItem
		Private toggleFirstRowItem1 As DevExpress.XtraRichEdit.UI.ToggleFirstRowItem
		Private toggleLastRowItem1 As DevExpress.XtraRichEdit.UI.ToggleLastRowItem
		Private toggleBandedRowsItem1 As DevExpress.XtraRichEdit.UI.ToggleBandedRowsItem
		Private toggleFirstColumnItem1 As DevExpress.XtraRichEdit.UI.ToggleFirstColumnItem
		Private toggleLastColumnItem1 As DevExpress.XtraRichEdit.UI.ToggleLastColumnItem
		Private toggleBandedColumnsItem1 As DevExpress.XtraRichEdit.UI.ToggleBandedColumnsItem
		Private galleryChangeTableStyleItem1 As DevExpress.XtraRichEdit.UI.GalleryChangeTableStyleItem
		Private changeTableBorderLineStyleItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem
		Private repositoryItemBorderLineStyle1 As DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle
		Private changeTableBorderLineWeightItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem
		Private repositoryItemBorderLineWeight1 As DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight
		Private changeTableBorderColorItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem
		Private changeTableBordersItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBordersItem
		Private toggleTableCellsBottomBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomBorderItem
		Private toggleTableCellsTopBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopBorderItem
		Private toggleTableCellsLeftBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsLeftBorderItem
		Private toggleTableCellsRightBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsRightBorderItem
		Private resetTableCellsAllBordersItem1 As DevExpress.XtraRichEdit.UI.ResetTableCellsAllBordersItem
		Private toggleTableCellsAllBordersItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsAllBordersItem
		Private toggleTableCellsOutsideBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsOutsideBorderItem
		Private toggleTableCellsInsideBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideBorderItem
		Private toggleTableCellsInsideHorizontalBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideHorizontalBorderItem
		Private toggleTableCellsInsideVerticalBorderItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideVerticalBorderItem
		Private toggleShowTableGridLinesItem1 As DevExpress.XtraRichEdit.UI.ToggleShowTableGridLinesItem
		Private changeTableCellsShadingItem1 As DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem
		Private selectTableElementsItem1 As DevExpress.XtraRichEdit.UI.SelectTableElementsItem
		Private selectTableCellItem1 As DevExpress.XtraRichEdit.UI.SelectTableCellItem
		Private selectTableColumnItem1 As DevExpress.XtraRichEdit.UI.SelectTableColumnItem
		Private selectTableRowItem1 As DevExpress.XtraRichEdit.UI.SelectTableRowItem
		Private selectTableItem1 As DevExpress.XtraRichEdit.UI.SelectTableItem
		Private showTablePropertiesFormItem1 As DevExpress.XtraRichEdit.UI.ShowTablePropertiesFormItem
		Private deleteTableElementsItem1 As DevExpress.XtraRichEdit.UI.DeleteTableElementsItem
		Private showDeleteTableCellsFormItem1 As DevExpress.XtraRichEdit.UI.ShowDeleteTableCellsFormItem
		Private deleteTableColumnsItem1 As DevExpress.XtraRichEdit.UI.DeleteTableColumnsItem
		Private deleteTableRowsItem1 As DevExpress.XtraRichEdit.UI.DeleteTableRowsItem
		Private deleteTableItem1 As DevExpress.XtraRichEdit.UI.DeleteTableItem
		Private insertTableRowAboveItem1 As DevExpress.XtraRichEdit.UI.InsertTableRowAboveItem
		Private insertTableRowBelowItem1 As DevExpress.XtraRichEdit.UI.InsertTableRowBelowItem
		Private insertTableColumnToLeftItem1 As DevExpress.XtraRichEdit.UI.InsertTableColumnToLeftItem
		Private insertTableColumnToRightItem1 As DevExpress.XtraRichEdit.UI.InsertTableColumnToRightItem
		Private mergeTableCellsItem1 As DevExpress.XtraRichEdit.UI.MergeTableCellsItem
		Private showSplitTableCellsForm1 As DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm
		Private splitTableItem1 As DevExpress.XtraRichEdit.UI.SplitTableItem
		Private toggleTableAutoFitItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem
		Private toggleTableAutoFitContentsItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem
		Private toggleTableAutoFitWindowItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem
		Private toggleTableFixedColumnWidthItem1 As DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem
		Private toggleTableCellsTopLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem
		Private toggleTableCellsMiddleLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem
		Private toggleTableCellsBottomLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem
		Private toggleTableCellsTopCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem
		Private toggleTableCellsMiddleCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem
		Private toggleTableCellsBottomCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem
		Private toggleTableCellsTopRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem
		Private toggleTableCellsMiddleRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem
		Private toggleTableCellsBottomRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem
		Private showTableOptionsFormItem1 As DevExpress.XtraRichEdit.UI.ShowTableOptionsFormItem
		Private changeFloatingObjectFillColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFloatingObjectFillColorItem
		Private changeFloatingObjectOutlineColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineColorItem
		Private changeFloatingObjectOutlineWeightItem1 As DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineWeightItem
		Private repositoryItemFloatingObjectOutlineWeight1 As DevExpress.XtraRichEdit.Forms.Design.RepositoryItemFloatingObjectOutlineWeight
		Private changeFloatingObjectTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.ChangeFloatingObjectTextWrapTypeItem
		Private setFloatingObjectInlineTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectInlineTextWrapTypeItem
		Private setFloatingObjectSquareTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectSquareTextWrapTypeItem
		Private setFloatingObjectTightTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectTightTextWrapTypeItem
		Private setFloatingObjectThroughTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectThroughTextWrapTypeItem
		Private setFloatingObjectTopAndBottomTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectTopAndBottomTextWrapTypeItem
		Private setFloatingObjectBehindTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectBehindTextWrapTypeItem
		Private setFloatingObjectInFrontOfTextWrapTypeItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectInFrontOfTextWrapTypeItem
		Private changeFloatingObjectAlignmentItem1 As DevExpress.XtraRichEdit.UI.ChangeFloatingObjectAlignmentItem
		Private setFloatingObjectTopLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectTopLeftAlignmentItem
		Private setFloatingObjectTopCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectTopCenterAlignmentItem
		Private setFloatingObjectTopRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectTopRightAlignmentItem
		Private setFloatingObjectMiddleLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleLeftAlignmentItem
		Private setFloatingObjectMiddleCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleCenterAlignmentItem
		Private setFloatingObjectMiddleRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleRightAlignmentItem
		Private setFloatingObjectBottomLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomLeftAlignmentItem
		Private setFloatingObjectBottomCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomCenterAlignmentItem
		Private setFloatingObjectBottomRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomRightAlignmentItem
		Private floatingObjectBringForwardSubItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardSubItem
		Private floatingObjectBringForwardItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardItem
		Private floatingObjectBringToFrontItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectBringToFrontItem
		Private floatingObjectBringInFrontOfTextItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectBringInFrontOfTextItem
		Private floatingObjectSendBackwardSubItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardSubItem
		Private floatingObjectSendBackwardItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardItem
		Private floatingObjectSendToBackItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectSendToBackItem
		Private floatingObjectSendBehindTextItem1 As DevExpress.XtraRichEdit.UI.FloatingObjectSendBehindTextItem
		Private headerFooterToolsRibbonPageCategory1 As DevExpress.XtraRichEdit.UI.HeaderFooterToolsRibbonPageCategory
		Private headerFooterToolsDesignRibbonPage1 As DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignRibbonPage
		Private headerFooterToolsDesignNavigationRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignNavigationRibbonPageGroup
		Private headerFooterToolsDesignOptionsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignOptionsRibbonPageGroup
		Private headerFooterToolsDesignCloseRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignCloseRibbonPageGroup
		Private tableToolsRibbonPageCategory1 As DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory
		Private tableDesignRibbonPage1 As DevExpress.XtraRichEdit.UI.TableDesignRibbonPage
		Private tableStyleOptionsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableStyleOptionsRibbonPageGroup
		Private tableStylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup
		Private tableDrawBordersRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup
		Private tableLayoutRibbonPage1 As DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage
		Private tableTableRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup
		Private tableRowsAndColumnsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup
		Private tableMergeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup
		Private tableCellSizeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup
		Private tableAlignmentRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup
		Private floatingPictureToolsRibbonPageCategory1 As DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory
		Private floatingPictureToolsFormatPage1 As DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage
		Private floatingPictureToolsShapeStylesPageGroup1 As DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup
		Private floatingPictureToolsArrangePageGroup1 As DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup
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
		Private referencesRibbonPage1 As DevExpress.XtraRichEdit.UI.ReferencesRibbonPage
		Private tableOfContentsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup
		Private captionsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup
		Private mailingsRibbonPage1 As DevExpress.XtraRichEdit.UI.MailingsRibbonPage
		Private mailMergeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup
		Private reviewRibbonPage1 As DevExpress.XtraRichEdit.UI.ReviewRibbonPage
		Private documentProofingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentProofingRibbonPageGroup
		Private documentProtectionRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentProtectionRibbonPageGroup
		Private documentCommentRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentCommentRibbonPageGroup
		Private documentTrackingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentTrackingRibbonPageGroup
		Private viewRibbonPage1 As DevExpress.XtraRichEdit.UI.ViewRibbonPage
		Private documentViewsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup
		Private showRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup
		Private zoomRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup
		Private dockPanel1 As DevExpress.XtraBars.Docking.DockPanel
		Private dockPanel1_Container As DevExpress.XtraBars.Docking.ControlContainer
		Private richEditCommentControl1 As DevExpress.XtraRichEdit.RichEditCommentControl
		Private ribbonPage2 As DevExpress.XtraBars.Ribbon.RibbonPage
	End Class
End Namespace
