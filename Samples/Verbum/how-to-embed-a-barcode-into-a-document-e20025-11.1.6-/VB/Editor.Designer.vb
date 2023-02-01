Imports Microsoft.VisualBasic
Imports System
Namespace BizPad
	Partial Public Class Editor
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
			Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Editor))
			Dim borderInfo1 As New DevExpress.XtraRichEdit.Model.BorderInfo()
			Me.ribbonControl = New DevExpress.XtraBars.Ribbon.RibbonControl()
			Me.applicationMenu = New DevExpress.XtraBars.Ribbon.ApplicationMenu(Me.components)
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
			Me.changeFontNameItem = New DevExpress.XtraRichEdit.UI.ChangeFontNameItem()
			Me.repositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
			Me.changeFontSizeItem = New DevExpress.XtraRichEdit.UI.ChangeFontSizeItem()
			Me.repositoryItemRichEditFontSizeEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit()
			Me.richEdit = New BizPad.Extensions.RichEditEx()
			Me.changeFontColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontColorItem()
			Me.changeFontBackColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem()
			Me.toggleFontBoldItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontBoldItem()
			Me.toggleFontItalicItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontItalicItem()
			Me.toggleFontUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem()
			Me.toggleFontDoubleUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem()
			Me.toggleFontStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem()
			Me.toggleFontDoubleStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem()
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
			Me.insertPageBreakItem1 = New DevExpress.XtraRichEdit.UI.InsertPageBreakItem()
			Me.insertTableItem1 = New DevExpress.XtraRichEdit.UI.InsertTableItem()
			Me.insertPictureItem1 = New DevExpress.XtraRichEdit.UI.InsertPictureItem()
			Me.insertBookmarkItem1 = New DevExpress.XtraRichEdit.UI.InsertBookmarkItem()
			Me.insertHyperlinkItem1 = New DevExpress.XtraRichEdit.UI.InsertHyperlinkItem()
			Me.editPageHeaderItem1 = New DevExpress.XtraRichEdit.UI.EditPageHeaderItem()
			Me.editPageFooterItem1 = New DevExpress.XtraRichEdit.UI.EditPageFooterItem()
			Me.insertPageNumberItem1 = New DevExpress.XtraRichEdit.UI.InsertPageNumberItem()
			Me.insertPageCountItem1 = New DevExpress.XtraRichEdit.UI.InsertPageCountItem()
			Me.insertSymbolItem1 = New DevExpress.XtraRichEdit.UI.InsertSymbolItem()
			Me.changeTableCellsShadingItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem()
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
			Me.changeTableBorderLineStyleItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem()
			Me.repositoryItemBorderLineStyle1 = New DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle()
			Me.changeTableBorderLineWeightItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem()
			Me.repositoryItemBorderLineWeight1 = New DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight()
			Me.changeTableBorderColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem()
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
			Me.showInsertTableCellsFormItem1 = New DevExpress.XtraRichEdit.UI.ShowInsertTableCellsFormItem()
			Me.mergeTableCellsItem1 = New DevExpress.XtraRichEdit.UI.MergeTableCellsItem()
			Me.showSplitTableCellsForm1 = New DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm()
			Me.splitTableItem1 = New DevExpress.XtraRichEdit.UI.SplitTableItem()
			Me.toggleTableAutoFitItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem()
			Me.toggleTableAutoFitContentsItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem()
			Me.toggleTableAutoFitWindowItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem()
			Me.toggleTableFixedColumnWidthItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem()
			Me.toggleTableCellsTopLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem()
			Me.toggleTableCellsTopCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem()
			Me.toggleTableCellsTopRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem()
			Me.toggleTableCellsMiddleLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem()
			Me.toggleTableCellsMiddleCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem()
			Me.toggleTableCellsMiddleRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem()
			Me.toggleTableCellsBottomLeftAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem()
			Me.toggleTableCellsBottomCenterAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem()
			Me.toggleTableCellsBottomRightAlignmentItem1 = New DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem()
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
			Me.insertFiguresCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems()
			Me.insertTablesCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems()
			Me.insertEquationsCaptionItems1 = New DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems()
			Me.insertTableOfFiguresItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems()
			Me.insertTableOfTablesItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems()
			Me.insertTableOfEquationsItems1 = New DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems()
			Me.showAllFieldCodesItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem()
			Me.showAllFieldResultsItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem()
			Me.barStaticItem1 = New DevExpress.XtraBars.BarStaticItem()
			Me.barStaticItem2 = New DevExpress.XtraBars.BarStaticItem()
			Me.barButtonItem1 = New DevExpress.XtraBars.BarButtonItem()
			Me.barCheckItem1 = New DevExpress.XtraBars.BarCheckItem()
			Me.barButtonGroup3 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup4 = New DevExpress.XtraBars.BarButtonGroup()
			Me.insertTableOfContentsItem1 = New DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem()
			Me.updateTableOfContentsItem1 = New DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem()
			Me.addParagraphsToTableOfContentItem1 = New DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem()
			Me.setParagraphHeadingLevelItem11 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem12 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem13 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem14 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem15 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem16 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem17 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem18 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem19 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.setParagraphHeadingLevelItem20 = New DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem()
			Me.insertCaptionPlaceholderItem1 = New DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem()
			Me.insertFiguresCaptionItems2 = New DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems()
			Me.insertTablesCaptionItems2 = New DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems()
			Me.insertEquationsCaptionItems2 = New DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems()
			Me.insertTableOfFiguresPlaceholderItem1 = New DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem()
			Me.insertTableOfFiguresItems2 = New DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems()
			Me.insertTableOfTablesItems2 = New DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems()
			Me.insertTableOfEquationsItems2 = New DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems()
			Me.tableToolsRibbonPageCategory1 = New DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory()
			Me.tableDesignRibbonPage1 = New DevExpress.XtraRichEdit.UI.TableDesignRibbonPage()
			Me.tableStylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup()
			Me.tableDrawBordersRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup()
			Me.tableLayoutRibbonPage1 = New DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage()
			Me.tableTableRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup()
			Me.tableRowsAndColumnsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup()
			Me.tableMergeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup()
			Me.tableCellSizeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup()
			Me.tableAlignmentRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup()
			Me.homeRibbonPage1 = New DevExpress.XtraRichEdit.UI.HomeRibbonPage()
			Me.clipboardRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup()
			Me.editingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup()
			Me.stylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup()
			Me.insertRibbonPage1 = New DevExpress.XtraRichEdit.UI.InsertRibbonPage()
			Me.pagesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup()
			Me.tablesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup()
			Me.illustrationsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup()
			Me.linksRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup()
			Me.headerFooterRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup()
			Me.symbolsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup()
			Me.referencesRibbonPage1 = New DevExpress.XtraRichEdit.UI.ReferencesRibbonPage()
			Me.tableOfContentsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup()
			Me.captionsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup()
			Me.richEditBarController = New DevExpress.XtraRichEdit.UI.RichEditBarController()
			CType(Me.ribbonControl, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.applicationMenu, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemBorderLineStyle1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemBorderLineWeight1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.richEditBarController, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' ribbonControl
			' 
			Me.ribbonControl.ApplicationButtonDropDownControl = Me.applicationMenu
			Me.ribbonControl.ApplicationButtonText = Nothing
			' 
			' 
			' 
			Me.ribbonControl.ExpandCollapseItem.Id = 0
			Me.ribbonControl.ExpandCollapseItem.Name = ""
			Me.ribbonControl.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl.ExpandCollapseItem, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.undoItem1, Me.redoItem1, Me.cutItem1, Me.copyItem1, Me.pasteItem1, Me.pasteSpecialItem1, Me.changeFontNameItem, Me.changeFontSizeItem, Me.changeFontColorItem1, Me.changeFontBackColorItem1, Me.toggleFontBoldItem1, Me.toggleFontItalicItem1, Me.toggleFontUnderlineItem1, Me.toggleFontDoubleUnderlineItem1, Me.toggleFontStrikeoutItem1, Me.toggleFontDoubleStrikeoutItem1, Me.toggleFontSuperscriptItem1, Me.toggleFontSubscriptItem1, Me.changeTextCaseItem1, Me.makeTextUpperCaseItem1, Me.makeTextLowerCaseItem1, Me.toggleTextCaseItem1, Me.fontSizeIncreaseItem1, Me.fontSizeDecreaseItem1, Me.clearFormattingItem1, Me.showFontFormItem1, Me.toggleParagraphAlignmentLeftItem1, Me.toggleParagraphAlignmentCenterItem1, Me.toggleParagraphAlignmentRightItem1, Me.toggleParagraphAlignmentJustifyItem1, Me.changeParagraphLineSpacingItem1, Me.setSingleParagraphSpacingItem1, Me.setSesquialteralParagraphSpacingItem1, Me.setDoubleParagraphSpacingItem1, Me.showLineSpacingFormItem1, Me.addSpacingBeforeParagraphItem1, Me.removeSpacingBeforeParagraphItem1, Me.addSpacingAfterParagraphItem1, Me.removeSpacingAfterParagraphItem1, Me.toggleBulletedListItem1, Me.toggleNumberingListItem1, Me.toggleMultiLevelListItem1, Me.decreaseIndentItem1, Me.increaseIndentItem1, Me.toggleShowWhitespaceItem1, Me.showParagraphFormItem1, Me.changeStyleItem1, Me.findItem1, Me.replaceItem1, Me.insertPageBreakItem1, Me.insertTableItem1, Me.insertPictureItem1, Me.insertBookmarkItem1, Me.insertHyperlinkItem1, Me.editPageHeaderItem1, Me.editPageFooterItem1, Me.insertPageNumberItem1, Me.insertPageCountItem1, Me.insertSymbolItem1, Me.changeTableCellsShadingItem1, Me.changeTableBordersItem1, Me.toggleTableCellsBottomBorderItem1, Me.toggleTableCellsTopBorderItem1, Me.toggleTableCellsLeftBorderItem1, Me.toggleTableCellsRightBorderItem1, Me.resetTableCellsAllBordersItem1, Me.toggleTableCellsAllBordersItem1, Me.toggleTableCellsOutsideBorderItem1, Me.toggleTableCellsInsideBorderItem1, Me.toggleTableCellsInsideHorizontalBorderItem1, Me.toggleTableCellsInsideVerticalBorderItem1, Me.toggleShowTableGridLinesItem1, Me.changeTableBorderLineStyleItem1, Me.changeTableBorderLineWeightItem1, Me.changeTableBorderColorItem1, Me.selectTableElementsItem1, Me.selectTableCellItem1, Me.selectTableColumnItem1, Me.selectTableRowItem1, Me.selectTableItem1, Me.showTablePropertiesFormItem1, Me.deleteTableElementsItem1, Me.showDeleteTableCellsFormItem1, Me.deleteTableColumnsItem1, Me.deleteTableRowsItem1, Me.deleteTableItem1, Me.insertTableRowAboveItem1, Me.insertTableRowBelowItem1, Me.insertTableColumnToLeftItem1, Me.insertTableColumnToRightItem1, Me.showInsertTableCellsFormItem1, Me.mergeTableCellsItem1, Me.showSplitTableCellsForm1, Me.splitTableItem1, Me.toggleTableAutoFitItem1, Me.toggleTableAutoFitContentsItem1, Me.toggleTableAutoFitWindowItem1, Me.toggleTableFixedColumnWidthItem1, Me.toggleTableCellsTopLeftAlignmentItem1, Me.toggleTableCellsTopCenterAlignmentItem1, Me.toggleTableCellsTopRightAlignmentItem1, Me.toggleTableCellsMiddleLeftAlignmentItem1, Me.toggleTableCellsMiddleCenterAlignmentItem1, Me.toggleTableCellsMiddleRightAlignmentItem1, Me.toggleTableCellsBottomLeftAlignmentItem1, Me.toggleTableCellsBottomCenterAlignmentItem1, Me.toggleTableCellsBottomRightAlignmentItem1, Me.setParagraphHeadingLevelItem1, Me.setParagraphHeadingLevelItem2, Me.setParagraphHeadingLevelItem3, Me.setParagraphHeadingLevelItem4, Me.setParagraphHeadingLevelItem5, Me.setParagraphHeadingLevelItem6, Me.setParagraphHeadingLevelItem7, Me.setParagraphHeadingLevelItem8, Me.setParagraphHeadingLevelItem9, Me.setParagraphHeadingLevelItem10, Me.insertFiguresCaptionItems1, Me.insertTablesCaptionItems1, Me.insertEquationsCaptionItems1, Me.insertTableOfFiguresItems1, Me.insertTableOfTablesItems1, Me.insertTableOfEquationsItems1, Me.showAllFieldCodesItem1, Me.showAllFieldResultsItem1, Me.barStaticItem1, Me.barStaticItem2, Me.barButtonItem1, Me.barCheckItem1, Me.barButtonGroup3, Me.barButtonGroup4, Me.insertTableOfContentsItem1, Me.updateTableOfContentsItem1, Me.addParagraphsToTableOfContentItem1, Me.setParagraphHeadingLevelItem11, Me.setParagraphHeadingLevelItem12, Me.setParagraphHeadingLevelItem13, Me.setParagraphHeadingLevelItem14, Me.setParagraphHeadingLevelItem15, Me.setParagraphHeadingLevelItem16, Me.setParagraphHeadingLevelItem17, Me.setParagraphHeadingLevelItem18, Me.setParagraphHeadingLevelItem19, Me.setParagraphHeadingLevelItem20, Me.insertCaptionPlaceholderItem1, Me.insertFiguresCaptionItems2, Me.insertTablesCaptionItems2, Me.insertEquationsCaptionItems2, Me.insertTableOfFiguresPlaceholderItem1, Me.insertTableOfFiguresItems2, Me.insertTableOfTablesItems2, Me.insertTableOfEquationsItems2})
			Me.ribbonControl.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl.MaxItemId = 182
			Me.ribbonControl.Name = "ribbonControl"
			Me.ribbonControl.PageCategories.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageCategory() { Me.tableToolsRibbonPageCategory1})
			Me.ribbonControl.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.homeRibbonPage1, Me.insertRibbonPage1, Me.referencesRibbonPage1})
			Me.ribbonControl.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() { Me.repositoryItemFontEdit1, Me.repositoryItemRichEditFontSizeEdit1, Me.repositoryItemRichEditStyleEdit1, Me.repositoryItemBorderLineStyle1, Me.repositoryItemBorderLineWeight1})
			Me.ribbonControl.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office2010
			Me.ribbonControl.SelectedPage = Me.homeRibbonPage1
			Me.ribbonControl.ShowApplicationButton = DevExpress.Utils.DefaultBoolean.True
			Me.ribbonControl.Size = New System.Drawing.Size(895, 149)
			Me.ribbonControl.Toolbar.ItemLinks.Add(Me.fileSaveItem1)
			Me.ribbonControl.Toolbar.ItemLinks.Add(Me.undoItem1)
			Me.ribbonControl.Toolbar.ItemLinks.Add(Me.redoItem1)
			' 
			' applicationMenu
			' 
			Me.applicationMenu.ItemLinks.Add(Me.fileNewItem1)
			Me.applicationMenu.ItemLinks.Add(Me.fileOpenItem1)
			Me.applicationMenu.ItemLinks.Add(Me.fileSaveItem1, True)
			Me.applicationMenu.ItemLinks.Add(Me.fileSaveAsItem1)
			Me.applicationMenu.ItemLinks.Add(Me.quickPrintItem1, True)
			Me.applicationMenu.ItemLinks.Add(Me.printItem1)
			Me.applicationMenu.ItemLinks.Add(Me.printPreviewItem1)
			Me.applicationMenu.MenuDrawMode = DevExpress.XtraBars.MenuDrawMode.LargeImagesText
			Me.applicationMenu.Name = "applicationMenu"
			Me.applicationMenu.Ribbon = Me.ribbonControl
			Me.applicationMenu.ShowRightPane = True
			' 
			' fileNewItem1
			' 
			Me.fileNewItem1.Glyph = (CType(resources.GetObject("fileNewItem1.Glyph"), System.Drawing.Image))
			Me.fileNewItem1.Id = 1
			Me.fileNewItem1.LargeGlyph = (CType(resources.GetObject("fileNewItem1.LargeGlyph"), System.Drawing.Image))
			Me.fileNewItem1.Name = "fileNewItem1"
			' 
			' fileOpenItem1
			' 
			Me.fileOpenItem1.Glyph = (CType(resources.GetObject("fileOpenItem1.Glyph"), System.Drawing.Image))
			Me.fileOpenItem1.Id = 2
			Me.fileOpenItem1.LargeGlyph = (CType(resources.GetObject("fileOpenItem1.LargeGlyph"), System.Drawing.Image))
			Me.fileOpenItem1.Name = "fileOpenItem1"
			' 
			' fileSaveItem1
			' 
			Me.fileSaveItem1.Glyph = (CType(resources.GetObject("fileSaveItem1.Glyph"), System.Drawing.Image))
			Me.fileSaveItem1.Id = 3
			Me.fileSaveItem1.LargeGlyph = (CType(resources.GetObject("fileSaveItem1.LargeGlyph"), System.Drawing.Image))
			Me.fileSaveItem1.Name = "fileSaveItem1"
			' 
			' fileSaveAsItem1
			' 
			Me.fileSaveAsItem1.Glyph = (CType(resources.GetObject("fileSaveAsItem1.Glyph"), System.Drawing.Image))
			Me.fileSaveAsItem1.Id = 4
			Me.fileSaveAsItem1.LargeGlyph = (CType(resources.GetObject("fileSaveAsItem1.LargeGlyph"), System.Drawing.Image))
			Me.fileSaveAsItem1.Name = "fileSaveAsItem1"
			' 
			' quickPrintItem1
			' 
			Me.quickPrintItem1.Glyph = (CType(resources.GetObject("quickPrintItem1.Glyph"), System.Drawing.Image))
			Me.quickPrintItem1.Id = 5
			Me.quickPrintItem1.LargeGlyph = (CType(resources.GetObject("quickPrintItem1.LargeGlyph"), System.Drawing.Image))
			Me.quickPrintItem1.Name = "quickPrintItem1"
			' 
			' printItem1
			' 
			Me.printItem1.Glyph = (CType(resources.GetObject("printItem1.Glyph"), System.Drawing.Image))
			Me.printItem1.Id = 6
			Me.printItem1.LargeGlyph = (CType(resources.GetObject("printItem1.LargeGlyph"), System.Drawing.Image))
			Me.printItem1.Name = "printItem1"
			' 
			' printPreviewItem1
			' 
			Me.printPreviewItem1.Glyph = (CType(resources.GetObject("printPreviewItem1.Glyph"), System.Drawing.Image))
			Me.printPreviewItem1.Id = 7
			Me.printPreviewItem1.LargeGlyph = (CType(resources.GetObject("printPreviewItem1.LargeGlyph"), System.Drawing.Image))
			Me.printPreviewItem1.Name = "printPreviewItem1"
			' 
			' undoItem1
			' 
			Me.undoItem1.Glyph = (CType(resources.GetObject("undoItem1.Glyph"), System.Drawing.Image))
			Me.undoItem1.Id = 8
			Me.undoItem1.LargeGlyph = (CType(resources.GetObject("undoItem1.LargeGlyph"), System.Drawing.Image))
			Me.undoItem1.Name = "undoItem1"
			' 
			' redoItem1
			' 
			Me.redoItem1.Glyph = (CType(resources.GetObject("redoItem1.Glyph"), System.Drawing.Image))
			Me.redoItem1.Id = 9
			Me.redoItem1.LargeGlyph = (CType(resources.GetObject("redoItem1.LargeGlyph"), System.Drawing.Image))
			Me.redoItem1.Name = "redoItem1"
			' 
			' cutItem1
			' 
			Me.cutItem1.Glyph = (CType(resources.GetObject("cutItem1.Glyph"), System.Drawing.Image))
			Me.cutItem1.Id = 10
			Me.cutItem1.LargeGlyph = (CType(resources.GetObject("cutItem1.LargeGlyph"), System.Drawing.Image))
			Me.cutItem1.Name = "cutItem1"
			Me.cutItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' copyItem1
			' 
			Me.copyItem1.Glyph = (CType(resources.GetObject("copyItem1.Glyph"), System.Drawing.Image))
			Me.copyItem1.Id = 11
			Me.copyItem1.LargeGlyph = (CType(resources.GetObject("copyItem1.LargeGlyph"), System.Drawing.Image))
			Me.copyItem1.Name = "copyItem1"
			Me.copyItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' pasteItem1
			' 
			Me.pasteItem1.Glyph = (CType(resources.GetObject("pasteItem1.Glyph"), System.Drawing.Image))
			Me.pasteItem1.Id = 12
			Me.pasteItem1.LargeGlyph = (CType(resources.GetObject("pasteItem1.LargeGlyph"), System.Drawing.Image))
			Me.pasteItem1.Name = "pasteItem1"
			' 
			' pasteSpecialItem1
			' 
			Me.pasteSpecialItem1.Glyph = (CType(resources.GetObject("pasteSpecialItem1.Glyph"), System.Drawing.Image))
			Me.pasteSpecialItem1.Id = 13
			Me.pasteSpecialItem1.LargeGlyph = (CType(resources.GetObject("pasteSpecialItem1.LargeGlyph"), System.Drawing.Image))
			Me.pasteSpecialItem1.Name = "pasteSpecialItem1"
			Me.pasteSpecialItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' changeFontNameItem
			' 
			Me.changeFontNameItem.Edit = Me.repositoryItemFontEdit1
			Me.changeFontNameItem.Id = 14
			Me.changeFontNameItem.Name = "changeFontNameItem"
			Me.changeFontNameItem.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			Me.changeFontNameItem.Width = 150
			' 
			' repositoryItemFontEdit1
			' 
			Me.repositoryItemFontEdit1.AutoHeight = False
			Me.repositoryItemFontEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemFontEdit1.Name = "repositoryItemFontEdit1"
			' 
			' changeFontSizeItem
			' 
			Me.changeFontSizeItem.Edit = Me.repositoryItemRichEditFontSizeEdit1
			Me.changeFontSizeItem.Id = 15
			Me.changeFontSizeItem.Name = "changeFontSizeItem"
			Me.changeFontSizeItem.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' repositoryItemRichEditFontSizeEdit1
			' 
			Me.repositoryItemRichEditFontSizeEdit1.AutoHeight = False
			Me.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemRichEditFontSizeEdit1.Control = Me.richEdit
			Me.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1"
			' 
			' richEdit
			' 
			Me.richEdit.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEdit.Location = New System.Drawing.Point(0, 149)
			Me.richEdit.MenuManager = Me.ribbonControl
			Me.richEdit.Name = "richEdit"
			Me.richEdit.Size = New System.Drawing.Size(895, 403)
			Me.richEdit.TabIndex = 1
			' 
			' changeFontColorItem1
			' 
			Me.changeFontColorItem1.ActAsDropDown = True
			Me.changeFontColorItem1.Glyph = (CType(resources.GetObject("changeFontColorItem1.Glyph"), System.Drawing.Image))
			Me.changeFontColorItem1.Id = 16
			Me.changeFontColorItem1.LargeGlyph = (CType(resources.GetObject("changeFontColorItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeFontColorItem1.Name = "changeFontColorItem1"
			Me.changeFontColorItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' changeFontBackColorItem1
			' 
			Me.changeFontBackColorItem1.Glyph = (CType(resources.GetObject("changeFontBackColorItem1.Glyph"), System.Drawing.Image))
			Me.changeFontBackColorItem1.Id = 17
			Me.changeFontBackColorItem1.LargeGlyph = (CType(resources.GetObject("changeFontBackColorItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeFontBackColorItem1.Name = "changeFontBackColorItem1"
			Me.changeFontBackColorItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontBoldItem1
			' 
			Me.toggleFontBoldItem1.Glyph = (CType(resources.GetObject("toggleFontBoldItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontBoldItem1.Id = 18
			Me.toggleFontBoldItem1.LargeGlyph = (CType(resources.GetObject("toggleFontBoldItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontBoldItem1.Name = "toggleFontBoldItem1"
			Me.toggleFontBoldItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontItalicItem1
			' 
			Me.toggleFontItalicItem1.Glyph = (CType(resources.GetObject("toggleFontItalicItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontItalicItem1.Id = 19
			Me.toggleFontItalicItem1.LargeGlyph = (CType(resources.GetObject("toggleFontItalicItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontItalicItem1.Name = "toggleFontItalicItem1"
			Me.toggleFontItalicItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontUnderlineItem1
			' 
			Me.toggleFontUnderlineItem1.Glyph = (CType(resources.GetObject("toggleFontUnderlineItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontUnderlineItem1.Id = 20
			Me.toggleFontUnderlineItem1.LargeGlyph = (CType(resources.GetObject("toggleFontUnderlineItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1"
			Me.toggleFontUnderlineItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontDoubleUnderlineItem1
			' 
			Me.toggleFontDoubleUnderlineItem1.Glyph = (CType(resources.GetObject("toggleFontDoubleUnderlineItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontDoubleUnderlineItem1.Id = 21
			Me.toggleFontDoubleUnderlineItem1.LargeGlyph = (CType(resources.GetObject("toggleFontDoubleUnderlineItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1"
			Me.toggleFontDoubleUnderlineItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontStrikeoutItem1
			' 
			Me.toggleFontStrikeoutItem1.Glyph = (CType(resources.GetObject("toggleFontStrikeoutItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontStrikeoutItem1.Id = 22
			Me.toggleFontStrikeoutItem1.LargeGlyph = (CType(resources.GetObject("toggleFontStrikeoutItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1"
			Me.toggleFontStrikeoutItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontDoubleStrikeoutItem1
			' 
			Me.toggleFontDoubleStrikeoutItem1.Glyph = (CType(resources.GetObject("toggleFontDoubleStrikeoutItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontDoubleStrikeoutItem1.Id = 23
			Me.toggleFontDoubleStrikeoutItem1.LargeGlyph = (CType(resources.GetObject("toggleFontDoubleStrikeoutItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1"
			Me.toggleFontDoubleStrikeoutItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontSuperscriptItem1
			' 
			Me.toggleFontSuperscriptItem1.Glyph = (CType(resources.GetObject("toggleFontSuperscriptItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontSuperscriptItem1.Id = 24
			Me.toggleFontSuperscriptItem1.LargeGlyph = (CType(resources.GetObject("toggleFontSuperscriptItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1"
			Me.toggleFontSuperscriptItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleFontSubscriptItem1
			' 
			Me.toggleFontSubscriptItem1.Glyph = (CType(resources.GetObject("toggleFontSubscriptItem1.Glyph"), System.Drawing.Image))
			Me.toggleFontSubscriptItem1.Id = 25
			Me.toggleFontSubscriptItem1.LargeGlyph = (CType(resources.GetObject("toggleFontSubscriptItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1"
			Me.toggleFontSubscriptItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' changeTextCaseItem1
			' 
			Me.changeTextCaseItem1.Glyph = (CType(resources.GetObject("changeTextCaseItem1.Glyph"), System.Drawing.Image))
			Me.changeTextCaseItem1.Id = 26
			Me.changeTextCaseItem1.LargeGlyph = (CType(resources.GetObject("changeTextCaseItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeTextCaseItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextUpperCaseItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextLowerCaseItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTextCaseItem1)})
			Me.changeTextCaseItem1.Name = "changeTextCaseItem1"
			Me.changeTextCaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' makeTextUpperCaseItem1
			' 
			Me.makeTextUpperCaseItem1.Id = 27
			Me.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1"
			' 
			' makeTextLowerCaseItem1
			' 
			Me.makeTextLowerCaseItem1.Id = 28
			Me.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1"
			' 
			' toggleTextCaseItem1
			' 
			Me.toggleTextCaseItem1.Id = 29
			Me.toggleTextCaseItem1.Name = "toggleTextCaseItem1"
			' 
			' fontSizeIncreaseItem1
			' 
			Me.fontSizeIncreaseItem1.Glyph = (CType(resources.GetObject("fontSizeIncreaseItem1.Glyph"), System.Drawing.Image))
			Me.fontSizeIncreaseItem1.Id = 30
			Me.fontSizeIncreaseItem1.LargeGlyph = (CType(resources.GetObject("fontSizeIncreaseItem1.LargeGlyph"), System.Drawing.Image))
			Me.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1"
			Me.fontSizeIncreaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' fontSizeDecreaseItem1
			' 
			Me.fontSizeDecreaseItem1.Glyph = (CType(resources.GetObject("fontSizeDecreaseItem1.Glyph"), System.Drawing.Image))
			Me.fontSizeDecreaseItem1.Id = 31
			Me.fontSizeDecreaseItem1.LargeGlyph = (CType(resources.GetObject("fontSizeDecreaseItem1.LargeGlyph"), System.Drawing.Image))
			Me.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1"
			Me.fontSizeDecreaseItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' clearFormattingItem1
			' 
			Me.clearFormattingItem1.Glyph = (CType(resources.GetObject("clearFormattingItem1.Glyph"), System.Drawing.Image))
			Me.clearFormattingItem1.Id = 32
			Me.clearFormattingItem1.LargeGlyph = (CType(resources.GetObject("clearFormattingItem1.LargeGlyph"), System.Drawing.Image))
			Me.clearFormattingItem1.Name = "clearFormattingItem1"
			Me.clearFormattingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' showFontFormItem1
			' 
			Me.showFontFormItem1.Glyph = (CType(resources.GetObject("showFontFormItem1.Glyph"), System.Drawing.Image))
			Me.showFontFormItem1.Id = 33
			Me.showFontFormItem1.LargeGlyph = (CType(resources.GetObject("showFontFormItem1.LargeGlyph"), System.Drawing.Image))
			Me.showFontFormItem1.Name = "showFontFormItem1"
			Me.showFontFormItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleParagraphAlignmentLeftItem1
			' 
			Me.toggleParagraphAlignmentLeftItem1.Glyph = (CType(resources.GetObject("toggleParagraphAlignmentLeftItem1.Glyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentLeftItem1.Id = 34
			Me.toggleParagraphAlignmentLeftItem1.LargeGlyph = (CType(resources.GetObject("toggleParagraphAlignmentLeftItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1"
			Me.toggleParagraphAlignmentLeftItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleParagraphAlignmentCenterItem1
			' 
			Me.toggleParagraphAlignmentCenterItem1.Glyph = (CType(resources.GetObject("toggleParagraphAlignmentCenterItem1.Glyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentCenterItem1.Id = 35
			Me.toggleParagraphAlignmentCenterItem1.LargeGlyph = (CType(resources.GetObject("toggleParagraphAlignmentCenterItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1"
			Me.toggleParagraphAlignmentCenterItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleParagraphAlignmentRightItem1
			' 
			Me.toggleParagraphAlignmentRightItem1.Glyph = (CType(resources.GetObject("toggleParagraphAlignmentRightItem1.Glyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentRightItem1.Id = 36
			Me.toggleParagraphAlignmentRightItem1.LargeGlyph = (CType(resources.GetObject("toggleParagraphAlignmentRightItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1"
			Me.toggleParagraphAlignmentRightItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleParagraphAlignmentJustifyItem1
			' 
			Me.toggleParagraphAlignmentJustifyItem1.Glyph = (CType(resources.GetObject("toggleParagraphAlignmentJustifyItem1.Glyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentJustifyItem1.Id = 37
			Me.toggleParagraphAlignmentJustifyItem1.LargeGlyph = (CType(resources.GetObject("toggleParagraphAlignmentJustifyItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1"
			Me.toggleParagraphAlignmentJustifyItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' changeParagraphLineSpacingItem1
			' 
			Me.changeParagraphLineSpacingItem1.Glyph = (CType(resources.GetObject("changeParagraphLineSpacingItem1.Glyph"), System.Drawing.Image))
			Me.changeParagraphLineSpacingItem1.Id = 38
			Me.changeParagraphLineSpacingItem1.LargeGlyph = (CType(resources.GetObject("changeParagraphLineSpacingItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.setSingleParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.setSesquialteralParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.setDoubleParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.showLineSpacingFormItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingBeforeParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingBeforeParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingAfterParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingAfterParagraphItem1)})
			Me.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1"
			Me.changeParagraphLineSpacingItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' setSingleParagraphSpacingItem1
			' 
			Me.setSingleParagraphSpacingItem1.Id = 39
			Me.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1"
			' 
			' setSesquialteralParagraphSpacingItem1
			' 
			Me.setSesquialteralParagraphSpacingItem1.Id = 40
			Me.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1"
			' 
			' setDoubleParagraphSpacingItem1
			' 
			Me.setDoubleParagraphSpacingItem1.Id = 41
			Me.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1"
			' 
			' showLineSpacingFormItem1
			' 
			Me.showLineSpacingFormItem1.Id = 42
			Me.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1"
			' 
			' addSpacingBeforeParagraphItem1
			' 
			Me.addSpacingBeforeParagraphItem1.Id = 43
			Me.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1"
			' 
			' removeSpacingBeforeParagraphItem1
			' 
			Me.removeSpacingBeforeParagraphItem1.Id = 44
			Me.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1"
			' 
			' addSpacingAfterParagraphItem1
			' 
			Me.addSpacingAfterParagraphItem1.Id = 45
			Me.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1"
			' 
			' removeSpacingAfterParagraphItem1
			' 
			Me.removeSpacingAfterParagraphItem1.Id = 46
			Me.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1"
			' 
			' toggleBulletedListItem1
			' 
			Me.toggleBulletedListItem1.Glyph = (CType(resources.GetObject("toggleBulletedListItem1.Glyph"), System.Drawing.Image))
			Me.toggleBulletedListItem1.Id = 47
			Me.toggleBulletedListItem1.LargeGlyph = (CType(resources.GetObject("toggleBulletedListItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleBulletedListItem1.Name = "toggleBulletedListItem1"
			Me.toggleBulletedListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleNumberingListItem1
			' 
			Me.toggleNumberingListItem1.Glyph = (CType(resources.GetObject("toggleNumberingListItem1.Glyph"), System.Drawing.Image))
			Me.toggleNumberingListItem1.Id = 48
			Me.toggleNumberingListItem1.LargeGlyph = (CType(resources.GetObject("toggleNumberingListItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleNumberingListItem1.Name = "toggleNumberingListItem1"
			Me.toggleNumberingListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleMultiLevelListItem1
			' 
			Me.toggleMultiLevelListItem1.Glyph = (CType(resources.GetObject("toggleMultiLevelListItem1.Glyph"), System.Drawing.Image))
			Me.toggleMultiLevelListItem1.Id = 49
			Me.toggleMultiLevelListItem1.LargeGlyph = (CType(resources.GetObject("toggleMultiLevelListItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1"
			Me.toggleMultiLevelListItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' decreaseIndentItem1
			' 
			Me.decreaseIndentItem1.Glyph = (CType(resources.GetObject("decreaseIndentItem1.Glyph"), System.Drawing.Image))
			Me.decreaseIndentItem1.Id = 50
			Me.decreaseIndentItem1.LargeGlyph = (CType(resources.GetObject("decreaseIndentItem1.LargeGlyph"), System.Drawing.Image))
			Me.decreaseIndentItem1.Name = "decreaseIndentItem1"
			Me.decreaseIndentItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' increaseIndentItem1
			' 
			Me.increaseIndentItem1.Glyph = (CType(resources.GetObject("increaseIndentItem1.Glyph"), System.Drawing.Image))
			Me.increaseIndentItem1.Id = 51
			Me.increaseIndentItem1.LargeGlyph = (CType(resources.GetObject("increaseIndentItem1.LargeGlyph"), System.Drawing.Image))
			Me.increaseIndentItem1.Name = "increaseIndentItem1"
			Me.increaseIndentItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' toggleShowWhitespaceItem1
			' 
			Me.toggleShowWhitespaceItem1.Glyph = (CType(resources.GetObject("toggleShowWhitespaceItem1.Glyph"), System.Drawing.Image))
			Me.toggleShowWhitespaceItem1.Id = 52
			Me.toggleShowWhitespaceItem1.LargeGlyph = (CType(resources.GetObject("toggleShowWhitespaceItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1"
			Me.toggleShowWhitespaceItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' showParagraphFormItem1
			' 
			Me.showParagraphFormItem1.Glyph = (CType(resources.GetObject("showParagraphFormItem1.Glyph"), System.Drawing.Image))
			Me.showParagraphFormItem1.Id = 53
			Me.showParagraphFormItem1.LargeGlyph = (CType(resources.GetObject("showParagraphFormItem1.LargeGlyph"), System.Drawing.Image))
			Me.showParagraphFormItem1.Name = "showParagraphFormItem1"
			Me.showParagraphFormItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' changeStyleItem1
			' 
			Me.changeStyleItem1.Edit = Me.repositoryItemRichEditStyleEdit1
			Me.changeStyleItem1.Id = 54
			Me.changeStyleItem1.Name = "changeStyleItem1"
			' 
			' repositoryItemRichEditStyleEdit1
			' 
			Me.repositoryItemRichEditStyleEdit1.AutoHeight = False
			Me.repositoryItemRichEditStyleEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemRichEditStyleEdit1.Control = Me.richEdit
			Me.repositoryItemRichEditStyleEdit1.Name = "repositoryItemRichEditStyleEdit1"
			' 
			' findItem1
			' 
			Me.findItem1.Glyph = (CType(resources.GetObject("findItem1.Glyph"), System.Drawing.Image))
			Me.findItem1.Id = 55
			Me.findItem1.LargeGlyph = (CType(resources.GetObject("findItem1.LargeGlyph"), System.Drawing.Image))
			Me.findItem1.Name = "findItem1"
			' 
			' replaceItem1
			' 
			Me.replaceItem1.Glyph = (CType(resources.GetObject("replaceItem1.Glyph"), System.Drawing.Image))
			Me.replaceItem1.Id = 56
			Me.replaceItem1.LargeGlyph = (CType(resources.GetObject("replaceItem1.LargeGlyph"), System.Drawing.Image))
			Me.replaceItem1.Name = "replaceItem1"
			' 
			' insertPageBreakItem1
			' 
			Me.insertPageBreakItem1.Glyph = (CType(resources.GetObject("insertPageBreakItem1.Glyph"), System.Drawing.Image))
			Me.insertPageBreakItem1.Id = 57
			Me.insertPageBreakItem1.LargeGlyph = (CType(resources.GetObject("insertPageBreakItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertPageBreakItem1.Name = "insertPageBreakItem1"
			' 
			' insertTableItem1
			' 
			Me.insertTableItem1.Glyph = (CType(resources.GetObject("insertTableItem1.Glyph"), System.Drawing.Image))
			Me.insertTableItem1.Id = 58
			Me.insertTableItem1.LargeGlyph = (CType(resources.GetObject("insertTableItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableItem1.Name = "insertTableItem1"
			' 
			' insertPictureItem1
			' 
			Me.insertPictureItem1.Glyph = (CType(resources.GetObject("insertPictureItem1.Glyph"), System.Drawing.Image))
			Me.insertPictureItem1.Id = 59
			Me.insertPictureItem1.LargeGlyph = (CType(resources.GetObject("insertPictureItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertPictureItem1.Name = "insertPictureItem1"
			' 
			' insertBookmarkItem1
			' 
			Me.insertBookmarkItem1.Glyph = (CType(resources.GetObject("insertBookmarkItem1.Glyph"), System.Drawing.Image))
			Me.insertBookmarkItem1.Id = 60
			Me.insertBookmarkItem1.LargeGlyph = (CType(resources.GetObject("insertBookmarkItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertBookmarkItem1.Name = "insertBookmarkItem1"
			' 
			' insertHyperlinkItem1
			' 
			Me.insertHyperlinkItem1.Glyph = (CType(resources.GetObject("insertHyperlinkItem1.Glyph"), System.Drawing.Image))
			Me.insertHyperlinkItem1.Id = 61
			Me.insertHyperlinkItem1.LargeGlyph = (CType(resources.GetObject("insertHyperlinkItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertHyperlinkItem1.Name = "insertHyperlinkItem1"
			' 
			' editPageHeaderItem1
			' 
			Me.editPageHeaderItem1.Glyph = (CType(resources.GetObject("editPageHeaderItem1.Glyph"), System.Drawing.Image))
			Me.editPageHeaderItem1.Id = 62
			Me.editPageHeaderItem1.LargeGlyph = (CType(resources.GetObject("editPageHeaderItem1.LargeGlyph"), System.Drawing.Image))
			Me.editPageHeaderItem1.Name = "editPageHeaderItem1"
			' 
			' editPageFooterItem1
			' 
			Me.editPageFooterItem1.Glyph = (CType(resources.GetObject("editPageFooterItem1.Glyph"), System.Drawing.Image))
			Me.editPageFooterItem1.Id = 63
			Me.editPageFooterItem1.LargeGlyph = (CType(resources.GetObject("editPageFooterItem1.LargeGlyph"), System.Drawing.Image))
			Me.editPageFooterItem1.Name = "editPageFooterItem1"
			' 
			' insertPageNumberItem1
			' 
			Me.insertPageNumberItem1.Glyph = (CType(resources.GetObject("insertPageNumberItem1.Glyph"), System.Drawing.Image))
			Me.insertPageNumberItem1.Id = 64
			Me.insertPageNumberItem1.LargeGlyph = (CType(resources.GetObject("insertPageNumberItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertPageNumberItem1.Name = "insertPageNumberItem1"
			' 
			' insertPageCountItem1
			' 
			Me.insertPageCountItem1.Glyph = (CType(resources.GetObject("insertPageCountItem1.Glyph"), System.Drawing.Image))
			Me.insertPageCountItem1.Id = 65
			Me.insertPageCountItem1.LargeGlyph = (CType(resources.GetObject("insertPageCountItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertPageCountItem1.Name = "insertPageCountItem1"
			' 
			' insertSymbolItem1
			' 
			Me.insertSymbolItem1.Glyph = (CType(resources.GetObject("insertSymbolItem1.Glyph"), System.Drawing.Image))
			Me.insertSymbolItem1.Id = 66
			Me.insertSymbolItem1.LargeGlyph = (CType(resources.GetObject("insertSymbolItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertSymbolItem1.Name = "insertSymbolItem1"
			' 
			' changeTableCellsShadingItem1
			' 
			Me.changeTableCellsShadingItem1.Glyph = (CType(resources.GetObject("changeTableCellsShadingItem1.Glyph"), System.Drawing.Image))
			Me.changeTableCellsShadingItem1.Id = 67
			Me.changeTableCellsShadingItem1.LargeGlyph = (CType(resources.GetObject("changeTableCellsShadingItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeTableCellsShadingItem1.Name = "changeTableCellsShadingItem1"
			' 
			' changeTableBordersItem1
			' 
			Me.changeTableBordersItem1.Glyph = (CType(resources.GetObject("changeTableBordersItem1.Glyph"), System.Drawing.Image))
			Me.changeTableBordersItem1.Id = 68
			Me.changeTableBordersItem1.LargeGlyph = (CType(resources.GetObject("changeTableBordersItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeTableBordersItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsBottomBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsTopBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsLeftBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsRightBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.resetTableCellsAllBordersItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsAllBordersItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsOutsideBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideHorizontalBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableCellsInsideVerticalBorderItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleShowTableGridLinesItem1)})
			Me.changeTableBordersItem1.Name = "changeTableBordersItem1"
			' 
			' toggleTableCellsBottomBorderItem1
			' 
			Me.toggleTableCellsBottomBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsBottomBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomBorderItem1.Id = 69
			Me.toggleTableCellsBottomBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsBottomBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomBorderItem1.Name = "toggleTableCellsBottomBorderItem1"
			' 
			' toggleTableCellsTopBorderItem1
			' 
			Me.toggleTableCellsTopBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsTopBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsTopBorderItem1.Id = 70
			Me.toggleTableCellsTopBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsTopBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsTopBorderItem1.Name = "toggleTableCellsTopBorderItem1"
			' 
			' toggleTableCellsLeftBorderItem1
			' 
			Me.toggleTableCellsLeftBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsLeftBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsLeftBorderItem1.Id = 71
			Me.toggleTableCellsLeftBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsLeftBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsLeftBorderItem1.Name = "toggleTableCellsLeftBorderItem1"
			' 
			' toggleTableCellsRightBorderItem1
			' 
			Me.toggleTableCellsRightBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsRightBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsRightBorderItem1.Id = 72
			Me.toggleTableCellsRightBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsRightBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsRightBorderItem1.Name = "toggleTableCellsRightBorderItem1"
			' 
			' resetTableCellsAllBordersItem1
			' 
			Me.resetTableCellsAllBordersItem1.Glyph = (CType(resources.GetObject("resetTableCellsAllBordersItem1.Glyph"), System.Drawing.Image))
			Me.resetTableCellsAllBordersItem1.Id = 73
			Me.resetTableCellsAllBordersItem1.LargeGlyph = (CType(resources.GetObject("resetTableCellsAllBordersItem1.LargeGlyph"), System.Drawing.Image))
			Me.resetTableCellsAllBordersItem1.Name = "resetTableCellsAllBordersItem1"
			' 
			' toggleTableCellsAllBordersItem1
			' 
			Me.toggleTableCellsAllBordersItem1.Glyph = (CType(resources.GetObject("toggleTableCellsAllBordersItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsAllBordersItem1.Id = 74
			Me.toggleTableCellsAllBordersItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsAllBordersItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsAllBordersItem1.Name = "toggleTableCellsAllBordersItem1"
			' 
			' toggleTableCellsOutsideBorderItem1
			' 
			Me.toggleTableCellsOutsideBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsOutsideBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsOutsideBorderItem1.Id = 75
			Me.toggleTableCellsOutsideBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsOutsideBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsOutsideBorderItem1.Name = "toggleTableCellsOutsideBorderItem1"
			' 
			' toggleTableCellsInsideBorderItem1
			' 
			Me.toggleTableCellsInsideBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsInsideBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideBorderItem1.Id = 76
			Me.toggleTableCellsInsideBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsInsideBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideBorderItem1.Name = "toggleTableCellsInsideBorderItem1"
			' 
			' toggleTableCellsInsideHorizontalBorderItem1
			' 
			Me.toggleTableCellsInsideHorizontalBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsInsideHorizontalBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideHorizontalBorderItem1.Id = 77
			Me.toggleTableCellsInsideHorizontalBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsInsideHorizontalBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideHorizontalBorderItem1.Name = "toggleTableCellsInsideHorizontalBorderItem1"
			' 
			' toggleTableCellsInsideVerticalBorderItem1
			' 
			Me.toggleTableCellsInsideVerticalBorderItem1.Glyph = (CType(resources.GetObject("toggleTableCellsInsideVerticalBorderItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideVerticalBorderItem1.Id = 78
			Me.toggleTableCellsInsideVerticalBorderItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsInsideVerticalBorderItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsInsideVerticalBorderItem1.Name = "toggleTableCellsInsideVerticalBorderItem1"
			' 
			' toggleShowTableGridLinesItem1
			' 
			Me.toggleShowTableGridLinesItem1.Glyph = (CType(resources.GetObject("toggleShowTableGridLinesItem1.Glyph"), System.Drawing.Image))
			Me.toggleShowTableGridLinesItem1.Id = 79
			Me.toggleShowTableGridLinesItem1.LargeGlyph = (CType(resources.GetObject("toggleShowTableGridLinesItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleShowTableGridLinesItem1.Name = "toggleShowTableGridLinesItem1"
			' 
			' changeTableBorderLineStyleItem1
			' 
			Me.changeTableBorderLineStyleItem1.Edit = Me.repositoryItemBorderLineStyle1
			borderInfo1.Color = System.Drawing.Color.Black
			borderInfo1.Frame = False
			borderInfo1.Offset = 0
			borderInfo1.Shadow = False
			borderInfo1.Style = DevExpress.XtraRichEdit.Model.BorderLineStyle.Single
			borderInfo1.Width = 10
			Me.changeTableBorderLineStyleItem1.EditValue = borderInfo1
			Me.changeTableBorderLineStyleItem1.Id = 80
			Me.changeTableBorderLineStyleItem1.Name = "changeTableBorderLineStyleItem1"
			' 
			' repositoryItemBorderLineStyle1
			' 
			Me.repositoryItemBorderLineStyle1.AutoHeight = False
			Me.repositoryItemBorderLineStyle1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemBorderLineStyle1.Control = Me.richEdit
			Me.repositoryItemBorderLineStyle1.Name = "repositoryItemBorderLineStyle1"
			' 
			' changeTableBorderLineWeightItem1
			' 
			Me.changeTableBorderLineWeightItem1.Edit = Me.repositoryItemBorderLineWeight1
			Me.changeTableBorderLineWeightItem1.EditValue = 20
			Me.changeTableBorderLineWeightItem1.Id = 81
			Me.changeTableBorderLineWeightItem1.Name = "changeTableBorderLineWeightItem1"
			' 
			' repositoryItemBorderLineWeight1
			' 
			Me.repositoryItemBorderLineWeight1.AutoHeight = False
			Me.repositoryItemBorderLineWeight1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemBorderLineWeight1.Control = Me.richEdit
			Me.repositoryItemBorderLineWeight1.Name = "repositoryItemBorderLineWeight1"
			' 
			' changeTableBorderColorItem1
			' 
			Me.changeTableBorderColorItem1.Glyph = (CType(resources.GetObject("changeTableBorderColorItem1.Glyph"), System.Drawing.Image))
			Me.changeTableBorderColorItem1.Id = 82
			Me.changeTableBorderColorItem1.LargeGlyph = (CType(resources.GetObject("changeTableBorderColorItem1.LargeGlyph"), System.Drawing.Image))
			Me.changeTableBorderColorItem1.Name = "changeTableBorderColorItem1"
			' 
			' selectTableElementsItem1
			' 
			Me.selectTableElementsItem1.Glyph = (CType(resources.GetObject("selectTableElementsItem1.Glyph"), System.Drawing.Image))
			Me.selectTableElementsItem1.Id = 83
			Me.selectTableElementsItem1.LargeGlyph = (CType(resources.GetObject("selectTableElementsItem1.LargeGlyph"), System.Drawing.Image))
			Me.selectTableElementsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableCellItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableColumnItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableRowItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.selectTableItem1)})
			Me.selectTableElementsItem1.Name = "selectTableElementsItem1"
			' 
			' selectTableCellItem1
			' 
			Me.selectTableCellItem1.Glyph = (CType(resources.GetObject("selectTableCellItem1.Glyph"), System.Drawing.Image))
			Me.selectTableCellItem1.Id = 84
			Me.selectTableCellItem1.LargeGlyph = (CType(resources.GetObject("selectTableCellItem1.LargeGlyph"), System.Drawing.Image))
			Me.selectTableCellItem1.Name = "selectTableCellItem1"
			' 
			' selectTableColumnItem1
			' 
			Me.selectTableColumnItem1.Glyph = (CType(resources.GetObject("selectTableColumnItem1.Glyph"), System.Drawing.Image))
			Me.selectTableColumnItem1.Id = 85
			Me.selectTableColumnItem1.LargeGlyph = (CType(resources.GetObject("selectTableColumnItem1.LargeGlyph"), System.Drawing.Image))
			Me.selectTableColumnItem1.Name = "selectTableColumnItem1"
			' 
			' selectTableRowItem1
			' 
			Me.selectTableRowItem1.Glyph = (CType(resources.GetObject("selectTableRowItem1.Glyph"), System.Drawing.Image))
			Me.selectTableRowItem1.Id = 86
			Me.selectTableRowItem1.LargeGlyph = (CType(resources.GetObject("selectTableRowItem1.LargeGlyph"), System.Drawing.Image))
			Me.selectTableRowItem1.Name = "selectTableRowItem1"
			' 
			' selectTableItem1
			' 
			Me.selectTableItem1.Glyph = (CType(resources.GetObject("selectTableItem1.Glyph"), System.Drawing.Image))
			Me.selectTableItem1.Id = 87
			Me.selectTableItem1.LargeGlyph = (CType(resources.GetObject("selectTableItem1.LargeGlyph"), System.Drawing.Image))
			Me.selectTableItem1.Name = "selectTableItem1"
			' 
			' showTablePropertiesFormItem1
			' 
			Me.showTablePropertiesFormItem1.Glyph = (CType(resources.GetObject("showTablePropertiesFormItem1.Glyph"), System.Drawing.Image))
			Me.showTablePropertiesFormItem1.Id = 88
			Me.showTablePropertiesFormItem1.LargeGlyph = (CType(resources.GetObject("showTablePropertiesFormItem1.LargeGlyph"), System.Drawing.Image))
			Me.showTablePropertiesFormItem1.Name = "showTablePropertiesFormItem1"
			' 
			' deleteTableElementsItem1
			' 
			Me.deleteTableElementsItem1.Glyph = (CType(resources.GetObject("deleteTableElementsItem1.Glyph"), System.Drawing.Image))
			Me.deleteTableElementsItem1.Id = 89
			Me.deleteTableElementsItem1.LargeGlyph = (CType(resources.GetObject("deleteTableElementsItem1.LargeGlyph"), System.Drawing.Image))
			Me.deleteTableElementsItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.showDeleteTableCellsFormItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableColumnsItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableRowsItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.deleteTableItem1)})
			Me.deleteTableElementsItem1.Name = "deleteTableElementsItem1"
			' 
			' showDeleteTableCellsFormItem1
			' 
			Me.showDeleteTableCellsFormItem1.Glyph = (CType(resources.GetObject("showDeleteTableCellsFormItem1.Glyph"), System.Drawing.Image))
			Me.showDeleteTableCellsFormItem1.Id = 90
			Me.showDeleteTableCellsFormItem1.LargeGlyph = (CType(resources.GetObject("showDeleteTableCellsFormItem1.LargeGlyph"), System.Drawing.Image))
			Me.showDeleteTableCellsFormItem1.Name = "showDeleteTableCellsFormItem1"
			' 
			' deleteTableColumnsItem1
			' 
			Me.deleteTableColumnsItem1.Glyph = (CType(resources.GetObject("deleteTableColumnsItem1.Glyph"), System.Drawing.Image))
			Me.deleteTableColumnsItem1.Id = 91
			Me.deleteTableColumnsItem1.LargeGlyph = (CType(resources.GetObject("deleteTableColumnsItem1.LargeGlyph"), System.Drawing.Image))
			Me.deleteTableColumnsItem1.Name = "deleteTableColumnsItem1"
			' 
			' deleteTableRowsItem1
			' 
			Me.deleteTableRowsItem1.Glyph = (CType(resources.GetObject("deleteTableRowsItem1.Glyph"), System.Drawing.Image))
			Me.deleteTableRowsItem1.Id = 92
			Me.deleteTableRowsItem1.LargeGlyph = (CType(resources.GetObject("deleteTableRowsItem1.LargeGlyph"), System.Drawing.Image))
			Me.deleteTableRowsItem1.Name = "deleteTableRowsItem1"
			' 
			' deleteTableItem1
			' 
			Me.deleteTableItem1.Glyph = (CType(resources.GetObject("deleteTableItem1.Glyph"), System.Drawing.Image))
			Me.deleteTableItem1.Id = 93
			Me.deleteTableItem1.LargeGlyph = (CType(resources.GetObject("deleteTableItem1.LargeGlyph"), System.Drawing.Image))
			Me.deleteTableItem1.Name = "deleteTableItem1"
			' 
			' insertTableRowAboveItem1
			' 
			Me.insertTableRowAboveItem1.Glyph = (CType(resources.GetObject("insertTableRowAboveItem1.Glyph"), System.Drawing.Image))
			Me.insertTableRowAboveItem1.Id = 94
			Me.insertTableRowAboveItem1.LargeGlyph = (CType(resources.GetObject("insertTableRowAboveItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableRowAboveItem1.Name = "insertTableRowAboveItem1"
			' 
			' insertTableRowBelowItem1
			' 
			Me.insertTableRowBelowItem1.Glyph = (CType(resources.GetObject("insertTableRowBelowItem1.Glyph"), System.Drawing.Image))
			Me.insertTableRowBelowItem1.Id = 95
			Me.insertTableRowBelowItem1.LargeGlyph = (CType(resources.GetObject("insertTableRowBelowItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableRowBelowItem1.Name = "insertTableRowBelowItem1"
			' 
			' insertTableColumnToLeftItem1
			' 
			Me.insertTableColumnToLeftItem1.Glyph = (CType(resources.GetObject("insertTableColumnToLeftItem1.Glyph"), System.Drawing.Image))
			Me.insertTableColumnToLeftItem1.Id = 96
			Me.insertTableColumnToLeftItem1.LargeGlyph = (CType(resources.GetObject("insertTableColumnToLeftItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableColumnToLeftItem1.Name = "insertTableColumnToLeftItem1"
			' 
			' insertTableColumnToRightItem1
			' 
			Me.insertTableColumnToRightItem1.Glyph = (CType(resources.GetObject("insertTableColumnToRightItem1.Glyph"), System.Drawing.Image))
			Me.insertTableColumnToRightItem1.Id = 97
			Me.insertTableColumnToRightItem1.LargeGlyph = (CType(resources.GetObject("insertTableColumnToRightItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableColumnToRightItem1.Name = "insertTableColumnToRightItem1"
			' 
			' showInsertTableCellsFormItem1
			' 
			Me.showInsertTableCellsFormItem1.Glyph = (CType(resources.GetObject("showInsertTableCellsFormItem1.Glyph"), System.Drawing.Image))
			Me.showInsertTableCellsFormItem1.Id = 98
			Me.showInsertTableCellsFormItem1.LargeGlyph = (CType(resources.GetObject("showInsertTableCellsFormItem1.LargeGlyph"), System.Drawing.Image))
			Me.showInsertTableCellsFormItem1.Name = "showInsertTableCellsFormItem1"
			' 
			' mergeTableCellsItem1
			' 
			Me.mergeTableCellsItem1.Glyph = (CType(resources.GetObject("mergeTableCellsItem1.Glyph"), System.Drawing.Image))
			Me.mergeTableCellsItem1.Id = 99
			Me.mergeTableCellsItem1.LargeGlyph = (CType(resources.GetObject("mergeTableCellsItem1.LargeGlyph"), System.Drawing.Image))
			Me.mergeTableCellsItem1.Name = "mergeTableCellsItem1"
			' 
			' showSplitTableCellsForm1
			' 
			Me.showSplitTableCellsForm1.Glyph = (CType(resources.GetObject("showSplitTableCellsForm1.Glyph"), System.Drawing.Image))
			Me.showSplitTableCellsForm1.Id = 100
			Me.showSplitTableCellsForm1.LargeGlyph = (CType(resources.GetObject("showSplitTableCellsForm1.LargeGlyph"), System.Drawing.Image))
			Me.showSplitTableCellsForm1.Name = "showSplitTableCellsForm1"
			' 
			' splitTableItem1
			' 
			Me.splitTableItem1.Glyph = (CType(resources.GetObject("splitTableItem1.Glyph"), System.Drawing.Image))
			Me.splitTableItem1.Id = 101
			Me.splitTableItem1.LargeGlyph = (CType(resources.GetObject("splitTableItem1.LargeGlyph"), System.Drawing.Image))
			Me.splitTableItem1.Name = "splitTableItem1"
			' 
			' toggleTableAutoFitItem1
			' 
			Me.toggleTableAutoFitItem1.Glyph = (CType(resources.GetObject("toggleTableAutoFitItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableAutoFitItem1.Id = 102
			Me.toggleTableAutoFitItem1.LargeGlyph = (CType(resources.GetObject("toggleTableAutoFitItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableAutoFitItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableAutoFitContentsItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableAutoFitWindowItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTableFixedColumnWidthItem1)})
			Me.toggleTableAutoFitItem1.Name = "toggleTableAutoFitItem1"
			' 
			' toggleTableAutoFitContentsItem1
			' 
			Me.toggleTableAutoFitContentsItem1.Glyph = (CType(resources.GetObject("toggleTableAutoFitContentsItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableAutoFitContentsItem1.Id = 103
			Me.toggleTableAutoFitContentsItem1.LargeGlyph = (CType(resources.GetObject("toggleTableAutoFitContentsItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableAutoFitContentsItem1.Name = "toggleTableAutoFitContentsItem1"
			' 
			' toggleTableAutoFitWindowItem1
			' 
			Me.toggleTableAutoFitWindowItem1.Glyph = (CType(resources.GetObject("toggleTableAutoFitWindowItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableAutoFitWindowItem1.Id = 104
			Me.toggleTableAutoFitWindowItem1.LargeGlyph = (CType(resources.GetObject("toggleTableAutoFitWindowItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableAutoFitWindowItem1.Name = "toggleTableAutoFitWindowItem1"
			' 
			' toggleTableFixedColumnWidthItem1
			' 
			Me.toggleTableFixedColumnWidthItem1.Glyph = (CType(resources.GetObject("toggleTableFixedColumnWidthItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableFixedColumnWidthItem1.Id = 105
			Me.toggleTableFixedColumnWidthItem1.LargeGlyph = (CType(resources.GetObject("toggleTableFixedColumnWidthItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableFixedColumnWidthItem1.Name = "toggleTableFixedColumnWidthItem1"
			' 
			' toggleTableCellsTopLeftAlignmentItem1
			' 
			Me.toggleTableCellsTopLeftAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsTopLeftAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsTopLeftAlignmentItem1.Id = 106
			Me.toggleTableCellsTopLeftAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsTopLeftAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsTopLeftAlignmentItem1.Name = "toggleTableCellsTopLeftAlignmentItem1"
			' 
			' toggleTableCellsTopCenterAlignmentItem1
			' 
			Me.toggleTableCellsTopCenterAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsTopCenterAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsTopCenterAlignmentItem1.Id = 107
			Me.toggleTableCellsTopCenterAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsTopCenterAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsTopCenterAlignmentItem1.Name = "toggleTableCellsTopCenterAlignmentItem1"
			' 
			' toggleTableCellsTopRightAlignmentItem1
			' 
			Me.toggleTableCellsTopRightAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsTopRightAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsTopRightAlignmentItem1.Id = 108
			Me.toggleTableCellsTopRightAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsTopRightAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsTopRightAlignmentItem1.Name = "toggleTableCellsTopRightAlignmentItem1"
			' 
			' toggleTableCellsMiddleLeftAlignmentItem1
			' 
			Me.toggleTableCellsMiddleLeftAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsMiddleLeftAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleLeftAlignmentItem1.Id = 109
			Me.toggleTableCellsMiddleLeftAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsMiddleLeftAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleLeftAlignmentItem1.Name = "toggleTableCellsMiddleLeftAlignmentItem1"
			' 
			' toggleTableCellsMiddleCenterAlignmentItem1
			' 
			Me.toggleTableCellsMiddleCenterAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsMiddleCenterAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleCenterAlignmentItem1.Id = 110
			Me.toggleTableCellsMiddleCenterAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsMiddleCenterAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleCenterAlignmentItem1.Name = "toggleTableCellsMiddleCenterAlignmentItem1"
			' 
			' toggleTableCellsMiddleRightAlignmentItem1
			' 
			Me.toggleTableCellsMiddleRightAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsMiddleRightAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleRightAlignmentItem1.Id = 111
			Me.toggleTableCellsMiddleRightAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsMiddleRightAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsMiddleRightAlignmentItem1.Name = "toggleTableCellsMiddleRightAlignmentItem1"
			' 
			' toggleTableCellsBottomLeftAlignmentItem1
			' 
			Me.toggleTableCellsBottomLeftAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsBottomLeftAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomLeftAlignmentItem1.Id = 112
			Me.toggleTableCellsBottomLeftAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsBottomLeftAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomLeftAlignmentItem1.Name = "toggleTableCellsBottomLeftAlignmentItem1"
			' 
			' toggleTableCellsBottomCenterAlignmentItem1
			' 
			Me.toggleTableCellsBottomCenterAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsBottomCenterAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomCenterAlignmentItem1.Id = 113
			Me.toggleTableCellsBottomCenterAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsBottomCenterAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomCenterAlignmentItem1.Name = "toggleTableCellsBottomCenterAlignmentItem1"
			' 
			' toggleTableCellsBottomRightAlignmentItem1
			' 
			Me.toggleTableCellsBottomRightAlignmentItem1.Glyph = (CType(resources.GetObject("toggleTableCellsBottomRightAlignmentItem1.Glyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomRightAlignmentItem1.Id = 114
			Me.toggleTableCellsBottomRightAlignmentItem1.LargeGlyph = (CType(resources.GetObject("toggleTableCellsBottomRightAlignmentItem1.LargeGlyph"), System.Drawing.Image))
			Me.toggleTableCellsBottomRightAlignmentItem1.Name = "toggleTableCellsBottomRightAlignmentItem1"
			' 
			' setParagraphHeadingLevelItem1
			' 
			Me.setParagraphHeadingLevelItem1.Id = 118
			Me.setParagraphHeadingLevelItem1.Name = "setParagraphHeadingLevelItem1"
			Me.setParagraphHeadingLevelItem1.OutlineLevel = 0
			' 
			' setParagraphHeadingLevelItem2
			' 
			Me.setParagraphHeadingLevelItem2.Id = 119
			Me.setParagraphHeadingLevelItem2.Name = "setParagraphHeadingLevelItem2"
			Me.setParagraphHeadingLevelItem2.OutlineLevel = 1
			' 
			' setParagraphHeadingLevelItem3
			' 
			Me.setParagraphHeadingLevelItem3.Id = 120
			Me.setParagraphHeadingLevelItem3.Name = "setParagraphHeadingLevelItem3"
			Me.setParagraphHeadingLevelItem3.OutlineLevel = 2
			' 
			' setParagraphHeadingLevelItem4
			' 
			Me.setParagraphHeadingLevelItem4.Id = 121
			Me.setParagraphHeadingLevelItem4.Name = "setParagraphHeadingLevelItem4"
			Me.setParagraphHeadingLevelItem4.OutlineLevel = 3
			' 
			' setParagraphHeadingLevelItem5
			' 
			Me.setParagraphHeadingLevelItem5.Id = 122
			Me.setParagraphHeadingLevelItem5.Name = "setParagraphHeadingLevelItem5"
			Me.setParagraphHeadingLevelItem5.OutlineLevel = 4
			' 
			' setParagraphHeadingLevelItem6
			' 
			Me.setParagraphHeadingLevelItem6.Id = 123
			Me.setParagraphHeadingLevelItem6.Name = "setParagraphHeadingLevelItem6"
			Me.setParagraphHeadingLevelItem6.OutlineLevel = 5
			' 
			' setParagraphHeadingLevelItem7
			' 
			Me.setParagraphHeadingLevelItem7.Id = 124
			Me.setParagraphHeadingLevelItem7.Name = "setParagraphHeadingLevelItem7"
			Me.setParagraphHeadingLevelItem7.OutlineLevel = 6
			' 
			' setParagraphHeadingLevelItem8
			' 
			Me.setParagraphHeadingLevelItem8.Id = 125
			Me.setParagraphHeadingLevelItem8.Name = "setParagraphHeadingLevelItem8"
			Me.setParagraphHeadingLevelItem8.OutlineLevel = 7
			' 
			' setParagraphHeadingLevelItem9
			' 
			Me.setParagraphHeadingLevelItem9.Id = 126
			Me.setParagraphHeadingLevelItem9.Name = "setParagraphHeadingLevelItem9"
			Me.setParagraphHeadingLevelItem9.OutlineLevel = 8
			' 
			' setParagraphHeadingLevelItem10
			' 
			Me.setParagraphHeadingLevelItem10.Id = 127
			Me.setParagraphHeadingLevelItem10.Name = "setParagraphHeadingLevelItem10"
			Me.setParagraphHeadingLevelItem10.OutlineLevel = 9
			' 
			' insertFiguresCaptionItems1
			' 
			Me.insertFiguresCaptionItems1.Glyph = (CType(resources.GetObject("insertFiguresCaptionItems1.Glyph"), System.Drawing.Image))
			Me.insertFiguresCaptionItems1.Id = 129
			Me.insertFiguresCaptionItems1.LargeGlyph = (CType(resources.GetObject("insertFiguresCaptionItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertFiguresCaptionItems1.Name = "insertFiguresCaptionItems1"
			' 
			' insertTablesCaptionItems1
			' 
			Me.insertTablesCaptionItems1.Glyph = (CType(resources.GetObject("insertTablesCaptionItems1.Glyph"), System.Drawing.Image))
			Me.insertTablesCaptionItems1.Id = 130
			Me.insertTablesCaptionItems1.LargeGlyph = (CType(resources.GetObject("insertTablesCaptionItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertTablesCaptionItems1.Name = "insertTablesCaptionItems1"
			' 
			' insertEquationsCaptionItems1
			' 
			Me.insertEquationsCaptionItems1.Glyph = (CType(resources.GetObject("insertEquationsCaptionItems1.Glyph"), System.Drawing.Image))
			Me.insertEquationsCaptionItems1.Id = 131
			Me.insertEquationsCaptionItems1.LargeGlyph = (CType(resources.GetObject("insertEquationsCaptionItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertEquationsCaptionItems1.Name = "insertEquationsCaptionItems1"
			' 
			' insertTableOfFiguresItems1
			' 
			Me.insertTableOfFiguresItems1.Glyph = (CType(resources.GetObject("insertTableOfFiguresItems1.Glyph"), System.Drawing.Image))
			Me.insertTableOfFiguresItems1.Id = 133
			Me.insertTableOfFiguresItems1.LargeGlyph = (CType(resources.GetObject("insertTableOfFiguresItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfFiguresItems1.Name = "insertTableOfFiguresItems1"
			' 
			' insertTableOfTablesItems1
			' 
			Me.insertTableOfTablesItems1.Glyph = (CType(resources.GetObject("insertTableOfTablesItems1.Glyph"), System.Drawing.Image))
			Me.insertTableOfTablesItems1.Id = 134
			Me.insertTableOfTablesItems1.LargeGlyph = (CType(resources.GetObject("insertTableOfTablesItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfTablesItems1.Name = "insertTableOfTablesItems1"
			' 
			' insertTableOfEquationsItems1
			' 
			Me.insertTableOfEquationsItems1.Glyph = (CType(resources.GetObject("insertTableOfEquationsItems1.Glyph"), System.Drawing.Image))
			Me.insertTableOfEquationsItems1.Id = 135
			Me.insertTableOfEquationsItems1.LargeGlyph = (CType(resources.GetObject("insertTableOfEquationsItems1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfEquationsItems1.Name = "insertTableOfEquationsItems1"
			' 
			' showAllFieldCodesItem1
			' 
			Me.showAllFieldCodesItem1.Glyph = (CType(resources.GetObject("showAllFieldCodesItem1.Glyph"), System.Drawing.Image))
			Me.showAllFieldCodesItem1.Id = 137
			Me.showAllFieldCodesItem1.LargeGlyph = (CType(resources.GetObject("showAllFieldCodesItem1.LargeGlyph"), System.Drawing.Image))
			Me.showAllFieldCodesItem1.Name = "showAllFieldCodesItem1"
			' 
			' showAllFieldResultsItem1
			' 
			Me.showAllFieldResultsItem1.Glyph = (CType(resources.GetObject("showAllFieldResultsItem1.Glyph"), System.Drawing.Image))
			Me.showAllFieldResultsItem1.Id = 138
			Me.showAllFieldResultsItem1.LargeGlyph = (CType(resources.GetObject("showAllFieldResultsItem1.LargeGlyph"), System.Drawing.Image))
			Me.showAllFieldResultsItem1.Name = "showAllFieldResultsItem1"
			' 
			' barStaticItem1
			' 
			Me.barStaticItem1.Caption = "barStaticItem1"
			Me.barStaticItem1.Id = 151
			Me.barStaticItem1.Name = "barStaticItem1"
			Me.barStaticItem1.TextAlignment = System.Drawing.StringAlignment.Near
			' 
			' barStaticItem2
			' 
			Me.barStaticItem2.Caption = "barStaticItem2"
			Me.barStaticItem2.Id = 156
			Me.barStaticItem2.Name = "barStaticItem2"
			Me.barStaticItem2.TextAlignment = System.Drawing.StringAlignment.Near
			' 
			' barButtonItem1
			' 
			Me.barButtonItem1.Caption = "barButtonItem1"
			Me.barButtonItem1.Id = 157
			Me.barButtonItem1.Name = "barButtonItem1"
			' 
			' barCheckItem1
			' 
			Me.barCheckItem1.Caption = "barCheckItem1"
			Me.barCheckItem1.Id = 158
			Me.barCheckItem1.Name = "barCheckItem1"
			' 
			' barButtonGroup3
			' 
			Me.barButtonGroup3.Caption = "barButtonGroup3"
			Me.barButtonGroup3.Id = 159
			Me.barButtonGroup3.Name = "barButtonGroup3"
			' 
			' barButtonGroup4
			' 
			Me.barButtonGroup4.Caption = "barButtonGroup4"
			Me.barButtonGroup4.Id = 160
			Me.barButtonGroup4.Name = "barButtonGroup4"
			' 
			' insertTableOfContentsItem1
			' 
			Me.insertTableOfContentsItem1.Glyph = (CType(resources.GetObject("insertTableOfContentsItem1.Glyph"), System.Drawing.Image))
			Me.insertTableOfContentsItem1.Id = 161
			Me.insertTableOfContentsItem1.LargeGlyph = (CType(resources.GetObject("insertTableOfContentsItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfContentsItem1.Name = "insertTableOfContentsItem1"
			' 
			' updateTableOfContentsItem1
			' 
			Me.updateTableOfContentsItem1.Glyph = (CType(resources.GetObject("updateTableOfContentsItem1.Glyph"), System.Drawing.Image))
			Me.updateTableOfContentsItem1.Id = 162
			Me.updateTableOfContentsItem1.LargeGlyph = (CType(resources.GetObject("updateTableOfContentsItem1.LargeGlyph"), System.Drawing.Image))
			Me.updateTableOfContentsItem1.Name = "updateTableOfContentsItem1"
			' 
			' addParagraphsToTableOfContentItem1
			' 
			Me.addParagraphsToTableOfContentItem1.Glyph = (CType(resources.GetObject("addParagraphsToTableOfContentItem1.Glyph"), System.Drawing.Image))
			Me.addParagraphsToTableOfContentItem1.Id = 163
			Me.addParagraphsToTableOfContentItem1.LargeGlyph = (CType(resources.GetObject("addParagraphsToTableOfContentItem1.LargeGlyph"), System.Drawing.Image))
			Me.addParagraphsToTableOfContentItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem11), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem12), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem13), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem14), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem15), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem16), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem17), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem18), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem19), New DevExpress.XtraBars.LinkPersistInfo(Me.setParagraphHeadingLevelItem20)})
			Me.addParagraphsToTableOfContentItem1.Name = "addParagraphsToTableOfContentItem1"
			' 
			' setParagraphHeadingLevelItem11
			' 
			Me.setParagraphHeadingLevelItem11.Id = 164
			Me.setParagraphHeadingLevelItem11.Name = "setParagraphHeadingLevelItem11"
			Me.setParagraphHeadingLevelItem11.OutlineLevel = 0
			' 
			' setParagraphHeadingLevelItem12
			' 
			Me.setParagraphHeadingLevelItem12.Id = 165
			Me.setParagraphHeadingLevelItem12.Name = "setParagraphHeadingLevelItem12"
			Me.setParagraphHeadingLevelItem12.OutlineLevel = 1
			' 
			' setParagraphHeadingLevelItem13
			' 
			Me.setParagraphHeadingLevelItem13.Id = 166
			Me.setParagraphHeadingLevelItem13.Name = "setParagraphHeadingLevelItem13"
			Me.setParagraphHeadingLevelItem13.OutlineLevel = 2
			' 
			' setParagraphHeadingLevelItem14
			' 
			Me.setParagraphHeadingLevelItem14.Id = 167
			Me.setParagraphHeadingLevelItem14.Name = "setParagraphHeadingLevelItem14"
			Me.setParagraphHeadingLevelItem14.OutlineLevel = 3
			' 
			' setParagraphHeadingLevelItem15
			' 
			Me.setParagraphHeadingLevelItem15.Id = 168
			Me.setParagraphHeadingLevelItem15.Name = "setParagraphHeadingLevelItem15"
			Me.setParagraphHeadingLevelItem15.OutlineLevel = 4
			' 
			' setParagraphHeadingLevelItem16
			' 
			Me.setParagraphHeadingLevelItem16.Id = 169
			Me.setParagraphHeadingLevelItem16.Name = "setParagraphHeadingLevelItem16"
			Me.setParagraphHeadingLevelItem16.OutlineLevel = 5
			' 
			' setParagraphHeadingLevelItem17
			' 
			Me.setParagraphHeadingLevelItem17.Id = 170
			Me.setParagraphHeadingLevelItem17.Name = "setParagraphHeadingLevelItem17"
			Me.setParagraphHeadingLevelItem17.OutlineLevel = 6
			' 
			' setParagraphHeadingLevelItem18
			' 
			Me.setParagraphHeadingLevelItem18.Id = 171
			Me.setParagraphHeadingLevelItem18.Name = "setParagraphHeadingLevelItem18"
			Me.setParagraphHeadingLevelItem18.OutlineLevel = 7
			' 
			' setParagraphHeadingLevelItem19
			' 
			Me.setParagraphHeadingLevelItem19.Id = 172
			Me.setParagraphHeadingLevelItem19.Name = "setParagraphHeadingLevelItem19"
			Me.setParagraphHeadingLevelItem19.OutlineLevel = 8
			' 
			' setParagraphHeadingLevelItem20
			' 
			Me.setParagraphHeadingLevelItem20.Id = 173
			Me.setParagraphHeadingLevelItem20.Name = "setParagraphHeadingLevelItem20"
			Me.setParagraphHeadingLevelItem20.OutlineLevel = 9
			' 
			' insertCaptionPlaceholderItem1
			' 
			Me.insertCaptionPlaceholderItem1.Glyph = (CType(resources.GetObject("insertCaptionPlaceholderItem1.Glyph"), System.Drawing.Image))
			Me.insertCaptionPlaceholderItem1.Id = 174
			Me.insertCaptionPlaceholderItem1.LargeGlyph = (CType(resources.GetObject("insertCaptionPlaceholderItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertCaptionPlaceholderItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.insertFiguresCaptionItems2), New DevExpress.XtraBars.LinkPersistInfo(Me.insertTablesCaptionItems2), New DevExpress.XtraBars.LinkPersistInfo(Me.insertEquationsCaptionItems2)})
			Me.insertCaptionPlaceholderItem1.Name = "insertCaptionPlaceholderItem1"
			' 
			' insertFiguresCaptionItems2
			' 
			Me.insertFiguresCaptionItems2.Glyph = (CType(resources.GetObject("insertFiguresCaptionItems2.Glyph"), System.Drawing.Image))
			Me.insertFiguresCaptionItems2.Id = 175
			Me.insertFiguresCaptionItems2.LargeGlyph = (CType(resources.GetObject("insertFiguresCaptionItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertFiguresCaptionItems2.Name = "insertFiguresCaptionItems2"
			' 
			' insertTablesCaptionItems2
			' 
			Me.insertTablesCaptionItems2.Glyph = (CType(resources.GetObject("insertTablesCaptionItems2.Glyph"), System.Drawing.Image))
			Me.insertTablesCaptionItems2.Id = 176
			Me.insertTablesCaptionItems2.LargeGlyph = (CType(resources.GetObject("insertTablesCaptionItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertTablesCaptionItems2.Name = "insertTablesCaptionItems2"
			' 
			' insertEquationsCaptionItems2
			' 
			Me.insertEquationsCaptionItems2.Glyph = (CType(resources.GetObject("insertEquationsCaptionItems2.Glyph"), System.Drawing.Image))
			Me.insertEquationsCaptionItems2.Id = 177
			Me.insertEquationsCaptionItems2.LargeGlyph = (CType(resources.GetObject("insertEquationsCaptionItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertEquationsCaptionItems2.Name = "insertEquationsCaptionItems2"
			' 
			' insertTableOfFiguresPlaceholderItem1
			' 
			Me.insertTableOfFiguresPlaceholderItem1.Glyph = (CType(resources.GetObject("insertTableOfFiguresPlaceholderItem1.Glyph"), System.Drawing.Image))
			Me.insertTableOfFiguresPlaceholderItem1.Id = 178
			Me.insertTableOfFiguresPlaceholderItem1.LargeGlyph = (CType(resources.GetObject("insertTableOfFiguresPlaceholderItem1.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfFiguresPlaceholderItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfFiguresItems2), New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfTablesItems2), New DevExpress.XtraBars.LinkPersistInfo(Me.insertTableOfEquationsItems2)})
			Me.insertTableOfFiguresPlaceholderItem1.Name = "insertTableOfFiguresPlaceholderItem1"
			' 
			' insertTableOfFiguresItems2
			' 
			Me.insertTableOfFiguresItems2.Glyph = (CType(resources.GetObject("insertTableOfFiguresItems2.Glyph"), System.Drawing.Image))
			Me.insertTableOfFiguresItems2.Id = 179
			Me.insertTableOfFiguresItems2.LargeGlyph = (CType(resources.GetObject("insertTableOfFiguresItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfFiguresItems2.Name = "insertTableOfFiguresItems2"
			' 
			' insertTableOfTablesItems2
			' 
			Me.insertTableOfTablesItems2.Glyph = (CType(resources.GetObject("insertTableOfTablesItems2.Glyph"), System.Drawing.Image))
			Me.insertTableOfTablesItems2.Id = 180
			Me.insertTableOfTablesItems2.LargeGlyph = (CType(resources.GetObject("insertTableOfTablesItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfTablesItems2.Name = "insertTableOfTablesItems2"
			' 
			' insertTableOfEquationsItems2
			' 
			Me.insertTableOfEquationsItems2.Glyph = (CType(resources.GetObject("insertTableOfEquationsItems2.Glyph"), System.Drawing.Image))
			Me.insertTableOfEquationsItems2.Id = 181
			Me.insertTableOfEquationsItems2.LargeGlyph = (CType(resources.GetObject("insertTableOfEquationsItems2.LargeGlyph"), System.Drawing.Image))
			Me.insertTableOfEquationsItems2.Name = "insertTableOfEquationsItems2"
			' 
			' tableToolsRibbonPageCategory1
			' 
			Me.tableToolsRibbonPageCategory1.Name = "tableToolsRibbonPageCategory1"
			Me.tableToolsRibbonPageCategory1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.tableDesignRibbonPage1, Me.tableLayoutRibbonPage1})
			' 
			' tableDesignRibbonPage1
			' 
			Me.tableDesignRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableStylesRibbonPageGroup1, Me.tableDrawBordersRibbonPageGroup1})
			Me.tableDesignRibbonPage1.Name = "tableDesignRibbonPage1"
			' 
			' tableStylesRibbonPageGroup1
			' 
			Me.tableStylesRibbonPageGroup1.ItemLinks.Add(Me.changeTableCellsShadingItem1)
			Me.tableStylesRibbonPageGroup1.ItemLinks.Add(Me.changeTableBordersItem1)
			Me.tableStylesRibbonPageGroup1.Name = "tableStylesRibbonPageGroup1"
			Me.tableStylesRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableDrawBordersRibbonPageGroup1
			' 
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderLineStyleItem1)
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderLineWeightItem1)
			Me.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(Me.changeTableBorderColorItem1)
			Me.tableDrawBordersRibbonPageGroup1.Name = "tableDrawBordersRibbonPageGroup1"
			Me.tableDrawBordersRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableLayoutRibbonPage1
			' 
			Me.tableLayoutRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableTableRibbonPageGroup1, Me.tableRowsAndColumnsRibbonPageGroup1, Me.tableMergeRibbonPageGroup1, Me.tableCellSizeRibbonPageGroup1, Me.tableAlignmentRibbonPageGroup1})
			Me.tableLayoutRibbonPage1.Name = "tableLayoutRibbonPage1"
			' 
			' tableTableRibbonPageGroup1
			' 
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.selectTableElementsItem1)
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.toggleShowTableGridLinesItem1)
			Me.tableTableRibbonPageGroup1.ItemLinks.Add(Me.showTablePropertiesFormItem1)
			Me.tableTableRibbonPageGroup1.Name = "tableTableRibbonPageGroup1"
			Me.tableTableRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableRowsAndColumnsRibbonPageGroup1
			' 
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.deleteTableElementsItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableRowAboveItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableRowBelowItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableColumnToLeftItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.insertTableColumnToRightItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(Me.showInsertTableCellsFormItem1)
			Me.tableRowsAndColumnsRibbonPageGroup1.Name = "tableRowsAndColumnsRibbonPageGroup1"
			Me.tableRowsAndColumnsRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableMergeRibbonPageGroup1
			' 
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.mergeTableCellsItem1)
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.showSplitTableCellsForm1)
			Me.tableMergeRibbonPageGroup1.ItemLinks.Add(Me.splitTableItem1)
			Me.tableMergeRibbonPageGroup1.Name = "tableMergeRibbonPageGroup1"
			Me.tableMergeRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableCellSizeRibbonPageGroup1
			' 
			Me.tableCellSizeRibbonPageGroup1.ItemLinks.Add(Me.toggleTableAutoFitItem1)
			Me.tableCellSizeRibbonPageGroup1.Name = "tableCellSizeRibbonPageGroup1"
			Me.tableCellSizeRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tableAlignmentRibbonPageGroup1
			' 
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopLeftAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopCenterAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsTopRightAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleLeftAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleCenterAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsMiddleRightAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomLeftAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomCenterAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.ItemLinks.Add(Me.toggleTableCellsBottomRightAlignmentItem1)
			Me.tableAlignmentRibbonPageGroup1.Name = "tableAlignmentRibbonPageGroup1"
			Me.tableAlignmentRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' homeRibbonPage1
			' 
			Me.homeRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.clipboardRibbonPageGroup1, Me.editingRibbonPageGroup1, Me.stylesRibbonPageGroup1})
			Me.homeRibbonPage1.Name = "homeRibbonPage1"
			' 
			' clipboardRibbonPageGroup1
			' 
			Me.clipboardRibbonPageGroup1.AllowMinimize = False
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.cutItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.copyItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteSpecialItem1)
			Me.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1"
			Me.clipboardRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' editingRibbonPageGroup1
			' 
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.showAllFieldCodesItem1)
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.showAllFieldResultsItem1)
			Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
			Me.editingRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' stylesRibbonPageGroup1
			' 
			Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.changeStyleItem1)
			Me.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1"
			Me.stylesRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' insertRibbonPage1
			' 
			Me.insertRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.pagesRibbonPageGroup1, Me.tablesRibbonPageGroup1, Me.illustrationsRibbonPageGroup1, Me.linksRibbonPageGroup1, Me.headerFooterRibbonPageGroup1, Me.symbolsRibbonPageGroup1})
			Me.insertRibbonPage1.Name = "insertRibbonPage1"
			' 
			' pagesRibbonPageGroup1
			' 
			Me.pagesRibbonPageGroup1.ItemLinks.Add(Me.insertPageBreakItem1)
			Me.pagesRibbonPageGroup1.Name = "pagesRibbonPageGroup1"
			Me.pagesRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' tablesRibbonPageGroup1
			' 
			Me.tablesRibbonPageGroup1.ItemLinks.Add(Me.insertTableItem1)
			Me.tablesRibbonPageGroup1.Name = "tablesRibbonPageGroup1"
			Me.tablesRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' illustrationsRibbonPageGroup1
			' 
			Me.illustrationsRibbonPageGroup1.ItemLinks.Add(Me.insertPictureItem1)
			Me.illustrationsRibbonPageGroup1.Name = "illustrationsRibbonPageGroup1"
			Me.illustrationsRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' linksRibbonPageGroup1
			' 
			Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertBookmarkItem1)
			Me.linksRibbonPageGroup1.ItemLinks.Add(Me.insertHyperlinkItem1)
			Me.linksRibbonPageGroup1.Name = "linksRibbonPageGroup1"
			Me.linksRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' headerFooterRibbonPageGroup1
			' 
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageHeaderItem1)
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.editPageFooterItem1)
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageNumberItem1)
			Me.headerFooterRibbonPageGroup1.ItemLinks.Add(Me.insertPageCountItem1)
			Me.headerFooterRibbonPageGroup1.Name = "headerFooterRibbonPageGroup1"
			Me.headerFooterRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' symbolsRibbonPageGroup1
			' 
			Me.symbolsRibbonPageGroup1.ItemLinks.Add(Me.insertSymbolItem1)
			Me.symbolsRibbonPageGroup1.Name = "symbolsRibbonPageGroup1"
			Me.symbolsRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' referencesRibbonPage1
			' 
			Me.referencesRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.tableOfContentsRibbonPageGroup1, Me.captionsRibbonPageGroup1})
			Me.referencesRibbonPage1.Name = "referencesRibbonPage1"
			' 
			' tableOfContentsRibbonPageGroup1
			' 
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.insertTableOfContentsItem1)
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.updateTableOfContentsItem1)
			Me.tableOfContentsRibbonPageGroup1.ItemLinks.Add(Me.addParagraphsToTableOfContentItem1)
			Me.tableOfContentsRibbonPageGroup1.Name = "tableOfContentsRibbonPageGroup1"
			Me.tableOfContentsRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' captionsRibbonPageGroup1
			' 
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.insertCaptionPlaceholderItem1)
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.insertTableOfFiguresPlaceholderItem1)
			Me.captionsRibbonPageGroup1.ItemLinks.Add(Me.updateTableOfContentsItem1)
			Me.captionsRibbonPageGroup1.Name = "captionsRibbonPageGroup1"
			Me.captionsRibbonPageGroup1.RichEditControl = Me.richEdit
			' 
			' richEditBarController
			' 
			Me.richEditBarController.BarItems.Add(Me.fileNewItem1)
			Me.richEditBarController.BarItems.Add(Me.fileOpenItem1)
			Me.richEditBarController.BarItems.Add(Me.fileSaveItem1)
			Me.richEditBarController.BarItems.Add(Me.fileSaveAsItem1)
			Me.richEditBarController.BarItems.Add(Me.quickPrintItem1)
			Me.richEditBarController.BarItems.Add(Me.printItem1)
			Me.richEditBarController.BarItems.Add(Me.printPreviewItem1)
			Me.richEditBarController.BarItems.Add(Me.undoItem1)
			Me.richEditBarController.BarItems.Add(Me.redoItem1)
			Me.richEditBarController.BarItems.Add(Me.cutItem1)
			Me.richEditBarController.BarItems.Add(Me.copyItem1)
			Me.richEditBarController.BarItems.Add(Me.pasteItem1)
			Me.richEditBarController.BarItems.Add(Me.pasteSpecialItem1)
			Me.richEditBarController.BarItems.Add(Me.changeFontNameItem)
			Me.richEditBarController.BarItems.Add(Me.changeFontSizeItem)
			Me.richEditBarController.BarItems.Add(Me.changeFontColorItem1)
			Me.richEditBarController.BarItems.Add(Me.changeFontBackColorItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontBoldItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontItalicItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontUnderlineItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontDoubleUnderlineItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontStrikeoutItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontDoubleStrikeoutItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontSuperscriptItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleFontSubscriptItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTextCaseItem1)
			Me.richEditBarController.BarItems.Add(Me.makeTextUpperCaseItem1)
			Me.richEditBarController.BarItems.Add(Me.makeTextLowerCaseItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTextCaseItem1)
			Me.richEditBarController.BarItems.Add(Me.fontSizeIncreaseItem1)
			Me.richEditBarController.BarItems.Add(Me.fontSizeDecreaseItem1)
			Me.richEditBarController.BarItems.Add(Me.clearFormattingItem1)
			Me.richEditBarController.BarItems.Add(Me.showFontFormItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleParagraphAlignmentLeftItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleParagraphAlignmentCenterItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleParagraphAlignmentRightItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleParagraphAlignmentJustifyItem1)
			Me.richEditBarController.BarItems.Add(Me.changeParagraphLineSpacingItem1)
			Me.richEditBarController.BarItems.Add(Me.setSingleParagraphSpacingItem1)
			Me.richEditBarController.BarItems.Add(Me.setSesquialteralParagraphSpacingItem1)
			Me.richEditBarController.BarItems.Add(Me.setDoubleParagraphSpacingItem1)
			Me.richEditBarController.BarItems.Add(Me.showLineSpacingFormItem1)
			Me.richEditBarController.BarItems.Add(Me.addSpacingBeforeParagraphItem1)
			Me.richEditBarController.BarItems.Add(Me.removeSpacingBeforeParagraphItem1)
			Me.richEditBarController.BarItems.Add(Me.addSpacingAfterParagraphItem1)
			Me.richEditBarController.BarItems.Add(Me.removeSpacingAfterParagraphItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleBulletedListItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleNumberingListItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleMultiLevelListItem1)
			Me.richEditBarController.BarItems.Add(Me.decreaseIndentItem1)
			Me.richEditBarController.BarItems.Add(Me.increaseIndentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleShowWhitespaceItem1)
			Me.richEditBarController.BarItems.Add(Me.showParagraphFormItem1)
			Me.richEditBarController.BarItems.Add(Me.changeStyleItem1)
			Me.richEditBarController.BarItems.Add(Me.findItem1)
			Me.richEditBarController.BarItems.Add(Me.replaceItem1)
			Me.richEditBarController.BarItems.Add(Me.insertPageBreakItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableItem1)
			Me.richEditBarController.BarItems.Add(Me.insertPictureItem1)
			Me.richEditBarController.BarItems.Add(Me.insertBookmarkItem1)
			Me.richEditBarController.BarItems.Add(Me.insertHyperlinkItem1)
			Me.richEditBarController.BarItems.Add(Me.editPageHeaderItem1)
			Me.richEditBarController.BarItems.Add(Me.editPageFooterItem1)
			Me.richEditBarController.BarItems.Add(Me.insertPageNumberItem1)
			Me.richEditBarController.BarItems.Add(Me.insertPageCountItem1)
			Me.richEditBarController.BarItems.Add(Me.insertSymbolItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTableCellsShadingItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTableBordersItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsBottomBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsTopBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsLeftBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsRightBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.resetTableCellsAllBordersItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsAllBordersItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsOutsideBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsInsideBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsInsideHorizontalBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsInsideVerticalBorderItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleShowTableGridLinesItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTableBorderLineStyleItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTableBorderLineWeightItem1)
			Me.richEditBarController.BarItems.Add(Me.changeTableBorderColorItem1)
			Me.richEditBarController.BarItems.Add(Me.selectTableElementsItem1)
			Me.richEditBarController.BarItems.Add(Me.selectTableCellItem1)
			Me.richEditBarController.BarItems.Add(Me.selectTableColumnItem1)
			Me.richEditBarController.BarItems.Add(Me.selectTableRowItem1)
			Me.richEditBarController.BarItems.Add(Me.selectTableItem1)
			Me.richEditBarController.BarItems.Add(Me.showTablePropertiesFormItem1)
			Me.richEditBarController.BarItems.Add(Me.deleteTableElementsItem1)
			Me.richEditBarController.BarItems.Add(Me.showDeleteTableCellsFormItem1)
			Me.richEditBarController.BarItems.Add(Me.deleteTableColumnsItem1)
			Me.richEditBarController.BarItems.Add(Me.deleteTableRowsItem1)
			Me.richEditBarController.BarItems.Add(Me.deleteTableItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableRowAboveItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableRowBelowItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableColumnToLeftItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableColumnToRightItem1)
			Me.richEditBarController.BarItems.Add(Me.showInsertTableCellsFormItem1)
			Me.richEditBarController.BarItems.Add(Me.mergeTableCellsItem1)
			Me.richEditBarController.BarItems.Add(Me.showSplitTableCellsForm1)
			Me.richEditBarController.BarItems.Add(Me.splitTableItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableAutoFitItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableAutoFitContentsItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableAutoFitWindowItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableFixedColumnWidthItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsTopLeftAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsTopCenterAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsTopRightAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsMiddleLeftAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsMiddleCenterAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsMiddleRightAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsBottomLeftAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsBottomCenterAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.toggleTableCellsBottomRightAlignmentItem1)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem1)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem2)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem3)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem4)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem5)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem6)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem7)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem8)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem9)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem10)
			Me.richEditBarController.BarItems.Add(Me.insertFiguresCaptionItems1)
			Me.richEditBarController.BarItems.Add(Me.insertTablesCaptionItems1)
			Me.richEditBarController.BarItems.Add(Me.insertEquationsCaptionItems1)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfFiguresItems1)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfTablesItems1)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfEquationsItems1)
			Me.richEditBarController.BarItems.Add(Me.showAllFieldCodesItem1)
			Me.richEditBarController.BarItems.Add(Me.showAllFieldResultsItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfContentsItem1)
			Me.richEditBarController.BarItems.Add(Me.updateTableOfContentsItem1)
			Me.richEditBarController.BarItems.Add(Me.addParagraphsToTableOfContentItem1)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem11)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem12)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem13)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem14)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem15)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem16)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem17)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem18)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem19)
			Me.richEditBarController.BarItems.Add(Me.setParagraphHeadingLevelItem20)
			Me.richEditBarController.BarItems.Add(Me.insertCaptionPlaceholderItem1)
			Me.richEditBarController.BarItems.Add(Me.insertFiguresCaptionItems2)
			Me.richEditBarController.BarItems.Add(Me.insertTablesCaptionItems2)
			Me.richEditBarController.BarItems.Add(Me.insertEquationsCaptionItems2)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfFiguresPlaceholderItem1)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfFiguresItems2)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfTablesItems2)
			Me.richEditBarController.BarItems.Add(Me.insertTableOfEquationsItems2)
			Me.richEditBarController.RichEditControl = Me.richEdit
			' 
			' Editor
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(895, 552)
			Me.Controls.Add(Me.richEdit)
			Me.Controls.Add(Me.ribbonControl)
			Me.Icon = (CType(resources.GetObject("$this.Icon"), System.Drawing.Icon))
			Me.Name = "Editor"
			Me.Ribbon = Me.ribbonControl
			Me.Text = "BizPad"
			CType(Me.ribbonControl, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.applicationMenu, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemBorderLineStyle1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemBorderLineWeight1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.richEditBarController, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private ribbonControl As DevExpress.XtraBars.Ribbon.RibbonControl
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
		Private changeFontNameItem As DevExpress.XtraRichEdit.UI.ChangeFontNameItem
		Private repositoryItemFontEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemFontEdit
		Private changeFontSizeItem As DevExpress.XtraRichEdit.UI.ChangeFontSizeItem
		Private repositoryItemRichEditFontSizeEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit
		Private changeFontColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontColorItem
		Private changeFontBackColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem
		Private toggleFontBoldItem1 As DevExpress.XtraRichEdit.UI.ToggleFontBoldItem
		Private toggleFontItalicItem1 As DevExpress.XtraRichEdit.UI.ToggleFontItalicItem
		Private toggleFontUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem
		Private toggleFontDoubleUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem
		Private toggleFontStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem
		Private toggleFontDoubleStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem
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
		Private changeTableCellsShadingItem1 As DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem
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
		Private changeTableBorderLineStyleItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem
		Private repositoryItemBorderLineStyle1 As DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle
		Private changeTableBorderLineWeightItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem
		Private repositoryItemBorderLineWeight1 As DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight
		Private changeTableBorderColorItem1 As DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem
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
		Private showInsertTableCellsFormItem1 As DevExpress.XtraRichEdit.UI.ShowInsertTableCellsFormItem
		Private mergeTableCellsItem1 As DevExpress.XtraRichEdit.UI.MergeTableCellsItem
		Private showSplitTableCellsForm1 As DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm
		Private splitTableItem1 As DevExpress.XtraRichEdit.UI.SplitTableItem
		Private toggleTableAutoFitItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem
		Private toggleTableAutoFitContentsItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem
		Private toggleTableAutoFitWindowItem1 As DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem
		Private toggleTableFixedColumnWidthItem1 As DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem
		Private toggleTableCellsTopLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem
		Private toggleTableCellsTopCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem
		Private toggleTableCellsTopRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem
		Private toggleTableCellsMiddleLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem
		Private toggleTableCellsMiddleCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem
		Private toggleTableCellsMiddleRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem
		Private toggleTableCellsBottomLeftAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem
		Private toggleTableCellsBottomCenterAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem
		Private toggleTableCellsBottomRightAlignmentItem1 As DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem
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
		Private insertFiguresCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems
		Private insertTablesCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems
		Private insertEquationsCaptionItems1 As DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems
		Private insertTableOfFiguresItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems
		Private insertTableOfTablesItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems
		Private insertTableOfEquationsItems1 As DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems
		Private homeRibbonPage1 As DevExpress.XtraRichEdit.UI.HomeRibbonPage
		Private clipboardRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup
		Private editingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup
		Private richEditBarController As DevExpress.XtraRichEdit.UI.RichEditBarController
		Private showAllFieldCodesItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem
		Private showAllFieldResultsItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem
		Private richEdit As Extensions.RichEditEx
		Private applicationMenu As DevExpress.XtraBars.Ribbon.ApplicationMenu
		Private barStaticItem1 As DevExpress.XtraBars.BarStaticItem
		Private barStaticItem2 As DevExpress.XtraBars.BarStaticItem
		Private barButtonItem1 As DevExpress.XtraBars.BarButtonItem
		Private barCheckItem1 As DevExpress.XtraBars.BarCheckItem
		Private barButtonGroup3 As DevExpress.XtraBars.BarButtonGroup
		Private barButtonGroup4 As DevExpress.XtraBars.BarButtonGroup
		Private tableToolsRibbonPageCategory1 As DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory
		Private tableDesignRibbonPage1 As DevExpress.XtraRichEdit.UI.TableDesignRibbonPage
		Private tableStylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup
		Private tableDrawBordersRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup
		Private tableLayoutRibbonPage1 As DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage
		Private tableTableRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup
		Private tableRowsAndColumnsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup
		Private tableMergeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup
		Private tableCellSizeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup
		Private tableAlignmentRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup
		Private insertRibbonPage1 As DevExpress.XtraRichEdit.UI.InsertRibbonPage
		Private pagesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup
		Private tablesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup
		Private illustrationsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup
		Private linksRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup
		Private headerFooterRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup
		Private symbolsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup
		Private insertTableOfContentsItem1 As DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem
		Private updateTableOfContentsItem1 As DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem
		Private addParagraphsToTableOfContentItem1 As DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem
		Private setParagraphHeadingLevelItem11 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem12 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem13 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem14 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem15 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem16 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem17 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem18 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem19 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private setParagraphHeadingLevelItem20 As DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem
		Private insertCaptionPlaceholderItem1 As DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem
		Private insertFiguresCaptionItems2 As DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems
		Private insertTablesCaptionItems2 As DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems
		Private insertEquationsCaptionItems2 As DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems
		Private insertTableOfFiguresPlaceholderItem1 As DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem
		Private insertTableOfFiguresItems2 As DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems
		Private insertTableOfTablesItems2 As DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems
		Private insertTableOfEquationsItems2 As DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems
		Private referencesRibbonPage1 As DevExpress.XtraRichEdit.UI.ReferencesRibbonPage
		Private tableOfContentsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup
		Private captionsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup
		Private stylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup
	End Class
End Namespace

