Imports System
Imports DevExpress.XtraBars

Namespace LineNumberingExample
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
			Me.switchToSimpleViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem()
			Me.switchToDraftViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem()
			Me.switchToPrintLayoutViewItem1 = New DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem()
			Me.toggleShowHorizontalRulerItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem()
			Me.toggleShowVerticalRulerItem1 = New DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem()
			Me.zoomOutItem1 = New DevExpress.XtraRichEdit.UI.ZoomOutItem()
			Me.zoomInItem1 = New DevExpress.XtraRichEdit.UI.ZoomInItem()
			Me.barCheckLineNumberBackColoring = New DevExpress.XtraBars.BarCheckItem()
			Me.resultBarStaticItem = New DevExpress.XtraBars.BarStaticItem()
			Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
			Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
			Me.infoRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.InfoRibbonPageGroup()
			Me.pageLayoutRibbonPage1 = New DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage()
			Me.pageSetupRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup()
			Me.pageBackgroundRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup()
			Me.viewRibbonPage1 = New DevExpress.XtraRichEdit.UI.ViewRibbonPage()
			Me.documentViewsRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup()
			Me.showRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup()
			Me.zoomRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup()
			Me.exampleRibbonPage1 = New DevExpress.XtraBars.Ribbon.RibbonPage()
			Me.optionsExampleRibbonPageGroup = New DevExpress.XtraBars.Ribbon.RibbonPageGroup()
			Me.resultExampleRibbonPageGroup = New DevExpress.XtraBars.Ribbon.RibbonPageGroup()
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(0, 139)
			Me.richEditControl1.MenuManager = Me.ribbonControl1
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(784, 422)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
			' 
			' ribbonControl1
			' 
			Me.ribbonControl1.ExpandCollapseItem.Id = 0
			Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.undoItem1, Me.redoItem1, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.showDocumentPropertiesFormItem1, Me.changeSectionPageMarginsItem1, Me.setNormalSectionPageMarginsItem1, Me.setNarrowSectionPageMarginsItem1, Me.setModerateSectionPageMarginsItem1, Me.setWideSectionPageMarginsItem1, Me.showPageMarginsSetupFormItem1, Me.changeSectionPageOrientationItem1, Me.setPortraitPageOrientationItem1, Me.setLandscapePageOrientationItem1, Me.changeSectionPaperKindItem1, Me.changeSectionColumnsItem1, Me.setSectionOneColumnItem1, Me.setSectionTwoColumnsItem1, Me.setSectionThreeColumnsItem1, Me.showColumnsSetupFormItem1, Me.insertBreakItem1, Me.insertPageBreakItem1, Me.insertColumnBreakItem1, Me.insertSectionBreakNextPageItem1, Me.insertSectionBreakEvenPageItem1, Me.insertSectionBreakOddPageItem1, Me.changeSectionLineNumberingItem1, Me.setSectionLineNumberingNoneItem1, Me.setSectionLineNumberingContinuousItem1, Me.setSectionLineNumberingRestartNewPageItem1, Me.setSectionLineNumberingRestartNewSectionItem1, Me.toggleParagraphSuppressLineNumbersItem1, Me.showLineNumberingFormItem1, Me.changePageColorItem1, Me.switchToSimpleViewItem1, Me.switchToDraftViewItem1, Me.switchToPrintLayoutViewItem1, Me.toggleShowHorizontalRulerItem1, Me.toggleShowVerticalRulerItem1, Me.zoomOutItem1, Me.zoomInItem1, Me.barCheckLineNumberBackColoring, Me.resultBarStaticItem})
			Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl1.MaxItemId = 49
			Me.ribbonControl1.Name = "ribbonControl1"
			Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1, Me.pageLayoutRibbonPage1, Me.viewRibbonPage1, Me.exampleRibbonPage1})
			Me.ribbonControl1.Size = New System.Drawing.Size(784, 139)
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
			' changeSectionPageMarginsItem1
			' 
			Me.changeSectionPageMarginsItem1.Id = 11
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
			Me.setNormalSectionPageMarginsItem1.Id = 12
			Me.setNormalSectionPageMarginsItem1.Name = "setNormalSectionPageMarginsItem1"
			' 
			' setNarrowSectionPageMarginsItem1
			' 
			Me.setNarrowSectionPageMarginsItem1.Id = 13
			Me.setNarrowSectionPageMarginsItem1.Name = "setNarrowSectionPageMarginsItem1"
			' 
			' setModerateSectionPageMarginsItem1
			' 
			Me.setModerateSectionPageMarginsItem1.Id = 14
			Me.setModerateSectionPageMarginsItem1.Name = "setModerateSectionPageMarginsItem1"
			' 
			' setWideSectionPageMarginsItem1
			' 
			Me.setWideSectionPageMarginsItem1.Id = 15
			Me.setWideSectionPageMarginsItem1.Name = "setWideSectionPageMarginsItem1"
			' 
			' showPageMarginsSetupFormItem1
			' 
			Me.showPageMarginsSetupFormItem1.Id = 16
			Me.showPageMarginsSetupFormItem1.Name = "showPageMarginsSetupFormItem1"
			' 
			' changeSectionPageOrientationItem1
			' 
			Me.changeSectionPageOrientationItem1.Id = 17
			Me.changeSectionPageOrientationItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.setPortraitPageOrientationItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.setLandscapePageOrientationItem1)
			})
			Me.changeSectionPageOrientationItem1.Name = "changeSectionPageOrientationItem1"
			' 
			' setPortraitPageOrientationItem1
			' 
			Me.setPortraitPageOrientationItem1.Id = 18
			Me.setPortraitPageOrientationItem1.Name = "setPortraitPageOrientationItem1"
			' 
			' setLandscapePageOrientationItem1
			' 
			Me.setLandscapePageOrientationItem1.Id = 19
			Me.setLandscapePageOrientationItem1.Name = "setLandscapePageOrientationItem1"
			' 
			' changeSectionPaperKindItem1
			' 
			Me.changeSectionPaperKindItem1.Id = 20
			Me.changeSectionPaperKindItem1.Name = "changeSectionPaperKindItem1"
			' 
			' changeSectionColumnsItem1
			' 
			Me.changeSectionColumnsItem1.Id = 21
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
			Me.setSectionOneColumnItem1.Id = 22
			Me.setSectionOneColumnItem1.Name = "setSectionOneColumnItem1"
			' 
			' setSectionTwoColumnsItem1
			' 
			Me.setSectionTwoColumnsItem1.Id = 23
			Me.setSectionTwoColumnsItem1.Name = "setSectionTwoColumnsItem1"
			' 
			' setSectionThreeColumnsItem1
			' 
			Me.setSectionThreeColumnsItem1.Id = 24
			Me.setSectionThreeColumnsItem1.Name = "setSectionThreeColumnsItem1"
			' 
			' showColumnsSetupFormItem1
			' 
			Me.showColumnsSetupFormItem1.Id = 25
			Me.showColumnsSetupFormItem1.Name = "showColumnsSetupFormItem1"
			' 
			' insertBreakItem1
			' 
			Me.insertBreakItem1.Id = 26
			Me.insertBreakItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.insertPageBreakItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "B", ""),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertColumnBreakItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakNextPageItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakEvenPageItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.insertSectionBreakOddPageItem1)
			})
			Me.insertBreakItem1.Name = "insertBreakItem1"
			' 
			' insertPageBreakItem1
			' 
			Me.insertPageBreakItem1.Id = 27
			Me.insertPageBreakItem1.Name = "insertPageBreakItem1"
			' 
			' insertColumnBreakItem1
			' 
			Me.insertColumnBreakItem1.Id = 28
			Me.insertColumnBreakItem1.Name = "insertColumnBreakItem1"
			' 
			' insertSectionBreakNextPageItem1
			' 
			Me.insertSectionBreakNextPageItem1.Id = 29
			Me.insertSectionBreakNextPageItem1.Name = "insertSectionBreakNextPageItem1"
			' 
			' insertSectionBreakEvenPageItem1
			' 
			Me.insertSectionBreakEvenPageItem1.Id = 30
			Me.insertSectionBreakEvenPageItem1.Name = "insertSectionBreakEvenPageItem1"
			' 
			' insertSectionBreakOddPageItem1
			' 
			Me.insertSectionBreakOddPageItem1.Id = 31
			Me.insertSectionBreakOddPageItem1.Name = "insertSectionBreakOddPageItem1"
			' 
			' changeSectionLineNumberingItem1
			' 
			Me.changeSectionLineNumberingItem1.Id = 32
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
			Me.setSectionLineNumberingNoneItem1.Id = 33
			Me.setSectionLineNumberingNoneItem1.Name = "setSectionLineNumberingNoneItem1"
			' 
			' setSectionLineNumberingContinuousItem1
			' 
			Me.setSectionLineNumberingContinuousItem1.Id = 34
			Me.setSectionLineNumberingContinuousItem1.Name = "setSectionLineNumberingContinuousItem1"
			' 
			' setSectionLineNumberingRestartNewPageItem1
			' 
			Me.setSectionLineNumberingRestartNewPageItem1.Id = 35
			Me.setSectionLineNumberingRestartNewPageItem1.Name = "setSectionLineNumberingRestartNewPageItem1"
			' 
			' setSectionLineNumberingRestartNewSectionItem1
			' 
			Me.setSectionLineNumberingRestartNewSectionItem1.Id = 36
			Me.setSectionLineNumberingRestartNewSectionItem1.Name = "setSectionLineNumberingRestartNewSectionItem1"
			' 
			' toggleParagraphSuppressLineNumbersItem1
			' 
			Me.toggleParagraphSuppressLineNumbersItem1.Id = 37
			Me.toggleParagraphSuppressLineNumbersItem1.Name = "toggleParagraphSuppressLineNumbersItem1"
			' 
			' showLineNumberingFormItem1
			' 
			Me.showLineNumberingFormItem1.Id = 38
			Me.showLineNumberingFormItem1.Name = "showLineNumberingFormItem1"
			' 
			' changePageColorItem1
			' 
			Me.changePageColorItem1.Id = 39
			Me.changePageColorItem1.Name = "changePageColorItem1"
			' 
			' switchToSimpleViewItem1
			' 
			Me.switchToSimpleViewItem1.Id = 40
			Me.switchToSimpleViewItem1.Name = "switchToSimpleViewItem1"
			' 
			' switchToDraftViewItem1
			' 
			Me.switchToDraftViewItem1.Id = 41
			Me.switchToDraftViewItem1.Name = "switchToDraftViewItem1"
			' 
			' switchToPrintLayoutViewItem1
			' 
			Me.switchToPrintLayoutViewItem1.Id = 42
			Me.switchToPrintLayoutViewItem1.Name = "switchToPrintLayoutViewItem1"
			' 
			' toggleShowHorizontalRulerItem1
			' 
			Me.toggleShowHorizontalRulerItem1.Id = 43
			Me.toggleShowHorizontalRulerItem1.Name = "toggleShowHorizontalRulerItem1"
			' 
			' toggleShowVerticalRulerItem1
			' 
			Me.toggleShowVerticalRulerItem1.Id = 44
			Me.toggleShowVerticalRulerItem1.Name = "toggleShowVerticalRulerItem1"
			' 
			' zoomOutItem1
			' 
			Me.zoomOutItem1.Id = 45
			Me.zoomOutItem1.Name = "zoomOutItem1"
			' 
			' zoomInItem1
			' 
			Me.zoomInItem1.Id = 46
			Me.zoomInItem1.Name = "zoomInItem1"
			' 
			' barCheckLineNumberBackColoring
			' 
			Me.barCheckLineNumberBackColoring.Caption = "Line Number Column Coloring"
			Me.barCheckLineNumberBackColoring.CheckStyle = DevExpress.XtraBars.BarCheckStyles.Radio
			Me.barCheckLineNumberBackColoring.Id = 47
			Me.barCheckLineNumberBackColoring.ImageOptions.Image = (CType(resources.GetObject("barCheckLineNumberBackColoring.ImageOptions.Image"), System.Drawing.Image))
			Me.barCheckLineNumberBackColoring.ImageOptions.LargeImage = (CType(resources.GetObject("barCheckLineNumberBackColoring.ImageOptions.LargeImage"), System.Drawing.Image))
			Me.barCheckLineNumberBackColoring.Name = "barCheckLineNumberBackColoring"
			Me.barCheckLineNumberBackColoring.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.barCheckLineNumberBackColoring.CheckedChanged += new DevExpress.XtraBars.ItemClickEventHandler(this.barCheckLineNumberBackColoring_CheckedChanged);
			' 
			' resultBarStaticItem
			' 
			Me.resultBarStaticItem.Caption = "lineNumberBarStaticItem"
			Me.resultBarStaticItem.Id = 48
			Me.resultBarStaticItem.Name = "resultBarStaticItem"
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
			' 
			' showRibbonPageGroup1
			' 
			Me.showRibbonPageGroup1.ItemLinks.Add(Me.toggleShowHorizontalRulerItem1)
			Me.showRibbonPageGroup1.ItemLinks.Add(Me.toggleShowVerticalRulerItem1)
			Me.showRibbonPageGroup1.Name = "showRibbonPageGroup1"
			' 
			' zoomRibbonPageGroup1
			' 
			Me.zoomRibbonPageGroup1.ItemLinks.Add(Me.zoomOutItem1)
			Me.zoomRibbonPageGroup1.ItemLinks.Add(Me.zoomInItem1)
			Me.zoomRibbonPageGroup1.Name = "zoomRibbonPageGroup1"
			' 
			' exampleRibbonPage1
			' 
			Me.exampleRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.optionsExampleRibbonPageGroup, Me.resultExampleRibbonPageGroup})
			Me.exampleRibbonPage1.Name = "exampleRibbonPage1"
			Me.exampleRibbonPage1.Text = "Example"
			' 
			' optionsExampleRibbonPageGroup
			' 
			Me.optionsExampleRibbonPageGroup.ItemLinks.Add(Me.barCheckLineNumberBackColoring)
			Me.optionsExampleRibbonPageGroup.Name = "optionsExampleRibbonPageGroup"
			Me.optionsExampleRibbonPageGroup.Text = "Options"
			' 
			' resultExampleRibbonPageGroup
			' 
			Me.resultExampleRibbonPageGroup.ItemLinks.Add(Me.resultBarStaticItem)
			Me.resultExampleRibbonPageGroup.Name = "resultExampleRibbonPageGroup"
			Me.resultExampleRibbonPageGroup.Text = "Statistics"
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
			Me.richEditBarController1.BarItems.Add(Me.switchToSimpleViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.switchToDraftViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.switchToPrintLayoutViewItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleShowHorizontalRulerItem1)
			Me.richEditBarController1.BarItems.Add(Me.toggleShowVerticalRulerItem1)
			Me.richEditBarController1.BarItems.Add(Me.zoomOutItem1)
			Me.richEditBarController1.BarItems.Add(Me.zoomInItem1)
			Me.richEditBarController1.Control = Me.richEditControl1
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(784, 561)
			Me.Controls.Add(Me.richEditControl1)
			Me.Controls.Add(Me.ribbonControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.Load += new System.EventHandler(this.Form1_Load);
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
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
		Private switchToSimpleViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToSimpleViewItem
		Private switchToDraftViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToDraftViewItem
		Private switchToPrintLayoutViewItem1 As DevExpress.XtraRichEdit.UI.SwitchToPrintLayoutViewItem
		Private toggleShowHorizontalRulerItem1 As DevExpress.XtraRichEdit.UI.ToggleShowHorizontalRulerItem
		Private toggleShowVerticalRulerItem1 As DevExpress.XtraRichEdit.UI.ToggleShowVerticalRulerItem
		Private zoomOutItem1 As DevExpress.XtraRichEdit.UI.ZoomOutItem
		Private zoomInItem1 As DevExpress.XtraRichEdit.UI.ZoomInItem
		Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
		Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
		Private infoRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.InfoRibbonPageGroup
		Private pageLayoutRibbonPage1 As DevExpress.XtraRichEdit.UI.PageLayoutRibbonPage
		Private pageSetupRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PageSetupRibbonPageGroup
		Private pageBackgroundRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.PageBackgroundRibbonPageGroup
		Private viewRibbonPage1 As DevExpress.XtraRichEdit.UI.ViewRibbonPage
		Private documentViewsRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.DocumentViewsRibbonPageGroup
		Private showRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ShowRibbonPageGroup
		Private zoomRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.ZoomRibbonPageGroup
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
		Private WithEvents barCheckLineNumberBackColoring As DevExpress.XtraBars.BarCheckItem
		Private exampleRibbonPage1 As DevExpress.XtraBars.Ribbon.RibbonPage
		Private optionsExampleRibbonPageGroup As DevExpress.XtraBars.Ribbon.RibbonPageGroup
		Private resultExampleRibbonPageGroup As DevExpress.XtraBars.Ribbon.RibbonPageGroup
		Private resultBarStaticItem As BarStaticItem
	End Class
End Namespace

