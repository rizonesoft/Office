Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1
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
			Dim reduceOperation1 As New DevExpress.XtraBars.Ribbon.ReduceOperation()
			Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
			Dim galleryItemGroup1 As New DevExpress.XtraBars.Ribbon.GalleryItemGroup()
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
			Me.barButtonItem1 = New DevExpress.XtraBars.BarButtonItem()
			Me.barButtonItem2 = New DevExpress.XtraBars.BarButtonItem()
			Me.insertMergeFieldItem1 = New DevExpress.XtraRichEdit.UI.InsertMergeFieldItem()
			Me.showAllFieldCodesItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem()
			Me.showAllFieldResultsItem1 = New DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem()
			Me.toggleViewMergedDataItem1 = New DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem()
			Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
			Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
			Me.mailingsRibbonPage1 = New DevExpress.XtraRichEdit.UI.MailingsRibbonPage()
			Me.mailMergeRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup()
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
			Me.layoutControl1 = New DevExpress.XtraLayout.LayoutControl()
			Me.spinEdit1 = New DevExpress.XtraEditors.SpinEdit()
			Me.simpleButton1 = New DevExpress.XtraEditors.SimpleButton()
			Me.memoEdit1 = New DevExpress.XtraEditors.MemoEdit()
			Me.textEdit1 = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem3 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem4 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem5 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.clipboardRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup()
			Me.homeRibbonPage1 = New DevExpress.XtraRichEdit.UI.HomeRibbonPage()
			Me.pasteItem1 = New DevExpress.XtraRichEdit.UI.PasteItem()
			Me.cutItem1 = New DevExpress.XtraRichEdit.UI.CutItem()
			Me.copyItem1 = New DevExpress.XtraRichEdit.UI.CopyItem()
			Me.pasteSpecialItem1 = New DevExpress.XtraRichEdit.UI.PasteSpecialItem()
			Me.fontRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.FontRibbonPageGroup()
			Me.changeFontNameItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontNameItem()
			Me.changeFontSizeItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontSizeItem()
			Me.fontSizeIncreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem()
			Me.fontSizeDecreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem()
			Me.toggleFontBoldItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontBoldItem()
			Me.toggleFontItalicItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontItalicItem()
			Me.toggleFontUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem()
			Me.toggleFontDoubleUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem()
			Me.toggleFontStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem()
			Me.toggleFontDoubleStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleStrikeoutItem()
			Me.toggleFontSuperscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem()
			Me.toggleFontSubscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem()
			Me.changeFontColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontColorItem()
			Me.changeFontBackColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem()
			Me.changeTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ChangeTextCaseItem()
			Me.makeTextUpperCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextUpperCaseItem()
			Me.makeTextLowerCaseItem1 = New DevExpress.XtraRichEdit.UI.MakeTextLowerCaseItem()
			Me.capitalizeEachWordCaseItem1 = New DevExpress.XtraRichEdit.UI.CapitalizeEachWordCaseItem()
			Me.toggleTextCaseItem1 = New DevExpress.XtraRichEdit.UI.ToggleTextCaseItem()
			Me.clearFormattingItem1 = New DevExpress.XtraRichEdit.UI.ClearFormattingItem()
			Me.barButtonGroup1 = New DevExpress.XtraBars.BarButtonGroup()
			Me.repositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
			Me.repositoryItemRichEditFontSizeEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit()
			Me.barButtonGroup2 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup3 = New DevExpress.XtraBars.BarButtonGroup()
			Me.paragraphRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup()
			Me.toggleBulletedListItem1 = New DevExpress.XtraRichEdit.UI.ToggleBulletedListItem()
			Me.toggleNumberingListItem1 = New DevExpress.XtraRichEdit.UI.ToggleNumberingListItem()
			Me.toggleMultiLevelListItem1 = New DevExpress.XtraRichEdit.UI.ToggleMultiLevelListItem()
			Me.decreaseIndentItem1 = New DevExpress.XtraRichEdit.UI.DecreaseIndentItem()
			Me.increaseIndentItem1 = New DevExpress.XtraRichEdit.UI.IncreaseIndentItem()
			Me.toggleParagraphAlignmentLeftItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentLeftItem()
			Me.toggleParagraphAlignmentCenterItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentCenterItem()
			Me.toggleParagraphAlignmentRightItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentRightItem()
			Me.toggleParagraphAlignmentJustifyItem1 = New DevExpress.XtraRichEdit.UI.ToggleParagraphAlignmentJustifyItem()
			Me.toggleShowWhitespaceItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowWhitespaceItem()
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
			Me.barButtonGroup4 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup5 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup6 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup7 = New DevExpress.XtraBars.BarButtonGroup()
			Me.stylesRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup()
			Me.galleryChangeStyleItem1 = New DevExpress.XtraRichEdit.UI.GalleryChangeStyleItem()
			Me.editingRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup()
			Me.findItem1 = New DevExpress.XtraRichEdit.UI.FindItem()
			Me.replaceItem1 = New DevExpress.XtraRichEdit.UI.ReplaceItem()
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.spinEdit1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.memoEdit1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEdit1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Location = New System.Drawing.Point(12, 12)
			Me.richEditControl1.MenuManager = Me.ribbonControl1
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(664, 526)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
			' 
			' ribbonControl1
			' 
			Me.ribbonControl1.ExpandCollapseItem.Id = 0
			Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.undoItem1, Me.redoItem1, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.barButtonItem1, Me.barButtonItem2, Me.insertMergeFieldItem1, Me.showAllFieldCodesItem1, Me.showAllFieldResultsItem1, Me.toggleViewMergedDataItem1, Me.pasteItem1, Me.cutItem1, Me.copyItem1, Me.pasteSpecialItem1, Me.barButtonGroup1, Me.changeFontNameItem1, Me.changeFontSizeItem1, Me.fontSizeIncreaseItem1, Me.fontSizeDecreaseItem1, Me.barButtonGroup2, Me.toggleFontBoldItem1, Me.toggleFontItalicItem1, Me.toggleFontUnderlineItem1, Me.toggleFontDoubleUnderlineItem1, Me.toggleFontStrikeoutItem1, Me.toggleFontDoubleStrikeoutItem1, Me.toggleFontSuperscriptItem1, Me.toggleFontSubscriptItem1, Me.barButtonGroup3, Me.changeFontColorItem1, Me.changeFontBackColorItem1, Me.changeTextCaseItem1, Me.makeTextUpperCaseItem1, Me.makeTextLowerCaseItem1, Me.capitalizeEachWordCaseItem1, Me.toggleTextCaseItem1, Me.clearFormattingItem1, Me.barButtonGroup4, Me.toggleBulletedListItem1, Me.toggleNumberingListItem1, Me.toggleMultiLevelListItem1, Me.barButtonGroup5, Me.decreaseIndentItem1, Me.increaseIndentItem1, Me.barButtonGroup6, Me.toggleParagraphAlignmentLeftItem1, Me.toggleParagraphAlignmentCenterItem1, Me.toggleParagraphAlignmentRightItem1, Me.toggleParagraphAlignmentJustifyItem1, Me.toggleShowWhitespaceItem1, Me.barButtonGroup7, Me.changeParagraphLineSpacingItem1, Me.setSingleParagraphSpacingItem1, Me.setSesquialteralParagraphSpacingItem1, Me.setDoubleParagraphSpacingItem1, Me.showLineSpacingFormItem1, Me.addSpacingBeforeParagraphItem1, Me.removeSpacingBeforeParagraphItem1, Me.addSpacingAfterParagraphItem1, Me.removeSpacingAfterParagraphItem1, Me.changeParagraphBackColorItem1, Me.galleryChangeStyleItem1, Me.findItem1, Me.replaceItem1})
			Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl1.MaxItemId = 73
			Me.ribbonControl1.Name = "ribbonControl1"
			Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1, Me.homeRibbonPage1, Me.mailingsRibbonPage1})
			Me.ribbonControl1.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() { Me.repositoryItemFontEdit1, Me.repositoryItemRichEditFontSizeEdit1})
			Me.ribbonControl1.Size = New System.Drawing.Size(1065, 143)
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
			' barButtonItem1
			' 
			Me.barButtonItem1.Caption = "CreateMultipageContent"
			Me.barButtonItem1.Id = 10
			Me.barButtonItem1.Name = "barButtonItem1"
			' 
			' barButtonItem2
			' 
			Me.barButtonItem2.Caption = "CreateTableOfContentsWithHyperlinks"
			Me.barButtonItem2.Id = 11
			Me.barButtonItem2.Name = "barButtonItem2"
			' 
			' insertMergeFieldItem1
			' 
			Me.insertMergeFieldItem1.Id = 12
			Me.insertMergeFieldItem1.Name = "insertMergeFieldItem1"
			' 
			' showAllFieldCodesItem1
			' 
			Me.showAllFieldCodesItem1.Id = 13
			Me.showAllFieldCodesItem1.Name = "showAllFieldCodesItem1"
			' 
			' showAllFieldResultsItem1
			' 
			Me.showAllFieldResultsItem1.Id = 14
			Me.showAllFieldResultsItem1.Name = "showAllFieldResultsItem1"
			' 
			' toggleViewMergedDataItem1
			' 
			Me.toggleViewMergedDataItem1.Id = 15
			Me.toggleViewMergedDataItem1.Name = "toggleViewMergedDataItem1"
			' 
			' fileRibbonPage1
			' 
			Me.fileRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.commonRibbonPageGroup1})
			Me.fileRibbonPage1.Name = "fileRibbonPage1"
			' 
			' commonRibbonPageGroup1
			' 
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.undoItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.redoItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileNewItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileOpenItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.fileSaveAsItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.quickPrintItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.printPreviewItem1)
			Me.commonRibbonPageGroup1.Name = "commonRibbonPageGroup1"
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
			Me.mailMergeRibbonPageGroup1.ItemLinks.Add(Me.toggleViewMergedDataItem1)
			Me.mailMergeRibbonPageGroup1.Name = "mailMergeRibbonPageGroup1"
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
			Me.richEditBarController1.BarItems.Add(Me.insertMergeFieldItem1)
			Me.richEditBarController1.BarItems.Add(Me.showAllFieldCodesItem1)
			Me.richEditBarController1.BarItems.Add(Me.showAllFieldResultsItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleViewMergedDataItem1)
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
			Me.richEditBarController1.BarItems.Add(Me.changeFontBackColorItem1)
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
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.spinEdit1)
			Me.layoutControl1.Controls.Add(Me.simpleButton1)
			Me.layoutControl1.Controls.Add(Me.memoEdit1)
			Me.layoutControl1.Controls.Add(Me.textEdit1)
			Me.layoutControl1.Controls.Add(Me.richEditControl1)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 143)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.OptionsCustomizationForm.DesignTimeCustomizationFormPositionAndSize = New System.Drawing.Rectangle(855, 428, 521, 432)
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(1065, 550)
			Me.layoutControl1.TabIndex = 2
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' spinEdit1
			' 
			Me.spinEdit1.EditValue = New Decimal(New Integer() { 1, 0, 0, 0})
			Me.spinEdit1.Location = New System.Drawing.Point(959, 28)
			Me.spinEdit1.MenuManager = Me.ribbonControl1
			Me.spinEdit1.Name = "spinEdit1"
			Me.spinEdit1.Properties.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.spinEdit1.Properties.IsFloatValue = False
			Me.spinEdit1.Properties.Mask.EditMask = "N00"
			Me.spinEdit1.Size = New System.Drawing.Size(94, 20)
			Me.spinEdit1.StyleController = Me.layoutControl1
			Me.spinEdit1.TabIndex = 7
			' 
			' simpleButton1
			' 
			Me.simpleButton1.Location = New System.Drawing.Point(680, 516)
			Me.simpleButton1.Name = "simpleButton1"
			Me.simpleButton1.Size = New System.Drawing.Size(373, 22)
			Me.simpleButton1.StyleController = Me.layoutControl1
			Me.simpleButton1.TabIndex = 6
			Me.simpleButton1.Text = "Append content/Update TOC"
'			Me.simpleButton1.Click += New System.EventHandler(Me.simpleButton1_Click);
			' 
			' memoEdit1
			' 
			Me.memoEdit1.Location = New System.Drawing.Point(680, 68)
			Me.memoEdit1.MenuManager = Me.ribbonControl1
			Me.memoEdit1.Name = "memoEdit1"
			Me.memoEdit1.Size = New System.Drawing.Size(373, 444)
			Me.memoEdit1.StyleController = Me.layoutControl1
			Me.memoEdit1.TabIndex = 5
			' 
			' textEdit1
			' 
			Me.textEdit1.Location = New System.Drawing.Point(680, 28)
			Me.textEdit1.MenuManager = Me.ribbonControl1
			Me.textEdit1.Name = "textEdit1"
			Me.textEdit1.Size = New System.Drawing.Size(275, 20)
			Me.textEdit1.StyleController = Me.layoutControl1
			Me.textEdit1.TabIndex = 4
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem3, Me.layoutControlItem2, Me.layoutControlItem4, Me.layoutControlItem5})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "Root"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(1065, 550)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.richEditControl1
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(668, 530)
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem1.TextVisible = False
			' 
			' layoutControlItem3
			' 
			Me.layoutControlItem3.Control = Me.memoEdit1
			Me.layoutControlItem3.Location = New System.Drawing.Point(668, 40)
			Me.layoutControlItem3.Name = "layoutControlItem3"
			Me.layoutControlItem3.Size = New System.Drawing.Size(377, 464)
			Me.layoutControlItem3.Text = "Appended content"
			Me.layoutControlItem3.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem3.TextSize = New System.Drawing.Size(101, 13)
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.textEdit1
			Me.layoutControlItem2.Location = New System.Drawing.Point(668, 0)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(279, 40)
			Me.layoutControlItem2.Text = "Heder (for TOC field)"
			Me.layoutControlItem2.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(101, 13)
			' 
			' layoutControlItem4
			' 
			Me.layoutControlItem4.Control = Me.simpleButton1
			Me.layoutControlItem4.Location = New System.Drawing.Point(668, 504)
			Me.layoutControlItem4.Name = "layoutControlItem4"
			Me.layoutControlItem4.Size = New System.Drawing.Size(377, 26)
			Me.layoutControlItem4.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem4.TextVisible = False
			' 
			' layoutControlItem5
			' 
			Me.layoutControlItem5.Control = Me.spinEdit1
			Me.layoutControlItem5.ControlAlignment = System.Drawing.ContentAlignment.BottomCenter
			Me.layoutControlItem5.Location = New System.Drawing.Point(947, 0)
			Me.layoutControlItem5.Name = "layoutControlItem5"
			Me.layoutControlItem5.Size = New System.Drawing.Size(98, 40)
			Me.layoutControlItem5.Text = "Header Level"
			Me.layoutControlItem5.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem5.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem5.TextVisible = False
			Me.layoutControlItem5.TrimClientAreaToControl = False
			' 
			' clipboardRibbonPageGroup1
			' 
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.cutItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.copyItem1)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.pasteSpecialItem1)
			Me.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1"
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
			' pasteItem1
			' 
			Me.pasteItem1.Id = 26
			Me.pasteItem1.Name = "pasteItem1"
			' 
			' cutItem1
			' 
			Me.cutItem1.Id = 27
			Me.cutItem1.Name = "cutItem1"
			' 
			' copyItem1
			' 
			Me.copyItem1.Id = 28
			Me.copyItem1.Name = "copyItem1"
			' 
			' pasteSpecialItem1
			' 
			Me.pasteSpecialItem1.Id = 29
			Me.pasteSpecialItem1.Name = "pasteSpecialItem1"
			' 
			' fontRibbonPageGroup1
			' 
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup1)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup2)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup3)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.changeTextCaseItem1)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.clearFormattingItem1)
			Me.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1"
			' 
			' changeFontNameItem1
			' 
			Me.changeFontNameItem1.Edit = Me.repositoryItemFontEdit1
			Me.changeFontNameItem1.Id = 30
			Me.changeFontNameItem1.Name = "changeFontNameItem1"
			' 
			' changeFontSizeItem1
			' 
			Me.changeFontSizeItem1.Edit = Me.repositoryItemRichEditFontSizeEdit1
			Me.changeFontSizeItem1.Id = 31
			Me.changeFontSizeItem1.Name = "changeFontSizeItem1"
			' 
			' fontSizeIncreaseItem1
			' 
			Me.fontSizeIncreaseItem1.Id = 32
			Me.fontSizeIncreaseItem1.Name = "fontSizeIncreaseItem1"
			' 
			' fontSizeDecreaseItem1
			' 
			Me.fontSizeDecreaseItem1.Id = 33
			Me.fontSizeDecreaseItem1.Name = "fontSizeDecreaseItem1"
			' 
			' toggleFontBoldItem1
			' 
			Me.toggleFontBoldItem1.Id = 34
			Me.toggleFontBoldItem1.Name = "toggleFontBoldItem1"
			' 
			' toggleFontItalicItem1
			' 
			Me.toggleFontItalicItem1.Id = 35
			Me.toggleFontItalicItem1.Name = "toggleFontItalicItem1"
			' 
			' toggleFontUnderlineItem1
			' 
			Me.toggleFontUnderlineItem1.Id = 36
			Me.toggleFontUnderlineItem1.Name = "toggleFontUnderlineItem1"
			' 
			' toggleFontDoubleUnderlineItem1
			' 
			Me.toggleFontDoubleUnderlineItem1.Id = 37
			Me.toggleFontDoubleUnderlineItem1.Name = "toggleFontDoubleUnderlineItem1"
			' 
			' toggleFontStrikeoutItem1
			' 
			Me.toggleFontStrikeoutItem1.Id = 38
			Me.toggleFontStrikeoutItem1.Name = "toggleFontStrikeoutItem1"
			' 
			' toggleFontDoubleStrikeoutItem1
			' 
			Me.toggleFontDoubleStrikeoutItem1.Id = 39
			Me.toggleFontDoubleStrikeoutItem1.Name = "toggleFontDoubleStrikeoutItem1"
			' 
			' toggleFontSuperscriptItem1
			' 
			Me.toggleFontSuperscriptItem1.Id = 40
			Me.toggleFontSuperscriptItem1.Name = "toggleFontSuperscriptItem1"
			' 
			' toggleFontSubscriptItem1
			' 
			Me.toggleFontSubscriptItem1.Id = 41
			Me.toggleFontSubscriptItem1.Name = "toggleFontSubscriptItem1"
			' 
			' changeFontColorItem1
			' 
			Me.changeFontColorItem1.Id = 42
			Me.changeFontColorItem1.Name = "changeFontColorItem1"
			' 
			' changeFontBackColorItem1
			' 
			Me.changeFontBackColorItem1.Id = 43
			Me.changeFontBackColorItem1.Name = "changeFontBackColorItem1"
			' 
			' changeTextCaseItem1
			' 
			Me.changeTextCaseItem1.Id = 44
			Me.changeTextCaseItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextUpperCaseItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.makeTextLowerCaseItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.capitalizeEachWordCaseItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.toggleTextCaseItem1)})
			Me.changeTextCaseItem1.Name = "changeTextCaseItem1"
			' 
			' makeTextUpperCaseItem1
			' 
			Me.makeTextUpperCaseItem1.Id = 45
			Me.makeTextUpperCaseItem1.Name = "makeTextUpperCaseItem1"
			' 
			' makeTextLowerCaseItem1
			' 
			Me.makeTextLowerCaseItem1.Id = 46
			Me.makeTextLowerCaseItem1.Name = "makeTextLowerCaseItem1"
			' 
			' capitalizeEachWordCaseItem1
			' 
			Me.capitalizeEachWordCaseItem1.Id = 47
			Me.capitalizeEachWordCaseItem1.Name = "capitalizeEachWordCaseItem1"
			' 
			' toggleTextCaseItem1
			' 
			Me.toggleTextCaseItem1.Id = 48
			Me.toggleTextCaseItem1.Name = "toggleTextCaseItem1"
			' 
			' clearFormattingItem1
			' 
			Me.clearFormattingItem1.Id = 49
			Me.clearFormattingItem1.Name = "clearFormattingItem1"
			' 
			' barButtonGroup1
			' 
			Me.barButtonGroup1.Id = 19
			Me.barButtonGroup1.ItemLinks.Add(Me.changeFontNameItem1)
			Me.barButtonGroup1.ItemLinks.Add(Me.changeFontSizeItem1)
			Me.barButtonGroup1.ItemLinks.Add(Me.fontSizeIncreaseItem1)
			Me.barButtonGroup1.ItemLinks.Add(Me.fontSizeDecreaseItem1)
			Me.barButtonGroup1.Name = "barButtonGroup1"
			Me.barButtonGroup1.Tag = "{97BBE334-159B-44d9-A168-0411957565E8}"
			' 
			' repositoryItemFontEdit1
			' 
			Me.repositoryItemFontEdit1.AutoHeight = False
			Me.repositoryItemFontEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemFontEdit1.Name = "repositoryItemFontEdit1"
			' 
			' repositoryItemRichEditFontSizeEdit1
			' 
			Me.repositoryItemRichEditFontSizeEdit1.AutoHeight = False
			Me.repositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemRichEditFontSizeEdit1.Control = Me.richEditControl1
			Me.repositoryItemRichEditFontSizeEdit1.Name = "repositoryItemRichEditFontSizeEdit1"
			' 
			' barButtonGroup2
			' 
			Me.barButtonGroup2.Id = 20
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
			' barButtonGroup3
			' 
			Me.barButtonGroup3.Id = 21
			Me.barButtonGroup3.ItemLinks.Add(Me.changeFontColorItem1)
			Me.barButtonGroup3.ItemLinks.Add(Me.changeFontBackColorItem1)
			Me.barButtonGroup3.Name = "barButtonGroup3"
			Me.barButtonGroup3.Tag = "{DF8C5334-EDE3-47c9-A42C-FE9A9247E180}"
			' 
			' paragraphRibbonPageGroup1
			' 
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup4)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup5)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup6)
			Me.paragraphRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup7)
			Me.paragraphRibbonPageGroup1.Name = "paragraphRibbonPageGroup1"
			' 
			' toggleBulletedListItem1
			' 
			Me.toggleBulletedListItem1.Id = 50
			Me.toggleBulletedListItem1.Name = "toggleBulletedListItem1"
			' 
			' toggleNumberingListItem1
			' 
			Me.toggleNumberingListItem1.Id = 51
			Me.toggleNumberingListItem1.Name = "toggleNumberingListItem1"
			' 
			' toggleMultiLevelListItem1
			' 
			Me.toggleMultiLevelListItem1.Id = 52
			Me.toggleMultiLevelListItem1.Name = "toggleMultiLevelListItem1"
			' 
			' decreaseIndentItem1
			' 
			Me.decreaseIndentItem1.Id = 53
			Me.decreaseIndentItem1.Name = "decreaseIndentItem1"
			' 
			' increaseIndentItem1
			' 
			Me.increaseIndentItem1.Id = 54
			Me.increaseIndentItem1.Name = "increaseIndentItem1"
			' 
			' toggleParagraphAlignmentLeftItem1
			' 
			Me.toggleParagraphAlignmentLeftItem1.Id = 55
			Me.toggleParagraphAlignmentLeftItem1.Name = "toggleParagraphAlignmentLeftItem1"
			' 
			' toggleParagraphAlignmentCenterItem1
			' 
			Me.toggleParagraphAlignmentCenterItem1.Id = 56
			Me.toggleParagraphAlignmentCenterItem1.Name = "toggleParagraphAlignmentCenterItem1"
			' 
			' toggleParagraphAlignmentRightItem1
			' 
			Me.toggleParagraphAlignmentRightItem1.Id = 57
			Me.toggleParagraphAlignmentRightItem1.Name = "toggleParagraphAlignmentRightItem1"
			' 
			' toggleParagraphAlignmentJustifyItem1
			' 
			Me.toggleParagraphAlignmentJustifyItem1.Id = 58
			Me.toggleParagraphAlignmentJustifyItem1.Name = "toggleParagraphAlignmentJustifyItem1"
			' 
			' toggleShowWhitespaceItem1
			' 
			Me.toggleShowWhitespaceItem1.Id = 59
			Me.toggleShowWhitespaceItem1.Name = "toggleShowWhitespaceItem1"
			' 
			' changeParagraphLineSpacingItem1
			' 
			Me.changeParagraphLineSpacingItem1.Id = 60
			Me.changeParagraphLineSpacingItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.setSingleParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.setSesquialteralParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.setDoubleParagraphSpacingItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.showLineSpacingFormItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingBeforeParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingBeforeParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.addSpacingAfterParagraphItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.removeSpacingAfterParagraphItem1)})
			Me.changeParagraphLineSpacingItem1.Name = "changeParagraphLineSpacingItem1"
			' 
			' setSingleParagraphSpacingItem1
			' 
			Me.setSingleParagraphSpacingItem1.Id = 61
			Me.setSingleParagraphSpacingItem1.Name = "setSingleParagraphSpacingItem1"
			' 
			' setSesquialteralParagraphSpacingItem1
			' 
			Me.setSesquialteralParagraphSpacingItem1.Id = 62
			Me.setSesquialteralParagraphSpacingItem1.Name = "setSesquialteralParagraphSpacingItem1"
			' 
			' setDoubleParagraphSpacingItem1
			' 
			Me.setDoubleParagraphSpacingItem1.Id = 63
			Me.setDoubleParagraphSpacingItem1.Name = "setDoubleParagraphSpacingItem1"
			' 
			' showLineSpacingFormItem1
			' 
			Me.showLineSpacingFormItem1.Id = 64
			Me.showLineSpacingFormItem1.Name = "showLineSpacingFormItem1"
			' 
			' addSpacingBeforeParagraphItem1
			' 
			Me.addSpacingBeforeParagraphItem1.Id = 65
			Me.addSpacingBeforeParagraphItem1.Name = "addSpacingBeforeParagraphItem1"
			' 
			' removeSpacingBeforeParagraphItem1
			' 
			Me.removeSpacingBeforeParagraphItem1.Id = 66
			Me.removeSpacingBeforeParagraphItem1.Name = "removeSpacingBeforeParagraphItem1"
			' 
			' addSpacingAfterParagraphItem1
			' 
			Me.addSpacingAfterParagraphItem1.Id = 67
			Me.addSpacingAfterParagraphItem1.Name = "addSpacingAfterParagraphItem1"
			' 
			' removeSpacingAfterParagraphItem1
			' 
			Me.removeSpacingAfterParagraphItem1.Id = 68
			Me.removeSpacingAfterParagraphItem1.Name = "removeSpacingAfterParagraphItem1"
			' 
			' changeParagraphBackColorItem1
			' 
			Me.changeParagraphBackColorItem1.Id = 69
			Me.changeParagraphBackColorItem1.Name = "changeParagraphBackColorItem1"
			' 
			' barButtonGroup4
			' 
			Me.barButtonGroup4.Id = 22
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleBulletedListItem1)
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleNumberingListItem1)
			Me.barButtonGroup4.ItemLinks.Add(Me.toggleMultiLevelListItem1)
			Me.barButtonGroup4.Name = "barButtonGroup4"
			Me.barButtonGroup4.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}"
			' 
			' barButtonGroup5
			' 
			Me.barButtonGroup5.Id = 23
			Me.barButtonGroup5.ItemLinks.Add(Me.decreaseIndentItem1)
			Me.barButtonGroup5.ItemLinks.Add(Me.increaseIndentItem1)
			Me.barButtonGroup5.ItemLinks.Add(Me.toggleShowWhitespaceItem1)
			Me.barButtonGroup5.Name = "barButtonGroup5"
			Me.barButtonGroup5.Tag = "{4747D5AB-2BEB-4ea6-9A1D-8E4FB36F1B40}"
			' 
			' barButtonGroup6
			' 
			Me.barButtonGroup6.Id = 24
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentLeftItem1)
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentCenterItem1)
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentRightItem1)
			Me.barButtonGroup6.ItemLinks.Add(Me.toggleParagraphAlignmentJustifyItem1)
			Me.barButtonGroup6.Name = "barButtonGroup6"
			Me.barButtonGroup6.Tag = "{8E89E775-996E-49a0-AADA-DE338E34732E}"
			' 
			' barButtonGroup7
			' 
			Me.barButtonGroup7.Id = 25
			Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphLineSpacingItem1)
			Me.barButtonGroup7.ItemLinks.Add(Me.changeParagraphBackColorItem1)
			Me.barButtonGroup7.Name = "barButtonGroup7"
			Me.barButtonGroup7.Tag = "{9A8DEAD8-3890-4857-A395-EC625FD02217}"
			' 
			' stylesRibbonPageGroup1
			' 
			Me.stylesRibbonPageGroup1.Glyph = (CType(resources.GetObject("stylesRibbonPageGroup1.Glyph"), System.Drawing.Image))
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
			Me.galleryChangeStyleItem1.Id = 70
			Me.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1"
			' 
			' editingRibbonPageGroup1
			' 
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.findItem1)
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.replaceItem1)
			Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
			' 
			' findItem1
			' 
			Me.findItem1.Id = 71
			Me.findItem1.Name = "findItem1"
			' 
			' replaceItem1
			' 
			Me.replaceItem1.Id = 72
			Me.replaceItem1.Name = "replaceItem1"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(1065, 693)
			Me.Controls.Add(Me.layoutControl1)
			Me.Controls.Add(Me.ribbonControl1)
			Me.Name = "Form1"
			Me.Ribbon = Me.ribbonControl1
			Me.Text = "Form1"
'			Me.Load += New System.EventHandler(Me.Form1_Load);
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.spinEdit1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.memoEdit1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEdit1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
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
		Private barButtonItem1 As DevExpress.XtraBars.BarButtonItem
		Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
		Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
		Private barButtonItem2 As DevExpress.XtraBars.BarButtonItem
		Private insertMergeFieldItem1 As DevExpress.XtraRichEdit.UI.InsertMergeFieldItem
		Private showAllFieldCodesItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldCodesItem
		Private showAllFieldResultsItem1 As DevExpress.XtraRichEdit.UI.ShowAllFieldResultsItem
		Private toggleViewMergedDataItem1 As DevExpress.XtraRichEdit.UI.ToggleViewMergedDataItem
		Private mailingsRibbonPage1 As DevExpress.XtraRichEdit.UI.MailingsRibbonPage
		Private mailMergeRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.MailMergeRibbonPageGroup
		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private WithEvents simpleButton1 As DevExpress.XtraEditors.SimpleButton
		Private memoEdit1 As DevExpress.XtraEditors.MemoEdit
		Private textEdit1 As DevExpress.XtraEditors.TextEdit
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem3 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem4 As DevExpress.XtraLayout.LayoutControlItem
		Private spinEdit1 As DevExpress.XtraEditors.SpinEdit
		Private layoutControlItem5 As DevExpress.XtraLayout.LayoutControlItem
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
		Private changeFontBackColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontBackColorItem
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
		Private homeRibbonPage1 As DevExpress.XtraRichEdit.UI.HomeRibbonPage
		Private clipboardRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ClipboardRibbonPageGroup
		Private fontRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.FontRibbonPageGroup
		Private paragraphRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ParagraphRibbonPageGroup
		Private stylesRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.StylesRibbonPageGroup
		Private editingRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.EditingRibbonPageGroup
	End Class
End Namespace

