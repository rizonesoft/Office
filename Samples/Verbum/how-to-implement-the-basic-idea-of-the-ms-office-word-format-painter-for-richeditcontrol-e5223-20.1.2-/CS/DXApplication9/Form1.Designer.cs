// Developer Express Code Central Example:
// How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
// 
// This example demonstrates how to copy the characters and paragraphs properties
// and apply formatting to the selected text. Try the Format Painter button on the
// ribbon Home tab.
// 
// To obtain the selected text range, the
// RichEditDocument.Document.Selection property is used. The characters and
// paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
// handler. Then, they are stored in the CharacterPropertiesObject and
// ParagraphPropertiesObject object containers.
// 
// In order to change the current
// RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
// the custom MouseCursorCalculator class Calculate method for clarification.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E5223

namespace DXApplication9
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            DevExpress.XtraBars.Ribbon.GalleryItemGroup galleryItemGroup1 = new DevExpress.XtraBars.Ribbon.GalleryItemGroup();
            DevExpress.XtraBars.Ribbon.GalleryItemGroup galleryItemGroup2 = new DevExpress.XtraBars.Ribbon.GalleryItemGroup();
            DevExpress.XtraRichEdit.Model.BorderInfo borderInfo1 = new DevExpress.XtraRichEdit.Model.BorderInfo();
            DevExpress.XtraBars.Ribbon.ReduceOperation reduceOperation1 = new DevExpress.XtraBars.Ribbon.ReduceOperation();
            this.stylesRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup();
            this.galleryChangeStyleItem1 = new DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem();
            this.ribbonControl = new DevExpress.XtraBars.Ribbon.RibbonControl();
            this.appMenu = new DevExpress.XtraBars.Ribbon.ApplicationMenu(this.components);
            this.popupControlContainer2 = new DevExpress.XtraBars.PopupControlContainer(this.components);
            this.buttonEdit = new DevExpress.XtraEditors.ButtonEdit();
            this.iExit = new DevExpress.XtraBars.BarButtonItem();
            this.popupControlContainer1 = new DevExpress.XtraBars.PopupControlContainer(this.components);
            this.someLabelControl2 = new DevExpress.XtraEditors.LabelControl();
            this.someLabelControl1 = new DevExpress.XtraEditors.LabelControl();
            this.ribbonImageCollection = new DevExpress.Utils.ImageCollection(this.components);
            this.iHelp = new DevExpress.XtraBars.BarButtonItem();
            this.iAbout = new DevExpress.XtraBars.BarButtonItem();
            this.siStatus = new DevExpress.XtraBars.BarStaticItem();
            this.siInfo = new DevExpress.XtraBars.BarStaticItem();
            this.rgbiSkins = new DevExpress.XtraBars.RibbonGalleryBarItem();
            this.changeFloatingObjectFillColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectFillColorItem();
            this.changeFloatingObjectOutlineColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineColorItem();
            this.changeFloatingObjectOutlineWeightItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineWeightItem();
            this.repositoryItemFloatingObjectOutlineWeight1 = new DevExpress.XtraRichEdit.Forms.Design.RepositoryItemFloatingObjectOutlineWeight();
            this.richEditControl = new DXApplication9.MyRichEditControl();
            this.spellChecker = new DevExpress.XtraSpellChecker.SpellChecker(this.components);
            this.changeFloatingObjectTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectTextWrapTypeItem();
            this.setFloatingObjectSquareTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectSquareTextWrapTypeItem();
            this.setFloatingObjectTightTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectTightTextWrapTypeItem();
            this.setFloatingObjectThroughTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectThroughTextWrapTypeItem();
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectTopAndBottomTextWrapTypeItem();
            this.setFloatingObjectBehindTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectBehindTextWrapTypeItem();
            this.setFloatingObjectInFrontOfTextWrapTypeItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectInFrontOfTextWrapTypeItem();
            this.changeFloatingObjectAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectAlignmentItem();
            this.setFloatingObjectTopLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectTopLeftAlignmentItem();
            this.setFloatingObjectTopCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectTopCenterAlignmentItem();
            this.setFloatingObjectTopRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectTopRightAlignmentItem();
            this.setFloatingObjectMiddleLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleLeftAlignmentItem();
            this.setFloatingObjectMiddleCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleCenterAlignmentItem();
            this.setFloatingObjectMiddleRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleRightAlignmentItem();
            this.setFloatingObjectBottomLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomLeftAlignmentItem();
            this.setFloatingObjectBottomCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomCenterAlignmentItem();
            this.setFloatingObjectBottomRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomRightAlignmentItem();
            this.floatingObjectBringForwardSubItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardSubItem();
            this.floatingObjectBringForwardItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardItem();
            this.floatingObjectBringToFrontItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectBringToFrontItem();
            this.floatingObjectBringInFrontOfTextItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectBringInFrontOfTextItem();
            this.floatingObjectSendBackwardSubItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardSubItem();
            this.floatingObjectSendBackwardItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardItem();
            this.floatingObjectSendToBackItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectSendToBackItem();
            this.floatingObjectSendBehindTextItem1 = new DevExpress.XtraRichEdit.UI.FloatingObjectSendBehindTextItem();
            this.toggleFirstRowItem1 = new DevExpress.XtraRichEdit.UI.ToggleFirstRowItem();
            this.toggleLastRowItem1 = new DevExpress.XtraRichEdit.UI.ToggleLastRowItem();
            this.toggleBandedRowsItem1 = new DevExpress.XtraRichEdit.UI.ToggleBandedRowsItem();
            this.toggleFirstColumnItem1 = new DevExpress.XtraRichEdit.UI.ToggleFirstColumnItem();
            this.toggleLastColumnItem1 = new DevExpress.XtraRichEdit.UI.ToggleLastColumnItem();
            this.toggleBandedColumnItem1 = new DevExpress.XtraRichEdit.UI.ToggleBandedColumnsItem();
            this.galleryChangeTableStyleItem1 = new DevExpress.XtraRichEdit.UI.GalleryChangeTableStyleItem();
            this.changeTableBorderLineStyleItem1 = new DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem();
            this.repositoryItemBorderLineStyle1 = new DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle();
            this.changeTableBorderLineWeightItem1 = new DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem();
            this.repositoryItemBorderLineWeight1 = new DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight();
            this.changeTableBorderColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem();
            this.changeTableBordersItem1 = new DevExpress.XtraRichEdit.UI.ChangeTableBordersItem();
            this.toggleTableCellsBottomBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomBorderItem();
            this.toggleTableCellsTopBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsTopBorderItem();
            this.toggleTableCellsLeftBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsLeftBorderItem();
            this.toggleTableCellsRightBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsRightBorderItem();
            this.resetTableCellsAllBordersItem1 = new DevExpress.XtraRichEdit.UI.ResetTableCellsAllBordersItem();
            this.toggleTableCellsAllBordersItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsAllBordersItem();
            this.toggleTableCellsOutsideBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsOutsideBorderItem();
            this.toggleTableCellsInsideBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideBorderItem();
            this.toggleTableCellsInsideHorizontalBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideHorizontalBorderItem();
            this.toggleTableCellsInsideVerticalBorderItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideVerticalBorderItem();
            this.toggleShowTableGridLinesItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowTableGridLinesItem();
            this.changeTableCellsShadingItem1 = new DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem();
            this.selectTableElementsItem1 = new DevExpress.XtraRichEdit.UI.SelectTableElementsItem();
            this.selectTableCellItem1 = new DevExpress.XtraRichEdit.UI.SelectTableCellItem();
            this.selectTableColumnItem1 = new DevExpress.XtraRichEdit.UI.SelectTableColumnItem();
            this.selectTableRowItem1 = new DevExpress.XtraRichEdit.UI.SelectTableRowItem();
            this.selectTableItem1 = new DevExpress.XtraRichEdit.UI.SelectTableItem();
            this.showTablePropertiesFormItem1 = new DevExpress.XtraRichEdit.UI.ShowTablePropertiesFormItem();
            this.deleteTableElementsItem1 = new DevExpress.XtraRichEdit.UI.DeleteTableElementsItem();
            this.showDeleteTableCellsFormItem1 = new DevExpress.XtraRichEdit.UI.ShowDeleteTableCellsFormItem();
            this.deleteTableColumnsItem1 = new DevExpress.XtraRichEdit.UI.DeleteTableColumnsItem();
            this.deleteTableRowsItem1 = new DevExpress.XtraRichEdit.UI.DeleteTableRowsItem();
            this.deleteTableItem1 = new DevExpress.XtraRichEdit.UI.DeleteTableItem();
            this.insertTableRowAboveItem1 = new DevExpress.XtraRichEdit.UI.InsertTableRowAboveItem();
            this.insertTableRowBelowItem1 = new DevExpress.XtraRichEdit.UI.InsertTableRowBelowItem();
            this.insertTableColumnToLeftItem1 = new DevExpress.XtraRichEdit.UI.InsertTableColumnToLeftItem();
            this.insertTableColumnToRightItem1 = new DevExpress.XtraRichEdit.UI.InsertTableColumnToRightItem();
            this.mergeTableCellsItem1 = new DevExpress.XtraRichEdit.UI.MergeTableCellsItem();
            this.showSplitTableCellsForm1 = new DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm();
            this.splitTableItem1 = new DevExpress.XtraRichEdit.UI.SplitTableItem();
            this.toggleTableAutoFitItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem();
            this.toggleTableAutoFitContentsItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem();
            this.toggleTableAutoFitWindowItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem();
            this.toggleTableFixedColumnWidthItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem();
            this.toggleTableCellsTopLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem();
            this.toggleTableCellsMiddleLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem();
            this.toggleTableCellsBottomLeftAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem();
            this.toggleTableCellsTopCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem();
            this.toggleTableCellsMiddleCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem();
            this.toggleTableCellsBottomCenterAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem();
            this.toggleTableCellsTopRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem();
            this.toggleTableCellsMiddleRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem();
            this.toggleTableCellsBottomRightAlignmentItem1 = new DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem();
            this.showTableOptionsFormItem1 = new DevExpress.XtraRichEdit.UI.ShowTableOptionsFormItem();
            this.goToPageHeaderItem1 = new DevExpress.XtraRichEdit.UI.GoToPageHeaderItem();
            this.goToPageFooterItem1 = new DevExpress.XtraRichEdit.UI.GoToPageFooterItem();
            this.goToNextHeaderFooterItem1 = new DevExpress.XtraRichEdit.UI.GoToNextHeaderFooterItem();
            this.goToPreviousHeaderFooterItem1 = new DevExpress.XtraRichEdit.UI.GoToPreviousHeaderFooterItem();
            this.toggleLinkToPreviousItem1 = new DevExpress.XtraRichEdit.UI.ToggleLinkToPreviousItem();
            this.toggleDifferentFirstPageItem1 = new DevExpress.XtraRichEdit.UI.ToggleDifferentFirstPageItem();
            this.toggleDifferentOddAndEvenPagesItem1 = new DevExpress.XtraRichEdit.UI.ToggleDifferentOddAndEvenPagesItem();
            this.closePageHeaderFooterItem1 = new DevExpress.XtraRichEdit.UI.ClosePageHeaderFooterItem();
            this.switchToSimpleViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem();
            this.switchToDraftViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem();
            this.switchToPrintLayoutViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem();
            this.toggleShowHorizontalRulerItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem();
            this.toggleShowVerticalRulerItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem();
            this.zoomOutItem1 = new DevExpress.XtraRichEdit.UI.ZoomOutItem();
            this.zoomInItem1 = new DevExpress.XtraRichEdit.UI.ZoomInItem();
            this.checkSpellingItem1 = new DevExpress.XtraRichEdit.UI.CheckSpellingItem();
            this.changeLanguageItem1 = new DevExpress.XtraRichEdit.UI.ChangeLanguageItem();
            this.protectDocumentItem1 = new DevExpress.XtraRichEdit.UI.ProtectDocumentItem();
            this.changeRangeEditingPermissionsItem1 = new DevExpress.XtraRichEdit.UI.ChangeRangeEditingPermissionsItem();
            this.unprotectDocumentItem1 = new DevExpress.XtraRichEdit.UI.UnprotectDocumentItem();
            this.insertMergeFieldItem1 = new DevExpress.XtraRichEdit.UI.InsertMergeFieldItem();
            this.showAllFieldCodesItem1 = new DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem();
            this.showAllFieldResultsItem1 = new DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem();
            this.toggleViewMergedDataItem1 = new DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem();
            this.insertTableOfContentsItem1 = new DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem();
            this.updateTableOfContentsItem1 = new DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem();
            this.addParagraphsToTableOfContentItem1 = new DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem();
            this.setParagraphHeadingLevelItem1 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem2 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem3 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem4 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem5 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem6 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem7 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem8 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem9 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.setParagraphHeadingLevelItem10 = new DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem();
            this.insertCaptionPlaceholderItem1 = new DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem();
            this.insertFiguresCaptionItems1 = new DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems();
            this.insertTablesCaptionItems1 = new DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems();
            this.insertEquationsCaptionItems1 = new DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems();
            this.insertTableOfFiguresPlaceholderItem1 = new DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem();
            this.insertTableOfFiguresItems1 = new DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems();
            this.insertTableOfTablesItems1 = new DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems();
            this.insertTableOfEquationsItems1 = new DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems();
            this.updateTableOfFiguresItem1 = new DevExpress.XtraRichEdit.UI.UpdateTableOfFiguresItem();
            this.changeSectionPageMarginsItem1 = new DevExpress.XtraRichEdit.UI.ChangeSectionPageMarginsItem();
            this.setNormalSectionPageMarginsItem1 = new DevExpress.XtraRichEdit.UI.SetNormalSectionPageMarginsItem();
            this.setNarrowSectionPageMarginsItem1 = new DevExpress.XtraRichEdit.UI.SetNarrowSectionPageMarginsItem();
            this.setModerateSectionPageMarginsItem1 = new DevExpress.XtraRichEdit.UI.SetModerateSectionPageMarginsItem();
            this.setWideSectionPageMarginsItem1 = new DevExpress.XtraRichEdit.UI.SetWideSectionPageMarginsItem();
            this.showPageMarginsSetupFormItem1 = new DevExpress.XtraRichEdit.UI.ShowPageMarginsSetupFormItem();
            this.changeSectionPageOrientationItem1 = new DevExpress.XtraRichEdit.UI.ChangeSectionPageOrientationItem();
            this.setPortraitPageOrientationItem1 = new DevExpress.XtraRichEdit.UI.SetPortraitPageOrientationItem();
            this.setLandscapePageOrientationItem1 = new DevExpress.XtraRichEdit.UI.SetLandscapePageOrientationItem();
            this.changeSectionPaperKindItem1 = new DevExpress.XtraRichEdit.UI.ChangeSectionPaperKindItem();
            this.changeSectionColumnsItem1 = new DevExpress.XtraRichEdit.UI.ChangeSectionColumnsItem();
            this.setSectionOneColumnItem1 = new DevExpress.XtraRichEdit.UI.SetSectionOneColumnItem();
            this.setSectionTwoColumnsItem1 = new DevExpress.XtraRichEdit.UI.SetSectionTwoColumnsItem();
            this.setSectionThreeColumnsItem1 = new DevExpress.XtraRichEdit.UI.SetSectionThreeColumnsItem();
            this.showColumnsSetupFormItem1 = new DevExpress.XtraRichEdit.UI.ShowColumnsSetupFormItem();
            this.insertBreakItem1 = new DevExpress.XtraRichEdit.UI.InsertBreakItem();
            this.insertPageBreakItem1 = new DevExpress.XtraRichEdit.UI.InsertPageBreakItem();
            this.insertColumnBreakItem1 = new DevExpress.XtraRichEdit.UI.InsertColumnBreakItem();
            this.insertSectionBreakNextPageItem1 = new DevExpress.XtraRichEdit.UI.InsertSectionBreakNextPageItem();
            this.insertSectionBreakEvenPageItem1 = new DevExpress.XtraRichEdit.UI.InsertSectionBreakEvenPageItem();
            this.insertSectionBreakOddPageItem1 = new DevExpress.XtraRichEdit.UI.InsertSectionBreakOddPageItem();
            this.changeSectionLineNumberingItem1 = new DevExpress.XtraRichEdit.UI.ChangeSectionLineNumberingItem();
            this.setSectionLineNumberingNoneItem1 = new DevExpress.XtraRichEdit.UI.SetSectionLineNumberingNoneItem();
            this.setSectionLineNumberingContinuousItem1 = new DevExpress.XtraRichEdit.UI.SetSectionLineNumberingContinuousItem();
            this.setSectionLineNumberingRestartNewPageItem1 = new DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewPageItem();
            this.setSectionLineNumberingRestartNewSectionItem1 = new DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewSectionItem();
            this.toggleParagraphSuppressLineNumbersItem1 = new DevExpress.XtraRichEdit.UI.ToggleParagraphSuppressLineNumbersItem();
            this.showLineNumberingFormItem1 = new DevExpress.XtraRichEdit.UI.ShowLineNumberingFormItem();
            this.changePageColorItem1 = new DevExpress.XtraRichEdit.UI.ChangePageColorItem();
            this.insertTableItem1 = new DevExpress.XtraRichEdit.UI.InsertTableItem();
            this.insertPictureItem1 = new DevExpress.XtraRichEdit.UI.InsertPictureItem();
            this.insertFloatingPictureItem1 = new DevExpress.XtraRichEdit.UI.InsertFloatingPictureItem();
            this.insertBookmarkItem1 = new DevExpress.XtraRichEdit.UI.InsertBookmarkItem();
            this.insertHyperlinkItem1 = new DevExpress.XtraRichEdit.UI.InsertHyperlinkItem();
            this.editPageHeaderItem1 = new DevExpress.XtraRichEdit.UI.EditPageHeaderItem();
            this.editPageFooterItem1 = new DevExpress.XtraRichEdit.UI.EditPageFooterItem();
            this.insertPageNumberItem1 = new DevExpress.XtraRichEdit.UI.InsertPageNumberItem();
            this.insertPageCountItem1 = new DevExpress.XtraRichEdit.UI.InsertPageCountItem();
            this.insertTextBoxItem1 = new DevExpress.XtraRichEdit.UI.InsertTextBoxItem();
            this.insertSymbolItem1 = new DevExpress.XtraRichEdit.UI.InsertSymbolItem();
            this.pasteItem1 = new DevExpress.XtraRichEdit.UI.PasteItem();
            this.cutItem1 = new DevExpress.XtraRichEdit.UI.CutItem();
            this.copyItem1 = new DevExpress.XtraRichEdit.UI.CopyItem();
            this.pasteSpecialItem1 = new DevExpress.XtraRichEdit.UI.PasteSpecialItem();
            this.barButtonGroup1 = new DevExpress.XtraBars.BarButtonGroup();
            this.changeFontNameItem1 = new DevExpress.XtraRichEdit.UI.ChangeFontNameItem();
            this.repositoryItemFontEdit1 = new DevExpress.XtraEditors.Repository.RepositoryItemFontEdit();
            this.changeFontSizeItem1 = new DevExpress.XtraRichEdit.UI.ChangeFontSizeItem();
            this.repositoryItemRichEditFontSizeEdit1 = new DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit();
            this.fontSizeIncreaseItem1 = new DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem();
            this.fontSizeDecreaseItem1 = new DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem();
            this.barButtonGroup2 = new DevExpress.XtraBars.BarButtonGroup();
            this.toggleFontBoldItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontBoldItem();
            this.toggleFontItalicItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontItalicItem();
            this.toggleFontUnderlineItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem();
            this.toggleFontDoubleUnderlineItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem();
            this.toggleFontStrikeoutItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem();
            this.toggleFontDoubleStrikeoutItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem();
            this.toggleFontSuperscriptItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem();
            this.toggleFontSubscriptItem1 = new DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem();
            this.barButtonGroup3 = new DevExpress.XtraBars.BarButtonGroup();
            this.changeFontColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFontColorItem();
            this.changeFontBackColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem();
            this.changeTextCaseItem1 = new DevExpress.XtraRichEdit.UI.ChangeTextCaseItem();
            this.makeTextUpperCaseItem1 = new DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem();
            this.makeTextLowerCaseItem1 = new DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem();
            this.capitalizeEachWordCaseItem1 = new DevExpress.XtraRichEdit.UI.CapitalizeEachWordCaseItem();
            this.toggleTextCaseItem1 = new DevExpress.XtraRichEdit.UI.ToggleTextCaseItem();
            this.clearFormattingItem1 = new DevExpress.XtraRichEdit.UI.ClearFormattingItem();
            this.barButtonGroup4 = new DevExpress.XtraBars.BarButtonGroup();
            this.toggleBulletedListItem1 = new DevExpress.XtraRichEdit.UI.ToggleBulletedListItem();
            this.toggleNumberingListItem1 = new DevExpress.XtraRichEdit.UI.ToggleNumberingListItem();
            this.toggleMultiLevelListItem1 = new DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem();
            this.barButtonGroup5 = new DevExpress.XtraBars.BarButtonGroup();
            this.decreaseIndentItem1 = new DevExpress.XtraRichEdit.UI.DecreaseIndentItem();
            this.increaseIndentItem1 = new DevExpress.XtraRichEdit.UI.IncreaseIndentItem();
            this.toggleShowWhitespaceItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem();
            this.barButtonGroup6 = new DevExpress.XtraBars.BarButtonGroup();
            this.toggleParagraphAlignmentLeftItem1 = new DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem();
            this.toggleParagraphAlignmentCenterItem1 = new DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem();
            this.toggleParagraphAlignmentRightItem1 = new DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem();
            this.toggleParagraphAlignmentJustifyItem1 = new DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem();
            this.barButtonGroup7 = new DevExpress.XtraBars.BarButtonGroup();
            this.changeParagraphLineSpacingItem1 = new DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem();
            this.setSingleParagraphSpacingItem1 = new DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem();
            this.setSesquialteralParagraphSpacingItem1 = new DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem();
            this.setDoubleParagraphSpacingItem1 = new DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem();
            this.showLineSpacingFormItem1 = new DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem();
            this.addSpacingBeforeParagraphItem1 = new DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem();
            this.removeSpacingBeforeParagraphItem1 = new DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem();
            this.addSpacingAfterParagraphItem1 = new DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem();
            this.removeSpacingAfterParagraphItem1 = new DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem();
            this.changeParagraphBackColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeParagraphBackColorItem();
            this.findItem1 = new DevExpress.XtraRichEdit.UI.FindItem();
            this.replaceItem1 = new DevExpress.XtraRichEdit.UI.ReplaceItem();
            this.undoItem1 = new DevExpress.XtraRichEdit.UI.UndoItem();
            this.redoItem1 = new DevExpress.XtraRichEdit.UI.RedoItem();
            this.fileNewItem1 = new DevExpress.XtraRichEdit.UI.FileNewItem();
            this.fileOpenItem1 = new DevExpress.XtraRichEdit.UI.FileOpenItem();
            this.fileSaveItem1 = new DevExpress.XtraRichEdit.UI.FileSaveItem();
            this.fileSaveAsItem1 = new DevExpress.XtraRichEdit.UI.FileSaveAsItem();
            this.quickPrintItem1 = new DevExpress.XtraRichEdit.UI.QuickPrintItem();
            this.printItem1 = new DevExpress.XtraRichEdit.UI.PrintItem();
            this.printPreviewItem1 = new DevExpress.XtraRichEdit.UI.PrintPreviewItem();
            this.barEditItem1 = new DevExpress.XtraBars.BarEditItem();
            this.repositoryItemColorPickEdit1 = new DevExpress.XtraEditors.Repository.RepositoryItemColorPickEdit();
            this.barCheckItem1 = new DevExpress.XtraBars.BarCheckItem();
            this.ribbonImageCollectionLarge = new DevExpress.Utils.ImageCollection(this.components);
            this.floatingPictureToolsRibbonPageCategory1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory();
            this.floatingPictureToolsFormatPage1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage();
            this.floatingPictureToolsShapeStylesPageGroup1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup();
            this.floatingPictureToolsArrangePageGroup1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup();
            this.tableToolsRibbonPageCategory1 = new DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory();
            this.tableLayoutRibbonPage1 = new DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage();
            this.tableTableRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup();
            this.tableRowsAndColumnsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup();
            this.tableMergeRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup();
            this.tableCellSizeRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup();
            this.tableAlignmentRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup();
            this.tableDesignRibbonPage1 = new DevExpress.XtraRichEdit.UI.TableDesignRibbonPage();
            this.tableStyleOptionsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableStyleOptionsRibbonPageGroup();
            this.tableStylesRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup();
            this.tableDrawBordersRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup();
            this.headerFooterToolsRibbonPageCategory1 = new DevExpress.XtraRichEdit.UI.HeaderFooterToolsRibbonPageCategory();
            this.headerFooterToolsDesignRibbonPage1 = new DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignRibbonPage();
            this.headerFooterToolsDesignNavigationRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignNavigationRibbonPageGroup();
            this.headerFooterToolsDesignOptionsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignOptionsRibbonPageGroup();
            this.headerFooterToolsDesignCloseRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignCloseRibbonPageGroup();
            this.fileRibbonPage1 = new DevExpress.XtraRichEdit.UI.FileRibbonPage();
            this.commonRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup();
            this.homeRibbonPage1 = new DevExpress.XtraRichEdit.UI.HomeRibbonPage();
            this.clipboardRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup();
            this.fontRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.FontRibbonPageGroup();
            this.paragraphRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup();
            this.editingRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup();
            this.insertRibbonPage1 = new DevExpress.XtraRichEdit.UI.InsertRibbonPage();
            this.pagesRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup();
            this.tablesRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup();
            this.illustrationsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup();
            this.linksRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup();
            this.headerFooterRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup();
            this.textRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TextRibbonPageGroup();
            this.symbolsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup();
            this.pageLayoutRibbonPage1 = new DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage();
            this.pageSetupRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup();
            this.pageBackgroundRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup();
            this.referencesRibbonPage1 = new DevExpress.XtraRichEdit.UI.ReferencesRibbonPage();
            this.tableOfContentsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup();
            this.captionsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup();
            this.mailingsRibbonPage1 = new DevExpress.XtraRichEdit.UI.MailingsRibbonPage();
            this.mailMergeRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup();
            this.reviewRibbonPage1 = new DevExpress.XtraRichEdit.UI.ReviewRibbonPage();
            this.documentProofingRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.DocumentProofingRibbonPageGroup();
            this.documentProtectionRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.DocumentProtectionRibbonPageGroup();
            this.viewRibbonPage1 = new DevExpress.XtraRichEdit.UI.ViewRibbonPage();
            this.documentViewsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup();
            this.showRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup();
            this.zoomRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup();
            this.ribbonPageSkins = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.skinsRibbonPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.helpRibbonPage = new DevExpress.XtraBars.Ribbon.RibbonPage();
            this.helpRibbonPageGroup = new DevExpress.XtraBars.Ribbon.RibbonPageGroup();
            this.ribbonStatusBar = new DevExpress.XtraBars.Ribbon.RibbonStatusBar();
            this.richEditBarController1 = new DevExpress.XtraRichEdit.UI.RichEditBarController();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonControl)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.appMenu)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.popupControlContainer2)).BeginInit();
            this.popupControlContainer2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.buttonEdit.Properties)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.popupControlContainer1)).BeginInit();
            this.popupControlContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonImageCollection)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFloatingObjectOutlineWeight1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemBorderLineStyle1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemBorderLineWeight1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFontEdit1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemRichEditFontSizeEdit1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemColorPickEdit1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonImageCollectionLarge)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.richEditBarController1)).BeginInit();
            this.SuspendLayout();
            // 
            // stylesRibbonPageGroup1
            // 
            this.stylesRibbonPageGroup1.Glyph = ((System.Drawing.Image)(resources.GetObject("stylesRibbonPageGroup1.Glyph")));
            this.stylesRibbonPageGroup1.ItemLinks.Add(this.galleryChangeStyleItem1);
            this.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1";
            // 
            // galleryChangeStyleItem1
            // 
            // 
            // 
            // 
            this.galleryChangeStyleItem1.Gallery.ColumnCount = 10;
            this.galleryChangeStyleItem1.Gallery.Groups.AddRange(new DevExpress.XtraBars.Ribbon.GalleryItemGroup[] {
            galleryItemGroup1});
            this.galleryChangeStyleItem1.Gallery.ImageSize = new System.Drawing.Size(65, 46);
            this.galleryChangeStyleItem1.Id = 283;
            this.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1";
            // 
            // ribbonControl
            // 
            this.ribbonControl.ApplicationButtonDropDownControl = this.appMenu;
            this.ribbonControl.ApplicationButtonText = null;
            this.ribbonControl.ExpandCollapseItem.Id = 0;
            this.ribbonControl.Images = this.ribbonImageCollection;
            this.ribbonControl.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.ribbonControl.ExpandCollapseItem,
            this.iExit,
            this.iHelp,
            this.iAbout,
            this.siStatus,
            this.siInfo,
            this.rgbiSkins,
            this.changeFloatingObjectFillColorItem1,
            this.changeFloatingObjectOutlineColorItem1,
            this.changeFloatingObjectOutlineWeightItem1,
            this.changeFloatingObjectTextWrapTypeItem1,
            this.setFloatingObjectSquareTextWrapTypeItem1,
            this.setFloatingObjectTightTextWrapTypeItem1,
            this.setFloatingObjectThroughTextWrapTypeItem1,
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1,
            this.setFloatingObjectBehindTextWrapTypeItem1,
            this.setFloatingObjectInFrontOfTextWrapTypeItem1,
            this.changeFloatingObjectAlignmentItem1,
            this.setFloatingObjectTopLeftAlignmentItem1,
            this.setFloatingObjectTopCenterAlignmentItem1,
            this.setFloatingObjectTopRightAlignmentItem1,
            this.setFloatingObjectMiddleLeftAlignmentItem1,
            this.setFloatingObjectMiddleCenterAlignmentItem1,
            this.setFloatingObjectMiddleRightAlignmentItem1,
            this.setFloatingObjectBottomLeftAlignmentItem1,
            this.setFloatingObjectBottomCenterAlignmentItem1,
            this.setFloatingObjectBottomRightAlignmentItem1,
            this.floatingObjectBringForwardSubItem1,
            this.floatingObjectBringForwardItem1,
            this.floatingObjectBringToFrontItem1,
            this.floatingObjectBringInFrontOfTextItem1,
            this.floatingObjectSendBackwardSubItem1,
            this.floatingObjectSendBackwardItem1,
            this.floatingObjectSendToBackItem1,
            this.floatingObjectSendBehindTextItem1,
            this.toggleFirstRowItem1,
            this.toggleLastRowItem1,
            this.toggleBandedRowsItem1,
            this.toggleFirstColumnItem1,
            this.toggleLastColumnItem1,
            this.toggleBandedColumnItem1,
            this.galleryChangeTableStyleItem1,
            this.changeTableBorderLineStyleItem1,
            this.changeTableBorderLineWeightItem1,
            this.changeTableBorderColorItem1,
            this.changeTableBordersItem1,
            this.toggleTableCellsBottomBorderItem1,
            this.toggleTableCellsTopBorderItem1,
            this.toggleTableCellsLeftBorderItem1,
            this.toggleTableCellsRightBorderItem1,
            this.resetTableCellsAllBordersItem1,
            this.toggleTableCellsAllBordersItem1,
            this.toggleTableCellsOutsideBorderItem1,
            this.toggleTableCellsInsideBorderItem1,
            this.toggleTableCellsInsideHorizontalBorderItem1,
            this.toggleTableCellsInsideVerticalBorderItem1,
            this.toggleShowTableGridLinesItem1,
            this.changeTableCellsShadingItem1,
            this.selectTableElementsItem1,
            this.selectTableCellItem1,
            this.selectTableColumnItem1,
            this.selectTableRowItem1,
            this.selectTableItem1,
            this.showTablePropertiesFormItem1,
            this.deleteTableElementsItem1,
            this.showDeleteTableCellsFormItem1,
            this.deleteTableColumnsItem1,
            this.deleteTableRowsItem1,
            this.deleteTableItem1,
            this.insertTableRowAboveItem1,
            this.insertTableRowBelowItem1,
            this.insertTableColumnToLeftItem1,
            this.insertTableColumnToRightItem1,
            this.mergeTableCellsItem1,
            this.showSplitTableCellsForm1,
            this.splitTableItem1,
            this.toggleTableAutoFitItem1,
            this.toggleTableAutoFitContentsItem1,
            this.toggleTableAutoFitWindowItem1,
            this.toggleTableFixedColumnWidthItem1,
            this.toggleTableCellsTopLeftAlignmentItem1,
            this.toggleTableCellsMiddleLeftAlignmentItem1,
            this.toggleTableCellsBottomLeftAlignmentItem1,
            this.toggleTableCellsTopCenterAlignmentItem1,
            this.toggleTableCellsMiddleCenterAlignmentItem1,
            this.toggleTableCellsBottomCenterAlignmentItem1,
            this.toggleTableCellsTopRightAlignmentItem1,
            this.toggleTableCellsMiddleRightAlignmentItem1,
            this.toggleTableCellsBottomRightAlignmentItem1,
            this.showTableOptionsFormItem1,
            this.goToPageHeaderItem1,
            this.goToPageFooterItem1,
            this.goToNextHeaderFooterItem1,
            this.goToPreviousHeaderFooterItem1,
            this.toggleLinkToPreviousItem1,
            this.toggleDifferentFirstPageItem1,
            this.toggleDifferentOddAndEvenPagesItem1,
            this.closePageHeaderFooterItem1,
            this.switchToSimpleViewItem1,
            this.switchToDraftViewItem1,
            this.switchToPrintLayoutViewItem1,
            this.toggleShowHorizontalRulerItem1,
            this.toggleShowVerticalRulerItem1,
            this.zoomOutItem1,
            this.zoomInItem1,
            this.checkSpellingItem1,
            this.changeLanguageItem1,
            this.protectDocumentItem1,
            this.changeRangeEditingPermissionsItem1,
            this.unprotectDocumentItem1,
            this.insertMergeFieldItem1,
            this.showAllFieldCodesItem1,
            this.showAllFieldResultsItem1,
            this.toggleViewMergedDataItem1,
            this.insertTableOfContentsItem1,
            this.updateTableOfContentsItem1,
            this.addParagraphsToTableOfContentItem1,
            this.setParagraphHeadingLevelItem1,
            this.setParagraphHeadingLevelItem2,
            this.setParagraphHeadingLevelItem3,
            this.setParagraphHeadingLevelItem4,
            this.setParagraphHeadingLevelItem5,
            this.setParagraphHeadingLevelItem6,
            this.setParagraphHeadingLevelItem7,
            this.setParagraphHeadingLevelItem8,
            this.setParagraphHeadingLevelItem9,
            this.setParagraphHeadingLevelItem10,
            this.insertCaptionPlaceholderItem1,
            this.insertFiguresCaptionItems1,
            this.insertTablesCaptionItems1,
            this.insertEquationsCaptionItems1,
            this.insertTableOfFiguresPlaceholderItem1,
            this.insertTableOfFiguresItems1,
            this.insertTableOfTablesItems1,
            this.insertTableOfEquationsItems1,
            this.updateTableOfFiguresItem1,
            this.changeSectionPageMarginsItem1,
            this.setNormalSectionPageMarginsItem1,
            this.setNarrowSectionPageMarginsItem1,
            this.setModerateSectionPageMarginsItem1,
            this.setWideSectionPageMarginsItem1,
            this.showPageMarginsSetupFormItem1,
            this.changeSectionPageOrientationItem1,
            this.setPortraitPageOrientationItem1,
            this.setLandscapePageOrientationItem1,
            this.changeSectionPaperKindItem1,
            this.changeSectionColumnsItem1,
            this.setSectionOneColumnItem1,
            this.setSectionTwoColumnsItem1,
            this.setSectionThreeColumnsItem1,
            this.showColumnsSetupFormItem1,
            this.insertBreakItem1,
            this.insertPageBreakItem1,
            this.insertColumnBreakItem1,
            this.insertSectionBreakNextPageItem1,
            this.insertSectionBreakEvenPageItem1,
            this.insertSectionBreakOddPageItem1,
            this.changeSectionLineNumberingItem1,
            this.setSectionLineNumberingNoneItem1,
            this.setSectionLineNumberingContinuousItem1,
            this.setSectionLineNumberingRestartNewPageItem1,
            this.setSectionLineNumberingRestartNewSectionItem1,
            this.toggleParagraphSuppressLineNumbersItem1,
            this.showLineNumberingFormItem1,
            this.changePageColorItem1,
            this.insertTableItem1,
            this.insertPictureItem1,
            this.insertFloatingPictureItem1,
            this.insertBookmarkItem1,
            this.insertHyperlinkItem1,
            this.editPageHeaderItem1,
            this.editPageFooterItem1,
            this.insertPageNumberItem1,
            this.insertPageCountItem1,
            this.insertTextBoxItem1,
            this.insertSymbolItem1,
            this.pasteItem1,
            this.cutItem1,
            this.copyItem1,
            this.pasteSpecialItem1,
            this.barButtonGroup1,
            this.changeFontNameItem1,
            this.changeFontSizeItem1,
            this.fontSizeIncreaseItem1,
            this.fontSizeDecreaseItem1,
            this.barButtonGroup2,
            this.toggleFontBoldItem1,
            this.toggleFontItalicItem1,
            this.toggleFontUnderlineItem1,
            this.toggleFontDoubleUnderlineItem1,
            this.toggleFontStrikeoutItem1,
            this.toggleFontDoubleStrikeoutItem1,
            this.toggleFontSuperscriptItem1,
            this.toggleFontSubscriptItem1,
            this.barButtonGroup3,
            this.changeFontColorItem1,
            this.changeFontBackColorItem1,
            this.changeTextCaseItem1,
            this.makeTextUpperCaseItem1,
            this.makeTextLowerCaseItem1,
            this.capitalizeEachWordCaseItem1,
            this.toggleTextCaseItem1,
            this.clearFormattingItem1,
            this.barButtonGroup4,
            this.toggleBulletedListItem1,
            this.toggleNumberingListItem1,
            this.toggleMultiLevelListItem1,
            this.barButtonGroup5,
            this.decreaseIndentItem1,
            this.increaseIndentItem1,
            this.barButtonGroup6,
            this.toggleParagraphAlignmentLeftItem1,
            this.toggleParagraphAlignmentCenterItem1,
            this.toggleParagraphAlignmentRightItem1,
            this.toggleParagraphAlignmentJustifyItem1,
            this.toggleShowWhitespaceItem1,
            this.barButtonGroup7,
            this.changeParagraphLineSpacingItem1,
            this.setSingleParagraphSpacingItem1,
            this.setSesquialteralParagraphSpacingItem1,
            this.setDoubleParagraphSpacingItem1,
            this.showLineSpacingFormItem1,
            this.addSpacingBeforeParagraphItem1,
            this.removeSpacingBeforeParagraphItem1,
            this.addSpacingAfterParagraphItem1,
            this.removeSpacingAfterParagraphItem1,
            this.changeParagraphBackColorItem1,
            this.galleryChangeStyleItem1,
            this.findItem1,
            this.replaceItem1,
            this.undoItem1,
            this.redoItem1,
            this.fileNewItem1,
            this.fileOpenItem1,
            this.fileSaveItem1,
            this.fileSaveAsItem1,
            this.quickPrintItem1,
            this.printItem1,
            this.printPreviewItem1,
            this.barEditItem1,
            this.barCheckItem1});
            this.ribbonControl.LargeImages = this.ribbonImageCollectionLarge;
            this.ribbonControl.Location = new System.Drawing.Point(0, 0);
            this.ribbonControl.MaxItemId = 300;
            this.ribbonControl.Name = "ribbonControl";
            this.ribbonControl.PageCategories.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageCategory[] {
            this.floatingPictureToolsRibbonPageCategory1,
            this.tableToolsRibbonPageCategory1,
            this.headerFooterToolsRibbonPageCategory1});
            this.ribbonControl.PageHeaderItemLinks.Add(this.iAbout);
            this.ribbonControl.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage1,
            this.homeRibbonPage1,
            this.insertRibbonPage1,
            this.pageLayoutRibbonPage1,
            this.referencesRibbonPage1,
            this.mailingsRibbonPage1,
            this.reviewRibbonPage1,
            this.viewRibbonPage1,
            this.ribbonPageSkins,
            this.helpRibbonPage});
            this.ribbonControl.RepositoryItems.AddRange(new DevExpress.XtraEditors.Repository.RepositoryItem[] {
            this.repositoryItemFloatingObjectOutlineWeight1,
            this.repositoryItemBorderLineStyle1,
            this.repositoryItemBorderLineWeight1,
            this.repositoryItemFontEdit1,
            this.repositoryItemRichEditFontSizeEdit1,
            this.repositoryItemColorPickEdit1});
            this.ribbonControl.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonControlStyle.Office2010;
            this.ribbonControl.Size = new System.Drawing.Size(1100, 144);
            this.ribbonControl.StatusBar = this.ribbonStatusBar;
            this.ribbonControl.Toolbar.ItemLinks.Add(this.iHelp);
            // 
            // appMenu
            // 
            this.appMenu.BottomPaneControlContainer = this.popupControlContainer2;
            this.appMenu.ItemLinks.Add(this.iExit);
            this.appMenu.Name = "appMenu";
            this.appMenu.Ribbon = this.ribbonControl;
            this.appMenu.RightPaneControlContainer = this.popupControlContainer1;
            this.appMenu.ShowRightPane = true;
            // 
            // popupControlContainer2
            // 
            this.popupControlContainer2.Appearance.BackColor = System.Drawing.Color.Transparent;
            this.popupControlContainer2.Appearance.Options.UseBackColor = true;
            this.popupControlContainer2.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.popupControlContainer2.Controls.Add(this.buttonEdit);
            this.popupControlContainer2.Location = new System.Drawing.Point(238, 289);
            this.popupControlContainer2.Name = "popupControlContainer2";
            this.popupControlContainer2.Ribbon = this.ribbonControl;
            this.popupControlContainer2.Size = new System.Drawing.Size(118, 28);
            this.popupControlContainer2.TabIndex = 3;
            this.popupControlContainer2.Visible = false;
            // 
            // buttonEdit
            // 
            this.buttonEdit.EditValue = "Some Text";
            this.buttonEdit.Location = new System.Drawing.Point(3, 5);
            this.buttonEdit.MenuManager = this.ribbonControl;
            this.buttonEdit.Name = "buttonEdit";
            this.buttonEdit.Properties.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton()});
            this.buttonEdit.Size = new System.Drawing.Size(100, 20);
            this.buttonEdit.TabIndex = 0;
            // 
            // iExit
            // 
            this.iExit.Caption = "Exit";
            this.iExit.Description = "Closes this program after prompting you to save unsaved data.";
            this.iExit.Hint = "Closes this program after prompting you to save unsaved data";
            this.iExit.Id = 20;
            this.iExit.ImageIndex = 6;
            this.iExit.LargeImageIndex = 6;
            this.iExit.Name = "iExit";
            // 
            // popupControlContainer1
            // 
            this.popupControlContainer1.Appearance.BackColor = System.Drawing.Color.Transparent;
            this.popupControlContainer1.Appearance.Options.UseBackColor = true;
            this.popupControlContainer1.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.popupControlContainer1.Controls.Add(this.someLabelControl2);
            this.popupControlContainer1.Controls.Add(this.someLabelControl1);
            this.popupControlContainer1.Location = new System.Drawing.Point(111, 197);
            this.popupControlContainer1.Name = "popupControlContainer1";
            this.popupControlContainer1.Ribbon = this.ribbonControl;
            this.popupControlContainer1.Size = new System.Drawing.Size(76, 70);
            this.popupControlContainer1.TabIndex = 2;
            this.popupControlContainer1.Visible = false;
            // 
            // someLabelControl2
            // 
            this.someLabelControl2.Location = new System.Drawing.Point(3, 57);
            this.someLabelControl2.Name = "someLabelControl2";
            this.someLabelControl2.Size = new System.Drawing.Size(49, 13);
            this.someLabelControl2.TabIndex = 0;
            this.someLabelControl2.Text = "Some Info";
            // 
            // someLabelControl1
            // 
            this.someLabelControl1.Location = new System.Drawing.Point(3, 3);
            this.someLabelControl1.Name = "someLabelControl1";
            this.someLabelControl1.Size = new System.Drawing.Size(49, 13);
            this.someLabelControl1.TabIndex = 0;
            this.someLabelControl1.Text = "Some Info";
            // 
            // ribbonImageCollection
            // 
            this.ribbonImageCollection.ImageStream = ((DevExpress.Utils.ImageCollectionStreamer)(resources.GetObject("ribbonImageCollection.ImageStream")));
            this.ribbonImageCollection.Images.SetKeyName(0, "Ribbon_Exit_16x16.png");
            this.ribbonImageCollection.Images.SetKeyName(1, "Ribbon_Content_16x16.png");
            this.ribbonImageCollection.Images.SetKeyName(2, "Ribbon_Info_16x16.png");
            // 
            // iHelp
            // 
            this.iHelp.Caption = "Help";
            this.iHelp.Description = "Start the program help system.";
            this.iHelp.Hint = "Start the program help system";
            this.iHelp.Id = 22;
            this.iHelp.ImageIndex = 7;
            this.iHelp.LargeImageIndex = 7;
            this.iHelp.Name = "iHelp";
            // 
            // iAbout
            // 
            this.iAbout.Caption = "About";
            this.iAbout.Description = "Displays general program information.";
            this.iAbout.Hint = "Displays general program information";
            this.iAbout.Id = 24;
            this.iAbout.ImageIndex = 8;
            this.iAbout.LargeImageIndex = 8;
            this.iAbout.Name = "iAbout";
            // 
            // siStatus
            // 
            this.siStatus.Caption = "Some Status Info";
            this.siStatus.Id = 31;
            this.siStatus.Name = "siStatus";
            this.siStatus.TextAlignment = System.Drawing.StringAlignment.Near;
            // 
            // siInfo
            // 
            this.siInfo.Caption = "Some Info";
            this.siInfo.Id = 32;
            this.siInfo.Name = "siInfo";
            this.siInfo.TextAlignment = System.Drawing.StringAlignment.Near;
            // 
            // rgbiSkins
            // 
            this.rgbiSkins.Caption = "Skins";
            // 
            // 
            // 
            this.rgbiSkins.Gallery.AllowHoverImages = true;
            this.rgbiSkins.Gallery.Appearance.ItemCaptionAppearance.Normal.Options.UseFont = true;
            this.rgbiSkins.Gallery.Appearance.ItemCaptionAppearance.Normal.Options.UseTextOptions = true;
            this.rgbiSkins.Gallery.Appearance.ItemCaptionAppearance.Normal.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Center;
            this.rgbiSkins.Gallery.ColumnCount = 4;
            this.rgbiSkins.Gallery.FixedHoverImageSize = false;
            this.rgbiSkins.Gallery.ImageSize = new System.Drawing.Size(32, 17);
            this.rgbiSkins.Gallery.ItemImageLocation = DevExpress.Utils.Locations.Top;
            this.rgbiSkins.Gallery.RowCount = 4;
            this.rgbiSkins.Id = 60;
            this.rgbiSkins.Name = "rgbiSkins";
            // 
            // changeFloatingObjectFillColorItem1
            // 
            this.changeFloatingObjectFillColorItem1.Id = 62;
            this.changeFloatingObjectFillColorItem1.Name = "changeFloatingObjectFillColorItem1";
            // 
            // changeFloatingObjectOutlineColorItem1
            // 
            this.changeFloatingObjectOutlineColorItem1.Id = 63;
            this.changeFloatingObjectOutlineColorItem1.Name = "changeFloatingObjectOutlineColorItem1";
            // 
            // changeFloatingObjectOutlineWeightItem1
            // 
            this.changeFloatingObjectOutlineWeightItem1.Edit = this.repositoryItemFloatingObjectOutlineWeight1;
            this.changeFloatingObjectOutlineWeightItem1.EditValue = 20;
            this.changeFloatingObjectOutlineWeightItem1.Id = 64;
            this.changeFloatingObjectOutlineWeightItem1.Name = "changeFloatingObjectOutlineWeightItem1";
            // 
            // repositoryItemFloatingObjectOutlineWeight1
            // 
            this.repositoryItemFloatingObjectOutlineWeight1.AutoHeight = false;
            this.repositoryItemFloatingObjectOutlineWeight1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemFloatingObjectOutlineWeight1.Control = this.richEditControl;
            this.repositoryItemFloatingObjectOutlineWeight1.Name = "repositoryItemFloatingObjectOutlineWeight1";
            // 
            // richEditControl
            // 
            this.richEditControl.BorderStyle = DevExpress.XtraEditors.Controls.BorderStyles.NoBorder;
            this.richEditControl.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEditControl.Location = new System.Drawing.Point(0, 144);
            this.richEditControl.MenuManager = this.ribbonControl;
            this.richEditControl.Name = "richEditControl";
            this.richEditControl.Options.Fields.UseCurrentCultureDateTimeFormat = false;
            this.richEditControl.Options.MailMerge.KeepLastParagraph = true;
            this.richEditControl.Size = new System.Drawing.Size(1100, 525);
            this.richEditControl.SpellChecker = this.spellChecker;
            this.richEditControl.TabIndex = 1;
            this.richEditControl.MouseUp += new System.Windows.Forms.MouseEventHandler(this.richEditControl_MouseUp);
            // 
            // spellChecker
            // 
          
            this.spellChecker.ParentContainer = null;
            // 
            // changeFloatingObjectTextWrapTypeItem1
            // 
            this.changeFloatingObjectTextWrapTypeItem1.Id = 65;
            this.changeFloatingObjectTextWrapTypeItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectSquareTextWrapTypeItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectTightTextWrapTypeItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectThroughTextWrapTypeItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectTopAndBottomTextWrapTypeItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectBehindTextWrapTypeItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectInFrontOfTextWrapTypeItem1)});
            this.changeFloatingObjectTextWrapTypeItem1.Name = "changeFloatingObjectTextWrapTypeItem1";
            // 
            // setFloatingObjectSquareTextWrapTypeItem1
            // 
            this.setFloatingObjectSquareTextWrapTypeItem1.Id = 66;
            this.setFloatingObjectSquareTextWrapTypeItem1.Name = "setFloatingObjectSquareTextWrapTypeItem1";
            // 
            // setFloatingObjectTightTextWrapTypeItem1
            // 
            this.setFloatingObjectTightTextWrapTypeItem1.Id = 67;
            this.setFloatingObjectTightTextWrapTypeItem1.Name = "setFloatingObjectTightTextWrapTypeItem1";
            // 
            // setFloatingObjectThroughTextWrapTypeItem1
            // 
            this.setFloatingObjectThroughTextWrapTypeItem1.Id = 68;
            this.setFloatingObjectThroughTextWrapTypeItem1.Name = "setFloatingObjectThroughTextWrapTypeItem1";
            // 
            // setFloatingObjectTopAndBottomTextWrapTypeItem1
            // 
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1.Id = 69;
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1.Name = "setFloatingObjectTopAndBottomTextWrapTypeItem1";
            // 
            // setFloatingObjectBehindTextWrapTypeItem1
            // 
            this.setFloatingObjectBehindTextWrapTypeItem1.Id = 70;
            this.setFloatingObjectBehindTextWrapTypeItem1.Name = "setFloatingObjectBehindTextWrapTypeItem1";
            // 
            // setFloatingObjectInFrontOfTextWrapTypeItem1
            // 
            this.setFloatingObjectInFrontOfTextWrapTypeItem1.Id = 71;
            this.setFloatingObjectInFrontOfTextWrapTypeItem1.Name = "setFloatingObjectInFrontOfTextWrapTypeItem1";
            // 
            // changeFloatingObjectAlignmentItem1
            // 
            this.changeFloatingObjectAlignmentItem1.Id = 72;
            this.changeFloatingObjectAlignmentItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectTopLeftAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectTopCenterAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectTopRightAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectMiddleLeftAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectMiddleCenterAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectMiddleRightAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectBottomLeftAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectBottomCenterAlignmentItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setFloatingObjectBottomRightAlignmentItem1)});
            this.changeFloatingObjectAlignmentItem1.Name = "changeFloatingObjectAlignmentItem1";
            // 
            // setFloatingObjectTopLeftAlignmentItem1
            // 
            this.setFloatingObjectTopLeftAlignmentItem1.Id = 73;
            this.setFloatingObjectTopLeftAlignmentItem1.Name = "setFloatingObjectTopLeftAlignmentItem1";
            // 
            // setFloatingObjectTopCenterAlignmentItem1
            // 
            this.setFloatingObjectTopCenterAlignmentItem1.Id = 74;
            this.setFloatingObjectTopCenterAlignmentItem1.Name = "setFloatingObjectTopCenterAlignmentItem1";
            // 
            // setFloatingObjectTopRightAlignmentItem1
            // 
            this.setFloatingObjectTopRightAlignmentItem1.Id = 75;
            this.setFloatingObjectTopRightAlignmentItem1.Name = "setFloatingObjectTopRightAlignmentItem1";
            // 
            // setFloatingObjectMiddleLeftAlignmentItem1
            // 
            this.setFloatingObjectMiddleLeftAlignmentItem1.Id = 76;
            this.setFloatingObjectMiddleLeftAlignmentItem1.Name = "setFloatingObjectMiddleLeftAlignmentItem1";
            // 
            // setFloatingObjectMiddleCenterAlignmentItem1
            // 
            this.setFloatingObjectMiddleCenterAlignmentItem1.Id = 77;
            this.setFloatingObjectMiddleCenterAlignmentItem1.Name = "setFloatingObjectMiddleCenterAlignmentItem1";
            // 
            // setFloatingObjectMiddleRightAlignmentItem1
            // 
            this.setFloatingObjectMiddleRightAlignmentItem1.Id = 78;
            this.setFloatingObjectMiddleRightAlignmentItem1.Name = "setFloatingObjectMiddleRightAlignmentItem1";
            // 
            // setFloatingObjectBottomLeftAlignmentItem1
            // 
            this.setFloatingObjectBottomLeftAlignmentItem1.Id = 79;
            this.setFloatingObjectBottomLeftAlignmentItem1.Name = "setFloatingObjectBottomLeftAlignmentItem1";
            // 
            // setFloatingObjectBottomCenterAlignmentItem1
            // 
            this.setFloatingObjectBottomCenterAlignmentItem1.Id = 80;
            this.setFloatingObjectBottomCenterAlignmentItem1.Name = "setFloatingObjectBottomCenterAlignmentItem1";
            // 
            // setFloatingObjectBottomRightAlignmentItem1
            // 
            this.setFloatingObjectBottomRightAlignmentItem1.Id = 81;
            this.setFloatingObjectBottomRightAlignmentItem1.Name = "setFloatingObjectBottomRightAlignmentItem1";
            // 
            // floatingObjectBringForwardSubItem1
            // 
            this.floatingObjectBringForwardSubItem1.Id = 82;
            this.floatingObjectBringForwardSubItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringForwardItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringToFrontItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringInFrontOfTextItem1)});
            this.floatingObjectBringForwardSubItem1.Name = "floatingObjectBringForwardSubItem1";
            // 
            // floatingObjectBringForwardItem1
            // 
            this.floatingObjectBringForwardItem1.Id = 83;
            this.floatingObjectBringForwardItem1.Name = "floatingObjectBringForwardItem1";
            // 
            // floatingObjectBringToFrontItem1
            // 
            this.floatingObjectBringToFrontItem1.Id = 84;
            this.floatingObjectBringToFrontItem1.Name = "floatingObjectBringToFrontItem1";
            // 
            // floatingObjectBringInFrontOfTextItem1
            // 
            this.floatingObjectBringInFrontOfTextItem1.Id = 85;
            this.floatingObjectBringInFrontOfTextItem1.Name = "floatingObjectBringInFrontOfTextItem1";
            // 
            // floatingObjectSendBackwardSubItem1
            // 
            this.floatingObjectSendBackwardSubItem1.Id = 86;
            this.floatingObjectSendBackwardSubItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendBackwardItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendToBackItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendBehindTextItem1)});
            this.floatingObjectSendBackwardSubItem1.Name = "floatingObjectSendBackwardSubItem1";
            // 
            // floatingObjectSendBackwardItem1
            // 
            this.floatingObjectSendBackwardItem1.Id = 87;
            this.floatingObjectSendBackwardItem1.Name = "floatingObjectSendBackwardItem1";
            // 
            // floatingObjectSendToBackItem1
            // 
            this.floatingObjectSendToBackItem1.Id = 88;
            this.floatingObjectSendToBackItem1.Name = "floatingObjectSendToBackItem1";
            // 
            // floatingObjectSendBehindTextItem1
            // 
            this.floatingObjectSendBehindTextItem1.Id = 89;
            this.floatingObjectSendBehindTextItem1.Name = "floatingObjectSendBehindTextItem1";
            // 
            // toggleFirstRowItem1
            // 
            this.toggleFirstRowItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleFirstRowItem1.Id = 90;
            this.toggleFirstRowItem1.Name = "toggleFirstRowItem1";
            // 
            // toggleLastRowItem1
            // 
            this.toggleLastRowItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleLastRowItem1.Id = 91;
            this.toggleLastRowItem1.Name = "toggleLastRowItem1";
            // 
            // toggleBandedRowsItem1
            // 
            this.toggleBandedRowsItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleBandedRowsItem1.Id = 92;
            this.toggleBandedRowsItem1.Name = "toggleBandedRowsItem1";
            // 
            // toggleFirstColumnItem1
            // 
            this.toggleFirstColumnItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleFirstColumnItem1.Id = 93;
            this.toggleFirstColumnItem1.Name = "toggleFirstColumnItem1";
            // 
            // toggleLastColumnItem1
            // 
            this.toggleLastColumnItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleLastColumnItem1.Id = 94;
            this.toggleLastColumnItem1.Name = "toggleLastColumnItem1";
            // 
            // toggleBandedColumnItem1
            // 
            this.toggleBandedColumnItem1.CheckBoxVisibility = DevExpress.XtraBars.CheckBoxVisibility.BeforeText;
            this.toggleBandedColumnItem1.Id = 95;
            this.toggleBandedColumnItem1.Name = "toggleBandedColumnItem1";
            // 
            // galleryChangeTableStyleItem1
            // 
            this.galleryChangeTableStyleItem1.CurrentItem = null;
            this.galleryChangeTableStyleItem1.CurrentItemStyle = null;
            this.galleryChangeTableStyleItem1.CurrentStyle = null;
            this.galleryChangeTableStyleItem1.DeleteItemLink = null;
            // 
            // 
            // 
            this.galleryChangeTableStyleItem1.Gallery.ColumnCount = 3;
            this.galleryChangeTableStyleItem1.Gallery.Groups.AddRange(new DevExpress.XtraBars.Ribbon.GalleryItemGroup[] {
            galleryItemGroup2});
            this.galleryChangeTableStyleItem1.Gallery.ImageSize = new System.Drawing.Size(65, 46);
            this.galleryChangeTableStyleItem1.Id = 96;
            this.galleryChangeTableStyleItem1.ModifyItemLink = null;
            this.galleryChangeTableStyleItem1.Name = "galleryChangeTableStyleItem1";
            this.galleryChangeTableStyleItem1.NewItemLink = null;
            this.galleryChangeTableStyleItem1.PopupGallery = null;
            // 
            // changeTableBorderLineStyleItem1
            // 
            this.changeTableBorderLineStyleItem1.Edit = this.repositoryItemBorderLineStyle1;
            borderInfo1.Color = System.Drawing.Color.Black;
            borderInfo1.Frame = false;
            borderInfo1.Offset = 0;
            borderInfo1.Shadow = false;
            borderInfo1.Style = DevExpress.XtraRichEdit.Model.BorderLineStyle.Single;
            borderInfo1.Width = 10;
            this.changeTableBorderLineStyleItem1.EditValue = borderInfo1;
            this.changeTableBorderLineStyleItem1.Id = 97;
            this.changeTableBorderLineStyleItem1.Name = "changeTableBorderLineStyleItem1";
            // 
            // repositoryItemBorderLineStyle1
            // 
            this.repositoryItemBorderLineStyle1.AutoHeight = false;
            this.repositoryItemBorderLineStyle1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemBorderLineStyle1.Control = this.richEditControl;
            this.repositoryItemBorderLineStyle1.Name = "repositoryItemBorderLineStyle1";
            // 
            // changeTableBorderLineWeightItem1
            // 
            this.changeTableBorderLineWeightItem1.Edit = this.repositoryItemBorderLineWeight1;
            this.changeTableBorderLineWeightItem1.EditValue = 20;
            this.changeTableBorderLineWeightItem1.Id = 98;
            this.changeTableBorderLineWeightItem1.Name = "changeTableBorderLineWeightItem1";
            // 
            // repositoryItemBorderLineWeight1
            // 
            this.repositoryItemBorderLineWeight1.AutoHeight = false;
            this.repositoryItemBorderLineWeight1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemBorderLineWeight1.Control = this.richEditControl;
            this.repositoryItemBorderLineWeight1.Name = "repositoryItemBorderLineWeight1";
            // 
            // changeTableBorderColorItem1
            // 
            this.changeTableBorderColorItem1.Id = 99;
            this.changeTableBorderColorItem1.Name = "changeTableBorderColorItem1";
            // 
            // changeTableBordersItem1
            // 
            this.changeTableBordersItem1.Id = 100;
            this.changeTableBordersItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsBottomBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsTopBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsLeftBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsRightBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.resetTableCellsAllBordersItem1, true),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsAllBordersItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsOutsideBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsInsideBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsInsideHorizontalBorderItem1, true),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableCellsInsideVerticalBorderItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleShowTableGridLinesItem1, true)});
            this.changeTableBordersItem1.Name = "changeTableBordersItem1";
            // 
            // toggleTableCellsBottomBorderItem1
            // 
            this.toggleTableCellsBottomBorderItem1.Id = 101;
            this.toggleTableCellsBottomBorderItem1.Name = "toggleTableCellsBottomBorderItem1";
            // 
            // toggleTableCellsTopBorderItem1
            // 
            this.toggleTableCellsTopBorderItem1.Id = 102;
            this.toggleTableCellsTopBorderItem1.Name = "toggleTableCellsTopBorderItem1";
            // 
            // toggleTableCellsLeftBorderItem1
            // 
            this.toggleTableCellsLeftBorderItem1.Id = 103;
            this.toggleTableCellsLeftBorderItem1.Name = "toggleTableCellsLeftBorderItem1";
            // 
            // toggleTableCellsRightBorderItem1
            // 
            this.toggleTableCellsRightBorderItem1.Id = 104;
            this.toggleTableCellsRightBorderItem1.Name = "toggleTableCellsRightBorderItem1";
            // 
            // resetTableCellsAllBordersItem1
            // 
            this.resetTableCellsAllBordersItem1.Id = 105;
            this.resetTableCellsAllBordersItem1.Name = "resetTableCellsAllBordersItem1";
            // 
            // toggleTableCellsAllBordersItem1
            // 
            this.toggleTableCellsAllBordersItem1.Id = 106;
            this.toggleTableCellsAllBordersItem1.Name = "toggleTableCellsAllBordersItem1";
            // 
            // toggleTableCellsOutsideBorderItem1
            // 
            this.toggleTableCellsOutsideBorderItem1.Id = 107;
            this.toggleTableCellsOutsideBorderItem1.Name = "toggleTableCellsOutsideBorderItem1";
            // 
            // toggleTableCellsInsideBorderItem1
            // 
            this.toggleTableCellsInsideBorderItem1.Id = 108;
            this.toggleTableCellsInsideBorderItem1.Name = "toggleTableCellsInsideBorderItem1";
            // 
            // toggleTableCellsInsideHorizontalBorderItem1
            // 
            this.toggleTableCellsInsideHorizontalBorderItem1.Id = 109;
            this.toggleTableCellsInsideHorizontalBorderItem1.Name = "toggleTableCellsInsideHorizontalBorderItem1";
            // 
            // toggleTableCellsInsideVerticalBorderItem1
            // 
            this.toggleTableCellsInsideVerticalBorderItem1.Id = 110;
            this.toggleTableCellsInsideVerticalBorderItem1.Name = "toggleTableCellsInsideVerticalBorderItem1";
            // 
            // toggleShowTableGridLinesItem1
            // 
            this.toggleShowTableGridLinesItem1.Id = 111;
            this.toggleShowTableGridLinesItem1.Name = "toggleShowTableGridLinesItem1";
            // 
            // changeTableCellsShadingItem1
            // 
            this.changeTableCellsShadingItem1.Id = 112;
            this.changeTableCellsShadingItem1.Name = "changeTableCellsShadingItem1";
            // 
            // selectTableElementsItem1
            // 
            this.selectTableElementsItem1.Id = 113;
            this.selectTableElementsItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.selectTableCellItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.selectTableColumnItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.selectTableRowItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.selectTableItem1)});
            this.selectTableElementsItem1.Name = "selectTableElementsItem1";
            // 
            // selectTableCellItem1
            // 
            this.selectTableCellItem1.Id = 114;
            this.selectTableCellItem1.Name = "selectTableCellItem1";
            // 
            // selectTableColumnItem1
            // 
            this.selectTableColumnItem1.Id = 115;
            this.selectTableColumnItem1.Name = "selectTableColumnItem1";
            // 
            // selectTableRowItem1
            // 
            this.selectTableRowItem1.Id = 116;
            this.selectTableRowItem1.Name = "selectTableRowItem1";
            // 
            // selectTableItem1
            // 
            this.selectTableItem1.Id = 117;
            this.selectTableItem1.Name = "selectTableItem1";
            // 
            // showTablePropertiesFormItem1
            // 
            this.showTablePropertiesFormItem1.Id = 118;
            this.showTablePropertiesFormItem1.Name = "showTablePropertiesFormItem1";
            // 
            // deleteTableElementsItem1
            // 
            this.deleteTableElementsItem1.Id = 119;
            this.deleteTableElementsItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.showDeleteTableCellsFormItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.deleteTableColumnsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.deleteTableRowsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.deleteTableItem1)});
            this.deleteTableElementsItem1.Name = "deleteTableElementsItem1";
            // 
            // showDeleteTableCellsFormItem1
            // 
            this.showDeleteTableCellsFormItem1.Id = 120;
            this.showDeleteTableCellsFormItem1.Name = "showDeleteTableCellsFormItem1";
            // 
            // deleteTableColumnsItem1
            // 
            this.deleteTableColumnsItem1.Id = 121;
            this.deleteTableColumnsItem1.Name = "deleteTableColumnsItem1";
            // 
            // deleteTableRowsItem1
            // 
            this.deleteTableRowsItem1.Id = 122;
            this.deleteTableRowsItem1.Name = "deleteTableRowsItem1";
            // 
            // deleteTableItem1
            // 
            this.deleteTableItem1.Id = 123;
            this.deleteTableItem1.Name = "deleteTableItem1";
            // 
            // insertTableRowAboveItem1
            // 
            this.insertTableRowAboveItem1.Id = 124;
            this.insertTableRowAboveItem1.Name = "insertTableRowAboveItem1";
            // 
            // insertTableRowBelowItem1
            // 
            this.insertTableRowBelowItem1.Id = 125;
            this.insertTableRowBelowItem1.Name = "insertTableRowBelowItem1";
            // 
            // insertTableColumnToLeftItem1
            // 
            this.insertTableColumnToLeftItem1.Id = 126;
            this.insertTableColumnToLeftItem1.Name = "insertTableColumnToLeftItem1";
            // 
            // insertTableColumnToRightItem1
            // 
            this.insertTableColumnToRightItem1.Id = 127;
            this.insertTableColumnToRightItem1.Name = "insertTableColumnToRightItem1";
            // 
            // mergeTableCellsItem1
            // 
            this.mergeTableCellsItem1.Id = 128;
            this.mergeTableCellsItem1.Name = "mergeTableCellsItem1";
            // 
            // showSplitTableCellsForm1
            // 
            this.showSplitTableCellsForm1.Id = 129;
            this.showSplitTableCellsForm1.Name = "showSplitTableCellsForm1";
            // 
            // splitTableItem1
            // 
            this.splitTableItem1.Id = 130;
            this.splitTableItem1.Name = "splitTableItem1";
            // 
            // toggleTableAutoFitItem1
            // 
            this.toggleTableAutoFitItem1.Id = 131;
            this.toggleTableAutoFitItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableAutoFitContentsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableAutoFitWindowItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTableFixedColumnWidthItem1)});
            this.toggleTableAutoFitItem1.Name = "toggleTableAutoFitItem1";
            // 
            // toggleTableAutoFitContentsItem1
            // 
            this.toggleTableAutoFitContentsItem1.Id = 132;
            this.toggleTableAutoFitContentsItem1.Name = "toggleTableAutoFitContentsItem1";
            // 
            // toggleTableAutoFitWindowItem1
            // 
            this.toggleTableAutoFitWindowItem1.Id = 133;
            this.toggleTableAutoFitWindowItem1.Name = "toggleTableAutoFitWindowItem1";
            // 
            // toggleTableFixedColumnWidthItem1
            // 
            this.toggleTableFixedColumnWidthItem1.Id = 134;
            this.toggleTableFixedColumnWidthItem1.Name = "toggleTableFixedColumnWidthItem1";
            // 
            // toggleTableCellsTopLeftAlignmentItem1
            // 
            this.toggleTableCellsTopLeftAlignmentItem1.Id = 135;
            this.toggleTableCellsTopLeftAlignmentItem1.Name = "toggleTableCellsTopLeftAlignmentItem1";
            // 
            // toggleTableCellsMiddleLeftAlignmentItem1
            // 
            this.toggleTableCellsMiddleLeftAlignmentItem1.Id = 136;
            this.toggleTableCellsMiddleLeftAlignmentItem1.Name = "toggleTableCellsMiddleLeftAlignmentItem1";
            // 
            // toggleTableCellsBottomLeftAlignmentItem1
            // 
            this.toggleTableCellsBottomLeftAlignmentItem1.Id = 137;
            this.toggleTableCellsBottomLeftAlignmentItem1.Name = "toggleTableCellsBottomLeftAlignmentItem1";
            // 
            // toggleTableCellsTopCenterAlignmentItem1
            // 
            this.toggleTableCellsTopCenterAlignmentItem1.Id = 138;
            this.toggleTableCellsTopCenterAlignmentItem1.Name = "toggleTableCellsTopCenterAlignmentItem1";
            // 
            // toggleTableCellsMiddleCenterAlignmentItem1
            // 
            this.toggleTableCellsMiddleCenterAlignmentItem1.Id = 139;
            this.toggleTableCellsMiddleCenterAlignmentItem1.Name = "toggleTableCellsMiddleCenterAlignmentItem1";
            // 
            // toggleTableCellsBottomCenterAlignmentItem1
            // 
            this.toggleTableCellsBottomCenterAlignmentItem1.Id = 140;
            this.toggleTableCellsBottomCenterAlignmentItem1.Name = "toggleTableCellsBottomCenterAlignmentItem1";
            // 
            // toggleTableCellsTopRightAlignmentItem1
            // 
            this.toggleTableCellsTopRightAlignmentItem1.Id = 141;
            this.toggleTableCellsTopRightAlignmentItem1.Name = "toggleTableCellsTopRightAlignmentItem1";
            // 
            // toggleTableCellsMiddleRightAlignmentItem1
            // 
            this.toggleTableCellsMiddleRightAlignmentItem1.Id = 142;
            this.toggleTableCellsMiddleRightAlignmentItem1.Name = "toggleTableCellsMiddleRightAlignmentItem1";
            // 
            // toggleTableCellsBottomRightAlignmentItem1
            // 
            this.toggleTableCellsBottomRightAlignmentItem1.Id = 143;
            this.toggleTableCellsBottomRightAlignmentItem1.Name = "toggleTableCellsBottomRightAlignmentItem1";
            // 
            // showTableOptionsFormItem1
            // 
            this.showTableOptionsFormItem1.Id = 144;
            this.showTableOptionsFormItem1.Name = "showTableOptionsFormItem1";
            // 
            // goToPageHeaderItem1
            // 
            this.goToPageHeaderItem1.Id = 145;
            this.goToPageHeaderItem1.Name = "goToPageHeaderItem1";
            // 
            // goToPageFooterItem1
            // 
            this.goToPageFooterItem1.Id = 146;
            this.goToPageFooterItem1.Name = "goToPageFooterItem1";
            // 
            // goToNextHeaderFooterItem1
            // 
            this.goToNextHeaderFooterItem1.Id = 147;
            this.goToNextHeaderFooterItem1.Name = "goToNextHeaderFooterItem1";
            // 
            // goToPreviousHeaderFooterItem1
            // 
            this.goToPreviousHeaderFooterItem1.Id = 148;
            this.goToPreviousHeaderFooterItem1.Name = "goToPreviousHeaderFooterItem1";
            // 
            // toggleLinkToPreviousItem1
            // 
            this.toggleLinkToPreviousItem1.Id = 149;
            this.toggleLinkToPreviousItem1.Name = "toggleLinkToPreviousItem1";
            // 
            // toggleDifferentFirstPageItem1
            // 
            this.toggleDifferentFirstPageItem1.Id = 150;
            this.toggleDifferentFirstPageItem1.Name = "toggleDifferentFirstPageItem1";
            // 
            // toggleDifferentOddAndEvenPagesItem1
            // 
            this.toggleDifferentOddAndEvenPagesItem1.Id = 151;
            this.toggleDifferentOddAndEvenPagesItem1.Name = "toggleDifferentOddAndEvenPagesItem1";
            // 
            // closePageHeaderFooterItem1
            // 
            this.closePageHeaderFooterItem1.Id = 152;
            this.closePageHeaderFooterItem1.Name = "closePageHeaderFooterItem1";
            // 
            // switchToSimpleViewItem1
            // 
            this.switchToSimpleViewItem1.Id = 153;
            this.switchToSimpleViewItem1.Name = "switchToSimpleViewItem1";
            // 
            // switchToDraftViewItem1
            // 
            this.switchToDraftViewItem1.Id = 154;
            this.switchToDraftViewItem1.Name = "switchToDraftViewItem1";
            // 
            // switchToPrintLayoutViewItem1
            // 
            this.switchToPrintLayoutViewItem1.Id = 155;
            this.switchToPrintLayoutViewItem1.Name = "switchToPrintLayoutViewItem1";
            // 
            // toggleShowHorizontalRulerItem1
            // 
            this.toggleShowHorizontalRulerItem1.Id = 156;
            this.toggleShowHorizontalRulerItem1.Name = "toggleShowHorizontalRulerItem1";
            // 
            // toggleShowVerticalRulerItem1
            // 
            this.toggleShowVerticalRulerItem1.Id = 157;
            this.toggleShowVerticalRulerItem1.Name = "toggleShowVerticalRulerItem1";
            // 
            // zoomOutItem1
            // 
            this.zoomOutItem1.Id = 158;
            this.zoomOutItem1.Name = "zoomOutItem1";
            // 
            // zoomInItem1
            // 
            this.zoomInItem1.Id = 159;
            this.zoomInItem1.Name = "zoomInItem1";
            // 
            // checkSpellingItem1
            // 
            this.checkSpellingItem1.Id = 160;
            this.checkSpellingItem1.Name = "checkSpellingItem1";
            // 
            // changeLanguageItem1
            // 
            this.changeLanguageItem1.Id = 161;
            this.changeLanguageItem1.Name = "changeLanguageItem1";
            // 
            // protectDocumentItem1
            // 
            this.protectDocumentItem1.Id = 162;
            this.protectDocumentItem1.Name = "protectDocumentItem1";
            // 
            // changeRangeEditingPermissionsItem1
            // 
            this.changeRangeEditingPermissionsItem1.Id = 163;
            this.changeRangeEditingPermissionsItem1.Name = "changeRangeEditingPermissionsItem1";
            // 
            // unprotectDocumentItem1
            // 
            this.unprotectDocumentItem1.Id = 164;
            this.unprotectDocumentItem1.Name = "unprotectDocumentItem1";
            // 
            // insertMergeFieldItem1
            // 
            this.insertMergeFieldItem1.Id = 165;
            this.insertMergeFieldItem1.Name = "insertMergeFieldItem1";
            // 
            // showAllFieldCodesItem1
            // 
            this.showAllFieldCodesItem1.Id = 166;
            this.showAllFieldCodesItem1.Name = "showAllFieldCodesItem1";
            // 
            // showAllFieldResultsItem1
            // 
            this.showAllFieldResultsItem1.Id = 167;
            this.showAllFieldResultsItem1.Name = "showAllFieldResultsItem1";
            // 
            // toggleViewMergedDataItem1
            // 
            this.toggleViewMergedDataItem1.Id = 168;
            this.toggleViewMergedDataItem1.Name = "toggleViewMergedDataItem1";
            // 
            // insertTableOfContentsItem1
            // 
            this.insertTableOfContentsItem1.Id = 169;
            this.insertTableOfContentsItem1.Name = "insertTableOfContentsItem1";
            // 
            // updateTableOfContentsItem1
            // 
            this.updateTableOfContentsItem1.Id = 170;
            this.updateTableOfContentsItem1.Name = "updateTableOfContentsItem1";
            // 
            // addParagraphsToTableOfContentItem1
            // 
            this.addParagraphsToTableOfContentItem1.Id = 171;
            this.addParagraphsToTableOfContentItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem2),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem3),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem4),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem5),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem6),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem7),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem8),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem9),
            new DevExpress.XtraBars.LinkPersistInfo(this.setParagraphHeadingLevelItem10)});
            this.addParagraphsToTableOfContentItem1.Name = "addParagraphsToTableOfContentItem1";
            // 
            // setParagraphHeadingLevelItem1
            // 
            this.setParagraphHeadingLevelItem1.Id = 172;
            this.setParagraphHeadingLevelItem1.Name = "setParagraphHeadingLevelItem1";
            this.setParagraphHeadingLevelItem1.OutlineLevel = 0;
            // 
            // setParagraphHeadingLevelItem2
            // 
            this.setParagraphHeadingLevelItem2.Id = 173;
            this.setParagraphHeadingLevelItem2.Name = "setParagraphHeadingLevelItem2";
            this.setParagraphHeadingLevelItem2.OutlineLevel = 1;
            // 
            // setParagraphHeadingLevelItem3
            // 
            this.setParagraphHeadingLevelItem3.Id = 174;
            this.setParagraphHeadingLevelItem3.Name = "setParagraphHeadingLevelItem3";
            this.setParagraphHeadingLevelItem3.OutlineLevel = 2;
            // 
            // setParagraphHeadingLevelItem4
            // 
            this.setParagraphHeadingLevelItem4.Id = 175;
            this.setParagraphHeadingLevelItem4.Name = "setParagraphHeadingLevelItem4";
            this.setParagraphHeadingLevelItem4.OutlineLevel = 3;
            // 
            // setParagraphHeadingLevelItem5
            // 
            this.setParagraphHeadingLevelItem5.Id = 176;
            this.setParagraphHeadingLevelItem5.Name = "setParagraphHeadingLevelItem5";
            this.setParagraphHeadingLevelItem5.OutlineLevel = 4;
            // 
            // setParagraphHeadingLevelItem6
            // 
            this.setParagraphHeadingLevelItem6.Id = 177;
            this.setParagraphHeadingLevelItem6.Name = "setParagraphHeadingLevelItem6";
            this.setParagraphHeadingLevelItem6.OutlineLevel = 5;
            // 
            // setParagraphHeadingLevelItem7
            // 
            this.setParagraphHeadingLevelItem7.Id = 178;
            this.setParagraphHeadingLevelItem7.Name = "setParagraphHeadingLevelItem7";
            this.setParagraphHeadingLevelItem7.OutlineLevel = 6;
            // 
            // setParagraphHeadingLevelItem8
            // 
            this.setParagraphHeadingLevelItem8.Id = 179;
            this.setParagraphHeadingLevelItem8.Name = "setParagraphHeadingLevelItem8";
            this.setParagraphHeadingLevelItem8.OutlineLevel = 7;
            // 
            // setParagraphHeadingLevelItem9
            // 
            this.setParagraphHeadingLevelItem9.Id = 180;
            this.setParagraphHeadingLevelItem9.Name = "setParagraphHeadingLevelItem9";
            this.setParagraphHeadingLevelItem9.OutlineLevel = 8;
            // 
            // setParagraphHeadingLevelItem10
            // 
            this.setParagraphHeadingLevelItem10.Id = 181;
            this.setParagraphHeadingLevelItem10.Name = "setParagraphHeadingLevelItem10";
            this.setParagraphHeadingLevelItem10.OutlineLevel = 9;
            // 
            // insertCaptionPlaceholderItem1
            // 
            this.insertCaptionPlaceholderItem1.Id = 182;
            this.insertCaptionPlaceholderItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.insertFiguresCaptionItems1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertTablesCaptionItems1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertEquationsCaptionItems1)});
            this.insertCaptionPlaceholderItem1.Name = "insertCaptionPlaceholderItem1";
            // 
            // insertFiguresCaptionItems1
            // 
            this.insertFiguresCaptionItems1.Id = 183;
            this.insertFiguresCaptionItems1.Name = "insertFiguresCaptionItems1";
            // 
            // insertTablesCaptionItems1
            // 
            this.insertTablesCaptionItems1.Id = 184;
            this.insertTablesCaptionItems1.Name = "insertTablesCaptionItems1";
            // 
            // insertEquationsCaptionItems1
            // 
            this.insertEquationsCaptionItems1.Id = 185;
            this.insertEquationsCaptionItems1.Name = "insertEquationsCaptionItems1";
            // 
            // insertTableOfFiguresPlaceholderItem1
            // 
            this.insertTableOfFiguresPlaceholderItem1.Id = 186;
            this.insertTableOfFiguresPlaceholderItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.insertTableOfFiguresItems1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertTableOfTablesItems1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertTableOfEquationsItems1)});
            this.insertTableOfFiguresPlaceholderItem1.Name = "insertTableOfFiguresPlaceholderItem1";
            // 
            // insertTableOfFiguresItems1
            // 
            this.insertTableOfFiguresItems1.Id = 187;
            this.insertTableOfFiguresItems1.Name = "insertTableOfFiguresItems1";
            // 
            // insertTableOfTablesItems1
            // 
            this.insertTableOfTablesItems1.Id = 188;
            this.insertTableOfTablesItems1.Name = "insertTableOfTablesItems1";
            // 
            // insertTableOfEquationsItems1
            // 
            this.insertTableOfEquationsItems1.Id = 189;
            this.insertTableOfEquationsItems1.Name = "insertTableOfEquationsItems1";
            // 
            // updateTableOfFiguresItem1
            // 
            this.updateTableOfFiguresItem1.Id = 190;
            this.updateTableOfFiguresItem1.Name = "updateTableOfFiguresItem1";
            // 
            // changeSectionPageMarginsItem1
            // 
            this.changeSectionPageMarginsItem1.Id = 191;
            this.changeSectionPageMarginsItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setNormalSectionPageMarginsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setNarrowSectionPageMarginsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setModerateSectionPageMarginsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setWideSectionPageMarginsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.showPageMarginsSetupFormItem1, true)});
            this.changeSectionPageMarginsItem1.Name = "changeSectionPageMarginsItem1";
            // 
            // setNormalSectionPageMarginsItem1
            // 
            this.setNormalSectionPageMarginsItem1.Id = 192;
            this.setNormalSectionPageMarginsItem1.Name = "setNormalSectionPageMarginsItem1";
            // 
            // setNarrowSectionPageMarginsItem1
            // 
            this.setNarrowSectionPageMarginsItem1.Id = 193;
            this.setNarrowSectionPageMarginsItem1.Name = "setNarrowSectionPageMarginsItem1";
            // 
            // setModerateSectionPageMarginsItem1
            // 
            this.setModerateSectionPageMarginsItem1.Id = 194;
            this.setModerateSectionPageMarginsItem1.Name = "setModerateSectionPageMarginsItem1";
            // 
            // setWideSectionPageMarginsItem1
            // 
            this.setWideSectionPageMarginsItem1.Id = 195;
            this.setWideSectionPageMarginsItem1.Name = "setWideSectionPageMarginsItem1";
            // 
            // showPageMarginsSetupFormItem1
            // 
            this.showPageMarginsSetupFormItem1.Id = 196;
            this.showPageMarginsSetupFormItem1.Name = "showPageMarginsSetupFormItem1";
            // 
            // changeSectionPageOrientationItem1
            // 
            this.changeSectionPageOrientationItem1.Id = 197;
            this.changeSectionPageOrientationItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setPortraitPageOrientationItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setLandscapePageOrientationItem1)});
            this.changeSectionPageOrientationItem1.Name = "changeSectionPageOrientationItem1";
            // 
            // setPortraitPageOrientationItem1
            // 
            this.setPortraitPageOrientationItem1.Id = 198;
            this.setPortraitPageOrientationItem1.Name = "setPortraitPageOrientationItem1";
            // 
            // setLandscapePageOrientationItem1
            // 
            this.setLandscapePageOrientationItem1.Id = 199;
            this.setLandscapePageOrientationItem1.Name = "setLandscapePageOrientationItem1";
            // 
            // changeSectionPaperKindItem1
            // 
            this.changeSectionPaperKindItem1.Id = 200;
            this.changeSectionPaperKindItem1.Name = "changeSectionPaperKindItem1";
            // 
            // changeSectionColumnsItem1
            // 
            this.changeSectionColumnsItem1.Id = 201;
            this.changeSectionColumnsItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionOneColumnItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionTwoColumnsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionThreeColumnsItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.showColumnsSetupFormItem1, true)});
            this.changeSectionColumnsItem1.Name = "changeSectionColumnsItem1";
            // 
            // setSectionOneColumnItem1
            // 
            this.setSectionOneColumnItem1.Id = 202;
            this.setSectionOneColumnItem1.Name = "setSectionOneColumnItem1";
            // 
            // setSectionTwoColumnsItem1
            // 
            this.setSectionTwoColumnsItem1.Id = 203;
            this.setSectionTwoColumnsItem1.Name = "setSectionTwoColumnsItem1";
            // 
            // setSectionThreeColumnsItem1
            // 
            this.setSectionThreeColumnsItem1.Id = 204;
            this.setSectionThreeColumnsItem1.Name = "setSectionThreeColumnsItem1";
            // 
            // showColumnsSetupFormItem1
            // 
            this.showColumnsSetupFormItem1.Id = 205;
            this.showColumnsSetupFormItem1.Name = "showColumnsSetupFormItem1";
            // 
            // insertBreakItem1
            // 
            this.insertBreakItem1.Id = 206;
            this.insertBreakItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.insertPageBreakItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertColumnBreakItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertSectionBreakNextPageItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertSectionBreakEvenPageItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.insertSectionBreakOddPageItem1)});
            this.insertBreakItem1.Name = "insertBreakItem1";
            // 
            // insertPageBreakItem1
            // 
            this.insertPageBreakItem1.Id = 207;
            this.insertPageBreakItem1.Name = "insertPageBreakItem1";
            // 
            // insertColumnBreakItem1
            // 
            this.insertColumnBreakItem1.Id = 208;
            this.insertColumnBreakItem1.Name = "insertColumnBreakItem1";
            // 
            // insertSectionBreakNextPageItem1
            // 
            this.insertSectionBreakNextPageItem1.Id = 209;
            this.insertSectionBreakNextPageItem1.Name = "insertSectionBreakNextPageItem1";
            // 
            // insertSectionBreakEvenPageItem1
            // 
            this.insertSectionBreakEvenPageItem1.Id = 210;
            this.insertSectionBreakEvenPageItem1.Name = "insertSectionBreakEvenPageItem1";
            // 
            // insertSectionBreakOddPageItem1
            // 
            this.insertSectionBreakOddPageItem1.Id = 211;
            this.insertSectionBreakOddPageItem1.Name = "insertSectionBreakOddPageItem1";
            // 
            // changeSectionLineNumberingItem1
            // 
            this.changeSectionLineNumberingItem1.Id = 212;
            this.changeSectionLineNumberingItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionLineNumberingNoneItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionLineNumberingContinuousItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionLineNumberingRestartNewPageItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSectionLineNumberingRestartNewSectionItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleParagraphSuppressLineNumbersItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.showLineNumberingFormItem1, true)});
            this.changeSectionLineNumberingItem1.Name = "changeSectionLineNumberingItem1";
            // 
            // setSectionLineNumberingNoneItem1
            // 
            this.setSectionLineNumberingNoneItem1.Id = 213;
            this.setSectionLineNumberingNoneItem1.Name = "setSectionLineNumberingNoneItem1";
            // 
            // setSectionLineNumberingContinuousItem1
            // 
            this.setSectionLineNumberingContinuousItem1.Id = 214;
            this.setSectionLineNumberingContinuousItem1.Name = "setSectionLineNumberingContinuousItem1";
            // 
            // setSectionLineNumberingRestartNewPageItem1
            // 
            this.setSectionLineNumberingRestartNewPageItem1.Id = 215;
            this.setSectionLineNumberingRestartNewPageItem1.Name = "setSectionLineNumberingRestartNewPageItem1";
            // 
            // setSectionLineNumberingRestartNewSectionItem1
            // 
            this.setSectionLineNumberingRestartNewSectionItem1.Id = 216;
            this.setSectionLineNumberingRestartNewSectionItem1.Name = "setSectionLineNumberingRestartNewSectionItem1";
            // 
            // toggleParagraphSuppressLineNumbersItem1
            // 
            this.toggleParagraphSuppressLineNumbersItem1.Id = 217;
            this.toggleParagraphSuppressLineNumbersItem1.Name = "toggleParagraphSuppressLineNumbersItem1";
            // 
            // showLineNumberingFormItem1
            // 
            this.showLineNumberingFormItem1.Id = 218;
            this.showLineNumberingFormItem1.Name = "showLineNumberingFormItem1";
            // 
            // changePageColorItem1
            // 
            this.changePageColorItem1.Id = 219;
            this.changePageColorItem1.Name = "changePageColorItem1";
            // 
            // insertTableItem1
            // 
            this.insertTableItem1.Id = 221;
            this.insertTableItem1.Name = "insertTableItem1";
            // 
            // insertPictureItem1
            // 
            this.insertPictureItem1.Id = 222;
            this.insertPictureItem1.Name = "insertPictureItem1";
            // 
            // insertFloatingPictureItem1
            // 
            this.insertFloatingPictureItem1.Id = 223;
            this.insertFloatingPictureItem1.Name = "insertFloatingPictureItem1";
            // 
            // insertBookmarkItem1
            // 
            this.insertBookmarkItem1.Id = 224;
            this.insertBookmarkItem1.Name = "insertBookmarkItem1";
            // 
            // insertHyperlinkItem1
            // 
            this.insertHyperlinkItem1.Id = 225;
            this.insertHyperlinkItem1.Name = "insertHyperlinkItem1";
            // 
            // editPageHeaderItem1
            // 
            this.editPageHeaderItem1.Id = 226;
            this.editPageHeaderItem1.Name = "editPageHeaderItem1";
            // 
            // editPageFooterItem1
            // 
            this.editPageFooterItem1.Id = 227;
            this.editPageFooterItem1.Name = "editPageFooterItem1";
            // 
            // insertPageNumberItem1
            // 
            this.insertPageNumberItem1.Id = 228;
            this.insertPageNumberItem1.Name = "insertPageNumberItem1";
            // 
            // insertPageCountItem1
            // 
            this.insertPageCountItem1.Id = 229;
            this.insertPageCountItem1.Name = "insertPageCountItem1";
            // 
            // insertTextBoxItem1
            // 
            this.insertTextBoxItem1.Id = 230;
            this.insertTextBoxItem1.Name = "insertTextBoxItem1";
            // 
            // insertSymbolItem1
            // 
            this.insertSymbolItem1.Id = 231;
            this.insertSymbolItem1.Name = "insertSymbolItem1";
            // 
            // pasteItem1
            // 
            this.pasteItem1.Id = 239;
            this.pasteItem1.Name = "pasteItem1";
            // 
            // cutItem1
            // 
            this.cutItem1.Id = 240;
            this.cutItem1.Name = "cutItem1";
            // 
            // copyItem1
            // 
            this.copyItem1.Id = 241;
            this.copyItem1.Name = "copyItem1";
            // 
            // pasteSpecialItem1
            // 
            this.pasteSpecialItem1.Id = 242;
            this.pasteSpecialItem1.Name = "pasteSpecialItem1";
            // 
            // barButtonGroup1
            // 
            this.barButtonGroup1.Id = 232;
            this.barButtonGroup1.ItemLinks.Add(this.changeFontNameItem1);
            this.barButtonGroup1.ItemLinks.Add(this.changeFontSizeItem1);
            this.barButtonGroup1.ItemLinks.Add(this.fontSizeIncreaseItem1);
            this.barButtonGroup1.ItemLinks.Add(this.fontSizeDecreaseItem1);
            this.barButtonGroup1.Name = "barButtonGroup1";
            this.barButtonGroup1.Tag = "{97BBE334-159B-44d9-A168-0411957565E8}";
            // 
            // changeFontNameItem1
            // 
            this.changeFontNameItem1.Edit = this.repositoryItemFontEdit1;
            this.changeFontNameItem1.Id = 243;
            this.changeFontNameItem1.Name = "changeFontNameItem1";
            // 
            // repositoryItemFontEdit1
            // 
            this.repositoryItemFontEdit1.AutoHeight = false;
            this.repositoryItemFontEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemFontEdit1.Name = "repositoryItemFontEdit1";
            // 
            // changeFontSizeItem1
            // 
            this.changeFontSizeItem1.Edit = this.repositoryItemRichEditFontSizeEdit1;
            this.changeFontSizeItem1.Id = 244;
            this.changeFontSizeItem1.Name = "changeFontSizeItem1";
            // 
            // repositoryItemRichEditFontSizeEdit1
            // 
            this.repositoryItemRichEditFontSizeEdit1.AutoHeight = false;
            this.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemRichEditFontSizeEdit1.Control = this.richEditControl;
            this.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1";
            // 
            // fontSizeIncreaseItem1
            // 
            this.fontSizeIncreaseItem1.Id = 245;
            this.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1";
            // 
            // fontSizeDecreaseItem1
            // 
            this.fontSizeDecreaseItem1.Id = 246;
            this.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1";
            // 
            // barButtonGroup2
            // 
            this.barButtonGroup2.Id = 233;
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontBoldItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontItalicItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontUnderlineItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontDoubleUnderlineItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontStrikeoutItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontDoubleStrikeoutItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontSuperscriptItem1);
            this.barButtonGroup2.ItemLinks.Add(this.toggleFontSubscriptItem1);
            this.barButtonGroup2.Name = "barButtonGroup2";
            this.barButtonGroup2.Tag = "{433DA7F0-03E2-4650-9DB5-66DD92D16E39}";
            // 
            // toggleFontBoldItem1
            // 
            this.toggleFontBoldItem1.Id = 247;
            this.toggleFontBoldItem1.Name = "toggleFontBoldItem1";
            // 
            // toggleFontItalicItem1
            // 
            this.toggleFontItalicItem1.Id = 248;
            this.toggleFontItalicItem1.Name = "toggleFontItalicItem1";
            // 
            // toggleFontUnderlineItem1
            // 
            this.toggleFontUnderlineItem1.Id = 249;
            this.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1";
            // 
            // toggleFontDoubleUnderlineItem1
            // 
            this.toggleFontDoubleUnderlineItem1.Id = 250;
            this.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1";
            // 
            // toggleFontStrikeoutItem1
            // 
            this.toggleFontStrikeoutItem1.Id = 251;
            this.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1";
            // 
            // toggleFontDoubleStrikeoutItem1
            // 
            this.toggleFontDoubleStrikeoutItem1.Id = 252;
            this.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1";
            // 
            // toggleFontSuperscriptItem1
            // 
            this.toggleFontSuperscriptItem1.Id = 253;
            this.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1";
            // 
            // toggleFontSubscriptItem1
            // 
            this.toggleFontSubscriptItem1.Id = 254;
            this.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1";
            // 
            // barButtonGroup3
            // 
            this.barButtonGroup3.Id = 234;
            this.barButtonGroup3.ItemLinks.Add(this.changeFontColorItem1);
            this.barButtonGroup3.ItemLinks.Add(this.changeFontBackColorItem1);
            this.barButtonGroup3.Name = "barButtonGroup3";
            this.barButtonGroup3.Tag = "{DF8C5334-EDE3-47c9-A42C-FE9A9247E180}";
            // 
            // changeFontColorItem1
            // 
            this.changeFontColorItem1.Id = 255;
            this.changeFontColorItem1.Name = "changeFontColorItem1";
            // 
            // changeFontBackColorItem1
            // 
            this.changeFontBackColorItem1.Id = 256;
            this.changeFontBackColorItem1.Name = "changeFontBackColorItem1";
            // 
            // changeTextCaseItem1
            // 
            this.changeTextCaseItem1.Id = 257;
            this.changeTextCaseItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.makeTextUpperCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.makeTextLowerCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.capitalizeEachWordCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTextCaseItem1)});
            this.changeTextCaseItem1.Name = "changeTextCaseItem1";
            // 
            // makeTextUpperCaseItem1
            // 
            this.makeTextUpperCaseItem1.Id = 258;
            this.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1";
            // 
            // makeTextLowerCaseItem1
            // 
            this.makeTextLowerCaseItem1.Id = 259;
            this.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1";
            // 
            // capitalizeEachWordCaseItem1
            // 
            this.capitalizeEachWordCaseItem1.Id = 260;
            this.capitalizeEachWordCaseItem1.Name = "capitalizeEachWordCaseItem1";
            // 
            // toggleTextCaseItem1
            // 
            this.toggleTextCaseItem1.Id = 261;
            this.toggleTextCaseItem1.Name = "toggleTextCaseItem1";
            // 
            // clearFormattingItem1
            // 
            this.clearFormattingItem1.Id = 262;
            this.clearFormattingItem1.Name = "clearFormattingItem1";
            // 
            // barButtonGroup4
            // 
            this.barButtonGroup4.Id = 235;
            this.barButtonGroup4.ItemLinks.Add(this.toggleBulletedListItem1);
            this.barButtonGroup4.ItemLinks.Add(this.toggleNumberingListItem1);
            this.barButtonGroup4.ItemLinks.Add(this.toggleMultiLevelListItem1);
            this.barButtonGroup4.Name = "barButtonGroup4";
            this.barButtonGroup4.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}";
            // 
            // toggleBulletedListItem1
            // 
            this.toggleBulletedListItem1.Id = 263;
            this.toggleBulletedListItem1.Name = "toggleBulletedListItem1";
            // 
            // toggleNumberingListItem1
            // 
            this.toggleNumberingListItem1.Id = 264;
            this.toggleNumberingListItem1.Name = "toggleNumberingListItem1";
            // 
            // toggleMultiLevelListItem1
            // 
            this.toggleMultiLevelListItem1.Id = 265;
            this.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1";
            // 
            // barButtonGroup5
            // 
            this.barButtonGroup5.Id = 236;
            this.barButtonGroup5.ItemLinks.Add(this.decreaseIndentItem1);
            this.barButtonGroup5.ItemLinks.Add(this.increaseIndentItem1);
            this.barButtonGroup5.ItemLinks.Add(this.toggleShowWhitespaceItem1);
            this.barButtonGroup5.Name = "barButtonGroup5";
            this.barButtonGroup5.Tag = "{4747D5AB-2BEB-4ea6-9A1D-8E4FB36F1B40}";
            // 
            // decreaseIndentItem1
            // 
            this.decreaseIndentItem1.Id = 266;
            this.decreaseIndentItem1.Name = "decreaseIndentItem1";
            // 
            // increaseIndentItem1
            // 
            this.increaseIndentItem1.Id = 267;
            this.increaseIndentItem1.Name = "increaseIndentItem1";
            // 
            // toggleShowWhitespaceItem1
            // 
            this.toggleShowWhitespaceItem1.Id = 272;
            this.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1";
            // 
            // barButtonGroup6
            // 
            this.barButtonGroup6.Id = 237;
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentLeftItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentCenterItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentRightItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentJustifyItem1);
            this.barButtonGroup6.Name = "barButtonGroup6";
            this.barButtonGroup6.Tag = "{8E89E775-996E-49a0-AADA-DE338E34732E}";
            // 
            // toggleParagraphAlignmentLeftItem1
            // 
            this.toggleParagraphAlignmentLeftItem1.Id = 268;
            this.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1";
            // 
            // toggleParagraphAlignmentCenterItem1
            // 
            this.toggleParagraphAlignmentCenterItem1.Id = 269;
            this.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1";
            // 
            // toggleParagraphAlignmentRightItem1
            // 
            this.toggleParagraphAlignmentRightItem1.Id = 270;
            this.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1";
            // 
            // toggleParagraphAlignmentJustifyItem1
            // 
            this.toggleParagraphAlignmentJustifyItem1.Id = 271;
            this.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1";
            // 
            // barButtonGroup7
            // 
            this.barButtonGroup7.Id = 238;
            this.barButtonGroup7.ItemLinks.Add(this.changeParagraphLineSpacingItem1);
            this.barButtonGroup7.ItemLinks.Add(this.changeParagraphBackColorItem1);
            this.barButtonGroup7.Name = "barButtonGroup7";
            this.barButtonGroup7.Tag = "{9A8DEAD8-3890-4857-A395-EC625FD02217}";
            // 
            // changeParagraphLineSpacingItem1
            // 
            this.changeParagraphLineSpacingItem1.Id = 273;
            this.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.setSingleParagraphSpacingItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setSesquialteralParagraphSpacingItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.setDoubleParagraphSpacingItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.showLineSpacingFormItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.addSpacingBeforeParagraphItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.removeSpacingBeforeParagraphItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.addSpacingAfterParagraphItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.removeSpacingAfterParagraphItem1)});
            this.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1";
            // 
            // setSingleParagraphSpacingItem1
            // 
            this.setSingleParagraphSpacingItem1.Id = 274;
            this.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1";
            // 
            // setSesquialteralParagraphSpacingItem1
            // 
            this.setSesquialteralParagraphSpacingItem1.Id = 275;
            this.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1";
            // 
            // setDoubleParagraphSpacingItem1
            // 
            this.setDoubleParagraphSpacingItem1.Id = 276;
            this.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1";
            // 
            // showLineSpacingFormItem1
            // 
            this.showLineSpacingFormItem1.Id = 277;
            this.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1";
            // 
            // addSpacingBeforeParagraphItem1
            // 
            this.addSpacingBeforeParagraphItem1.Id = 278;
            this.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1";
            // 
            // removeSpacingBeforeParagraphItem1
            // 
            this.removeSpacingBeforeParagraphItem1.Id = 279;
            this.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1";
            // 
            // addSpacingAfterParagraphItem1
            // 
            this.addSpacingAfterParagraphItem1.Id = 280;
            this.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1";
            // 
            // removeSpacingAfterParagraphItem1
            // 
            this.removeSpacingAfterParagraphItem1.Id = 281;
            this.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1";
            // 
            // changeParagraphBackColorItem1
            // 
            this.changeParagraphBackColorItem1.Id = 282;
            this.changeParagraphBackColorItem1.Name = "changeParagraphBackColorItem1";
            // 
            // findItem1
            // 
            this.findItem1.Id = 284;
            this.findItem1.Name = "findItem1";
            // 
            // replaceItem1
            // 
            this.replaceItem1.Id = 285;
            this.replaceItem1.Name = "replaceItem1";
            // 
            // undoItem1
            // 
            this.undoItem1.Id = 286;
            this.undoItem1.Name = "undoItem1";
            // 
            // redoItem1
            // 
            this.redoItem1.Id = 287;
            this.redoItem1.Name = "redoItem1";
            // 
            // fileNewItem1
            // 
            this.fileNewItem1.Id = 288;
            this.fileNewItem1.Name = "fileNewItem1";
            // 
            // fileOpenItem1
            // 
            this.fileOpenItem1.Id = 289;
            this.fileOpenItem1.Name = "fileOpenItem1";
            // 
            // fileSaveItem1
            // 
            this.fileSaveItem1.Id = 290;
            this.fileSaveItem1.Name = "fileSaveItem1";
            // 
            // fileSaveAsItem1
            // 
            this.fileSaveAsItem1.Id = 291;
            this.fileSaveAsItem1.Name = "fileSaveAsItem1";
            // 
            // quickPrintItem1
            // 
            this.quickPrintItem1.Id = 292;
            this.quickPrintItem1.Name = "quickPrintItem1";
            // 
            // printItem1
            // 
            this.printItem1.Id = 293;
            this.printItem1.Name = "printItem1";
            // 
            // printPreviewItem1
            // 
            this.printPreviewItem1.Id = 294;
            this.printPreviewItem1.Name = "printPreviewItem1";
            // 
            // barEditItem1
            // 
            this.barEditItem1.Caption = "barEditItem1";
            this.barEditItem1.Edit = this.repositoryItemColorPickEdit1;
            this.barEditItem1.Id = 297;
            this.barEditItem1.Name = "barEditItem1";
            // 
            // repositoryItemColorPickEdit1
            // 
            this.repositoryItemColorPickEdit1.AutoHeight = false;
            this.repositoryItemColorPickEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemColorPickEdit1.Name = "repositoryItemColorPickEdit1";
            // 
            // barCheckItem1
            // 
            this.barCheckItem1.Caption = "Format Painter";
            this.barCheckItem1.Glyph = ((System.Drawing.Image)(resources.GetObject("barCheckItem1.Glyph")));
            this.barCheckItem1.Id = 298;
            this.barCheckItem1.LargeGlyph = ((System.Drawing.Image)(resources.GetObject("barCheckItem1.LargeGlyph")));
            this.barCheckItem1.Name = "barCheckItem1";
            this.barCheckItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText;
            this.barCheckItem1.CheckedChanged += new DevExpress.XtraBars.ItemClickEventHandler(this.barCheckItem1_CheckedChanged);
            // 
            // ribbonImageCollectionLarge
            // 
            this.ribbonImageCollectionLarge.ImageSize = new System.Drawing.Size(32, 32);
            this.ribbonImageCollectionLarge.ImageStream = ((DevExpress.Utils.ImageCollectionStreamer)(resources.GetObject("ribbonImageCollectionLarge.ImageStream")));
            this.ribbonImageCollectionLarge.Images.SetKeyName(0, "Ribbon_Exit_32x32.png");
            this.ribbonImageCollectionLarge.Images.SetKeyName(1, "Ribbon_Content_32x32.png");
            this.ribbonImageCollectionLarge.Images.SetKeyName(2, "Ribbon_Info_32x32.png");
            // 
            // floatingPictureToolsRibbonPageCategory1
            // 
            this.floatingPictureToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb(((int)(((byte)(201)))), ((int)(((byte)(0)))), ((int)(((byte)(119)))));
            this.floatingPictureToolsRibbonPageCategory1.Control = this.richEditControl;
            this.floatingPictureToolsRibbonPageCategory1.Name = "floatingPictureToolsRibbonPageCategory1";
            this.floatingPictureToolsRibbonPageCategory1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.floatingPictureToolsFormatPage1});
            // 
            // floatingPictureToolsFormatPage1
            // 
            this.floatingPictureToolsFormatPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.floatingPictureToolsShapeStylesPageGroup1,
            this.floatingPictureToolsArrangePageGroup1});
            this.floatingPictureToolsFormatPage1.Name = "floatingPictureToolsFormatPage1";
            // 
            // floatingPictureToolsShapeStylesPageGroup1
            // 
            this.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(this.changeFloatingObjectFillColorItem1);
            this.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(this.changeFloatingObjectOutlineColorItem1);
            this.floatingPictureToolsShapeStylesPageGroup1.ItemLinks.Add(this.changeFloatingObjectOutlineWeightItem1);
            this.floatingPictureToolsShapeStylesPageGroup1.Name = "floatingPictureToolsShapeStylesPageGroup1";
            // 
            // floatingPictureToolsArrangePageGroup1
            // 
            this.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(this.changeFloatingObjectTextWrapTypeItem1);
            this.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(this.changeFloatingObjectAlignmentItem1);
            this.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(this.floatingObjectBringForwardSubItem1);
            this.floatingPictureToolsArrangePageGroup1.ItemLinks.Add(this.floatingObjectSendBackwardSubItem1);
            this.floatingPictureToolsArrangePageGroup1.Name = "floatingPictureToolsArrangePageGroup1";
            // 
            // tableToolsRibbonPageCategory1
            // 
            this.tableToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb(((int)(((byte)(252)))), ((int)(((byte)(233)))), ((int)(((byte)(20)))));
            this.tableToolsRibbonPageCategory1.Control = this.richEditControl;
            this.tableToolsRibbonPageCategory1.Name = "tableToolsRibbonPageCategory1";
            this.tableToolsRibbonPageCategory1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.tableLayoutRibbonPage1,
            this.tableDesignRibbonPage1});
            // 
            // tableLayoutRibbonPage1
            // 
            this.tableLayoutRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.tableTableRibbonPageGroup1,
            this.tableRowsAndColumnsRibbonPageGroup1,
            this.tableMergeRibbonPageGroup1,
            this.tableCellSizeRibbonPageGroup1,
            this.tableAlignmentRibbonPageGroup1});
            this.tableLayoutRibbonPage1.Name = "tableLayoutRibbonPage1";
            // 
            // tableTableRibbonPageGroup1
            // 
            this.tableTableRibbonPageGroup1.ItemLinks.Add(this.selectTableElementsItem1);
            this.tableTableRibbonPageGroup1.ItemLinks.Add(this.toggleShowTableGridLinesItem1);
            this.tableTableRibbonPageGroup1.ItemLinks.Add(this.showTablePropertiesFormItem1);
            this.tableTableRibbonPageGroup1.Name = "tableTableRibbonPageGroup1";
            // 
            // tableRowsAndColumnsRibbonPageGroup1
            // 
            this.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(this.deleteTableElementsItem1);
            this.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(this.insertTableRowAboveItem1);
            this.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(this.insertTableRowBelowItem1);
            this.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(this.insertTableColumnToLeftItem1);
            this.tableRowsAndColumnsRibbonPageGroup1.ItemLinks.Add(this.insertTableColumnToRightItem1);
            this.tableRowsAndColumnsRibbonPageGroup1.Name = "tableRowsAndColumnsRibbonPageGroup1";
            // 
            // tableMergeRibbonPageGroup1
            // 
            this.tableMergeRibbonPageGroup1.ItemLinks.Add(this.mergeTableCellsItem1);
            this.tableMergeRibbonPageGroup1.ItemLinks.Add(this.showSplitTableCellsForm1);
            this.tableMergeRibbonPageGroup1.ItemLinks.Add(this.splitTableItem1);
            this.tableMergeRibbonPageGroup1.Name = "tableMergeRibbonPageGroup1";
            // 
            // tableCellSizeRibbonPageGroup1
            // 
            this.tableCellSizeRibbonPageGroup1.AllowTextClipping = false;
            this.tableCellSizeRibbonPageGroup1.ItemLinks.Add(this.toggleTableAutoFitItem1);
            this.tableCellSizeRibbonPageGroup1.Name = "tableCellSizeRibbonPageGroup1";
            // 
            // tableAlignmentRibbonPageGroup1
            // 
            this.tableAlignmentRibbonPageGroup1.Glyph = ((System.Drawing.Image)(resources.GetObject("tableAlignmentRibbonPageGroup1.Glyph")));
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsTopLeftAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsMiddleLeftAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsBottomLeftAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsTopCenterAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsMiddleCenterAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsBottomCenterAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsTopRightAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsMiddleRightAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.toggleTableCellsBottomRightAlignmentItem1);
            this.tableAlignmentRibbonPageGroup1.ItemLinks.Add(this.showTableOptionsFormItem1);
            this.tableAlignmentRibbonPageGroup1.Name = "tableAlignmentRibbonPageGroup1";
            // 
            // tableDesignRibbonPage1
            // 
            this.tableDesignRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.tableStyleOptionsRibbonPageGroup1,
            this.tableStylesRibbonPageGroup1,
            this.tableDrawBordersRibbonPageGroup1});
            this.tableDesignRibbonPage1.Name = "tableDesignRibbonPage1";
            // 
            // tableStyleOptionsRibbonPageGroup1
            // 
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleFirstRowItem1);
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleLastRowItem1);
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleBandedRowsItem1);
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleFirstColumnItem1);
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleLastColumnItem1);
            this.tableStyleOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleBandedColumnItem1);
            this.tableStyleOptionsRibbonPageGroup1.Name = "tableStyleOptionsRibbonPageGroup1";
            // 
            // tableStylesRibbonPageGroup1
            // 
            this.tableStylesRibbonPageGroup1.ItemLinks.Add(this.galleryChangeTableStyleItem1);
            this.tableStylesRibbonPageGroup1.Name = "tableStylesRibbonPageGroup1";
            // 
            // tableDrawBordersRibbonPageGroup1
            // 
            this.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(this.changeTableBorderLineStyleItem1);
            this.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(this.changeTableBorderLineWeightItem1);
            this.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(this.changeTableBorderColorItem1);
            this.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(this.changeTableBordersItem1);
            this.tableDrawBordersRibbonPageGroup1.ItemLinks.Add(this.changeTableCellsShadingItem1);
            this.tableDrawBordersRibbonPageGroup1.Name = "tableDrawBordersRibbonPageGroup1";
            // 
            // headerFooterToolsRibbonPageCategory1
            // 
            this.headerFooterToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb(((int)(((byte)(38)))), ((int)(((byte)(176)))), ((int)(((byte)(35)))));
            this.headerFooterToolsRibbonPageCategory1.Control = this.richEditControl;
            this.headerFooterToolsRibbonPageCategory1.Name = "headerFooterToolsRibbonPageCategory1";
            this.headerFooterToolsRibbonPageCategory1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.headerFooterToolsDesignRibbonPage1});
            // 
            // headerFooterToolsDesignRibbonPage1
            // 
            this.headerFooterToolsDesignRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.headerFooterToolsDesignNavigationRibbonPageGroup1,
            this.headerFooterToolsDesignOptionsRibbonPageGroup1,
            this.headerFooterToolsDesignCloseRibbonPageGroup1});
            this.headerFooterToolsDesignRibbonPage1.Name = "headerFooterToolsDesignRibbonPage1";
            // 
            // headerFooterToolsDesignNavigationRibbonPageGroup1
            // 
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(this.goToPageHeaderItem1);
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(this.goToPageFooterItem1);
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(this.goToNextHeaderFooterItem1);
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(this.goToPreviousHeaderFooterItem1);
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.ItemLinks.Add(this.toggleLinkToPreviousItem1);
            this.headerFooterToolsDesignNavigationRibbonPageGroup1.Name = "headerFooterToolsDesignNavigationRibbonPageGroup1";
            // 
            // headerFooterToolsDesignOptionsRibbonPageGroup1
            // 
            this.headerFooterToolsDesignOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleDifferentFirstPageItem1);
            this.headerFooterToolsDesignOptionsRibbonPageGroup1.ItemLinks.Add(this.toggleDifferentOddAndEvenPagesItem1);
            this.headerFooterToolsDesignOptionsRibbonPageGroup1.Name = "headerFooterToolsDesignOptionsRibbonPageGroup1";
            // 
            // headerFooterToolsDesignCloseRibbonPageGroup1
            // 
            this.headerFooterToolsDesignCloseRibbonPageGroup1.ItemLinks.Add(this.closePageHeaderFooterItem1);
            this.headerFooterToolsDesignCloseRibbonPageGroup1.Name = "headerFooterToolsDesignCloseRibbonPageGroup1";
            // 
            // fileRibbonPage1
            // 
            this.fileRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.commonRibbonPageGroup1});
            this.fileRibbonPage1.Name = "fileRibbonPage1";
            // 
            // commonRibbonPageGroup1
            // 
            this.commonRibbonPageGroup1.ItemLinks.Add(this.undoItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.redoItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.fileNewItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.fileOpenItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.fileSaveItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.fileSaveAsItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.quickPrintItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.printItem1);
            this.commonRibbonPageGroup1.ItemLinks.Add(this.printPreviewItem1);
            this.commonRibbonPageGroup1.Name = "commonRibbonPageGroup1";
            // 
            // homeRibbonPage1
            // 
            this.homeRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.clipboardRibbonPageGroup1,
            this.fontRibbonPageGroup1,
            this.paragraphRibbonPageGroup1,
            this.stylesRibbonPageGroup1,
            this.editingRibbonPageGroup1});
            this.homeRibbonPage1.Name = "homeRibbonPage1";
            reduceOperation1.Behavior = DevExpress.XtraBars.Ribbon.ReduceOperationBehavior.UntilAvailable;
            reduceOperation1.Group = this.stylesRibbonPageGroup1;
            reduceOperation1.ItemLinkIndex = 0;
            reduceOperation1.ItemLinksCount = 0;
            reduceOperation1.Operation = DevExpress.XtraBars.Ribbon.ReduceOperationType.Gallery;
            this.homeRibbonPage1.ReduceOperations.Add(reduceOperation1);
            // 
            // clipboardRibbonPageGroup1
            // 
            this.clipboardRibbonPageGroup1.ItemLinks.Add(this.pasteItem1);
            this.clipboardRibbonPageGroup1.ItemLinks.Add(this.cutItem1);
            this.clipboardRibbonPageGroup1.ItemLinks.Add(this.copyItem1);
            this.clipboardRibbonPageGroup1.ItemLinks.Add(this.pasteSpecialItem1);
            this.clipboardRibbonPageGroup1.ItemLinks.Add(this.barCheckItem1);
            this.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1";
            // 
            // fontRibbonPageGroup1
            // 
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup1);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup2);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup3);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.changeTextCaseItem1);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.clearFormattingItem1);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barEditItem1);
            this.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1";
            // 
            // paragraphRibbonPageGroup1
            // 
            this.paragraphRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup4);
            this.paragraphRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup5);
            this.paragraphRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup6);
            this.paragraphRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup7);
            this.paragraphRibbonPageGroup1.Name = "paragraphRibbonPageGroup1";
            // 
            // editingRibbonPageGroup1
            // 
            this.editingRibbonPageGroup1.ItemLinks.Add(this.findItem1);
            this.editingRibbonPageGroup1.ItemLinks.Add(this.replaceItem1);
            this.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1";
            // 
            // insertRibbonPage1
            // 
            this.insertRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.pagesRibbonPageGroup1,
            this.tablesRibbonPageGroup1,
            this.illustrationsRibbonPageGroup1,
            this.linksRibbonPageGroup1,
            this.headerFooterRibbonPageGroup1,
            this.textRibbonPageGroup1,
            this.symbolsRibbonPageGroup1});
            this.insertRibbonPage1.Name = "insertRibbonPage1";
            // 
            // pagesRibbonPageGroup1
            // 
            this.pagesRibbonPageGroup1.AllowTextClipping = false;
            this.pagesRibbonPageGroup1.Name = "pagesRibbonPageGroup1";
            this.pagesRibbonPageGroup1.Text = "";
            // 
            // tablesRibbonPageGroup1
            // 
            this.tablesRibbonPageGroup1.AllowTextClipping = false;
            this.tablesRibbonPageGroup1.ItemLinks.Add(this.insertTableItem1);
            this.tablesRibbonPageGroup1.Name = "tablesRibbonPageGroup1";
            // 
            // illustrationsRibbonPageGroup1
            // 
            this.illustrationsRibbonPageGroup1.ItemLinks.Add(this.insertPictureItem1);
            this.illustrationsRibbonPageGroup1.ItemLinks.Add(this.insertFloatingPictureItem1);
            this.illustrationsRibbonPageGroup1.Name = "illustrationsRibbonPageGroup1";
            // 
            // linksRibbonPageGroup1
            // 
            this.linksRibbonPageGroup1.ItemLinks.Add(this.insertBookmarkItem1);
            this.linksRibbonPageGroup1.ItemLinks.Add(this.insertHyperlinkItem1);
            this.linksRibbonPageGroup1.Name = "linksRibbonPageGroup1";
            // 
            // headerFooterRibbonPageGroup1
            // 
            this.headerFooterRibbonPageGroup1.ItemLinks.Add(this.editPageHeaderItem1);
            this.headerFooterRibbonPageGroup1.ItemLinks.Add(this.editPageFooterItem1);
            this.headerFooterRibbonPageGroup1.ItemLinks.Add(this.insertPageNumberItem1);
            this.headerFooterRibbonPageGroup1.ItemLinks.Add(this.insertPageCountItem1);
            this.headerFooterRibbonPageGroup1.Name = "headerFooterRibbonPageGroup1";
            // 
            // textRibbonPageGroup1
            // 
            this.textRibbonPageGroup1.Glyph = ((System.Drawing.Image)(resources.GetObject("textRibbonPageGroup1.Glyph")));
            this.textRibbonPageGroup1.ItemLinks.Add(this.insertTextBoxItem1);
            this.textRibbonPageGroup1.Name = "textRibbonPageGroup1";
            // 
            // symbolsRibbonPageGroup1
            // 
            this.symbolsRibbonPageGroup1.AllowTextClipping = false;
            this.symbolsRibbonPageGroup1.ItemLinks.Add(this.insertSymbolItem1);
            this.symbolsRibbonPageGroup1.Name = "symbolsRibbonPageGroup1";
            // 
            // pageLayoutRibbonPage1
            // 
            this.pageLayoutRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.pageSetupRibbonPageGroup1,
            this.pageBackgroundRibbonPageGroup1});
            this.pageLayoutRibbonPage1.Name = "pageLayoutRibbonPage1";
            // 
            // pageSetupRibbonPageGroup1
            // 
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.changeSectionPageMarginsItem1);
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.changeSectionPageOrientationItem1);
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.changeSectionPaperKindItem1);
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.changeSectionColumnsItem1);
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.insertBreakItem1);
            this.pageSetupRibbonPageGroup1.ItemLinks.Add(this.changeSectionLineNumberingItem1);
            this.pageSetupRibbonPageGroup1.Name = "pageSetupRibbonPageGroup1";
            // 
            // pageBackgroundRibbonPageGroup1
            // 
            this.pageBackgroundRibbonPageGroup1.AllowTextClipping = false;
            this.pageBackgroundRibbonPageGroup1.ItemLinks.Add(this.changePageColorItem1);
            this.pageBackgroundRibbonPageGroup1.Name = "pageBackgroundRibbonPageGroup1";
            // 
            // referencesRibbonPage1
            // 
            this.referencesRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.tableOfContentsRibbonPageGroup1,
            this.captionsRibbonPageGroup1});
            this.referencesRibbonPage1.Name = "referencesRibbonPage1";
            // 
            // tableOfContentsRibbonPageGroup1
            // 
            this.tableOfContentsRibbonPageGroup1.ItemLinks.Add(this.insertTableOfContentsItem1);
            this.tableOfContentsRibbonPageGroup1.ItemLinks.Add(this.updateTableOfContentsItem1);
            this.tableOfContentsRibbonPageGroup1.ItemLinks.Add(this.addParagraphsToTableOfContentItem1);
            this.tableOfContentsRibbonPageGroup1.Name = "tableOfContentsRibbonPageGroup1";
            // 
            // captionsRibbonPageGroup1
            // 
            this.captionsRibbonPageGroup1.ItemLinks.Add(this.insertCaptionPlaceholderItem1);
            this.captionsRibbonPageGroup1.ItemLinks.Add(this.insertTableOfFiguresPlaceholderItem1);
            this.captionsRibbonPageGroup1.ItemLinks.Add(this.updateTableOfFiguresItem1);
            this.captionsRibbonPageGroup1.Name = "captionsRibbonPageGroup1";
            // 
            // mailingsRibbonPage1
            // 
            this.mailingsRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.mailMergeRibbonPageGroup1});
            this.mailingsRibbonPage1.Name = "mailingsRibbonPage1";
            // 
            // mailMergeRibbonPageGroup1
            // 
            this.mailMergeRibbonPageGroup1.ItemLinks.Add(this.insertMergeFieldItem1);
            this.mailMergeRibbonPageGroup1.ItemLinks.Add(this.showAllFieldCodesItem1);
            this.mailMergeRibbonPageGroup1.ItemLinks.Add(this.showAllFieldResultsItem1);
            this.mailMergeRibbonPageGroup1.ItemLinks.Add(this.toggleViewMergedDataItem1);
            this.mailMergeRibbonPageGroup1.Name = "mailMergeRibbonPageGroup1";
            // 
            // reviewRibbonPage1
            // 
            this.reviewRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.documentProofingRibbonPageGroup1,
            this.documentProtectionRibbonPageGroup1});
            this.reviewRibbonPage1.Name = "reviewRibbonPage1";
            // 
            // documentProofingRibbonPageGroup1
            // 
            this.documentProofingRibbonPageGroup1.ItemLinks.Add(this.checkSpellingItem1);
            this.documentProofingRibbonPageGroup1.ItemLinks.Add(this.changeLanguageItem1);
            this.documentProofingRibbonPageGroup1.Name = "documentProofingRibbonPageGroup1";
            // 
            // documentProtectionRibbonPageGroup1
            // 
            this.documentProtectionRibbonPageGroup1.ItemLinks.Add(this.protectDocumentItem1);
            this.documentProtectionRibbonPageGroup1.ItemLinks.Add(this.changeRangeEditingPermissionsItem1);
            this.documentProtectionRibbonPageGroup1.ItemLinks.Add(this.unprotectDocumentItem1);
            this.documentProtectionRibbonPageGroup1.Name = "documentProtectionRibbonPageGroup1";
            // 
            // viewRibbonPage1
            // 
            this.viewRibbonPage1.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.documentViewsRibbonPageGroup1,
            this.showRibbonPageGroup1,
            this.zoomRibbonPageGroup1});
            this.viewRibbonPage1.Name = "viewRibbonPage1";
            // 
            // documentViewsRibbonPageGroup1
            // 
            this.documentViewsRibbonPageGroup1.ItemLinks.Add(this.switchToSimpleViewItem1);
            this.documentViewsRibbonPageGroup1.ItemLinks.Add(this.switchToDraftViewItem1);
            this.documentViewsRibbonPageGroup1.ItemLinks.Add(this.switchToPrintLayoutViewItem1);
            this.documentViewsRibbonPageGroup1.Name = "documentViewsRibbonPageGroup1";
            // 
            // showRibbonPageGroup1
            // 
            this.showRibbonPageGroup1.ItemLinks.Add(this.toggleShowHorizontalRulerItem1);
            this.showRibbonPageGroup1.ItemLinks.Add(this.toggleShowVerticalRulerItem1);
            this.showRibbonPageGroup1.Name = "showRibbonPageGroup1";
            // 
            // zoomRibbonPageGroup1
            // 
            this.zoomRibbonPageGroup1.ItemLinks.Add(this.zoomOutItem1);
            this.zoomRibbonPageGroup1.ItemLinks.Add(this.zoomInItem1);
            this.zoomRibbonPageGroup1.Name = "zoomRibbonPageGroup1";
            // 
            // ribbonPageSkins
            // 
            this.ribbonPageSkins.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.skinsRibbonPageGroup});
            this.ribbonPageSkins.Name = "ribbonPageSkins";
            this.ribbonPageSkins.Text = "Skins";
            // 
            // skinsRibbonPageGroup
            // 
            this.skinsRibbonPageGroup.ItemLinks.Add(this.rgbiSkins);
            this.skinsRibbonPageGroup.Name = "skinsRibbonPageGroup";
            this.skinsRibbonPageGroup.ShowCaptionButton = false;
            this.skinsRibbonPageGroup.Text = "Skins";
            // 
            // helpRibbonPage
            // 
            this.helpRibbonPage.Groups.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageGroup[] {
            this.helpRibbonPageGroup});
            this.helpRibbonPage.Name = "helpRibbonPage";
            this.helpRibbonPage.Text = "Help";
            // 
            // helpRibbonPageGroup
            // 
            this.helpRibbonPageGroup.ItemLinks.Add(this.iHelp);
            this.helpRibbonPageGroup.ItemLinks.Add(this.iAbout);
            this.helpRibbonPageGroup.Name = "helpRibbonPageGroup";
            this.helpRibbonPageGroup.Text = "Help";
            // 
            // ribbonStatusBar
            // 
            this.ribbonStatusBar.ItemLinks.Add(this.siStatus);
            this.ribbonStatusBar.ItemLinks.Add(this.siInfo);
            this.ribbonStatusBar.Location = new System.Drawing.Point(0, 669);
            this.ribbonStatusBar.Name = "ribbonStatusBar";
            this.ribbonStatusBar.Ribbon = this.ribbonControl;
            this.ribbonStatusBar.Size = new System.Drawing.Size(1100, 31);
            // 
            // richEditBarController1
            // 
            this.richEditBarController1.BarItems.Add(this.changeFloatingObjectFillColorItem1);
            this.richEditBarController1.BarItems.Add(this.changeFloatingObjectOutlineColorItem1);
            this.richEditBarController1.BarItems.Add(this.changeFloatingObjectOutlineWeightItem1);
            this.richEditBarController1.BarItems.Add(this.changeFloatingObjectTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectSquareTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectTightTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectThroughTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectTopAndBottomTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectBehindTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectInFrontOfTextWrapTypeItem1);
            this.richEditBarController1.BarItems.Add(this.changeFloatingObjectAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectTopLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectTopCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectTopRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectMiddleLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectMiddleCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectMiddleRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectBottomLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectBottomCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.setFloatingObjectBottomRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectBringForwardSubItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectBringForwardItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectBringToFrontItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectBringInFrontOfTextItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectSendBackwardSubItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectSendBackwardItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectSendToBackItem1);
            this.richEditBarController1.BarItems.Add(this.floatingObjectSendBehindTextItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFirstRowItem1);
            this.richEditBarController1.BarItems.Add(this.toggleLastRowItem1);
            this.richEditBarController1.BarItems.Add(this.toggleBandedRowsItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFirstColumnItem1);
            this.richEditBarController1.BarItems.Add(this.toggleLastColumnItem1);
            this.richEditBarController1.BarItems.Add(this.toggleBandedColumnItem1);
            this.richEditBarController1.BarItems.Add(this.galleryChangeTableStyleItem1);
            this.richEditBarController1.BarItems.Add(this.changeTableBorderLineStyleItem1);
            this.richEditBarController1.BarItems.Add(this.changeTableBorderLineWeightItem1);
            this.richEditBarController1.BarItems.Add(this.changeTableBorderColorItem1);
            this.richEditBarController1.BarItems.Add(this.changeTableBordersItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsBottomBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsTopBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsLeftBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsRightBorderItem1);
            this.richEditBarController1.BarItems.Add(this.resetTableCellsAllBordersItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsAllBordersItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsOutsideBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsInsideBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsInsideHorizontalBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsInsideVerticalBorderItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowTableGridLinesItem1);
            this.richEditBarController1.BarItems.Add(this.changeTableCellsShadingItem1);
            this.richEditBarController1.BarItems.Add(this.selectTableElementsItem1);
            this.richEditBarController1.BarItems.Add(this.selectTableCellItem1);
            this.richEditBarController1.BarItems.Add(this.selectTableColumnItem1);
            this.richEditBarController1.BarItems.Add(this.selectTableRowItem1);
            this.richEditBarController1.BarItems.Add(this.selectTableItem1);
            this.richEditBarController1.BarItems.Add(this.showTablePropertiesFormItem1);
            this.richEditBarController1.BarItems.Add(this.deleteTableElementsItem1);
            this.richEditBarController1.BarItems.Add(this.showDeleteTableCellsFormItem1);
            this.richEditBarController1.BarItems.Add(this.deleteTableColumnsItem1);
            this.richEditBarController1.BarItems.Add(this.deleteTableRowsItem1);
            this.richEditBarController1.BarItems.Add(this.deleteTableItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableRowAboveItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableRowBelowItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableColumnToLeftItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableColumnToRightItem1);
            this.richEditBarController1.BarItems.Add(this.mergeTableCellsItem1);
            this.richEditBarController1.BarItems.Add(this.showSplitTableCellsForm1);
            this.richEditBarController1.BarItems.Add(this.splitTableItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableAutoFitItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableAutoFitContentsItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableAutoFitWindowItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableFixedColumnWidthItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsTopLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsMiddleLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsBottomLeftAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsTopCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsMiddleCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsBottomCenterAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsTopRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsMiddleRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTableCellsBottomRightAlignmentItem1);
            this.richEditBarController1.BarItems.Add(this.showTableOptionsFormItem1);
            this.richEditBarController1.BarItems.Add(this.goToPageHeaderItem1);
            this.richEditBarController1.BarItems.Add(this.goToPageFooterItem1);
            this.richEditBarController1.BarItems.Add(this.goToNextHeaderFooterItem1);
            this.richEditBarController1.BarItems.Add(this.goToPreviousHeaderFooterItem1);
            this.richEditBarController1.BarItems.Add(this.toggleLinkToPreviousItem1);
            this.richEditBarController1.BarItems.Add(this.toggleDifferentFirstPageItem1);
            this.richEditBarController1.BarItems.Add(this.toggleDifferentOddAndEvenPagesItem1);
            this.richEditBarController1.BarItems.Add(this.closePageHeaderFooterItem1);
            this.richEditBarController1.BarItems.Add(this.switchToSimpleViewItem1);
            this.richEditBarController1.BarItems.Add(this.switchToDraftViewItem1);
            this.richEditBarController1.BarItems.Add(this.switchToPrintLayoutViewItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowHorizontalRulerItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowVerticalRulerItem1);
            this.richEditBarController1.BarItems.Add(this.zoomOutItem1);
            this.richEditBarController1.BarItems.Add(this.zoomInItem1);
            this.richEditBarController1.BarItems.Add(this.checkSpellingItem1);
            this.richEditBarController1.BarItems.Add(this.changeLanguageItem1);
            this.richEditBarController1.BarItems.Add(this.protectDocumentItem1);
            this.richEditBarController1.BarItems.Add(this.changeRangeEditingPermissionsItem1);
            this.richEditBarController1.BarItems.Add(this.unprotectDocumentItem1);
            this.richEditBarController1.BarItems.Add(this.insertMergeFieldItem1);
            this.richEditBarController1.BarItems.Add(this.showAllFieldCodesItem1);
            this.richEditBarController1.BarItems.Add(this.showAllFieldResultsItem1);
            this.richEditBarController1.BarItems.Add(this.toggleViewMergedDataItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableOfContentsItem1);
            this.richEditBarController1.BarItems.Add(this.updateTableOfContentsItem1);
            this.richEditBarController1.BarItems.Add(this.addParagraphsToTableOfContentItem1);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem1);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem2);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem3);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem4);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem5);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem6);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem7);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem8);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem9);
            this.richEditBarController1.BarItems.Add(this.setParagraphHeadingLevelItem10);
            this.richEditBarController1.BarItems.Add(this.insertCaptionPlaceholderItem1);
            this.richEditBarController1.BarItems.Add(this.insertFiguresCaptionItems1);
            this.richEditBarController1.BarItems.Add(this.insertTablesCaptionItems1);
            this.richEditBarController1.BarItems.Add(this.insertEquationsCaptionItems1);
            this.richEditBarController1.BarItems.Add(this.insertTableOfFiguresPlaceholderItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableOfFiguresItems1);
            this.richEditBarController1.BarItems.Add(this.insertTableOfTablesItems1);
            this.richEditBarController1.BarItems.Add(this.insertTableOfEquationsItems1);
            this.richEditBarController1.BarItems.Add(this.updateTableOfFiguresItem1);
            this.richEditBarController1.BarItems.Add(this.changeSectionPageMarginsItem1);
            this.richEditBarController1.BarItems.Add(this.setNormalSectionPageMarginsItem1);
            this.richEditBarController1.BarItems.Add(this.setNarrowSectionPageMarginsItem1);
            this.richEditBarController1.BarItems.Add(this.setModerateSectionPageMarginsItem1);
            this.richEditBarController1.BarItems.Add(this.setWideSectionPageMarginsItem1);
            this.richEditBarController1.BarItems.Add(this.showPageMarginsSetupFormItem1);
            this.richEditBarController1.BarItems.Add(this.changeSectionPageOrientationItem1);
            this.richEditBarController1.BarItems.Add(this.setPortraitPageOrientationItem1);
            this.richEditBarController1.BarItems.Add(this.setLandscapePageOrientationItem1);
            this.richEditBarController1.BarItems.Add(this.changeSectionPaperKindItem1);
            this.richEditBarController1.BarItems.Add(this.changeSectionColumnsItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionOneColumnItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionTwoColumnsItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionThreeColumnsItem1);
            this.richEditBarController1.BarItems.Add(this.showColumnsSetupFormItem1);
            this.richEditBarController1.BarItems.Add(this.insertBreakItem1);
            this.richEditBarController1.BarItems.Add(this.insertPageBreakItem1);
            this.richEditBarController1.BarItems.Add(this.insertColumnBreakItem1);
            this.richEditBarController1.BarItems.Add(this.insertSectionBreakNextPageItem1);
            this.richEditBarController1.BarItems.Add(this.insertSectionBreakEvenPageItem1);
            this.richEditBarController1.BarItems.Add(this.insertSectionBreakOddPageItem1);
            this.richEditBarController1.BarItems.Add(this.changeSectionLineNumberingItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionLineNumberingNoneItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionLineNumberingContinuousItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionLineNumberingRestartNewPageItem1);
            this.richEditBarController1.BarItems.Add(this.setSectionLineNumberingRestartNewSectionItem1);
            this.richEditBarController1.BarItems.Add(this.toggleParagraphSuppressLineNumbersItem1);
            this.richEditBarController1.BarItems.Add(this.showLineNumberingFormItem1);
            this.richEditBarController1.BarItems.Add(this.changePageColorItem1);
            this.richEditBarController1.BarItems.Add(this.insertTableItem1);
            this.richEditBarController1.BarItems.Add(this.insertPictureItem1);
            this.richEditBarController1.BarItems.Add(this.insertFloatingPictureItem1);
            this.richEditBarController1.BarItems.Add(this.insertBookmarkItem1);
            this.richEditBarController1.BarItems.Add(this.insertHyperlinkItem1);
            this.richEditBarController1.BarItems.Add(this.editPageHeaderItem1);
            this.richEditBarController1.BarItems.Add(this.editPageFooterItem1);
            this.richEditBarController1.BarItems.Add(this.insertPageNumberItem1);
            this.richEditBarController1.BarItems.Add(this.insertPageCountItem1);
            this.richEditBarController1.BarItems.Add(this.insertTextBoxItem1);
            this.richEditBarController1.BarItems.Add(this.insertSymbolItem1);
            this.richEditBarController1.BarItems.Add(this.pasteItem1);
            this.richEditBarController1.BarItems.Add(this.cutItem1);
            this.richEditBarController1.BarItems.Add(this.copyItem1);
            this.richEditBarController1.BarItems.Add(this.pasteSpecialItem1);
            this.richEditBarController1.BarItems.Add(this.changeFontNameItem1);
            this.richEditBarController1.BarItems.Add(this.changeFontSizeItem1);
            this.richEditBarController1.BarItems.Add(this.fontSizeIncreaseItem1);
            this.richEditBarController1.BarItems.Add(this.fontSizeDecreaseItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontBoldItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontItalicItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontUnderlineItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontDoubleUnderlineItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontStrikeoutItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontDoubleStrikeoutItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontSuperscriptItem1);
            this.richEditBarController1.BarItems.Add(this.toggleFontSubscriptItem1);
            this.richEditBarController1.BarItems.Add(this.changeFontColorItem1);
            this.richEditBarController1.BarItems.Add(this.changeFontBackColorItem1);
            this.richEditBarController1.BarItems.Add(this.changeTextCaseItem1);
            this.richEditBarController1.BarItems.Add(this.makeTextUpperCaseItem1);
            this.richEditBarController1.BarItems.Add(this.makeTextLowerCaseItem1);
            this.richEditBarController1.BarItems.Add(this.capitalizeEachWordCaseItem1);
            this.richEditBarController1.BarItems.Add(this.toggleTextCaseItem1);
            this.richEditBarController1.BarItems.Add(this.clearFormattingItem1);
            this.richEditBarController1.BarItems.Add(this.toggleBulletedListItem1);
            this.richEditBarController1.BarItems.Add(this.toggleNumberingListItem1);
            this.richEditBarController1.BarItems.Add(this.toggleMultiLevelListItem1);
            this.richEditBarController1.BarItems.Add(this.decreaseIndentItem1);
            this.richEditBarController1.BarItems.Add(this.increaseIndentItem1);
            this.richEditBarController1.BarItems.Add(this.toggleParagraphAlignmentLeftItem1);
            this.richEditBarController1.BarItems.Add(this.toggleParagraphAlignmentCenterItem1);
            this.richEditBarController1.BarItems.Add(this.toggleParagraphAlignmentRightItem1);
            this.richEditBarController1.BarItems.Add(this.toggleParagraphAlignmentJustifyItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowWhitespaceItem1);
            this.richEditBarController1.BarItems.Add(this.changeParagraphLineSpacingItem1);
            this.richEditBarController1.BarItems.Add(this.setSingleParagraphSpacingItem1);
            this.richEditBarController1.BarItems.Add(this.setSesquialteralParagraphSpacingItem1);
            this.richEditBarController1.BarItems.Add(this.setDoubleParagraphSpacingItem1);
            this.richEditBarController1.BarItems.Add(this.showLineSpacingFormItem1);
            this.richEditBarController1.BarItems.Add(this.addSpacingBeforeParagraphItem1);
            this.richEditBarController1.BarItems.Add(this.removeSpacingBeforeParagraphItem1);
            this.richEditBarController1.BarItems.Add(this.addSpacingAfterParagraphItem1);
            this.richEditBarController1.BarItems.Add(this.removeSpacingAfterParagraphItem1);
            this.richEditBarController1.BarItems.Add(this.changeParagraphBackColorItem1);
            this.richEditBarController1.BarItems.Add(this.galleryChangeStyleItem1);
            this.richEditBarController1.BarItems.Add(this.findItem1);
            this.richEditBarController1.BarItems.Add(this.replaceItem1);
            this.richEditBarController1.BarItems.Add(this.undoItem1);
            this.richEditBarController1.BarItems.Add(this.redoItem1);
            this.richEditBarController1.BarItems.Add(this.fileNewItem1);
            this.richEditBarController1.BarItems.Add(this.fileOpenItem1);
            this.richEditBarController1.BarItems.Add(this.fileSaveItem1);
            this.richEditBarController1.BarItems.Add(this.fileSaveAsItem1);
            this.richEditBarController1.BarItems.Add(this.quickPrintItem1);
            this.richEditBarController1.BarItems.Add(this.printItem1);
            this.richEditBarController1.BarItems.Add(this.printPreviewItem1);
            this.richEditBarController1.Control = this.richEditControl;
            // 
            // Form1
            // 
            this.AllowFormGlass = DevExpress.Utils.DefaultBoolean.False;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1100, 700);
            this.Controls.Add(this.richEditControl);
            this.Controls.Add(this.popupControlContainer1);
            this.Controls.Add(this.popupControlContainer2);
            this.Controls.Add(this.ribbonStatusBar);
            this.Controls.Add(this.ribbonControl);
            this.Name = "Form1";
            this.Ribbon = this.ribbonControl;
            this.StatusBar = this.ribbonStatusBar;
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.ribbonControl)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.appMenu)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.popupControlContainer2)).EndInit();
            this.popupControlContainer2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.buttonEdit.Properties)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.popupControlContainer1)).EndInit();
            this.popupControlContainer1.ResumeLayout(false);
            this.popupControlContainer1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonImageCollection)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFloatingObjectOutlineWeight1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemBorderLineStyle1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemBorderLineWeight1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFontEdit1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemRichEditFontSizeEdit1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemColorPickEdit1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonImageCollectionLarge)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.richEditBarController1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private DevExpress.XtraBars.Ribbon.RibbonControl ribbonControl;
        private DevExpress.XtraBars.BarButtonItem iExit;
        private DevExpress.XtraBars.BarButtonItem iHelp;
        private DevExpress.XtraBars.BarButtonItem iAbout;
        private DevExpress.XtraBars.BarStaticItem siStatus;
        private DevExpress.XtraBars.BarStaticItem siInfo;
        private DevExpress.XtraBars.RibbonGalleryBarItem rgbiSkins;
        private DevExpress.XtraBars.Ribbon.RibbonPage ribbonPageSkins;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup skinsRibbonPageGroup;
        private DevExpress.XtraBars.Ribbon.RibbonPage helpRibbonPage;
        private DevExpress.XtraBars.Ribbon.RibbonPageGroup helpRibbonPageGroup;
        private DevExpress.XtraBars.Ribbon.ApplicationMenu appMenu;
        private DevExpress.XtraBars.PopupControlContainer popupControlContainer1;
        private DevExpress.XtraEditors.LabelControl someLabelControl2;
        private DevExpress.XtraEditors.LabelControl someLabelControl1;
        private DevExpress.XtraBars.PopupControlContainer popupControlContainer2;
        private DevExpress.XtraEditors.ButtonEdit buttonEdit;
        private DevExpress.XtraBars.Ribbon.RibbonStatusBar ribbonStatusBar;
        private DevExpress.Utils.ImageCollection ribbonImageCollection;
        private DevExpress.Utils.ImageCollection ribbonImageCollectionLarge;
        private MyRichEditControl richEditControl;
        private DevExpress.XtraSpellChecker.SpellChecker spellChecker;
        private DevExpress.XtraRichEdit.UI.ChangeFloatingObjectFillColorItem changeFloatingObjectFillColorItem1;
        private DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineColorItem changeFloatingObjectOutlineColorItem1;
        private DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineWeightItem changeFloatingObjectOutlineWeightItem1;
        private DevExpress.XtraRichEdit.Forms.Design.RepositoryItemFloatingObjectOutlineWeight repositoryItemFloatingObjectOutlineWeight1;
        private DevExpress.XtraRichEdit.UI.ChangeFloatingObjectTextWrapTypeItem changeFloatingObjectTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectSquareTextWrapTypeItem setFloatingObjectSquareTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectTightTextWrapTypeItem setFloatingObjectTightTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectThroughTextWrapTypeItem setFloatingObjectThroughTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectTopAndBottomTextWrapTypeItem setFloatingObjectTopAndBottomTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectBehindTextWrapTypeItem setFloatingObjectBehindTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectInFrontOfTextWrapTypeItem setFloatingObjectInFrontOfTextWrapTypeItem1;
        private DevExpress.XtraRichEdit.UI.ChangeFloatingObjectAlignmentItem changeFloatingObjectAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectTopLeftAlignmentItem setFloatingObjectTopLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectTopCenterAlignmentItem setFloatingObjectTopCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectTopRightAlignmentItem setFloatingObjectTopRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleLeftAlignmentItem setFloatingObjectMiddleLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleCenterAlignmentItem setFloatingObjectMiddleCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectMiddleRightAlignmentItem setFloatingObjectMiddleRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomLeftAlignmentItem setFloatingObjectBottomLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomCenterAlignmentItem setFloatingObjectBottomCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.SetFloatingObjectBottomRightAlignmentItem setFloatingObjectBottomRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardSubItem floatingObjectBringForwardSubItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectBringForwardItem floatingObjectBringForwardItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectBringToFrontItem floatingObjectBringToFrontItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectBringInFrontOfTextItem floatingObjectBringInFrontOfTextItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardSubItem floatingObjectSendBackwardSubItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectSendBackwardItem floatingObjectSendBackwardItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectSendToBackItem floatingObjectSendToBackItem1;
        private DevExpress.XtraRichEdit.UI.FloatingObjectSendBehindTextItem floatingObjectSendBehindTextItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFirstRowItem toggleFirstRowItem1;
        private DevExpress.XtraRichEdit.UI.ToggleLastRowItem toggleLastRowItem1;
        private DevExpress.XtraRichEdit.UI.ToggleBandedRowsItem toggleBandedRowsItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFirstColumnItem toggleFirstColumnItem1;
        private DevExpress.XtraRichEdit.UI.ToggleLastColumnItem toggleLastColumnItem1;
        private DevExpress.XtraRichEdit.UI.ToggleBandedColumnsItem toggleBandedColumnItem1;
        private DevExpress.XtraRichEdit.UI.GalleryChangeTableStyleItem galleryChangeTableStyleItem1;
        private DevExpress.XtraRichEdit.UI.ChangeTableBorderLineStyleItem changeTableBorderLineStyleItem1;
        private DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineStyle repositoryItemBorderLineStyle1;
        private DevExpress.XtraRichEdit.UI.ChangeTableBorderLineWeightItem changeTableBorderLineWeightItem1;
        private DevExpress.XtraRichEdit.Forms.Design.RepositoryItemBorderLineWeight repositoryItemBorderLineWeight1;
        private DevExpress.XtraRichEdit.UI.ChangeTableBorderColorItem changeTableBorderColorItem1;
        private DevExpress.XtraRichEdit.UI.ChangeTableBordersItem changeTableBordersItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomBorderItem toggleTableCellsBottomBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsTopBorderItem toggleTableCellsTopBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsLeftBorderItem toggleTableCellsLeftBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsRightBorderItem toggleTableCellsRightBorderItem1;
        private DevExpress.XtraRichEdit.UI.ResetTableCellsAllBordersItem resetTableCellsAllBordersItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsAllBordersItem toggleTableCellsAllBordersItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsOutsideBorderItem toggleTableCellsOutsideBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideBorderItem toggleTableCellsInsideBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideHorizontalBorderItem toggleTableCellsInsideHorizontalBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsInsideVerticalBorderItem toggleTableCellsInsideVerticalBorderItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowTableGridLinesItem toggleShowTableGridLinesItem1;
        private DevExpress.XtraRichEdit.UI.ChangeTableCellsShadingItem changeTableCellsShadingItem1;
        private DevExpress.XtraRichEdit.UI.SelectTableElementsItem selectTableElementsItem1;
        private DevExpress.XtraRichEdit.UI.SelectTableCellItem selectTableCellItem1;
        private DevExpress.XtraRichEdit.UI.SelectTableColumnItem selectTableColumnItem1;
        private DevExpress.XtraRichEdit.UI.SelectTableRowItem selectTableRowItem1;
        private DevExpress.XtraRichEdit.UI.SelectTableItem selectTableItem1;
        private DevExpress.XtraRichEdit.UI.ShowTablePropertiesFormItem showTablePropertiesFormItem1;
        private DevExpress.XtraRichEdit.UI.DeleteTableElementsItem deleteTableElementsItem1;
        private DevExpress.XtraRichEdit.UI.ShowDeleteTableCellsFormItem showDeleteTableCellsFormItem1;
        private DevExpress.XtraRichEdit.UI.DeleteTableColumnsItem deleteTableColumnsItem1;
        private DevExpress.XtraRichEdit.UI.DeleteTableRowsItem deleteTableRowsItem1;
        private DevExpress.XtraRichEdit.UI.DeleteTableItem deleteTableItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableRowAboveItem insertTableRowAboveItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableRowBelowItem insertTableRowBelowItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableColumnToLeftItem insertTableColumnToLeftItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableColumnToRightItem insertTableColumnToRightItem1;
        private DevExpress.XtraRichEdit.UI.MergeTableCellsItem mergeTableCellsItem1;
        private DevExpress.XtraRichEdit.UI.ShowSplitTableCellsForm showSplitTableCellsForm1;
        private DevExpress.XtraRichEdit.UI.SplitTableItem splitTableItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableAutoFitItem toggleTableAutoFitItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableAutoFitContentsItem toggleTableAutoFitContentsItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableAutoFitWindowItem toggleTableAutoFitWindowItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableFixedColumnWidthItem toggleTableFixedColumnWidthItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsTopLeftAlignmentItem toggleTableCellsTopLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleLeftAlignmentItem toggleTableCellsMiddleLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomLeftAlignmentItem toggleTableCellsBottomLeftAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsTopCenterAlignmentItem toggleTableCellsTopCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleCenterAlignmentItem toggleTableCellsMiddleCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomCenterAlignmentItem toggleTableCellsBottomCenterAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsTopRightAlignmentItem toggleTableCellsTopRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsMiddleRightAlignmentItem toggleTableCellsMiddleRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTableCellsBottomRightAlignmentItem toggleTableCellsBottomRightAlignmentItem1;
        private DevExpress.XtraRichEdit.UI.ShowTableOptionsFormItem showTableOptionsFormItem1;
        private DevExpress.XtraRichEdit.UI.GoToPageHeaderItem goToPageHeaderItem1;
        private DevExpress.XtraRichEdit.UI.GoToPageFooterItem goToPageFooterItem1;
        private DevExpress.XtraRichEdit.UI.GoToNextHeaderFooterItem goToNextHeaderFooterItem1;
        private DevExpress.XtraRichEdit.UI.GoToPreviousHeaderFooterItem goToPreviousHeaderFooterItem1;
        private DevExpress.XtraRichEdit.UI.ToggleLinkToPreviousItem toggleLinkToPreviousItem1;
        private DevExpress.XtraRichEdit.UI.ToggleDifferentFirstPageItem toggleDifferentFirstPageItem1;
        private DevExpress.XtraRichEdit.UI.ToggleDifferentOddAndEvenPagesItem toggleDifferentOddAndEvenPagesItem1;
        private DevExpress.XtraRichEdit.UI.ClosePageHeaderFooterItem closePageHeaderFooterItem1;
        private DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem switchToSimpleViewItem1;
        private DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem switchToDraftViewItem1;
        private DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem switchToPrintLayoutViewItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem toggleShowHorizontalRulerItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem toggleShowVerticalRulerItem1;
        private DevExpress.XtraRichEdit.UI.ZoomOutItem zoomOutItem1;
        private DevExpress.XtraRichEdit.UI.ZoomInItem zoomInItem1;
        private DevExpress.XtraRichEdit.UI.CheckSpellingItem checkSpellingItem1;
        private DevExpress.XtraRichEdit.UI.ChangeLanguageItem changeLanguageItem1;
        private DevExpress.XtraRichEdit.UI.ProtectDocumentItem protectDocumentItem1;
        private DevExpress.XtraRichEdit.UI.ChangeRangeEditingPermissionsItem changeRangeEditingPermissionsItem1;
        private DevExpress.XtraRichEdit.UI.UnprotectDocumentItem unprotectDocumentItem1;
        private DevExpress.XtraRichEdit.UI.InsertMergeFieldItem insertMergeFieldItem1;
        private DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem showAllFieldCodesItem1;
        private DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem showAllFieldResultsItem1;
        private DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem toggleViewMergedDataItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableOfContentsItem insertTableOfContentsItem1;
        private DevExpress.XtraRichEdit.UI.UpdateTableOfContentsItem updateTableOfContentsItem1;
        private DevExpress.XtraRichEdit.UI.AddParagraphsToTableOfContentItem addParagraphsToTableOfContentItem1;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem1;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem2;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem3;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem4;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem5;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem6;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem7;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem8;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem9;
        private DevExpress.XtraRichEdit.UI.SetParagraphHeadingLevelItem setParagraphHeadingLevelItem10;
        private DevExpress.XtraRichEdit.UI.InsertCaptionPlaceholderItem insertCaptionPlaceholderItem1;
        private DevExpress.XtraRichEdit.UI.InsertFiguresCaptionItems insertFiguresCaptionItems1;
        private DevExpress.XtraRichEdit.UI.InsertTablesCaptionItems insertTablesCaptionItems1;
        private DevExpress.XtraRichEdit.UI.InsertEquationsCaptionItems insertEquationsCaptionItems1;
        private DevExpress.XtraRichEdit.UI.InsertTableOfFiguresPlaceholderItem insertTableOfFiguresPlaceholderItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableOfFiguresItems insertTableOfFiguresItems1;
        private DevExpress.XtraRichEdit.UI.InsertTableOfTablesItems insertTableOfTablesItems1;
        private DevExpress.XtraRichEdit.UI.InsertTableOfEquationsItems insertTableOfEquationsItems1;
        private DevExpress.XtraRichEdit.UI.UpdateTableOfFiguresItem updateTableOfFiguresItem1;
        private DevExpress.XtraRichEdit.UI.ChangeSectionPageMarginsItem changeSectionPageMarginsItem1;
        private DevExpress.XtraRichEdit.UI.SetNormalSectionPageMarginsItem setNormalSectionPageMarginsItem1;
        private DevExpress.XtraRichEdit.UI.SetNarrowSectionPageMarginsItem setNarrowSectionPageMarginsItem1;
        private DevExpress.XtraRichEdit.UI.SetModerateSectionPageMarginsItem setModerateSectionPageMarginsItem1;
        private DevExpress.XtraRichEdit.UI.SetWideSectionPageMarginsItem setWideSectionPageMarginsItem1;
        private DevExpress.XtraRichEdit.UI.ShowPageMarginsSetupFormItem showPageMarginsSetupFormItem1;
        private DevExpress.XtraRichEdit.UI.ChangeSectionPageOrientationItem changeSectionPageOrientationItem1;
        private DevExpress.XtraRichEdit.UI.SetPortraitPageOrientationItem setPortraitPageOrientationItem1;
        private DevExpress.XtraRichEdit.UI.SetLandscapePageOrientationItem setLandscapePageOrientationItem1;
        private DevExpress.XtraRichEdit.UI.ChangeSectionPaperKindItem changeSectionPaperKindItem1;
        private DevExpress.XtraRichEdit.UI.ChangeSectionColumnsItem changeSectionColumnsItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionOneColumnItem setSectionOneColumnItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionTwoColumnsItem setSectionTwoColumnsItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionThreeColumnsItem setSectionThreeColumnsItem1;
        private DevExpress.XtraRichEdit.UI.ShowColumnsSetupFormItem showColumnsSetupFormItem1;
        private DevExpress.XtraRichEdit.UI.InsertBreakItem insertBreakItem1;
        private DevExpress.XtraRichEdit.UI.InsertPageBreakItem insertPageBreakItem1;
        private DevExpress.XtraRichEdit.UI.InsertColumnBreakItem insertColumnBreakItem1;
        private DevExpress.XtraRichEdit.UI.InsertSectionBreakNextPageItem insertSectionBreakNextPageItem1;
        private DevExpress.XtraRichEdit.UI.InsertSectionBreakEvenPageItem insertSectionBreakEvenPageItem1;
        private DevExpress.XtraRichEdit.UI.InsertSectionBreakOddPageItem insertSectionBreakOddPageItem1;
        private DevExpress.XtraRichEdit.UI.ChangeSectionLineNumberingItem changeSectionLineNumberingItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionLineNumberingNoneItem setSectionLineNumberingNoneItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionLineNumberingContinuousItem setSectionLineNumberingContinuousItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewPageItem setSectionLineNumberingRestartNewPageItem1;
        private DevExpress.XtraRichEdit.UI.SetSectionLineNumberingRestartNewSectionItem setSectionLineNumberingRestartNewSectionItem1;
        private DevExpress.XtraRichEdit.UI.ToggleParagraphSuppressLineNumbersItem toggleParagraphSuppressLineNumbersItem1;
        private DevExpress.XtraRichEdit.UI.ShowLineNumberingFormItem showLineNumberingFormItem1;
        private DevExpress.XtraRichEdit.UI.ChangePageColorItem changePageColorItem1;
        private DevExpress.XtraRichEdit.UI.InsertTableItem insertTableItem1;
        private DevExpress.XtraRichEdit.UI.InsertPictureItem insertPictureItem1;
        private DevExpress.XtraRichEdit.UI.InsertFloatingPictureItem insertFloatingPictureItem1;
        private DevExpress.XtraRichEdit.UI.InsertBookmarkItem insertBookmarkItem1;
        private DevExpress.XtraRichEdit.UI.InsertHyperlinkItem insertHyperlinkItem1;
        private DevExpress.XtraRichEdit.UI.EditPageHeaderItem editPageHeaderItem1;
        private DevExpress.XtraRichEdit.UI.EditPageFooterItem editPageFooterItem1;
        private DevExpress.XtraRichEdit.UI.InsertPageNumberItem insertPageNumberItem1;
        private DevExpress.XtraRichEdit.UI.InsertPageCountItem insertPageCountItem1;
        private DevExpress.XtraRichEdit.UI.InsertTextBoxItem insertTextBoxItem1;
        private DevExpress.XtraRichEdit.UI.InsertSymbolItem insertSymbolItem1;
        private DevExpress.XtraRichEdit.UI.PasteItem pasteItem1;
        private DevExpress.XtraRichEdit.UI.CutItem cutItem1;
        private DevExpress.XtraRichEdit.UI.CopyItem copyItem1;
        private DevExpress.XtraRichEdit.UI.PasteSpecialItem pasteSpecialItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup1;
        private DevExpress.XtraRichEdit.UI.ChangeFontNameItem changeFontNameItem1;
        private DevExpress.XtraEditors.Repository.RepositoryItemFontEdit repositoryItemFontEdit1;
        private DevExpress.XtraRichEdit.UI.ChangeFontSizeItem changeFontSizeItem1;
        private DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit repositoryItemRichEditFontSizeEdit1;
        private DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem fontSizeIncreaseItem1;
        private DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem fontSizeDecreaseItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup2;
        private DevExpress.XtraRichEdit.UI.ToggleFontBoldItem toggleFontBoldItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontItalicItem toggleFontItalicItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem toggleFontUnderlineItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem toggleFontDoubleUnderlineItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem toggleFontStrikeoutItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem toggleFontDoubleStrikeoutItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem toggleFontSuperscriptItem1;
        private DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem toggleFontSubscriptItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup3;
        private DevExpress.XtraRichEdit.UI.ChangeFontColorItem changeFontColorItem1;
        private DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem changeFontBackColorItem1;
        private DevExpress.XtraRichEdit.UI.ChangeTextCaseItem changeTextCaseItem1;
        private DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem makeTextUpperCaseItem1;
        private DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem makeTextLowerCaseItem1;
        private DevExpress.XtraRichEdit.UI.CapitalizeEachWordCaseItem capitalizeEachWordCaseItem1;
        private DevExpress.XtraRichEdit.UI.ToggleTextCaseItem toggleTextCaseItem1;
        private DevExpress.XtraRichEdit.UI.ClearFormattingItem clearFormattingItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup4;
        private DevExpress.XtraRichEdit.UI.ToggleBulletedListItem toggleBulletedListItem1;
        private DevExpress.XtraRichEdit.UI.ToggleNumberingListItem toggleNumberingListItem1;
        private DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem toggleMultiLevelListItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup5;
        private DevExpress.XtraRichEdit.UI.DecreaseIndentItem decreaseIndentItem1;
        private DevExpress.XtraRichEdit.UI.IncreaseIndentItem increaseIndentItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem toggleShowWhitespaceItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup6;
        private DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem toggleParagraphAlignmentLeftItem1;
        private DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem toggleParagraphAlignmentCenterItem1;
        private DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem toggleParagraphAlignmentRightItem1;
        private DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem toggleParagraphAlignmentJustifyItem1;
        private DevExpress.XtraBars.BarButtonGroup barButtonGroup7;
        private DevExpress.XtraRichEdit.UI.ChangeParagraphLineSpacingItem changeParagraphLineSpacingItem1;
        private DevExpress.XtraRichEdit.UI.SetSingleParagraphSpacingItem setSingleParagraphSpacingItem1;
        private DevExpress.XtraRichEdit.UI.SetSesquialteralParagraphSpacingItem setSesquialteralParagraphSpacingItem1;
        private DevExpress.XtraRichEdit.UI.SetDoubleParagraphSpacingItem setDoubleParagraphSpacingItem1;
        private DevExpress.XtraRichEdit.UI.ShowLineSpacingFormItem showLineSpacingFormItem1;
        private DevExpress.XtraRichEdit.UI.AddSpacingBeforeParagraphItem addSpacingBeforeParagraphItem1;
        private DevExpress.XtraRichEdit.UI.RemoveSpacingBeforeParagraphItem removeSpacingBeforeParagraphItem1;
        private DevExpress.XtraRichEdit.UI.AddSpacingAfterParagraphItem addSpacingAfterParagraphItem1;
        private DevExpress.XtraRichEdit.UI.RemoveSpacingAfterParagraphItem removeSpacingAfterParagraphItem1;
        private DevExpress.XtraRichEdit.UI.ChangeParagraphBackColorItem changeParagraphBackColorItem1;
        private DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem galleryChangeStyleItem1;
        private DevExpress.XtraRichEdit.UI.FindItem findItem1;
        private DevExpress.XtraRichEdit.UI.ReplaceItem replaceItem1;
        private DevExpress.XtraRichEdit.UI.UndoItem undoItem1;
        private DevExpress.XtraRichEdit.UI.RedoItem redoItem1;
        private DevExpress.XtraRichEdit.UI.FileNewItem fileNewItem1;
        private DevExpress.XtraRichEdit.UI.FileOpenItem fileOpenItem1;
        private DevExpress.XtraRichEdit.UI.FileSaveItem fileSaveItem1;
        private DevExpress.XtraRichEdit.UI.FileSaveAsItem fileSaveAsItem1;
        private DevExpress.XtraRichEdit.UI.QuickPrintItem quickPrintItem1;
        private DevExpress.XtraRichEdit.UI.PrintItem printItem1;
        private DevExpress.XtraRichEdit.UI.PrintPreviewItem printPreviewItem1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory floatingPictureToolsRibbonPageCategory1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage floatingPictureToolsFormatPage1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup floatingPictureToolsShapeStylesPageGroup1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup floatingPictureToolsArrangePageGroup1;
        private DevExpress.XtraRichEdit.UI.TableToolsRibbonPageCategory tableToolsRibbonPageCategory1;
        private DevExpress.XtraRichEdit.UI.TableLayoutRibbonPage tableLayoutRibbonPage1;
        private DevExpress.XtraRichEdit.UI.TableTableRibbonPageGroup tableTableRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableRowsAndColumnsRibbonPageGroup tableRowsAndColumnsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableMergeRibbonPageGroup tableMergeRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableCellSizeRibbonPageGroup tableCellSizeRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableAlignmentRibbonPageGroup tableAlignmentRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableDesignRibbonPage tableDesignRibbonPage1;
        private DevExpress.XtraRichEdit.UI.TableStyleOptionsRibbonPageGroup tableStyleOptionsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableStylesRibbonPageGroup tableStylesRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TableDrawBordersRibbonPageGroup tableDrawBordersRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterToolsRibbonPageCategory headerFooterToolsRibbonPageCategory1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignRibbonPage headerFooterToolsDesignRibbonPage1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignNavigationRibbonPageGroup headerFooterToolsDesignNavigationRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignOptionsRibbonPageGroup headerFooterToolsDesignOptionsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterToolsDesignCloseRibbonPageGroup headerFooterToolsDesignCloseRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.FileRibbonPage fileRibbonPage1;
        private DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup commonRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HomeRibbonPage homeRibbonPage1;
        private DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup clipboardRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.FontRibbonPageGroup fontRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup paragraphRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup stylesRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup editingRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.InsertRibbonPage insertRibbonPage1;
        private DevExpress.XtraRichEdit.UI.PagesRibbonPageGroup pagesRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TablesRibbonPageGroup tablesRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.IllustrationsRibbonPageGroup illustrationsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.LinksRibbonPageGroup linksRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HeaderFooterRibbonPageGroup headerFooterRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.TextRibbonPageGroup textRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.SymbolsRibbonPageGroup symbolsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage pageLayoutRibbonPage1;
        private DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup pageSetupRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup pageBackgroundRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ReferencesRibbonPage referencesRibbonPage1;
        private DevExpress.XtraRichEdit.UI.TableOfContentsRibbonPageGroup tableOfContentsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.CaptionsRibbonPageGroup captionsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.MailingsRibbonPage mailingsRibbonPage1;
        private DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup mailMergeRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ReviewRibbonPage reviewRibbonPage1;
        private DevExpress.XtraRichEdit.UI.DocumentProofingRibbonPageGroup documentProofingRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.DocumentProtectionRibbonPageGroup documentProtectionRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ViewRibbonPage viewRibbonPage1;
        private DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup documentViewsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup showRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup zoomRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.RichEditBarController richEditBarController1;
        private DevExpress.XtraBars.BarEditItem barEditItem1;
        private DevExpress.XtraEditors.Repository.RepositoryItemColorPickEdit repositoryItemColorPickEdit1;
        private DevExpress.XtraBars.BarCheckItem barCheckItem1;

    }
}
