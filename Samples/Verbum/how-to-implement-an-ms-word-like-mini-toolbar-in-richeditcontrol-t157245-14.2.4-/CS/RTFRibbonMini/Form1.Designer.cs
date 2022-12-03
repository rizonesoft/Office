// Developer Express Code Central Example:
// How to implement an MS Word-like Mini Toolbar in RichEditControl
// 
// This example demonstrates how to implement the MS Word-like Mini Toolbar feature
// using a RibbonMiniToolbar
// (https://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsRibbonRibbonMiniToolbartopic)
// component. It is a popup toolbar, whose transparency depends on the distance
// from the mouse cursor. Show this toolbar for the selected text in the
// RichEditControl document separately and display it together with a regular
// context menu in the RichEditControl.PopupMenuShowing event handler.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=T157245

using DevExpress.XtraRichEdit;
namespace RTFRibbonMini {
    partial class Form1 {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing) {
            if(disposing && (components != null)) {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent() {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            DevExpress.XtraBars.Ribbon.GalleryItemGroup galleryItemGroup1 = new DevExpress.XtraBars.Ribbon.GalleryItemGroup();
            DevExpress.XtraBars.Ribbon.ReduceOperation reduceOperation1 = new DevExpress.XtraBars.Ribbon.ReduceOperation();
            this.stylesRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup();
            this.galleryChangeStyleItem1 = new DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem();
            this.richEditControl1 = new DevExpress.XtraRichEdit.RichEditControl();
            this.ribbonControl1 = new RTFRibbonMini.MyRibbonControl();
            this.undoItem1 = new DevExpress.XtraRichEdit.UI.UndoItem();
            this.redoItem1 = new DevExpress.XtraRichEdit.UI.RedoItem();
            this.fileNewItem1 = new DevExpress.XtraRichEdit.UI.FileNewItem();
            this.fileOpenItem1 = new DevExpress.XtraRichEdit.UI.FileOpenItem();
            this.fileSaveItem1 = new DevExpress.XtraRichEdit.UI.FileSaveItem();
            this.fileSaveAsItem1 = new DevExpress.XtraRichEdit.UI.FileSaveAsItem();
            this.quickPrintItem1 = new DevExpress.XtraRichEdit.UI.QuickPrintItem();
            this.printItem1 = new DevExpress.XtraRichEdit.UI.PrintItem();
            this.printPreviewItem1 = new DevExpress.XtraRichEdit.UI.PrintPreviewItem();
            this.changeFloatingObjectFillColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectFillColorItem();
            this.changeFloatingObjectOutlineColorItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineColorItem();
            this.changeFloatingObjectOutlineWeightItem1 = new DevExpress.XtraRichEdit.UI.ChangeFloatingObjectOutlineWeightItem();
            this.repositoryItemFloatingObjectOutlineWeight1 = new DevExpress.XtraRichEdit.Forms.Design.RepositoryItemFloatingObjectOutlineWeight();
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
            this.switchToSimpleViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem();
            this.switchToDraftViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem();
            this.switchToPrintLayoutViewItem1 = new DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem();
            this.toggleShowHorizontalRulerItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem();
            this.toggleShowVerticalRulerItem1 = new DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem();
            this.zoomOutItem1 = new DevExpress.XtraRichEdit.UI.ZoomOutItem();
            this.zoomInItem1 = new DevExpress.XtraRichEdit.UI.ZoomInItem();
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
            this.ribbonMiniToolbar1 = new DevExpress.XtraBars.Ribbon.RibbonMiniToolbar(this.components);
            this.floatingPictureToolsRibbonPageCategory1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory();
            this.floatingPictureToolsFormatPage1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage();
            this.floatingPictureToolsShapeStylesPageGroup1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup();
            this.floatingPictureToolsArrangePageGroup1 = new DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup();
            this.fileRibbonPage1 = new DevExpress.XtraRichEdit.UI.FileRibbonPage();
            this.commonRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup();
            this.viewRibbonPage1 = new DevExpress.XtraRichEdit.UI.ViewRibbonPage();
            this.documentViewsRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup();
            this.showRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup();
            this.zoomRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup();
            this.homeRibbonPage1 = new DevExpress.XtraRichEdit.UI.HomeRibbonPage();
            this.clipboardRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup();
            this.fontRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.FontRibbonPageGroup();
            this.paragraphRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup();
            this.editingRibbonPageGroup1 = new DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup();
            this.richEditBarController1 = new DevExpress.XtraRichEdit.UI.RichEditBarController();
            ((System.ComponentModel.ISupportInitialize)(this.ribbonControl1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFloatingObjectOutlineWeight1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFontEdit1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemRichEditFontSizeEdit1)).BeginInit();
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
            this.galleryChangeStyleItem1.Id = 96;
            this.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1";
            // 
            // richEditControl1
            // 
            this.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEditControl1.EnableToolTips = true;
            this.richEditControl1.Location = new System.Drawing.Point(0, 144);
            this.richEditControl1.MenuManager = this.ribbonControl1;
            this.richEditControl1.Name = "richEditControl1";
            this.richEditControl1.Options.Comments.ShowAllAuthors = true;
            this.richEditControl1.Options.Comments.Visibility = RichEditCommentVisibility.Auto;
                //DevExpress.XtraRichEdit.Options.RichEditCommentVisibility.Auto;
            this.richEditControl1.Options.CopyPaste.MaintainDocumentSectionSettings = false;
            this.richEditControl1.Options.Fields.UseCurrentCultureDateTimeFormat = false;
            this.richEditControl1.Options.MailMerge.KeepLastParagraph = false;
            this.richEditControl1.Size = new System.Drawing.Size(894, 317);
            this.richEditControl1.TabIndex = 0;
            this.richEditControl1.Text = "richEditControl1";
            this.richEditControl1.PopupMenuShowing += new DevExpress.XtraRichEdit.PopupMenuShowingEventHandler(this.richEditControl1_PopupMenuShowing);
            // 
            // ribbonControl1
            // 
            this.ribbonControl1.ExpandCollapseItem.Id = 0;
            this.ribbonControl1.Items.AddRange(new DevExpress.XtraBars.BarItem[] {
            this.ribbonControl1.ExpandCollapseItem,
            this.undoItem1,
            this.redoItem1,
            this.fileNewItem1,
            this.fileOpenItem1,
            this.fileSaveItem1,
            this.fileSaveAsItem1,
            this.quickPrintItem1,
            this.printItem1,
            this.printPreviewItem1,
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
            this.switchToSimpleViewItem1,
            this.switchToDraftViewItem1,
            this.switchToPrintLayoutViewItem1,
            this.toggleShowHorizontalRulerItem1,
            this.toggleShowVerticalRulerItem1,
            this.zoomOutItem1,
            this.zoomInItem1,
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
            this.replaceItem1});
            this.ribbonControl1.Location = new System.Drawing.Point(0, 0);
            this.ribbonControl1.MaxItemId = 99;
            this.ribbonControl1.MiniToolbars.Add(this.ribbonMiniToolbar1);
            this.ribbonControl1.Name = "ribbonControl1";
            this.ribbonControl1.PageCategories.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPageCategory[] {
            this.floatingPictureToolsRibbonPageCategory1});
            this.ribbonControl1.Pages.AddRange(new DevExpress.XtraBars.Ribbon.RibbonPage[] {
            this.fileRibbonPage1,
            this.viewRibbonPage1,
            this.homeRibbonPage1});
            this.ribbonControl1.RepositoryItems.AddRange(new DevExpress.XtraEditors.Repository.RepositoryItem[] {
            this.repositoryItemFloatingObjectOutlineWeight1,
            this.repositoryItemFontEdit1,
            this.repositoryItemRichEditFontSizeEdit1});
            this.ribbonControl1.Size = new System.Drawing.Size(894, 144);
            // 
            // undoItem1
            // 
            this.undoItem1.Id = 1;
            this.undoItem1.Name = "undoItem1";
            // 
            // redoItem1
            // 
            this.redoItem1.Id = 2;
            this.redoItem1.Name = "redoItem1";
            // 
            // fileNewItem1
            // 
            this.fileNewItem1.Id = 3;
            this.fileNewItem1.Name = "fileNewItem1";
            // 
            // fileOpenItem1
            // 
            this.fileOpenItem1.Id = 4;
            this.fileOpenItem1.Name = "fileOpenItem1";
            // 
            // fileSaveItem1
            // 
            this.fileSaveItem1.Id = 5;
            this.fileSaveItem1.Name = "fileSaveItem1";
            // 
            // fileSaveAsItem1
            // 
            this.fileSaveAsItem1.Id = 6;
            this.fileSaveAsItem1.Name = "fileSaveAsItem1";
            // 
            // quickPrintItem1
            // 
            this.quickPrintItem1.Id = 7;
            this.quickPrintItem1.Name = "quickPrintItem1";
            // 
            // printItem1
            // 
            this.printItem1.Id = 8;
            this.printItem1.Name = "printItem1";
            // 
            // printPreviewItem1
            // 
            this.printPreviewItem1.Id = 9;
            this.printPreviewItem1.Name = "printPreviewItem1";
            // 
            // changeFloatingObjectFillColorItem1
            // 
            this.changeFloatingObjectFillColorItem1.Id = 10;
            this.changeFloatingObjectFillColorItem1.Name = "changeFloatingObjectFillColorItem1";
            // 
            // changeFloatingObjectOutlineColorItem1
            // 
            this.changeFloatingObjectOutlineColorItem1.Id = 11;
            this.changeFloatingObjectOutlineColorItem1.Name = "changeFloatingObjectOutlineColorItem1";
            // 
            // changeFloatingObjectOutlineWeightItem1
            // 
            this.changeFloatingObjectOutlineWeightItem1.Edit = this.repositoryItemFloatingObjectOutlineWeight1;
            this.changeFloatingObjectOutlineWeightItem1.EditValue = 20;
            this.changeFloatingObjectOutlineWeightItem1.Id = 12;
            this.changeFloatingObjectOutlineWeightItem1.Name = "changeFloatingObjectOutlineWeightItem1";
            // 
            // repositoryItemFloatingObjectOutlineWeight1
            // 
            this.repositoryItemFloatingObjectOutlineWeight1.AutoHeight = false;
            this.repositoryItemFloatingObjectOutlineWeight1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemFloatingObjectOutlineWeight1.Control = this.richEditControl1;
            this.repositoryItemFloatingObjectOutlineWeight1.Name = "repositoryItemFloatingObjectOutlineWeight1";
            // 
            // changeFloatingObjectTextWrapTypeItem1
            // 
            this.changeFloatingObjectTextWrapTypeItem1.Id = 13;
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
            this.setFloatingObjectSquareTextWrapTypeItem1.Id = 14;
            this.setFloatingObjectSquareTextWrapTypeItem1.Name = "setFloatingObjectSquareTextWrapTypeItem1";
            // 
            // setFloatingObjectTightTextWrapTypeItem1
            // 
            this.setFloatingObjectTightTextWrapTypeItem1.Id = 15;
            this.setFloatingObjectTightTextWrapTypeItem1.Name = "setFloatingObjectTightTextWrapTypeItem1";
            // 
            // setFloatingObjectThroughTextWrapTypeItem1
            // 
            this.setFloatingObjectThroughTextWrapTypeItem1.Id = 16;
            this.setFloatingObjectThroughTextWrapTypeItem1.Name = "setFloatingObjectThroughTextWrapTypeItem1";
            // 
            // setFloatingObjectTopAndBottomTextWrapTypeItem1
            // 
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1.Id = 17;
            this.setFloatingObjectTopAndBottomTextWrapTypeItem1.Name = "setFloatingObjectTopAndBottomTextWrapTypeItem1";
            // 
            // setFloatingObjectBehindTextWrapTypeItem1
            // 
            this.setFloatingObjectBehindTextWrapTypeItem1.Id = 18;
            this.setFloatingObjectBehindTextWrapTypeItem1.Name = "setFloatingObjectBehindTextWrapTypeItem1";
            // 
            // setFloatingObjectInFrontOfTextWrapTypeItem1
            // 
            this.setFloatingObjectInFrontOfTextWrapTypeItem1.Id = 19;
            this.setFloatingObjectInFrontOfTextWrapTypeItem1.Name = "setFloatingObjectInFrontOfTextWrapTypeItem1";
            // 
            // changeFloatingObjectAlignmentItem1
            // 
            this.changeFloatingObjectAlignmentItem1.Id = 20;
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
            this.setFloatingObjectTopLeftAlignmentItem1.Id = 21;
            this.setFloatingObjectTopLeftAlignmentItem1.Name = "setFloatingObjectTopLeftAlignmentItem1";
            // 
            // setFloatingObjectTopCenterAlignmentItem1
            // 
            this.setFloatingObjectTopCenterAlignmentItem1.Id = 22;
            this.setFloatingObjectTopCenterAlignmentItem1.Name = "setFloatingObjectTopCenterAlignmentItem1";
            // 
            // setFloatingObjectTopRightAlignmentItem1
            // 
            this.setFloatingObjectTopRightAlignmentItem1.Id = 23;
            this.setFloatingObjectTopRightAlignmentItem1.Name = "setFloatingObjectTopRightAlignmentItem1";
            // 
            // setFloatingObjectMiddleLeftAlignmentItem1
            // 
            this.setFloatingObjectMiddleLeftAlignmentItem1.Id = 24;
            this.setFloatingObjectMiddleLeftAlignmentItem1.Name = "setFloatingObjectMiddleLeftAlignmentItem1";
            // 
            // setFloatingObjectMiddleCenterAlignmentItem1
            // 
            this.setFloatingObjectMiddleCenterAlignmentItem1.Id = 25;
            this.setFloatingObjectMiddleCenterAlignmentItem1.Name = "setFloatingObjectMiddleCenterAlignmentItem1";
            // 
            // setFloatingObjectMiddleRightAlignmentItem1
            // 
            this.setFloatingObjectMiddleRightAlignmentItem1.Id = 26;
            this.setFloatingObjectMiddleRightAlignmentItem1.Name = "setFloatingObjectMiddleRightAlignmentItem1";
            // 
            // setFloatingObjectBottomLeftAlignmentItem1
            // 
            this.setFloatingObjectBottomLeftAlignmentItem1.Id = 27;
            this.setFloatingObjectBottomLeftAlignmentItem1.Name = "setFloatingObjectBottomLeftAlignmentItem1";
            // 
            // setFloatingObjectBottomCenterAlignmentItem1
            // 
            this.setFloatingObjectBottomCenterAlignmentItem1.Id = 28;
            this.setFloatingObjectBottomCenterAlignmentItem1.Name = "setFloatingObjectBottomCenterAlignmentItem1";
            // 
            // setFloatingObjectBottomRightAlignmentItem1
            // 
            this.setFloatingObjectBottomRightAlignmentItem1.Id = 29;
            this.setFloatingObjectBottomRightAlignmentItem1.Name = "setFloatingObjectBottomRightAlignmentItem1";
            // 
            // floatingObjectBringForwardSubItem1
            // 
            this.floatingObjectBringForwardSubItem1.Id = 30;
            this.floatingObjectBringForwardSubItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringForwardItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringToFrontItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectBringInFrontOfTextItem1)});
            this.floatingObjectBringForwardSubItem1.Name = "floatingObjectBringForwardSubItem1";
            // 
            // floatingObjectBringForwardItem1
            // 
            this.floatingObjectBringForwardItem1.Id = 31;
            this.floatingObjectBringForwardItem1.Name = "floatingObjectBringForwardItem1";
            // 
            // floatingObjectBringToFrontItem1
            // 
            this.floatingObjectBringToFrontItem1.Id = 32;
            this.floatingObjectBringToFrontItem1.Name = "floatingObjectBringToFrontItem1";
            // 
            // floatingObjectBringInFrontOfTextItem1
            // 
            this.floatingObjectBringInFrontOfTextItem1.Id = 33;
            this.floatingObjectBringInFrontOfTextItem1.Name = "floatingObjectBringInFrontOfTextItem1";
            // 
            // floatingObjectSendBackwardSubItem1
            // 
            this.floatingObjectSendBackwardSubItem1.Id = 34;
            this.floatingObjectSendBackwardSubItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendBackwardItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendToBackItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.floatingObjectSendBehindTextItem1)});
            this.floatingObjectSendBackwardSubItem1.Name = "floatingObjectSendBackwardSubItem1";
            // 
            // floatingObjectSendBackwardItem1
            // 
            this.floatingObjectSendBackwardItem1.Id = 35;
            this.floatingObjectSendBackwardItem1.Name = "floatingObjectSendBackwardItem1";
            // 
            // floatingObjectSendToBackItem1
            // 
            this.floatingObjectSendToBackItem1.Id = 36;
            this.floatingObjectSendToBackItem1.Name = "floatingObjectSendToBackItem1";
            // 
            // floatingObjectSendBehindTextItem1
            // 
            this.floatingObjectSendBehindTextItem1.Id = 37;
            this.floatingObjectSendBehindTextItem1.Name = "floatingObjectSendBehindTextItem1";
            // 
            // switchToSimpleViewItem1
            // 
            this.switchToSimpleViewItem1.Id = 38;
            this.switchToSimpleViewItem1.Name = "switchToSimpleViewItem1";
            // 
            // switchToDraftViewItem1
            // 
            this.switchToDraftViewItem1.Id = 39;
            this.switchToDraftViewItem1.Name = "switchToDraftViewItem1";
            // 
            // switchToPrintLayoutViewItem1
            // 
            this.switchToPrintLayoutViewItem1.Id = 40;
            this.switchToPrintLayoutViewItem1.Name = "switchToPrintLayoutViewItem1";
            // 
            // toggleShowHorizontalRulerItem1
            // 
            this.toggleShowHorizontalRulerItem1.Id = 41;
            this.toggleShowHorizontalRulerItem1.Name = "toggleShowHorizontalRulerItem1";
            // 
            // toggleShowVerticalRulerItem1
            // 
            this.toggleShowVerticalRulerItem1.Id = 42;
            this.toggleShowVerticalRulerItem1.Name = "toggleShowVerticalRulerItem1";
            // 
            // zoomOutItem1
            // 
            this.zoomOutItem1.Id = 43;
            this.zoomOutItem1.Name = "zoomOutItem1";
            // 
            // zoomInItem1
            // 
            this.zoomInItem1.Id = 44;
            this.zoomInItem1.Name = "zoomInItem1";
            // 
            // pasteItem1
            // 
            this.pasteItem1.Id = 52;
            this.pasteItem1.Name = "pasteItem1";
            // 
            // cutItem1
            // 
            this.cutItem1.Id = 53;
            this.cutItem1.Name = "cutItem1";
            // 
            // copyItem1
            // 
            this.copyItem1.Id = 54;
            this.copyItem1.Name = "copyItem1";
            // 
            // pasteSpecialItem1
            // 
            this.pasteSpecialItem1.Id = 55;
            this.pasteSpecialItem1.Name = "pasteSpecialItem1";
            // 
            // barButtonGroup1
            // 
            this.barButtonGroup1.Id = 45;
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
            this.changeFontNameItem1.Id = 56;
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
            this.changeFontSizeItem1.Id = 57;
            this.changeFontSizeItem1.Name = "changeFontSizeItem1";
            // 
            // repositoryItemRichEditFontSizeEdit1
            // 
            this.repositoryItemRichEditFontSizeEdit1.AutoHeight = false;
            this.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(new DevExpress.XtraEditors.Controls.EditorButton[] {
            new DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)});
            this.repositoryItemRichEditFontSizeEdit1.Control = this.richEditControl1;
            this.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1";
            // 
            // fontSizeIncreaseItem1
            // 
            this.fontSizeIncreaseItem1.Id = 58;
            this.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1";
            // 
            // fontSizeDecreaseItem1
            // 
            this.fontSizeDecreaseItem1.Id = 59;
            this.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1";
            // 
            // barButtonGroup2
            // 
            this.barButtonGroup2.Id = 46;
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
            this.toggleFontBoldItem1.Id = 60;
            this.toggleFontBoldItem1.Name = "toggleFontBoldItem1";
            // 
            // toggleFontItalicItem1
            // 
            this.toggleFontItalicItem1.Id = 61;
            this.toggleFontItalicItem1.Name = "toggleFontItalicItem1";
            // 
            // toggleFontUnderlineItem1
            // 
            this.toggleFontUnderlineItem1.Id = 62;
            this.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1";
            // 
            // toggleFontDoubleUnderlineItem1
            // 
            this.toggleFontDoubleUnderlineItem1.Id = 63;
            this.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1";
            // 
            // toggleFontStrikeoutItem1
            // 
            this.toggleFontStrikeoutItem1.Id = 64;
            this.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1";
            // 
            // toggleFontDoubleStrikeoutItem1
            // 
            this.toggleFontDoubleStrikeoutItem1.Id = 65;
            this.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1";
            // 
            // toggleFontSuperscriptItem1
            // 
            this.toggleFontSuperscriptItem1.Id = 66;
            this.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1";
            // 
            // toggleFontSubscriptItem1
            // 
            this.toggleFontSubscriptItem1.Id = 67;
            this.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1";
            // 
            // barButtonGroup3
            // 
            this.barButtonGroup3.Id = 47;
            this.barButtonGroup3.ItemLinks.Add(this.changeFontColorItem1);
            this.barButtonGroup3.ItemLinks.Add(this.changeFontBackColorItem1);
            this.barButtonGroup3.Name = "barButtonGroup3";
            this.barButtonGroup3.Tag = "{DF8C5334-EDE3-47c9-A42C-FE9A9247E180}";
            // 
            // changeFontColorItem1
            // 
            this.changeFontColorItem1.Id = 68;
            this.changeFontColorItem1.Name = "changeFontColorItem1";
            // 
            // changeFontBackColorItem1
            // 
            this.changeFontBackColorItem1.Id = 69;
            this.changeFontBackColorItem1.Name = "changeFontBackColorItem1";
            // 
            // changeTextCaseItem1
            // 
            this.changeTextCaseItem1.Id = 70;
            this.changeTextCaseItem1.LinksPersistInfo.AddRange(new DevExpress.XtraBars.LinkPersistInfo[] {
            new DevExpress.XtraBars.LinkPersistInfo(this.makeTextUpperCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.makeTextLowerCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.capitalizeEachWordCaseItem1),
            new DevExpress.XtraBars.LinkPersistInfo(this.toggleTextCaseItem1)});
            this.changeTextCaseItem1.Name = "changeTextCaseItem1";
            // 
            // makeTextUpperCaseItem1
            // 
            this.makeTextUpperCaseItem1.Id = 71;
            this.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1";
            // 
            // makeTextLowerCaseItem1
            // 
            this.makeTextLowerCaseItem1.Id = 72;
            this.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1";
            // 
            // capitalizeEachWordCaseItem1
            // 
            this.capitalizeEachWordCaseItem1.Id = 73;
            this.capitalizeEachWordCaseItem1.Name = "capitalizeEachWordCaseItem1";
            // 
            // toggleTextCaseItem1
            // 
            this.toggleTextCaseItem1.Id = 74;
            this.toggleTextCaseItem1.Name = "toggleTextCaseItem1";
            // 
            // clearFormattingItem1
            // 
            this.clearFormattingItem1.Id = 75;
            this.clearFormattingItem1.Name = "clearFormattingItem1";
            // 
            // barButtonGroup4
            // 
            this.barButtonGroup4.Id = 48;
            this.barButtonGroup4.ItemLinks.Add(this.toggleBulletedListItem1);
            this.barButtonGroup4.ItemLinks.Add(this.toggleNumberingListItem1);
            this.barButtonGroup4.ItemLinks.Add(this.toggleMultiLevelListItem1);
            this.barButtonGroup4.Name = "barButtonGroup4";
            this.barButtonGroup4.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}";
            // 
            // toggleBulletedListItem1
            // 
            this.toggleBulletedListItem1.Id = 76;
            this.toggleBulletedListItem1.Name = "toggleBulletedListItem1";
            // 
            // toggleNumberingListItem1
            // 
            this.toggleNumberingListItem1.Id = 77;
            this.toggleNumberingListItem1.Name = "toggleNumberingListItem1";
            // 
            // toggleMultiLevelListItem1
            // 
            this.toggleMultiLevelListItem1.Id = 78;
            this.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1";
            // 
            // barButtonGroup5
            // 
            this.barButtonGroup5.Id = 49;
            this.barButtonGroup5.ItemLinks.Add(this.decreaseIndentItem1);
            this.barButtonGroup5.ItemLinks.Add(this.increaseIndentItem1);
            this.barButtonGroup5.ItemLinks.Add(this.toggleShowWhitespaceItem1);
            this.barButtonGroup5.Name = "barButtonGroup5";
            this.barButtonGroup5.Tag = "{4747D5AB-2BEB-4ea6-9A1D-8E4FB36F1B40}";
            // 
            // decreaseIndentItem1
            // 
            this.decreaseIndentItem1.Id = 79;
            this.decreaseIndentItem1.Name = "decreaseIndentItem1";
            // 
            // increaseIndentItem1
            // 
            this.increaseIndentItem1.Id = 80;
            this.increaseIndentItem1.Name = "increaseIndentItem1";
            // 
            // toggleShowWhitespaceItem1
            // 
            this.toggleShowWhitespaceItem1.Id = 85;
            this.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1";
            // 
            // barButtonGroup6
            // 
            this.barButtonGroup6.Id = 50;
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentLeftItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentCenterItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentRightItem1);
            this.barButtonGroup6.ItemLinks.Add(this.toggleParagraphAlignmentJustifyItem1);
            this.barButtonGroup6.Name = "barButtonGroup6";
            this.barButtonGroup6.Tag = "{8E89E775-996E-49a0-AADA-DE338E34732E}";
            // 
            // toggleParagraphAlignmentLeftItem1
            // 
            this.toggleParagraphAlignmentLeftItem1.Id = 81;
            this.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1";
            // 
            // toggleParagraphAlignmentCenterItem1
            // 
            this.toggleParagraphAlignmentCenterItem1.Id = 82;
            this.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1";
            // 
            // toggleParagraphAlignmentRightItem1
            // 
            this.toggleParagraphAlignmentRightItem1.Id = 83;
            this.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1";
            // 
            // toggleParagraphAlignmentJustifyItem1
            // 
            this.toggleParagraphAlignmentJustifyItem1.Id = 84;
            this.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1";
            // 
            // barButtonGroup7
            // 
            this.barButtonGroup7.Id = 51;
            this.barButtonGroup7.ItemLinks.Add(this.changeParagraphLineSpacingItem1);
            this.barButtonGroup7.ItemLinks.Add(this.changeParagraphBackColorItem1);
            this.barButtonGroup7.Name = "barButtonGroup7";
            this.barButtonGroup7.Tag = "{9A8DEAD8-3890-4857-A395-EC625FD02217}";
            // 
            // changeParagraphLineSpacingItem1
            // 
            this.changeParagraphLineSpacingItem1.Id = 86;
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
            this.setSingleParagraphSpacingItem1.Id = 87;
            this.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1";
            // 
            // setSesquialteralParagraphSpacingItem1
            // 
            this.setSesquialteralParagraphSpacingItem1.Id = 88;
            this.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1";
            // 
            // setDoubleParagraphSpacingItem1
            // 
            this.setDoubleParagraphSpacingItem1.Id = 89;
            this.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1";
            // 
            // showLineSpacingFormItem1
            // 
            this.showLineSpacingFormItem1.Id = 90;
            this.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1";
            // 
            // addSpacingBeforeParagraphItem1
            // 
            this.addSpacingBeforeParagraphItem1.Id = 91;
            this.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1";
            // 
            // removeSpacingBeforeParagraphItem1
            // 
            this.removeSpacingBeforeParagraphItem1.Id = 92;
            this.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1";
            // 
            // addSpacingAfterParagraphItem1
            // 
            this.addSpacingAfterParagraphItem1.Id = 93;
            this.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1";
            // 
            // removeSpacingAfterParagraphItem1
            // 
            this.removeSpacingAfterParagraphItem1.Id = 94;
            this.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1";
            // 
            // changeParagraphBackColorItem1
            // 
            this.changeParagraphBackColorItem1.Id = 95;
            this.changeParagraphBackColorItem1.Name = "changeParagraphBackColorItem1";
            // 
            // findItem1
            // 
            this.findItem1.Id = 97;
            this.findItem1.Name = "findItem1";
            // 
            // replaceItem1
            // 
            this.replaceItem1.Id = 98;
            this.replaceItem1.Name = "replaceItem1";
            // 
            // ribbonMiniToolbar1
            // 
            this.ribbonMiniToolbar1.ItemLinks.Add(this.changeFontNameItem1);
            this.ribbonMiniToolbar1.ItemLinks.Add(this.changeFontSizeItem1);
            this.ribbonMiniToolbar1.ItemLinks.Add(this.toggleFontBoldItem1);
            this.ribbonMiniToolbar1.ItemLinks.Add(this.toggleFontItalicItem1);
            this.ribbonMiniToolbar1.ItemLinks.Add(this.toggleFontUnderlineItem1);
            this.ribbonMiniToolbar1.ItemLinks.Add(this.changeFontColorItem1);
            // 
            // floatingPictureToolsRibbonPageCategory1
            // 
            this.floatingPictureToolsRibbonPageCategory1.Color = System.Drawing.Color.FromArgb(((int)(((byte)(201)))), ((int)(((byte)(0)))), ((int)(((byte)(119)))));
            this.floatingPictureToolsRibbonPageCategory1.Control = this.richEditControl1;
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
            this.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1";
            // 
            // fontRibbonPageGroup1
            // 
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup1);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup2);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.barButtonGroup3);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.changeTextCaseItem1);
            this.fontRibbonPageGroup1.ItemLinks.Add(this.clearFormattingItem1);
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
            // richEditBarController1
            // 
            this.richEditBarController1.BarItems.Add(this.undoItem1);
            this.richEditBarController1.BarItems.Add(this.redoItem1);
            this.richEditBarController1.BarItems.Add(this.fileNewItem1);
            this.richEditBarController1.BarItems.Add(this.fileOpenItem1);
            this.richEditBarController1.BarItems.Add(this.fileSaveItem1);
            this.richEditBarController1.BarItems.Add(this.fileSaveAsItem1);
            this.richEditBarController1.BarItems.Add(this.quickPrintItem1);
            this.richEditBarController1.BarItems.Add(this.printItem1);
            this.richEditBarController1.BarItems.Add(this.printPreviewItem1);
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
            this.richEditBarController1.BarItems.Add(this.switchToSimpleViewItem1);
            this.richEditBarController1.BarItems.Add(this.switchToDraftViewItem1);
            this.richEditBarController1.BarItems.Add(this.switchToPrintLayoutViewItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowHorizontalRulerItem1);
            this.richEditBarController1.BarItems.Add(this.toggleShowVerticalRulerItem1);
            this.richEditBarController1.BarItems.Add(this.zoomOutItem1);
            this.richEditBarController1.BarItems.Add(this.zoomInItem1);
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
            this.richEditBarController1.Control = this.richEditControl1;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(894, 461);
            this.Controls.Add(this.richEditControl1);
            this.Controls.Add(this.ribbonControl1);
            this.Name = "Form1";
            this.Ribbon = this.ribbonControl1;
            this.Text = "Form1";
            ((System.ComponentModel.ISupportInitialize)(this.ribbonControl1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFloatingObjectOutlineWeight1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemFontEdit1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryItemRichEditFontSizeEdit1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.richEditBarController1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private RichEditControl richEditControl1;
        private DevExpress.XtraRichEdit.UI.UndoItem undoItem1;
        private DevExpress.XtraRichEdit.UI.RedoItem redoItem1;
        private DevExpress.XtraRichEdit.UI.FileNewItem fileNewItem1;
        private DevExpress.XtraRichEdit.UI.FileOpenItem fileOpenItem1;
        private DevExpress.XtraRichEdit.UI.FileSaveItem fileSaveItem1;
        private DevExpress.XtraRichEdit.UI.FileSaveAsItem fileSaveAsItem1;
        private DevExpress.XtraRichEdit.UI.QuickPrintItem quickPrintItem1;
        private DevExpress.XtraRichEdit.UI.PrintItem printItem1;
        private DevExpress.XtraRichEdit.UI.PrintPreviewItem printPreviewItem1;
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
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsRibbonPageCategory floatingPictureToolsRibbonPageCategory1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsFormatPage floatingPictureToolsFormatPage1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsShapeStylesPageGroup floatingPictureToolsShapeStylesPageGroup1;
        private DevExpress.XtraRichEdit.UI.FloatingPictureToolsArrangePageGroup floatingPictureToolsArrangePageGroup1;
        private DevExpress.XtraRichEdit.UI.FileRibbonPage fileRibbonPage1;
        private DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup commonRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.RichEditBarController richEditBarController1;
        private DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem switchToSimpleViewItem1;
        private DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem switchToDraftViewItem1;
        private DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem switchToPrintLayoutViewItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem toggleShowHorizontalRulerItem1;
        private DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem toggleShowVerticalRulerItem1;
        private DevExpress.XtraRichEdit.UI.ZoomOutItem zoomOutItem1;
        private DevExpress.XtraRichEdit.UI.ZoomInItem zoomInItem1;
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
        private DevExpress.XtraBars.Ribbon.RibbonMiniToolbar ribbonMiniToolbar1;
        private DevExpress.XtraRichEdit.UI.ViewRibbonPage viewRibbonPage1;
        private DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup documentViewsRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup showRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup zoomRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.HomeRibbonPage homeRibbonPage1;
        private DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup clipboardRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.FontRibbonPageGroup fontRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup paragraphRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup stylesRibbonPageGroup1;
        private DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup editingRibbonPageGroup1;
        private MyRibbonControl ribbonControl1;
    }
}

