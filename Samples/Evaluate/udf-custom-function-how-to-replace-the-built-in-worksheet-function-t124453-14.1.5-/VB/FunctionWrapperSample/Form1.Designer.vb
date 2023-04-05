Imports Microsoft.VisualBasic
Imports System
Namespace FunctionWrapperSample
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
			Dim reduceOperation1 As New DevExpress.XtraBars.Ribbon.ReduceOperation()
			Dim galleryItemGroup1 As New DevExpress.XtraBars.Ribbon.GalleryItemGroup()
			Dim spreadsheetCommandGalleryItem1 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem2 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem3 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem4 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem5 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem6 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem7 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem8 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem9 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem10 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem11 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup1 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem12 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem13 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem14 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem15 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem16 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem17 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup2 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem18 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem19 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem20 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem21 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem22 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem23 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup3 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem24 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem25 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem26 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem27 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem28 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem29 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem30 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem31 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem32 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem33 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem34 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem35 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup4 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem36 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem37 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem38 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem39 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem40 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem41 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem42 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup5 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem43 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem44 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem45 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem46 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem47 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup6 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem48 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem49 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem50 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItemGroup7 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItemGroup()
			Dim spreadsheetCommandGalleryItem51 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem52 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem53 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem54 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Dim spreadsheetCommandGalleryItem55 As New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandGalleryItem()
			Me.spreadsheetControl1 = New DevExpress.XtraSpreadsheet.SpreadsheetControl()
			Me.spreadsheetFormulaBarControl1 = New DevExpress.XtraSpreadsheet.SpreadsheetFormulaBarControl()
			Me.spreadsheetNameBoxControl1 = New DevExpress.XtraSpreadsheet.SpreadsheetNameBoxControl()
			Me.splitContainerControl1 = New DevExpress.XtraEditors.SplitContainerControl()
			Me.splitterControl1 = New DevExpress.XtraEditors.SplitterControl()
			Me.ribbonControl1 = New DevExpress.XtraBars.Ribbon.RibbonControl()
			Me.spreadsheetBarController1 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetBarController()
			Me.commonRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.CommonRibbonPageGroup()
			Me.fileRibbonPage1 = New DevExpress.XtraSpreadsheet.UI.FileRibbonPage()
			Me.spreadsheetCommandBarButtonItem1 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem2 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem3 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem4 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem5 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem6 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem7 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem8 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem9 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.clipboardRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.ClipboardRibbonPageGroup()
			Me.homeRibbonPage1 = New DevExpress.XtraSpreadsheet.UI.HomeRibbonPage()
			Me.spreadsheetCommandBarButtonItem10 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem11 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem12 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem13 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.fontRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.FontRibbonPageGroup()
			Me.changeFontNameItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeFontNameItem()
			Me.changeFontSizeItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeFontSizeItem()
			Me.spreadsheetCommandBarButtonItem14 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem15 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarCheckItem1 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem2 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem3 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem4 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarSubItem1 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem16 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem17 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem18 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem19 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem20 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem21 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem22 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem23 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem24 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem25 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem26 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem27 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem28 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.changeBorderLineColorItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeBorderLineColorItem()
			Me.changeBorderLineStyleItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeBorderLineStyleItem()
			Me.commandBarGalleryDropDown1 = New DevExpress.XtraBars.Commands.CommandBarGalleryDropDown(Me.components)
			Me.changeCellFillColorItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeCellFillColorItem()
			Me.changeFontColorItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeFontColorItem()
			Me.barButtonGroup1 = New DevExpress.XtraBars.BarButtonGroup()
			Me.repositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
			Me.repositoryItemSpreadsheetFontSizeEdit1 = New DevExpress.XtraSpreadsheet.Design.RepositoryItemSpreadsheetFontSizeEdit()
			Me.barButtonGroup2 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup3 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup4 = New DevExpress.XtraBars.BarButtonGroup()
			Me.alignmentRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.AlignmentRibbonPageGroup()
			Me.spreadsheetCommandBarCheckItem5 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem6 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem7 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem8 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem9 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarCheckItem10 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarButtonItem29 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem30 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarCheckItem11 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarSubItem2 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarCheckItem12 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			Me.spreadsheetCommandBarButtonItem31 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem32 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem33 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.barButtonGroup5 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup6 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup7 = New DevExpress.XtraBars.BarButtonGroup()
			Me.numberRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.NumberRibbonPageGroup()
			Me.changeNumberFormatItem1 = New DevExpress.XtraSpreadsheet.UI.ChangeNumberFormatItem()
			Me.spreadsheetCommandBarSubItem3 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem34 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem35 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem36 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem37 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem38 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem39 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem40 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem41 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem42 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.barButtonGroup8 = New DevExpress.XtraBars.BarButtonGroup()
			Me.repositoryItemPopupGalleryEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemPopupGalleryEdit()
			Me.barButtonGroup9 = New DevExpress.XtraBars.BarButtonGroup()
			Me.barButtonGroup10 = New DevExpress.XtraBars.BarButtonGroup()
			Me.stylesRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.StylesRibbonPageGroup()
			Me.spreadsheetCommandBarSubItem4 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarSubItem5 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem43 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem44 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem45 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem46 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem47 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem48 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem49 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem6 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem50 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem51 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem52 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem53 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem54 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem55 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem()
			Me.commandBarGalleryDropDown2 = New DevExpress.XtraBars.Commands.CommandBarGalleryDropDown(Me.components)
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem()
			Me.commandBarGalleryDropDown3 = New DevExpress.XtraBars.Commands.CommandBarGalleryDropDown(Me.components)
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem()
			Me.commandBarGalleryDropDown4 = New DevExpress.XtraBars.Commands.CommandBarGalleryDropDown(Me.components)
			Me.spreadsheetCommandBarSubItem7 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem56 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem57 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.galleryFormatAsTableItem1 = New DevExpress.XtraSpreadsheet.UI.GalleryFormatAsTableItem()
			Me.commandBarGalleryDropDown5 = New DevExpress.XtraBars.Commands.CommandBarGalleryDropDown(Me.components)
			Me.galleryChangeStyleItem1 = New DevExpress.XtraSpreadsheet.UI.GalleryChangeStyleItem()
			Me.cellsRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.CellsRibbonPageGroup()
			Me.spreadsheetCommandBarSubItem8 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem58 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem59 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem60 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem9 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem61 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem62 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem63 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem10 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem64 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem65 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem11 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem66 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem67 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem68 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem69 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem70 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem71 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem72 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.editingRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.EditingRibbonPageGroup()
			Me.spreadsheetCommandBarSubItem12 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem73 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem74 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem75 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem76 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem77 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem13 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem78 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem79 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem80 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem81 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarSubItem14 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem82 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem83 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem84 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem85 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem86 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem87 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.functionLibraryRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.FunctionLibraryRibbonPageGroup()
			Me.formulasRibbonPage1 = New DevExpress.XtraSpreadsheet.UI.FormulasRibbonPage()
			Me.spreadsheetCommandBarSubItem15 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.spreadsheetCommandBarButtonItem88 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem89 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem90 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem91 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.spreadsheetCommandBarButtonItem92 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem()
			Me.functionsFinancialItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsFinancialItem()
			Me.functionsLogicalItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsLogicalItem()
			Me.functionsTextItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsTextItem()
			Me.functionsDateAndTimeItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsDateAndTimeItem()
			Me.functionsLookupAndReferenceItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsLookupAndReferenceItem()
			Me.functionsMathAndTrigonometryItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsMathAndTrigonometryItem()
			Me.spreadsheetCommandBarSubItem16 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem()
			Me.functionsStatisticalItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsStatisticalItem()
			Me.functionsEngineeringItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsEngineeringItem()
			Me.functionsInformationItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsInformationItem()
			Me.functionsCompatibilityItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsCompatibilityItem()
			Me.functionsWebItem1 = New DevExpress.XtraSpreadsheet.UI.FunctionsWebItem()
			Me.formulaAuditingRibbonPageGroup1 = New DevExpress.XtraSpreadsheet.UI.FormulaAuditingRibbonPageGroup()
			Me.spreadsheetCommandBarCheckItem13 = New DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem()
			CType(Me.spreadsheetNameBoxControl1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.splitContainerControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.splitContainerControl1.SuspendLayout()
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.spreadsheetBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.commandBarGalleryDropDown1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemSpreadsheetFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.repositoryItemPopupGalleryEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.commandBarGalleryDropDown2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.commandBarGalleryDropDown3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.commandBarGalleryDropDown4, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.commandBarGalleryDropDown5, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' spreadsheetControl1
			' 
			Me.spreadsheetControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.spreadsheetControl1.Location = New System.Drawing.Point(0, 167)
			Me.spreadsheetControl1.MenuManager = Me.ribbonControl1
			Me.spreadsheetControl1.Name = "spreadsheetControl1"
			Me.spreadsheetControl1.Size = New System.Drawing.Size(941, 399)
			Me.spreadsheetControl1.TabIndex = 0
			Me.spreadsheetControl1.Text = "spreadsheetControl1"
			' 
			' spreadsheetFormulaBarControl1
			' 
			Me.spreadsheetFormulaBarControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.spreadsheetFormulaBarControl1.Location = New System.Drawing.Point(0, 0)
			Me.spreadsheetFormulaBarControl1.MinimumSize = New System.Drawing.Size(0, 20)
			Me.spreadsheetFormulaBarControl1.Name = "spreadsheetFormulaBarControl1"
			Me.spreadsheetFormulaBarControl1.Size = New System.Drawing.Size(791, 20)
			Me.spreadsheetFormulaBarControl1.SpreadsheetControl = Me.spreadsheetControl1
			Me.spreadsheetFormulaBarControl1.TabIndex = 0
			' 
			' spreadsheetNameBoxControl1
			' 
			Me.spreadsheetNameBoxControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.spreadsheetNameBoxControl1.EditValue = "A1"
			Me.spreadsheetNameBoxControl1.Location = New System.Drawing.Point(0, 0)
			Me.spreadsheetNameBoxControl1.Name = "spreadsheetNameBoxControl1"
			Me.spreadsheetNameBoxControl1.Properties.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.spreadsheetNameBoxControl1.Size = New System.Drawing.Size(145, 20)
			Me.spreadsheetNameBoxControl1.SpreadsheetControl = Me.spreadsheetControl1
			Me.spreadsheetNameBoxControl1.TabIndex = 0
			' 
			' splitContainerControl1
			' 
			Me.splitContainerControl1.Dock = System.Windows.Forms.DockStyle.Top
			Me.splitContainerControl1.Location = New System.Drawing.Point(0, 142)
			Me.splitContainerControl1.Name = "splitContainerControl1"
			Me.splitContainerControl1.Panel1.Controls.Add(Me.spreadsheetNameBoxControl1)
			Me.splitContainerControl1.Panel2.Controls.Add(Me.spreadsheetFormulaBarControl1)
			Me.splitContainerControl1.Size = New System.Drawing.Size(941, 20)
			Me.splitContainerControl1.SplitterPosition = 145
			Me.splitContainerControl1.TabIndex = 2
			' 
			' splitterControl1
			' 
			Me.splitterControl1.Dock = System.Windows.Forms.DockStyle.Top
			Me.splitterControl1.Location = New System.Drawing.Point(0, 162)
			Me.splitterControl1.MinSize = 20
			Me.splitterControl1.Name = "splitterControl1"
			Me.splitterControl1.Size = New System.Drawing.Size(941, 5)
			Me.splitterControl1.TabIndex = 1
			Me.splitterControl1.TabStop = False
			' 
			' ribbonControl1
			' 
			Me.ribbonControl1.ExpandCollapseItem.Id = 0
			Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.spreadsheetCommandBarButtonItem1, Me.spreadsheetCommandBarButtonItem2, Me.spreadsheetCommandBarButtonItem3, Me.spreadsheetCommandBarButtonItem4, Me.spreadsheetCommandBarButtonItem5, Me.spreadsheetCommandBarButtonItem6, Me.spreadsheetCommandBarButtonItem7, Me.spreadsheetCommandBarButtonItem8, Me.spreadsheetCommandBarButtonItem9, Me.spreadsheetCommandBarButtonItem10, Me.spreadsheetCommandBarButtonItem11, Me.spreadsheetCommandBarButtonItem12, Me.spreadsheetCommandBarButtonItem13, Me.barButtonGroup1, Me.changeFontNameItem1, Me.changeFontSizeItem1, Me.spreadsheetCommandBarButtonItem14, Me.spreadsheetCommandBarButtonItem15, Me.barButtonGroup2, Me.spreadsheetCommandBarCheckItem1, Me.spreadsheetCommandBarCheckItem2, Me.spreadsheetCommandBarCheckItem3, Me.spreadsheetCommandBarCheckItem4, Me.barButtonGroup3, Me.spreadsheetCommandBarSubItem1, Me.spreadsheetCommandBarButtonItem16, Me.spreadsheetCommandBarButtonItem17, Me.spreadsheetCommandBarButtonItem18, Me.spreadsheetCommandBarButtonItem19, Me.spreadsheetCommandBarButtonItem20, Me.spreadsheetCommandBarButtonItem21, Me.spreadsheetCommandBarButtonItem22, Me.spreadsheetCommandBarButtonItem23, Me.spreadsheetCommandBarButtonItem24, Me.spreadsheetCommandBarButtonItem25, Me.spreadsheetCommandBarButtonItem26, Me.spreadsheetCommandBarButtonItem27, Me.spreadsheetCommandBarButtonItem28, Me.changeBorderLineColorItem1, Me.changeBorderLineStyleItem1, Me.barButtonGroup4, Me.changeCellFillColorItem1, Me.changeFontColorItem1, Me.barButtonGroup5, Me.spreadsheetCommandBarCheckItem5, Me.spreadsheetCommandBarCheckItem6, Me.spreadsheetCommandBarCheckItem7, Me.barButtonGroup6, Me.spreadsheetCommandBarCheckItem8, Me.spreadsheetCommandBarCheckItem9, Me.spreadsheetCommandBarCheckItem10, Me.barButtonGroup7, Me.spreadsheetCommandBarButtonItem29, Me.spreadsheetCommandBarButtonItem30, Me.spreadsheetCommandBarCheckItem11, Me.spreadsheetCommandBarSubItem2, Me.spreadsheetCommandBarCheckItem12, Me.spreadsheetCommandBarButtonItem31, Me.spreadsheetCommandBarButtonItem32, Me.spreadsheetCommandBarButtonItem33, Me.barButtonGroup8, Me.changeNumberFormatItem1, Me.barButtonGroup9, Me.spreadsheetCommandBarSubItem3, Me.spreadsheetCommandBarButtonItem34, Me.spreadsheetCommandBarButtonItem35, Me.spreadsheetCommandBarButtonItem36, Me.spreadsheetCommandBarButtonItem37, Me.spreadsheetCommandBarButtonItem38, Me.spreadsheetCommandBarButtonItem39, Me.spreadsheetCommandBarButtonItem40, Me.barButtonGroup10, Me.spreadsheetCommandBarButtonItem41, Me.spreadsheetCommandBarButtonItem42, Me.spreadsheetCommandBarSubItem4, Me.spreadsheetCommandBarButtonItem43, Me.spreadsheetCommandBarButtonItem44, Me.spreadsheetCommandBarButtonItem45, Me.spreadsheetCommandBarButtonItem46, Me.spreadsheetCommandBarButtonItem47, Me.spreadsheetCommandBarButtonItem48, Me.spreadsheetCommandBarButtonItem49, Me.spreadsheetCommandBarSubItem5, Me.spreadsheetCommandBarButtonItem50, Me.spreadsheetCommandBarButtonItem51, Me.spreadsheetCommandBarButtonItem52, Me.spreadsheetCommandBarButtonItem53, Me.spreadsheetCommandBarButtonItem54, Me.spreadsheetCommandBarButtonItem55, Me.spreadsheetCommandBarSubItem6, Me.spreadsheetCommandBarButtonGalleryDropDownItem1, Me.spreadsheetCommandBarButtonGalleryDropDownItem2, Me.spreadsheetCommandBarButtonGalleryDropDownItem3, Me.spreadsheetCommandBarButtonItem56, Me.spreadsheetCommandBarButtonItem57, Me.spreadsheetCommandBarSubItem7, Me.galleryFormatAsTableItem1, Me.galleryChangeStyleItem1, Me.spreadsheetCommandBarSubItem8, Me.spreadsheetCommandBarButtonItem58, Me.spreadsheetCommandBarButtonItem59, Me.spreadsheetCommandBarButtonItem60, Me.spreadsheetCommandBarSubItem9, Me.spreadsheetCommandBarButtonItem61, Me.spreadsheetCommandBarButtonItem62, Me.spreadsheetCommandBarButtonItem63, Me.spreadsheetCommandBarSubItem10, Me.spreadsheetCommandBarButtonItem64, Me.spreadsheetCommandBarButtonItem65, Me.spreadsheetCommandBarButtonItem66, Me.spreadsheetCommandBarButtonItem67, Me.spreadsheetCommandBarButtonItem68, Me.spreadsheetCommandBarButtonItem69, Me.spreadsheetCommandBarButtonItem70, Me.spreadsheetCommandBarButtonItem71, Me.spreadsheetCommandBarSubItem11, Me.spreadsheetCommandBarButtonItem72, Me.spreadsheetCommandBarSubItem12, Me.spreadsheetCommandBarButtonItem73, Me.spreadsheetCommandBarButtonItem74, Me.spreadsheetCommandBarButtonItem75, Me.spreadsheetCommandBarButtonItem76, Me.spreadsheetCommandBarButtonItem77, Me.spreadsheetCommandBarSubItem13, Me.spreadsheetCommandBarButtonItem78, Me.spreadsheetCommandBarButtonItem79, Me.spreadsheetCommandBarButtonItem80, Me.spreadsheetCommandBarButtonItem81, Me.spreadsheetCommandBarSubItem14, Me.spreadsheetCommandBarButtonItem82, Me.spreadsheetCommandBarButtonItem83, Me.spreadsheetCommandBarButtonItem84, Me.spreadsheetCommandBarButtonItem85, Me.spreadsheetCommandBarButtonItem86, Me.spreadsheetCommandBarButtonItem87, Me.spreadsheetCommandBarSubItem15, Me.functionsFinancialItem1, Me.functionsLogicalItem1, Me.functionsTextItem1, Me.functionsDateAndTimeItem1, Me.functionsLookupAndReferenceItem1, Me.functionsMathAndTrigonometryItem1, Me.spreadsheetCommandBarSubItem16, Me.functionsStatisticalItem1, Me.functionsEngineeringItem1, Me.functionsInformationItem1, Me.functionsCompatibilityItem1, Me.functionsWebItem1, Me.spreadsheetCommandBarCheckItem13})
			Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl1.MaxItemId = 150
			Me.ribbonControl1.Name = "ribbonControl1"
			Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1, Me.homeRibbonPage1, Me.formulasRibbonPage1})
			Me.ribbonControl1.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() { Me.repositoryItemFontEdit1, Me.repositoryItemSpreadsheetFontSizeEdit1, Me.repositoryItemPopupGalleryEdit1})
			Me.ribbonControl1.Size = New System.Drawing.Size(941, 142)
			' 
			' spreadsheetBarController1
			' 
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem2)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem3)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem4)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem5)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem6)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem7)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem8)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem9)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem10)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem11)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem12)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem13)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeFontNameItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeFontSizeItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem14)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem15)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem2)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem3)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem4)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem16)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem17)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem18)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem19)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem20)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem21)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem22)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem23)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem24)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem25)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem26)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem27)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem28)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeBorderLineColorItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeBorderLineStyleItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeCellFillColorItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeFontColorItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem5)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem6)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem7)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem8)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem9)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem10)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem29)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem30)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem11)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem2)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem12)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem31)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem32)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem33)
			Me.spreadsheetBarController1.BarItems.Add(Me.changeNumberFormatItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem3)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem34)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem35)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem36)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem37)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem38)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem39)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem40)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem41)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem42)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem4)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem5)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem43)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem44)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem45)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem46)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem47)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem48)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem49)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem6)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem50)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem51)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem52)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem53)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem54)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem55)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonGalleryDropDownItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonGalleryDropDownItem2)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonGalleryDropDownItem3)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem7)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem56)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem57)
			Me.spreadsheetBarController1.BarItems.Add(Me.galleryFormatAsTableItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.galleryChangeStyleItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem8)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem58)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem59)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem60)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem9)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem61)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem62)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem63)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem10)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem64)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem65)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem11)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem66)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem67)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem68)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem69)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem70)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem71)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem72)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem12)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem73)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem74)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem75)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem76)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem77)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem13)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem78)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem79)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem80)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem81)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem14)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem82)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem83)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem84)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem85)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem86)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem87)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem15)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem88)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem89)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem90)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem91)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarButtonItem92)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsFinancialItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsLogicalItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsTextItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsDateAndTimeItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsLookupAndReferenceItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsMathAndTrigonometryItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarSubItem16)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsStatisticalItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsEngineeringItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsInformationItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsCompatibilityItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.functionsWebItem1)
			Me.spreadsheetBarController1.BarItems.Add(Me.spreadsheetCommandBarCheckItem13)
			Me.spreadsheetBarController1.Control = Me.spreadsheetControl1
			' 
			' commonRibbonPageGroup1
			' 
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem1)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem2)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem3)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem4)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem5)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem6)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem7)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem8)
			Me.commonRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem9)
			Me.commonRibbonPageGroup1.Name = "commonRibbonPageGroup1"
			' 
			' fileRibbonPage1
			' 
			Me.fileRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.commonRibbonPageGroup1})
			Me.fileRibbonPage1.Name = "fileRibbonPage1"
			' 
			' spreadsheetCommandBarButtonItem1
			' 
			Me.spreadsheetCommandBarButtonItem1.CommandName = "FileNew"
			Me.spreadsheetCommandBarButtonItem1.Id = 1
			Me.spreadsheetCommandBarButtonItem1.Name = "spreadsheetCommandBarButtonItem1"
			' 
			' spreadsheetCommandBarButtonItem2
			' 
			Me.spreadsheetCommandBarButtonItem2.CommandName = "FileOpen"
			Me.spreadsheetCommandBarButtonItem2.Id = 2
			Me.spreadsheetCommandBarButtonItem2.Name = "spreadsheetCommandBarButtonItem2"
			' 
			' spreadsheetCommandBarButtonItem3
			' 
			Me.spreadsheetCommandBarButtonItem3.CommandName = "FileSave"
			Me.spreadsheetCommandBarButtonItem3.Id = 3
			Me.spreadsheetCommandBarButtonItem3.Name = "spreadsheetCommandBarButtonItem3"
			' 
			' spreadsheetCommandBarButtonItem4
			' 
			Me.spreadsheetCommandBarButtonItem4.CommandName = "FileSaveAs"
			Me.spreadsheetCommandBarButtonItem4.Id = 4
			Me.spreadsheetCommandBarButtonItem4.Name = "spreadsheetCommandBarButtonItem4"
			' 
			' spreadsheetCommandBarButtonItem5
			' 
			Me.spreadsheetCommandBarButtonItem5.CommandName = "FileQuickPrint"
			Me.spreadsheetCommandBarButtonItem5.Id = 5
			Me.spreadsheetCommandBarButtonItem5.Name = "spreadsheetCommandBarButtonItem5"
			' 
			' spreadsheetCommandBarButtonItem6
			' 
			Me.spreadsheetCommandBarButtonItem6.CommandName = "FilePrint"
			Me.spreadsheetCommandBarButtonItem6.Id = 6
			Me.spreadsheetCommandBarButtonItem6.Name = "spreadsheetCommandBarButtonItem6"
			' 
			' spreadsheetCommandBarButtonItem7
			' 
			Me.spreadsheetCommandBarButtonItem7.CommandName = "FilePrintPreview"
			Me.spreadsheetCommandBarButtonItem7.Id = 7
			Me.spreadsheetCommandBarButtonItem7.Name = "spreadsheetCommandBarButtonItem7"
			' 
			' spreadsheetCommandBarButtonItem8
			' 
			Me.spreadsheetCommandBarButtonItem8.CommandName = "FileUndo"
			Me.spreadsheetCommandBarButtonItem8.Id = 8
			Me.spreadsheetCommandBarButtonItem8.Name = "spreadsheetCommandBarButtonItem8"
			' 
			' spreadsheetCommandBarButtonItem9
			' 
			Me.spreadsheetCommandBarButtonItem9.CommandName = "FileRedo"
			Me.spreadsheetCommandBarButtonItem9.Id = 9
			Me.spreadsheetCommandBarButtonItem9.Name = "spreadsheetCommandBarButtonItem9"
			' 
			' clipboardRibbonPageGroup1
			' 
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem10)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem11)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem12)
			Me.clipboardRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem13)
			Me.clipboardRibbonPageGroup1.Name = "clipboardRibbonPageGroup1"
			' 
			' homeRibbonPage1
			' 
			Me.homeRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.clipboardRibbonPageGroup1, Me.fontRibbonPageGroup1, Me.alignmentRibbonPageGroup1, Me.numberRibbonPageGroup1, Me.stylesRibbonPageGroup1, Me.cellsRibbonPageGroup1, Me.editingRibbonPageGroup1})
			Me.homeRibbonPage1.Name = "homeRibbonPage1"
			reduceOperation1.Behavior = DevExpress.XtraBars.Ribbon.ReduceOperationBehavior.UntilAvailable
			reduceOperation1.Group = Me.stylesRibbonPageGroup1
			reduceOperation1.ItemLinkIndex = 2
			reduceOperation1.ItemLinksCount = 0
			reduceOperation1.Operation = DevExpress.XtraBars.Ribbon.ReduceOperationType.Gallery
			Me.homeRibbonPage1.ReduceOperations.Add(reduceOperation1)
			' 
			' spreadsheetCommandBarButtonItem10
			' 
			Me.spreadsheetCommandBarButtonItem10.CommandName = "PasteSelection"
			Me.spreadsheetCommandBarButtonItem10.Id = 20
			Me.spreadsheetCommandBarButtonItem10.Name = "spreadsheetCommandBarButtonItem10"
			Me.spreadsheetCommandBarButtonItem10.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem11
			' 
			Me.spreadsheetCommandBarButtonItem11.CommandName = "CutSelection"
			Me.spreadsheetCommandBarButtonItem11.Id = 21
			Me.spreadsheetCommandBarButtonItem11.Name = "spreadsheetCommandBarButtonItem11"
			Me.spreadsheetCommandBarButtonItem11.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarButtonItem12
			' 
			Me.spreadsheetCommandBarButtonItem12.CommandName = "CopySelection"
			Me.spreadsheetCommandBarButtonItem12.Id = 22
			Me.spreadsheetCommandBarButtonItem12.Name = "spreadsheetCommandBarButtonItem12"
			Me.spreadsheetCommandBarButtonItem12.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarButtonItem13
			' 
			Me.spreadsheetCommandBarButtonItem13.CommandName = "ShowPasteSpecialForm"
			Me.spreadsheetCommandBarButtonItem13.Id = 23
			Me.spreadsheetCommandBarButtonItem13.Name = "spreadsheetCommandBarButtonItem13"
			Me.spreadsheetCommandBarButtonItem13.RibbonStyle = (CType((DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText Or DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText), DevExpress.XtraBars.Ribbon.RibbonItemStyles))
			' 
			' fontRibbonPageGroup1
			' 
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup1)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup2)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup3)
			Me.fontRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup4)
			Me.fontRibbonPageGroup1.Name = "fontRibbonPageGroup1"
			' 
			' changeFontNameItem1
			' 
			Me.changeFontNameItem1.Edit = Me.repositoryItemFontEdit1
			Me.changeFontNameItem1.Id = 24
			Me.changeFontNameItem1.Name = "changeFontNameItem1"
			' 
			' changeFontSizeItem1
			' 
			Me.changeFontSizeItem1.Edit = Me.repositoryItemSpreadsheetFontSizeEdit1
			Me.changeFontSizeItem1.Id = 25
			Me.changeFontSizeItem1.Name = "changeFontSizeItem1"
			' 
			' spreadsheetCommandBarButtonItem14
			' 
			Me.spreadsheetCommandBarButtonItem14.ButtonGroupTag = "{B0CA3FA8-82D6-4BC4-BD31-D9AE56C1D033}"
			Me.spreadsheetCommandBarButtonItem14.CommandName = "FormatIncreaseFontSize"
			Me.spreadsheetCommandBarButtonItem14.Id = 26
			Me.spreadsheetCommandBarButtonItem14.Name = "spreadsheetCommandBarButtonItem14"
			Me.spreadsheetCommandBarButtonItem14.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem15
			' 
			Me.spreadsheetCommandBarButtonItem15.ButtonGroupTag = "{B0CA3FA8-82D6-4BC4-BD31-D9AE56C1D033}"
			Me.spreadsheetCommandBarButtonItem15.CommandName = "FormatDecreaseFontSize"
			Me.spreadsheetCommandBarButtonItem15.Id = 27
			Me.spreadsheetCommandBarButtonItem15.Name = "spreadsheetCommandBarButtonItem15"
			Me.spreadsheetCommandBarButtonItem15.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem1
			' 
			Me.spreadsheetCommandBarCheckItem1.ButtonGroupTag = "{56C139FB-52E5-405B-A03F-FA7DCABD1D17}"
			Me.spreadsheetCommandBarCheckItem1.CommandName = "FormatFontBold"
			Me.spreadsheetCommandBarCheckItem1.Id = 28
			Me.spreadsheetCommandBarCheckItem1.Name = "spreadsheetCommandBarCheckItem1"
			Me.spreadsheetCommandBarCheckItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem2
			' 
			Me.spreadsheetCommandBarCheckItem2.ButtonGroupTag = "{56C139FB-52E5-405B-A03F-FA7DCABD1D17}"
			Me.spreadsheetCommandBarCheckItem2.CommandName = "FormatFontItalic"
			Me.spreadsheetCommandBarCheckItem2.Id = 29
			Me.spreadsheetCommandBarCheckItem2.Name = "spreadsheetCommandBarCheckItem2"
			Me.spreadsheetCommandBarCheckItem2.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem3
			' 
			Me.spreadsheetCommandBarCheckItem3.ButtonGroupTag = "{56C139FB-52E5-405B-A03F-FA7DCABD1D17}"
			Me.spreadsheetCommandBarCheckItem3.CommandName = "FormatFontUnderline"
			Me.spreadsheetCommandBarCheckItem3.Id = 30
			Me.spreadsheetCommandBarCheckItem3.Name = "spreadsheetCommandBarCheckItem3"
			Me.spreadsheetCommandBarCheckItem3.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem4
			' 
			Me.spreadsheetCommandBarCheckItem4.ButtonGroupTag = "{56C139FB-52E5-405B-A03F-FA7DCABD1D17}"
			Me.spreadsheetCommandBarCheckItem4.CommandName = "FormatFontStrikeout"
			Me.spreadsheetCommandBarCheckItem4.Id = 31
			Me.spreadsheetCommandBarCheckItem4.Name = "spreadsheetCommandBarCheckItem4"
			Me.spreadsheetCommandBarCheckItem4.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarSubItem1
			' 
			Me.spreadsheetCommandBarSubItem1.ButtonGroupTag = "{DDB05A32-9207-4556-85CB-FE3403A197C7}"
			Me.spreadsheetCommandBarSubItem1.CommandName = "FormatBordersCommandGroup"
			Me.spreadsheetCommandBarSubItem1.Id = 32
			Me.spreadsheetCommandBarSubItem1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem16), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem17), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem18), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem19), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem20), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem21), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem22), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem23), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem24), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem25), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem26), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem27), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem28), New DevExpress.XtraBars.LinkPersistInfo(Me.changeBorderLineColorItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.changeBorderLineStyleItem1)})
			Me.spreadsheetCommandBarSubItem1.Name = "spreadsheetCommandBarSubItem1"
			Me.spreadsheetCommandBarSubItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem16
			' 
			Me.spreadsheetCommandBarButtonItem16.CommandName = "FormatBottomBorder"
			Me.spreadsheetCommandBarButtonItem16.Id = 33
			Me.spreadsheetCommandBarButtonItem16.Name = "spreadsheetCommandBarButtonItem16"
			' 
			' spreadsheetCommandBarButtonItem17
			' 
			Me.spreadsheetCommandBarButtonItem17.CommandName = "FormatTopBorder"
			Me.spreadsheetCommandBarButtonItem17.Id = 34
			Me.spreadsheetCommandBarButtonItem17.Name = "spreadsheetCommandBarButtonItem17"
			' 
			' spreadsheetCommandBarButtonItem18
			' 
			Me.spreadsheetCommandBarButtonItem18.CommandName = "FormatLeftBorder"
			Me.spreadsheetCommandBarButtonItem18.Id = 35
			Me.spreadsheetCommandBarButtonItem18.Name = "spreadsheetCommandBarButtonItem18"
			' 
			' spreadsheetCommandBarButtonItem19
			' 
			Me.spreadsheetCommandBarButtonItem19.CommandName = "FormatRightBorder"
			Me.spreadsheetCommandBarButtonItem19.Id = 36
			Me.spreadsheetCommandBarButtonItem19.Name = "spreadsheetCommandBarButtonItem19"
			' 
			' spreadsheetCommandBarButtonItem20
			' 
			Me.spreadsheetCommandBarButtonItem20.CommandName = "FormatNoBorders"
			Me.spreadsheetCommandBarButtonItem20.Id = 37
			Me.spreadsheetCommandBarButtonItem20.Name = "spreadsheetCommandBarButtonItem20"
			' 
			' spreadsheetCommandBarButtonItem21
			' 
			Me.spreadsheetCommandBarButtonItem21.CommandName = "FormatAllBorders"
			Me.spreadsheetCommandBarButtonItem21.Id = 38
			Me.spreadsheetCommandBarButtonItem21.Name = "spreadsheetCommandBarButtonItem21"
			' 
			' spreadsheetCommandBarButtonItem22
			' 
			Me.spreadsheetCommandBarButtonItem22.CommandName = "FormatOutsideBorders"
			Me.spreadsheetCommandBarButtonItem22.Id = 39
			Me.spreadsheetCommandBarButtonItem22.Name = "spreadsheetCommandBarButtonItem22"
			' 
			' spreadsheetCommandBarButtonItem23
			' 
			Me.spreadsheetCommandBarButtonItem23.CommandName = "FormatThickBorder"
			Me.spreadsheetCommandBarButtonItem23.Id = 40
			Me.spreadsheetCommandBarButtonItem23.Name = "spreadsheetCommandBarButtonItem23"
			' 
			' spreadsheetCommandBarButtonItem24
			' 
			Me.spreadsheetCommandBarButtonItem24.CommandName = "FormatBottomDoubleBorder"
			Me.spreadsheetCommandBarButtonItem24.Id = 41
			Me.spreadsheetCommandBarButtonItem24.Name = "spreadsheetCommandBarButtonItem24"
			' 
			' spreadsheetCommandBarButtonItem25
			' 
			Me.spreadsheetCommandBarButtonItem25.CommandName = "FormatBottomThickBorder"
			Me.spreadsheetCommandBarButtonItem25.Id = 42
			Me.spreadsheetCommandBarButtonItem25.Name = "spreadsheetCommandBarButtonItem25"
			' 
			' spreadsheetCommandBarButtonItem26
			' 
			Me.spreadsheetCommandBarButtonItem26.CommandName = "FormatTopAndBottomBorder"
			Me.spreadsheetCommandBarButtonItem26.Id = 43
			Me.spreadsheetCommandBarButtonItem26.Name = "spreadsheetCommandBarButtonItem26"
			' 
			' spreadsheetCommandBarButtonItem27
			' 
			Me.spreadsheetCommandBarButtonItem27.CommandName = "FormatTopAndThickBottomBorder"
			Me.spreadsheetCommandBarButtonItem27.Id = 44
			Me.spreadsheetCommandBarButtonItem27.Name = "spreadsheetCommandBarButtonItem27"
			' 
			' spreadsheetCommandBarButtonItem28
			' 
			Me.spreadsheetCommandBarButtonItem28.CommandName = "FormatTopAndDoubleBottomBorder"
			Me.spreadsheetCommandBarButtonItem28.Id = 45
			Me.spreadsheetCommandBarButtonItem28.Name = "spreadsheetCommandBarButtonItem28"
			' 
			' changeBorderLineColorItem1
			' 
			Me.changeBorderLineColorItem1.ActAsDropDown = True
			Me.changeBorderLineColorItem1.Id = 46
			Me.changeBorderLineColorItem1.Name = "changeBorderLineColorItem1"
			' 
			' changeBorderLineStyleItem1
			' 
			Me.changeBorderLineStyleItem1.DropDownControl = Me.commandBarGalleryDropDown1
			Me.changeBorderLineStyleItem1.Id = 47
			Me.changeBorderLineStyleItem1.Name = "changeBorderLineStyleItem1"
			' 
			' commandBarGalleryDropDown1
			' 
			Me.commandBarGalleryDropDown1.Name = "commandBarGalleryDropDown1"
			Me.commandBarGalleryDropDown1.Ribbon = Me.ribbonControl1
			' 
			' changeCellFillColorItem1
			' 
			Me.changeCellFillColorItem1.Id = 48
			Me.changeCellFillColorItem1.Name = "changeCellFillColorItem1"
			' 
			' changeFontColorItem1
			' 
			Me.changeFontColorItem1.Id = 49
			Me.changeFontColorItem1.Name = "changeFontColorItem1"
			' 
			' barButtonGroup1
			' 
			Me.barButtonGroup1.Id = 10
			Me.barButtonGroup1.ItemLinks.Add(Me.changeFontNameItem1)
			Me.barButtonGroup1.ItemLinks.Add(Me.changeFontSizeItem1)
			Me.barButtonGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem14)
			Me.barButtonGroup1.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem15)
			Me.barButtonGroup1.Name = "barButtonGroup1"
			Me.barButtonGroup1.Tag = "{B0CA3FA8-82D6-4BC4-BD31-D9AE56C1D033}"
			' 
			' repositoryItemFontEdit1
			' 
			Me.repositoryItemFontEdit1.AutoHeight = False
			Me.repositoryItemFontEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemFontEdit1.Name = "repositoryItemFontEdit1"
			' 
			' repositoryItemSpreadsheetFontSizeEdit1
			' 
			Me.repositoryItemSpreadsheetFontSizeEdit1.AutoHeight = False
			Me.repositoryItemSpreadsheetFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.repositoryItemSpreadsheetFontSizeEdit1.Control = Me.spreadsheetControl1
			Me.repositoryItemSpreadsheetFontSizeEdit1.Name = "repositoryItemSpreadsheetFontSizeEdit1"
			' 
			' barButtonGroup2
			' 
			Me.barButtonGroup2.Id = 11
			Me.barButtonGroup2.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem1)
			Me.barButtonGroup2.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem2)
			Me.barButtonGroup2.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem3)
			Me.barButtonGroup2.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem4)
			Me.barButtonGroup2.Name = "barButtonGroup2"
			Me.barButtonGroup2.Tag = "{56C139FB-52E5-405B-A03F-FA7DCABD1D17}"
			' 
			' barButtonGroup3
			' 
			Me.barButtonGroup3.Id = 12
			Me.barButtonGroup3.ItemLinks.Add(Me.spreadsheetCommandBarSubItem1)
			Me.barButtonGroup3.Name = "barButtonGroup3"
			Me.barButtonGroup3.Tag = "{DDB05A32-9207-4556-85CB-FE3403A197C7}"
			' 
			' barButtonGroup4
			' 
			Me.barButtonGroup4.Id = 13
			Me.barButtonGroup4.ItemLinks.Add(Me.changeCellFillColorItem1)
			Me.barButtonGroup4.ItemLinks.Add(Me.changeFontColorItem1)
			Me.barButtonGroup4.Name = "barButtonGroup4"
			Me.barButtonGroup4.Tag = "{C2275623-04A3-41E8-8D6A-EB5C7F8541D1}"
			' 
			' alignmentRibbonPageGroup1
			' 
			Me.alignmentRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup5)
			Me.alignmentRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup6)
			Me.alignmentRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup7)
			Me.alignmentRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem11)
			Me.alignmentRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem2)
			Me.alignmentRibbonPageGroup1.Name = "alignmentRibbonPageGroup1"
			' 
			' spreadsheetCommandBarCheckItem5
			' 
			Me.spreadsheetCommandBarCheckItem5.ButtonGroupTag = "{03A0322B-12A2-4434-A487-8B5AAF64CCFC}"
			Me.spreadsheetCommandBarCheckItem5.CommandName = "FormatAlignmentTop"
			Me.spreadsheetCommandBarCheckItem5.Id = 50
			Me.spreadsheetCommandBarCheckItem5.Name = "spreadsheetCommandBarCheckItem5"
			Me.spreadsheetCommandBarCheckItem5.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem6
			' 
			Me.spreadsheetCommandBarCheckItem6.ButtonGroupTag = "{03A0322B-12A2-4434-A487-8B5AAF64CCFC}"
			Me.spreadsheetCommandBarCheckItem6.CommandName = "FormatAlignmentMiddle"
			Me.spreadsheetCommandBarCheckItem6.Id = 51
			Me.spreadsheetCommandBarCheckItem6.Name = "spreadsheetCommandBarCheckItem6"
			Me.spreadsheetCommandBarCheckItem6.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem7
			' 
			Me.spreadsheetCommandBarCheckItem7.ButtonGroupTag = "{03A0322B-12A2-4434-A487-8B5AAF64CCFC}"
			Me.spreadsheetCommandBarCheckItem7.CommandName = "FormatAlignmentBottom"
			Me.spreadsheetCommandBarCheckItem7.Id = 52
			Me.spreadsheetCommandBarCheckItem7.Name = "spreadsheetCommandBarCheckItem7"
			Me.spreadsheetCommandBarCheckItem7.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem8
			' 
			Me.spreadsheetCommandBarCheckItem8.ButtonGroupTag = "{ECC693B7-EF59-4007-A0DB-A9550214A0F2}"
			Me.spreadsheetCommandBarCheckItem8.CommandName = "FormatAlignmentLeft"
			Me.spreadsheetCommandBarCheckItem8.Id = 53
			Me.spreadsheetCommandBarCheckItem8.Name = "spreadsheetCommandBarCheckItem8"
			Me.spreadsheetCommandBarCheckItem8.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem9
			' 
			Me.spreadsheetCommandBarCheckItem9.ButtonGroupTag = "{ECC693B7-EF59-4007-A0DB-A9550214A0F2}"
			Me.spreadsheetCommandBarCheckItem9.CommandName = "FormatAlignmentCenter"
			Me.spreadsheetCommandBarCheckItem9.Id = 54
			Me.spreadsheetCommandBarCheckItem9.Name = "spreadsheetCommandBarCheckItem9"
			Me.spreadsheetCommandBarCheckItem9.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem10
			' 
			Me.spreadsheetCommandBarCheckItem10.ButtonGroupTag = "{ECC693B7-EF59-4007-A0DB-A9550214A0F2}"
			Me.spreadsheetCommandBarCheckItem10.CommandName = "FormatAlignmentRight"
			Me.spreadsheetCommandBarCheckItem10.Id = 55
			Me.spreadsheetCommandBarCheckItem10.Name = "spreadsheetCommandBarCheckItem10"
			Me.spreadsheetCommandBarCheckItem10.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem29
			' 
			Me.spreadsheetCommandBarButtonItem29.ButtonGroupTag = "{A5E37DED-106E-44FC-8044-CE3824C08225}"
			Me.spreadsheetCommandBarButtonItem29.CommandName = "FormatDecreaseIndent"
			Me.spreadsheetCommandBarButtonItem29.Id = 56
			Me.spreadsheetCommandBarButtonItem29.Name = "spreadsheetCommandBarButtonItem29"
			Me.spreadsheetCommandBarButtonItem29.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem30
			' 
			Me.spreadsheetCommandBarButtonItem30.ButtonGroupTag = "{A5E37DED-106E-44FC-8044-CE3824C08225}"
			Me.spreadsheetCommandBarButtonItem30.CommandName = "FormatIncreaseIndent"
			Me.spreadsheetCommandBarButtonItem30.Id = 57
			Me.spreadsheetCommandBarButtonItem30.Name = "spreadsheetCommandBarButtonItem30"
			Me.spreadsheetCommandBarButtonItem30.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarCheckItem11
			' 
			Me.spreadsheetCommandBarCheckItem11.CommandName = "FormatWrapText"
			Me.spreadsheetCommandBarCheckItem11.Id = 58
			Me.spreadsheetCommandBarCheckItem11.Name = "spreadsheetCommandBarCheckItem11"
			Me.spreadsheetCommandBarCheckItem11.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarSubItem2
			' 
			Me.spreadsheetCommandBarSubItem2.CommandName = "EditingMergeCellsCommandGroup"
			Me.spreadsheetCommandBarSubItem2.Id = 59
			Me.spreadsheetCommandBarSubItem2.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarCheckItem12), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem31), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem32), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem33)})
			Me.spreadsheetCommandBarSubItem2.Name = "spreadsheetCommandBarSubItem2"
			Me.spreadsheetCommandBarSubItem2.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarCheckItem12
			' 
			Me.spreadsheetCommandBarCheckItem12.CommandName = "EditingMergeAndCenterCells"
			Me.spreadsheetCommandBarCheckItem12.Id = 60
			Me.spreadsheetCommandBarCheckItem12.Name = "spreadsheetCommandBarCheckItem12"
			' 
			' spreadsheetCommandBarButtonItem31
			' 
			Me.spreadsheetCommandBarButtonItem31.CommandName = "EditingMergeCellsAcross"
			Me.spreadsheetCommandBarButtonItem31.Id = 61
			Me.spreadsheetCommandBarButtonItem31.Name = "spreadsheetCommandBarButtonItem31"
			' 
			' spreadsheetCommandBarButtonItem32
			' 
			Me.spreadsheetCommandBarButtonItem32.CommandName = "EditingMergeCells"
			Me.spreadsheetCommandBarButtonItem32.Id = 62
			Me.spreadsheetCommandBarButtonItem32.Name = "spreadsheetCommandBarButtonItem32"
			' 
			' spreadsheetCommandBarButtonItem33
			' 
			Me.spreadsheetCommandBarButtonItem33.CommandName = "EditingUnmergeCells"
			Me.spreadsheetCommandBarButtonItem33.Id = 63
			Me.spreadsheetCommandBarButtonItem33.Name = "spreadsheetCommandBarButtonItem33"
			' 
			' barButtonGroup5
			' 
			Me.barButtonGroup5.Id = 14
			Me.barButtonGroup5.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem5)
			Me.barButtonGroup5.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem6)
			Me.barButtonGroup5.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem7)
			Me.barButtonGroup5.Name = "barButtonGroup5"
			Me.barButtonGroup5.Tag = "{03A0322B-12A2-4434-A487-8B5AAF64CCFC}"
			' 
			' barButtonGroup6
			' 
			Me.barButtonGroup6.Id = 15
			Me.barButtonGroup6.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem8)
			Me.barButtonGroup6.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem9)
			Me.barButtonGroup6.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem10)
			Me.barButtonGroup6.Name = "barButtonGroup6"
			Me.barButtonGroup6.Tag = "{ECC693B7-EF59-4007-A0DB-A9550214A0F2}"
			' 
			' barButtonGroup7
			' 
			Me.barButtonGroup7.Id = 16
			Me.barButtonGroup7.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem29)
			Me.barButtonGroup7.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem30)
			Me.barButtonGroup7.Name = "barButtonGroup7"
			Me.barButtonGroup7.Tag = "{A5E37DED-106E-44FC-8044-CE3824C08225}"
			' 
			' numberRibbonPageGroup1
			' 
			Me.numberRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup8)
			Me.numberRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup9)
			Me.numberRibbonPageGroup1.ItemLinks.Add(Me.barButtonGroup10)
			Me.numberRibbonPageGroup1.Name = "numberRibbonPageGroup1"
			' 
			' changeNumberFormatItem1
			' 
			Me.changeNumberFormatItem1.Edit = Me.repositoryItemPopupGalleryEdit1
			Me.changeNumberFormatItem1.Id = 64
			Me.changeNumberFormatItem1.Name = "changeNumberFormatItem1"
			' 
			' spreadsheetCommandBarSubItem3
			' 
			Me.spreadsheetCommandBarSubItem3.ButtonGroupTag = "{508C2CE6-E1C8-4DD1-BA50-6C210FDB31B0}"
			Me.spreadsheetCommandBarSubItem3.CommandName = "FormatNumberAccountingCommandGroup"
			Me.spreadsheetCommandBarSubItem3.Id = 65
			Me.spreadsheetCommandBarSubItem3.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem34), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem35), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem36), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem37), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem38)})
			Me.spreadsheetCommandBarSubItem3.Name = "spreadsheetCommandBarSubItem3"
			Me.spreadsheetCommandBarSubItem3.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem34
			' 
			Me.spreadsheetCommandBarButtonItem34.CommandName = "FormatNumberAccountingUS"
			Me.spreadsheetCommandBarButtonItem34.Id = 66
			Me.spreadsheetCommandBarButtonItem34.Name = "spreadsheetCommandBarButtonItem34"
			' 
			' spreadsheetCommandBarButtonItem35
			' 
			Me.spreadsheetCommandBarButtonItem35.CommandName = "FormatNumberAccountingUK"
			Me.spreadsheetCommandBarButtonItem35.Id = 67
			Me.spreadsheetCommandBarButtonItem35.Name = "spreadsheetCommandBarButtonItem35"
			' 
			' spreadsheetCommandBarButtonItem36
			' 
			Me.spreadsheetCommandBarButtonItem36.CommandName = "FormatNumberAccountingEuro"
			Me.spreadsheetCommandBarButtonItem36.Id = 68
			Me.spreadsheetCommandBarButtonItem36.Name = "spreadsheetCommandBarButtonItem36"
			' 
			' spreadsheetCommandBarButtonItem37
			' 
			Me.spreadsheetCommandBarButtonItem37.CommandName = "FormatNumberAccountingPRC"
			Me.spreadsheetCommandBarButtonItem37.Id = 69
			Me.spreadsheetCommandBarButtonItem37.Name = "spreadsheetCommandBarButtonItem37"
			' 
			' spreadsheetCommandBarButtonItem38
			' 
			Me.spreadsheetCommandBarButtonItem38.CommandName = "FormatNumberAccountingSwiss"
			Me.spreadsheetCommandBarButtonItem38.Id = 70
			Me.spreadsheetCommandBarButtonItem38.Name = "spreadsheetCommandBarButtonItem38"
			' 
			' spreadsheetCommandBarButtonItem39
			' 
			Me.spreadsheetCommandBarButtonItem39.ButtonGroupTag = "{508C2CE6-E1C8-4DD1-BA50-6C210FDB31B0}"
			Me.spreadsheetCommandBarButtonItem39.CommandName = "FormatNumberPercent"
			Me.spreadsheetCommandBarButtonItem39.Id = 71
			Me.spreadsheetCommandBarButtonItem39.Name = "spreadsheetCommandBarButtonItem39"
			Me.spreadsheetCommandBarButtonItem39.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem40
			' 
			Me.spreadsheetCommandBarButtonItem40.ButtonGroupTag = "{508C2CE6-E1C8-4DD1-BA50-6C210FDB31B0}"
			Me.spreadsheetCommandBarButtonItem40.CommandName = "FormatNumberAccounting"
			Me.spreadsheetCommandBarButtonItem40.Id = 72
			Me.spreadsheetCommandBarButtonItem40.Name = "spreadsheetCommandBarButtonItem40"
			Me.spreadsheetCommandBarButtonItem40.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem41
			' 
			Me.spreadsheetCommandBarButtonItem41.ButtonGroupTag = "{BBAB348B-BDB2-487A-A883-EFB9982DC698}"
			Me.spreadsheetCommandBarButtonItem41.CommandName = "FormatNumberIncreaseDecimal"
			Me.spreadsheetCommandBarButtonItem41.Id = 73
			Me.spreadsheetCommandBarButtonItem41.Name = "spreadsheetCommandBarButtonItem41"
			Me.spreadsheetCommandBarButtonItem41.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' spreadsheetCommandBarButtonItem42
			' 
			Me.spreadsheetCommandBarButtonItem42.ButtonGroupTag = "{BBAB348B-BDB2-487A-A883-EFB9982DC698}"
			Me.spreadsheetCommandBarButtonItem42.CommandName = "FormatNumberDecreaseDecimal"
			Me.spreadsheetCommandBarButtonItem42.Id = 74
			Me.spreadsheetCommandBarButtonItem42.Name = "spreadsheetCommandBarButtonItem42"
			Me.spreadsheetCommandBarButtonItem42.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithoutText
			' 
			' barButtonGroup8
			' 
			Me.barButtonGroup8.Id = 17
			Me.barButtonGroup8.ItemLinks.Add(Me.changeNumberFormatItem1)
			Me.barButtonGroup8.Name = "barButtonGroup8"
			Me.barButtonGroup8.Tag = "{0B3A7A43-3079-4ce0-83A8-3789F5F6DC9F}"
			' 
			' repositoryItemPopupGalleryEdit1
			' 
			Me.repositoryItemPopupGalleryEdit1.AutoHeight = False
			Me.repositoryItemPopupGalleryEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			' 
			' 
			' 
			Me.repositoryItemPopupGalleryEdit1.Gallery.AllowFilter = False
			Me.repositoryItemPopupGalleryEdit1.Gallery.AutoFitColumns = False
			Me.repositoryItemPopupGalleryEdit1.Gallery.ColumnCount = 1
			Me.repositoryItemPopupGalleryEdit1.Gallery.FixedImageSize = False
			spreadsheetCommandGalleryItem1.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem1.CaptionAsValue = True
			spreadsheetCommandGalleryItem1.CommandName = "FormatNumberGeneral"
			spreadsheetCommandGalleryItem1.IsEmptyHint = True
			spreadsheetCommandGalleryItem2.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem2.CaptionAsValue = True
			spreadsheetCommandGalleryItem2.CommandName = "FormatNumberDecimal"
			spreadsheetCommandGalleryItem2.IsEmptyHint = True
			spreadsheetCommandGalleryItem3.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem3.CaptionAsValue = True
			spreadsheetCommandGalleryItem3.CommandName = "FormatNumberAccountingCurrency"
			spreadsheetCommandGalleryItem3.IsEmptyHint = True
			spreadsheetCommandGalleryItem4.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem4.CaptionAsValue = True
			spreadsheetCommandGalleryItem4.CommandName = "FormatNumberAccountingRegular"
			spreadsheetCommandGalleryItem4.IsEmptyHint = True
			spreadsheetCommandGalleryItem5.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem5.CaptionAsValue = True
			spreadsheetCommandGalleryItem5.CommandName = "FormatNumberShortDate"
			spreadsheetCommandGalleryItem5.IsEmptyHint = True
			spreadsheetCommandGalleryItem6.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem6.CaptionAsValue = True
			spreadsheetCommandGalleryItem6.CommandName = "FormatNumberLongDate"
			spreadsheetCommandGalleryItem6.IsEmptyHint = True
			spreadsheetCommandGalleryItem7.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem7.CaptionAsValue = True
			spreadsheetCommandGalleryItem7.CommandName = "FormatNumberTime"
			spreadsheetCommandGalleryItem7.IsEmptyHint = True
			spreadsheetCommandGalleryItem8.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem8.CaptionAsValue = True
			spreadsheetCommandGalleryItem8.CommandName = "FormatNumberPercentage"
			spreadsheetCommandGalleryItem8.IsEmptyHint = True
			spreadsheetCommandGalleryItem9.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem9.CaptionAsValue = True
			spreadsheetCommandGalleryItem9.CommandName = "FormatNumberFraction"
			spreadsheetCommandGalleryItem9.IsEmptyHint = True
			spreadsheetCommandGalleryItem10.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem10.CaptionAsValue = True
			spreadsheetCommandGalleryItem10.CommandName = "FormatNumberScientific"
			spreadsheetCommandGalleryItem10.IsEmptyHint = True
			spreadsheetCommandGalleryItem11.AlwaysUpdateDescription = True
			spreadsheetCommandGalleryItem11.CaptionAsValue = True
			spreadsheetCommandGalleryItem11.CommandName = "FormatNumberText"
			spreadsheetCommandGalleryItem11.IsEmptyHint = True
			galleryItemGroup1.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem1, spreadsheetCommandGalleryItem2, spreadsheetCommandGalleryItem3, spreadsheetCommandGalleryItem4, spreadsheetCommandGalleryItem5, spreadsheetCommandGalleryItem6, spreadsheetCommandGalleryItem7, spreadsheetCommandGalleryItem8, spreadsheetCommandGalleryItem9, spreadsheetCommandGalleryItem10, spreadsheetCommandGalleryItem11})
			Me.repositoryItemPopupGalleryEdit1.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { galleryItemGroup1})
			Me.repositoryItemPopupGalleryEdit1.Gallery.ItemImageLayout = DevExpress.Utils.Drawing.ImageLayoutMode.MiddleLeft
			Me.repositoryItemPopupGalleryEdit1.Gallery.ItemImageLocation = DevExpress.Utils.Locations.Left
			Me.repositoryItemPopupGalleryEdit1.Gallery.RowCount = 11
			Me.repositoryItemPopupGalleryEdit1.Gallery.ShowGroupCaption = False
			Me.repositoryItemPopupGalleryEdit1.Gallery.ShowItemText = True
			Me.repositoryItemPopupGalleryEdit1.Gallery.ShowScrollBar = DevExpress.XtraBars.Ribbon.Gallery.ShowScrollBar.Hide
			Me.repositoryItemPopupGalleryEdit1.Gallery.StretchItems = True
			Me.repositoryItemPopupGalleryEdit1.Name = "repositoryItemPopupGalleryEdit1"
			Me.repositoryItemPopupGalleryEdit1.ShowButtons = False
			Me.repositoryItemPopupGalleryEdit1.ShowPopupCloseButton = False
			Me.repositoryItemPopupGalleryEdit1.ShowSizeGrip = False
			' 
			' barButtonGroup9
			' 
			Me.barButtonGroup9.Id = 18
			Me.barButtonGroup9.ItemLinks.Add(Me.spreadsheetCommandBarSubItem3)
			Me.barButtonGroup9.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem39)
			Me.barButtonGroup9.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem40)
			Me.barButtonGroup9.Name = "barButtonGroup9"
			Me.barButtonGroup9.Tag = "{508C2CE6-E1C8-4DD1-BA50-6C210FDB31B0}"
			' 
			' barButtonGroup10
			' 
			Me.barButtonGroup10.Id = 19
			Me.barButtonGroup10.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem41)
			Me.barButtonGroup10.ItemLinks.Add(Me.spreadsheetCommandBarButtonItem42)
			Me.barButtonGroup10.Name = "barButtonGroup10"
			Me.barButtonGroup10.Tag = "{BBAB348B-BDB2-487A-A883-EFB9982DC698}"
			' 
			' stylesRibbonPageGroup1
			' 
			Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem4)
			Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.galleryFormatAsTableItem1)
			Me.stylesRibbonPageGroup1.ItemLinks.Add(Me.galleryChangeStyleItem1)
			Me.stylesRibbonPageGroup1.Name = "stylesRibbonPageGroup1"
			' 
			' spreadsheetCommandBarSubItem4
			' 
			Me.spreadsheetCommandBarSubItem4.CommandName = "ConditionalFormattingCommandGroup"
			Me.spreadsheetCommandBarSubItem4.Id = 75
			Me.spreadsheetCommandBarSubItem4.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarSubItem5), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarSubItem6), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonGalleryDropDownItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonGalleryDropDownItem2), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonGalleryDropDownItem3), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarSubItem7)})
			Me.spreadsheetCommandBarSubItem4.Name = "spreadsheetCommandBarSubItem4"
			' 
			' spreadsheetCommandBarSubItem5
			' 
			Me.spreadsheetCommandBarSubItem5.CommandName = "ConditionalFormattingHighlightCellsRuleCommandGroup"
			Me.spreadsheetCommandBarSubItem5.Id = 83
			Me.spreadsheetCommandBarSubItem5.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem43), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem44), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem45), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem46), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem47), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem48), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem49)})
			Me.spreadsheetCommandBarSubItem5.Name = "spreadsheetCommandBarSubItem5"
			' 
			' spreadsheetCommandBarButtonItem43
			' 
			Me.spreadsheetCommandBarButtonItem43.CommandName = "ConditionalFormattingGreaterThanRuleCommand"
			Me.spreadsheetCommandBarButtonItem43.Id = 76
			Me.spreadsheetCommandBarButtonItem43.Name = "spreadsheetCommandBarButtonItem43"
			Me.spreadsheetCommandBarButtonItem43.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem44
			' 
			Me.spreadsheetCommandBarButtonItem44.CommandName = "ConditionalFormattingLessThanRuleCommand"
			Me.spreadsheetCommandBarButtonItem44.Id = 77
			Me.spreadsheetCommandBarButtonItem44.Name = "spreadsheetCommandBarButtonItem44"
			Me.spreadsheetCommandBarButtonItem44.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem45
			' 
			Me.spreadsheetCommandBarButtonItem45.CommandName = "ConditionalFormattingBetweenRuleCommand"
			Me.spreadsheetCommandBarButtonItem45.Id = 78
			Me.spreadsheetCommandBarButtonItem45.Name = "spreadsheetCommandBarButtonItem45"
			Me.spreadsheetCommandBarButtonItem45.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem46
			' 
			Me.spreadsheetCommandBarButtonItem46.CommandName = "ConditionalFormattingEqualToRuleCommand"
			Me.spreadsheetCommandBarButtonItem46.Id = 79
			Me.spreadsheetCommandBarButtonItem46.Name = "spreadsheetCommandBarButtonItem46"
			Me.spreadsheetCommandBarButtonItem46.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem47
			' 
			Me.spreadsheetCommandBarButtonItem47.CommandName = "ConditionalFormattingTextContainsRuleCommand"
			Me.spreadsheetCommandBarButtonItem47.Id = 80
			Me.spreadsheetCommandBarButtonItem47.Name = "spreadsheetCommandBarButtonItem47"
			Me.spreadsheetCommandBarButtonItem47.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem48
			' 
			Me.spreadsheetCommandBarButtonItem48.CommandName = "ConditionalFormattingDateOccurringRuleCommand"
			Me.spreadsheetCommandBarButtonItem48.Id = 81
			Me.spreadsheetCommandBarButtonItem48.Name = "spreadsheetCommandBarButtonItem48"
			Me.spreadsheetCommandBarButtonItem48.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem49
			' 
			Me.spreadsheetCommandBarButtonItem49.CommandName = "ConditionalFormattingDuplicateValuesRuleCommand"
			Me.spreadsheetCommandBarButtonItem49.Id = 82
			Me.spreadsheetCommandBarButtonItem49.Name = "spreadsheetCommandBarButtonItem49"
			Me.spreadsheetCommandBarButtonItem49.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarSubItem6
			' 
			Me.spreadsheetCommandBarSubItem6.CommandName = "ConditionalFormattingTopBottomRuleCommandGroup"
			Me.spreadsheetCommandBarSubItem6.Id = 90
			Me.spreadsheetCommandBarSubItem6.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem50), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem51), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem52), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem53), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem54), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem55)})
			Me.spreadsheetCommandBarSubItem6.Name = "spreadsheetCommandBarSubItem6"
			' 
			' spreadsheetCommandBarButtonItem50
			' 
			Me.spreadsheetCommandBarButtonItem50.CommandName = "ConditionalFormattingTop10RuleCommand"
			Me.spreadsheetCommandBarButtonItem50.Id = 84
			Me.spreadsheetCommandBarButtonItem50.Name = "spreadsheetCommandBarButtonItem50"
			Me.spreadsheetCommandBarButtonItem50.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem51
			' 
			Me.spreadsheetCommandBarButtonItem51.CommandName = "ConditionalFormattingTop10PercentRuleCommand"
			Me.spreadsheetCommandBarButtonItem51.Id = 85
			Me.spreadsheetCommandBarButtonItem51.Name = "spreadsheetCommandBarButtonItem51"
			Me.spreadsheetCommandBarButtonItem51.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem52
			' 
			Me.spreadsheetCommandBarButtonItem52.CommandName = "ConditionalFormattingBottom10RuleCommand"
			Me.spreadsheetCommandBarButtonItem52.Id = 86
			Me.spreadsheetCommandBarButtonItem52.Name = "spreadsheetCommandBarButtonItem52"
			Me.spreadsheetCommandBarButtonItem52.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem53
			' 
			Me.spreadsheetCommandBarButtonItem53.CommandName = "ConditionalFormattingBottom10PercentRuleCommand"
			Me.spreadsheetCommandBarButtonItem53.Id = 87
			Me.spreadsheetCommandBarButtonItem53.Name = "spreadsheetCommandBarButtonItem53"
			Me.spreadsheetCommandBarButtonItem53.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem54
			' 
			Me.spreadsheetCommandBarButtonItem54.CommandName = "ConditionalFormattingAboveAverageRuleCommand"
			Me.spreadsheetCommandBarButtonItem54.Id = 88
			Me.spreadsheetCommandBarButtonItem54.Name = "spreadsheetCommandBarButtonItem54"
			Me.spreadsheetCommandBarButtonItem54.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonItem55
			' 
			Me.spreadsheetCommandBarButtonItem55.CommandName = "ConditionalFormattingBelowAverageRuleCommand"
			Me.spreadsheetCommandBarButtonItem55.Id = 89
			Me.spreadsheetCommandBarButtonItem55.Name = "spreadsheetCommandBarButtonItem55"
			Me.spreadsheetCommandBarButtonItem55.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' spreadsheetCommandBarButtonGalleryDropDownItem1
			' 
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1.CommandName = "ConditionalFormattingDataBarsCommandGroup"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1.DropDownControl = Me.commandBarGalleryDropDown2
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1.Id = 91
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1.Name = "spreadsheetCommandBarButtonGalleryDropDownItem1"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem1.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' commandBarGalleryDropDown2
			' 
			' 
			' 
			' 
			Me.commandBarGalleryDropDown2.Gallery.ColumnCount = 3
			spreadsheetCommandGalleryItemGroup1.CommandName = "ConditionalFormattingDataBarsGradientFillCommandGroup"
			spreadsheetCommandGalleryItem12.CommandName = "ConditionalFormattingDataBarGradientBlue"
			spreadsheetCommandGalleryItem13.CommandName = "ConditionalFormattingDataBarGradientGreen"
			spreadsheetCommandGalleryItem14.CommandName = "ConditionalFormattingDataBarGradientRed"
			spreadsheetCommandGalleryItem15.CommandName = "ConditionalFormattingDataBarGradientOrange"
			spreadsheetCommandGalleryItem16.CommandName = "ConditionalFormattingDataBarGradientLightBlue"
			spreadsheetCommandGalleryItem17.CommandName = "ConditionalFormattingDataBarGradientPurple"
			spreadsheetCommandGalleryItemGroup1.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem12, spreadsheetCommandGalleryItem13, spreadsheetCommandGalleryItem14, spreadsheetCommandGalleryItem15, spreadsheetCommandGalleryItem16, spreadsheetCommandGalleryItem17})
			spreadsheetCommandGalleryItemGroup2.CommandName = "ConditionalFormattingDataBarsSolidFillCommandGroup"
			spreadsheetCommandGalleryItem18.CommandName = "ConditionalFormattingDataBarSolidBlue"
			spreadsheetCommandGalleryItem19.CommandName = "ConditionalFormattingDataBarSolidGreen"
			spreadsheetCommandGalleryItem20.CommandName = "ConditionalFormattingDataBarSolidRed"
			spreadsheetCommandGalleryItem21.CommandName = "ConditionalFormattingDataBarSolidOrange"
			spreadsheetCommandGalleryItem22.CommandName = "ConditionalFormattingDataBarSolidLightBlue"
			spreadsheetCommandGalleryItem23.CommandName = "ConditionalFormattingDataBarSolidPurple"
			spreadsheetCommandGalleryItemGroup2.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem18, spreadsheetCommandGalleryItem19, spreadsheetCommandGalleryItem20, spreadsheetCommandGalleryItem21, spreadsheetCommandGalleryItem22, spreadsheetCommandGalleryItem23})
			Me.commandBarGalleryDropDown2.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { spreadsheetCommandGalleryItemGroup1, spreadsheetCommandGalleryItemGroup2})
			Me.commandBarGalleryDropDown2.Gallery.RowCount = 4
			Me.commandBarGalleryDropDown2.Name = "commandBarGalleryDropDown2"
			Me.commandBarGalleryDropDown2.Ribbon = Me.ribbonControl1
			' 
			' spreadsheetCommandBarButtonGalleryDropDownItem2
			' 
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2.CommandName = "ConditionalFormattingColorScalesCommandGroup"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2.DropDownControl = Me.commandBarGalleryDropDown3
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2.Id = 92
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2.Name = "spreadsheetCommandBarButtonGalleryDropDownItem2"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem2.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' commandBarGalleryDropDown3
			' 
			' 
			' 
			' 
			Me.commandBarGalleryDropDown3.Gallery.ColumnCount = 4
			spreadsheetCommandGalleryItemGroup3.CommandName = "ConditionalFormattingColorScalesCommandGroup"
			spreadsheetCommandGalleryItem24.CommandName = "ConditionalFormattingColorScaleGreenYellowRed"
			spreadsheetCommandGalleryItem25.CommandName = "ConditionalFormattingColorScaleRedYellowGreen"
			spreadsheetCommandGalleryItem26.CommandName = "ConditionalFormattingColorScaleGreenWhiteRed"
			spreadsheetCommandGalleryItem27.CommandName = "ConditionalFormattingColorScaleRedWhiteGreen"
			spreadsheetCommandGalleryItem28.CommandName = "ConditionalFormattingColorScaleBlueWhiteRed"
			spreadsheetCommandGalleryItem29.CommandName = "ConditionalFormattingColorScaleRedWhiteBlue"
			spreadsheetCommandGalleryItem30.CommandName = "ConditionalFormattingColorScaleWhiteRed"
			spreadsheetCommandGalleryItem31.CommandName = "ConditionalFormattingColorScaleRedWhite"
			spreadsheetCommandGalleryItem32.CommandName = "ConditionalFormattingColorScaleGreenWhite"
			spreadsheetCommandGalleryItem33.CommandName = "ConditionalFormattingColorScaleWhiteGreen"
			spreadsheetCommandGalleryItem34.CommandName = "ConditionalFormattingColorScaleGreenYellow"
			spreadsheetCommandGalleryItem35.CommandName = "ConditionalFormattingColorScaleYellowGreen"
			spreadsheetCommandGalleryItemGroup3.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem24, spreadsheetCommandGalleryItem25, spreadsheetCommandGalleryItem26, spreadsheetCommandGalleryItem27, spreadsheetCommandGalleryItem28, spreadsheetCommandGalleryItem29, spreadsheetCommandGalleryItem30, spreadsheetCommandGalleryItem31, spreadsheetCommandGalleryItem32, spreadsheetCommandGalleryItem33, spreadsheetCommandGalleryItem34, spreadsheetCommandGalleryItem35})
			Me.commandBarGalleryDropDown3.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { spreadsheetCommandGalleryItemGroup3})
			Me.commandBarGalleryDropDown3.Gallery.ShowGroupCaption = False
			Me.commandBarGalleryDropDown3.Name = "commandBarGalleryDropDown3"
			Me.commandBarGalleryDropDown3.Ribbon = Me.ribbonControl1
			' 
			' spreadsheetCommandBarButtonGalleryDropDownItem3
			' 
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3.CommandName = "ConditionalFormattingIconSetsCommandGroup"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3.DropDownControl = Me.commandBarGalleryDropDown4
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3.Id = 93
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3.Name = "spreadsheetCommandBarButtonGalleryDropDownItem3"
			Me.spreadsheetCommandBarButtonGalleryDropDownItem3.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.Large
			' 
			' commandBarGalleryDropDown4
			' 
			' 
			' 
			' 
			Me.commandBarGalleryDropDown4.Gallery.ColumnCount = 4
			spreadsheetCommandGalleryItemGroup4.CommandName = "ConditionalFormattingIconSetsDirectionalCommandGroup"
			spreadsheetCommandGalleryItem36.CommandName = "ConditionalFormattingIconSetArrows3Colored"
			spreadsheetCommandGalleryItem37.CommandName = "ConditionalFormattingIconSetArrows3Grayed"
			spreadsheetCommandGalleryItem38.CommandName = "ConditionalFormattingIconSetArrows4Colored"
			spreadsheetCommandGalleryItem39.CommandName = "ConditionalFormattingIconSetArrows4Grayed"
			spreadsheetCommandGalleryItem40.CommandName = "ConditionalFormattingIconSetArrows5Colored"
			spreadsheetCommandGalleryItem41.CommandName = "ConditionalFormattingIconSetArrows5Grayed"
			spreadsheetCommandGalleryItem42.CommandName = "ConditionalFormattingIconSetTriangles3"
			spreadsheetCommandGalleryItemGroup4.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem36, spreadsheetCommandGalleryItem37, spreadsheetCommandGalleryItem38, spreadsheetCommandGalleryItem39, spreadsheetCommandGalleryItem40, spreadsheetCommandGalleryItem41, spreadsheetCommandGalleryItem42})
			spreadsheetCommandGalleryItemGroup5.CommandName = "ConditionalFormattingIconSetsShapesCommandGroup"
			spreadsheetCommandGalleryItem43.CommandName = "ConditionalFormattingIconSetTrafficLights3"
			spreadsheetCommandGalleryItem44.CommandName = "ConditionalFormattingIconSetTrafficLights3Rimmed"
			spreadsheetCommandGalleryItem45.CommandName = "ConditionalFormattingIconSetTrafficLights4"
			spreadsheetCommandGalleryItem46.CommandName = "ConditionalFormattingIconSetSigns3"
			spreadsheetCommandGalleryItem47.CommandName = "ConditionalFormattingIconSetRedToBlack"
			spreadsheetCommandGalleryItemGroup5.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem43, spreadsheetCommandGalleryItem44, spreadsheetCommandGalleryItem45, spreadsheetCommandGalleryItem46, spreadsheetCommandGalleryItem47})
			spreadsheetCommandGalleryItemGroup6.CommandName = "ConditionalFormattingIconSetsIndicatorsCommandGroup"
			spreadsheetCommandGalleryItem48.CommandName = "ConditionalFormattingIconSetSymbols3Circled"
			spreadsheetCommandGalleryItem49.CommandName = "ConditionalFormattingIconSetSymbols3"
			spreadsheetCommandGalleryItem50.CommandName = "ConditionalFormattingIconSetFlags3"
			spreadsheetCommandGalleryItemGroup6.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem48, spreadsheetCommandGalleryItem49, spreadsheetCommandGalleryItem50})
			spreadsheetCommandGalleryItemGroup7.CommandName = "ConditionalFormattingIconSetsRatingsCommandGroup"
			spreadsheetCommandGalleryItem51.CommandName = "ConditionalFormattingIconSetStars3"
			spreadsheetCommandGalleryItem52.CommandName = "ConditionalFormattingIconSetRatings4"
			spreadsheetCommandGalleryItem53.CommandName = "ConditionalFormattingIconSetRatings5"
			spreadsheetCommandGalleryItem54.CommandName = "ConditionalFormattingIconSetQuarters5"
			spreadsheetCommandGalleryItem55.CommandName = "ConditionalFormattingIconSetBoxes5"
			spreadsheetCommandGalleryItemGroup7.Items.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItem() { spreadsheetCommandGalleryItem51, spreadsheetCommandGalleryItem52, spreadsheetCommandGalleryItem53, spreadsheetCommandGalleryItem54, spreadsheetCommandGalleryItem55})
			Me.commandBarGalleryDropDown4.Gallery.Groups.AddRange(New DevExpress.XtraBars.Ribbon.GalleryItemGroup() { spreadsheetCommandGalleryItemGroup4, spreadsheetCommandGalleryItemGroup5, spreadsheetCommandGalleryItemGroup6, spreadsheetCommandGalleryItemGroup7})
			Me.commandBarGalleryDropDown4.Gallery.RowCount = 7
			Me.commandBarGalleryDropDown4.Name = "commandBarGalleryDropDown4"
			Me.commandBarGalleryDropDown4.Ribbon = Me.ribbonControl1
			' 
			' spreadsheetCommandBarSubItem7
			' 
			Me.spreadsheetCommandBarSubItem7.CommandName = "ConditionalFormattingRemoveCommandGroup"
			Me.spreadsheetCommandBarSubItem7.Id = 96
			Me.spreadsheetCommandBarSubItem7.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem56), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem57)})
			Me.spreadsheetCommandBarSubItem7.Name = "spreadsheetCommandBarSubItem7"
			' 
			' spreadsheetCommandBarButtonItem56
			' 
			Me.spreadsheetCommandBarButtonItem56.CommandName = "ConditionalFormattingRemoveFromSheet"
			Me.spreadsheetCommandBarButtonItem56.Id = 94
			Me.spreadsheetCommandBarButtonItem56.Name = "spreadsheetCommandBarButtonItem56"
			' 
			' spreadsheetCommandBarButtonItem57
			' 
			Me.spreadsheetCommandBarButtonItem57.CommandName = "ConditionalFormattingRemove"
			Me.spreadsheetCommandBarButtonItem57.Id = 95
			Me.spreadsheetCommandBarButtonItem57.Name = "spreadsheetCommandBarButtonItem57"
			' 
			' galleryFormatAsTableItem1
			' 
			Me.galleryFormatAsTableItem1.DropDownControl = Me.commandBarGalleryDropDown5
			Me.galleryFormatAsTableItem1.Id = 97
			Me.galleryFormatAsTableItem1.Name = "galleryFormatAsTableItem1"
			' 
			' commandBarGalleryDropDown5
			' 
			' 
			' 
			' 
			Me.commandBarGalleryDropDown5.Gallery.AllowFilter = False
			Me.commandBarGalleryDropDown5.Gallery.ColumnCount = 7
			Me.commandBarGalleryDropDown5.Gallery.DrawImageBackground = False
			Me.commandBarGalleryDropDown5.Gallery.ItemAutoSizeMode = DevExpress.XtraBars.Ribbon.Gallery.GalleryItemAutoSizeMode.None
			Me.commandBarGalleryDropDown5.Gallery.ItemSize = New System.Drawing.Size(73, 58)
			Me.commandBarGalleryDropDown5.Gallery.RowCount = 10
			Me.commandBarGalleryDropDown5.Name = "commandBarGalleryDropDown5"
			Me.commandBarGalleryDropDown5.Ribbon = Me.ribbonControl1
			' 
			' galleryChangeStyleItem1
			' 
			' 
			' 
			' 
			Me.galleryChangeStyleItem1.Gallery.DrawImageBackground = False
			Me.galleryChangeStyleItem1.Gallery.ImageSize = New System.Drawing.Size(65, 46)
			Me.galleryChangeStyleItem1.Gallery.ItemAutoSizeMode = DevExpress.XtraBars.Ribbon.Gallery.GalleryItemAutoSizeMode.None
			Me.galleryChangeStyleItem1.Gallery.ItemSize = New System.Drawing.Size(106, 28)
			Me.galleryChangeStyleItem1.Gallery.RowCount = 9
			Me.galleryChangeStyleItem1.Gallery.ShowItemText = True
			Me.galleryChangeStyleItem1.Id = 98
			Me.galleryChangeStyleItem1.Name = "galleryChangeStyleItem1"
			' 
			' cellsRibbonPageGroup1
			' 
			Me.cellsRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem8)
			Me.cellsRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem9)
			Me.cellsRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem10)
			Me.cellsRibbonPageGroup1.Name = "cellsRibbonPageGroup1"
			' 
			' spreadsheetCommandBarSubItem8
			' 
			Me.spreadsheetCommandBarSubItem8.CommandName = "InsertCellsCommandGroup"
			Me.spreadsheetCommandBarSubItem8.Id = 99
			Me.spreadsheetCommandBarSubItem8.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem58), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem59), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem60)})
			Me.spreadsheetCommandBarSubItem8.Name = "spreadsheetCommandBarSubItem8"
			' 
			' spreadsheetCommandBarButtonItem58
			' 
			Me.spreadsheetCommandBarButtonItem58.CommandName = "InsertSheetRows"
			Me.spreadsheetCommandBarButtonItem58.Id = 100
			Me.spreadsheetCommandBarButtonItem58.Name = "spreadsheetCommandBarButtonItem58"
			' 
			' spreadsheetCommandBarButtonItem59
			' 
			Me.spreadsheetCommandBarButtonItem59.CommandName = "InsertSheetColumns"
			Me.spreadsheetCommandBarButtonItem59.Id = 101
			Me.spreadsheetCommandBarButtonItem59.Name = "spreadsheetCommandBarButtonItem59"
			' 
			' spreadsheetCommandBarButtonItem60
			' 
			Me.spreadsheetCommandBarButtonItem60.CommandName = "InsertSheet"
			Me.spreadsheetCommandBarButtonItem60.Id = 102
			Me.spreadsheetCommandBarButtonItem60.Name = "spreadsheetCommandBarButtonItem60"
			' 
			' spreadsheetCommandBarSubItem9
			' 
			Me.spreadsheetCommandBarSubItem9.CommandName = "RemoveCellsCommandGroup"
			Me.spreadsheetCommandBarSubItem9.Id = 103
			Me.spreadsheetCommandBarSubItem9.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem61), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem62), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem63)})
			Me.spreadsheetCommandBarSubItem9.Name = "spreadsheetCommandBarSubItem9"
			' 
			' spreadsheetCommandBarButtonItem61
			' 
			Me.spreadsheetCommandBarButtonItem61.CommandName = "RemoveSheetRows"
			Me.spreadsheetCommandBarButtonItem61.Id = 104
			Me.spreadsheetCommandBarButtonItem61.Name = "spreadsheetCommandBarButtonItem61"
			' 
			' spreadsheetCommandBarButtonItem62
			' 
			Me.spreadsheetCommandBarButtonItem62.CommandName = "RemoveSheetColumns"
			Me.spreadsheetCommandBarButtonItem62.Id = 105
			Me.spreadsheetCommandBarButtonItem62.Name = "spreadsheetCommandBarButtonItem62"
			' 
			' spreadsheetCommandBarButtonItem63
			' 
			Me.spreadsheetCommandBarButtonItem63.CommandName = "RemoveSheet"
			Me.spreadsheetCommandBarButtonItem63.Id = 106
			Me.spreadsheetCommandBarButtonItem63.Name = "spreadsheetCommandBarButtonItem63"
			' 
			' spreadsheetCommandBarSubItem10
			' 
			Me.spreadsheetCommandBarSubItem10.CommandName = "FormatCommandGroup"
			Me.spreadsheetCommandBarSubItem10.Id = 107
			Me.spreadsheetCommandBarSubItem10.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem64), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem65), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarSubItem11), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem72)})
			Me.spreadsheetCommandBarSubItem10.Name = "spreadsheetCommandBarSubItem10"
			' 
			' spreadsheetCommandBarButtonItem64
			' 
			Me.spreadsheetCommandBarButtonItem64.CommandName = "FormatAutoFitRowHeight"
			Me.spreadsheetCommandBarButtonItem64.Id = 108
			Me.spreadsheetCommandBarButtonItem64.Name = "spreadsheetCommandBarButtonItem64"
			' 
			' spreadsheetCommandBarButtonItem65
			' 
			Me.spreadsheetCommandBarButtonItem65.CommandName = "FormatAutoFitColumnWidth"
			Me.spreadsheetCommandBarButtonItem65.Id = 109
			Me.spreadsheetCommandBarButtonItem65.Name = "spreadsheetCommandBarButtonItem65"
			' 
			' spreadsheetCommandBarSubItem11
			' 
			Me.spreadsheetCommandBarSubItem11.CommandName = "HideAndUnhideCommandGroup"
			Me.spreadsheetCommandBarSubItem11.Id = 116
			Me.spreadsheetCommandBarSubItem11.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem66), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem67), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem68), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem69), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem70), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem71)})
			Me.spreadsheetCommandBarSubItem11.Name = "spreadsheetCommandBarSubItem11"
			' 
			' spreadsheetCommandBarButtonItem66
			' 
			Me.spreadsheetCommandBarButtonItem66.CommandName = "HideRows"
			Me.spreadsheetCommandBarButtonItem66.Id = 110
			Me.spreadsheetCommandBarButtonItem66.Name = "spreadsheetCommandBarButtonItem66"
			' 
			' spreadsheetCommandBarButtonItem67
			' 
			Me.spreadsheetCommandBarButtonItem67.CommandName = "HideColumns"
			Me.spreadsheetCommandBarButtonItem67.Id = 111
			Me.spreadsheetCommandBarButtonItem67.Name = "spreadsheetCommandBarButtonItem67"
			' 
			' spreadsheetCommandBarButtonItem68
			' 
			Me.spreadsheetCommandBarButtonItem68.CommandName = "HideSheet"
			Me.spreadsheetCommandBarButtonItem68.Id = 112
			Me.spreadsheetCommandBarButtonItem68.Name = "spreadsheetCommandBarButtonItem68"
			' 
			' spreadsheetCommandBarButtonItem69
			' 
			Me.spreadsheetCommandBarButtonItem69.CommandName = "UnhideRows"
			Me.spreadsheetCommandBarButtonItem69.Id = 113
			Me.spreadsheetCommandBarButtonItem69.Name = "spreadsheetCommandBarButtonItem69"
			' 
			' spreadsheetCommandBarButtonItem70
			' 
			Me.spreadsheetCommandBarButtonItem70.CommandName = "UnhideColumns"
			Me.spreadsheetCommandBarButtonItem70.Id = 114
			Me.spreadsheetCommandBarButtonItem70.Name = "spreadsheetCommandBarButtonItem70"
			' 
			' spreadsheetCommandBarButtonItem71
			' 
			Me.spreadsheetCommandBarButtonItem71.CommandName = "UnhideSheet"
			Me.spreadsheetCommandBarButtonItem71.Id = 115
			Me.spreadsheetCommandBarButtonItem71.Name = "spreadsheetCommandBarButtonItem71"
			' 
			' spreadsheetCommandBarButtonItem72
			' 
			Me.spreadsheetCommandBarButtonItem72.CommandName = "RenameSheet"
			Me.spreadsheetCommandBarButtonItem72.Id = 117
			Me.spreadsheetCommandBarButtonItem72.Name = "spreadsheetCommandBarButtonItem72"
			' 
			' editingRibbonPageGroup1
			' 
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem12)
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem13)
			Me.editingRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem14)
			Me.editingRibbonPageGroup1.Name = "editingRibbonPageGroup1"
			' 
			' spreadsheetCommandBarSubItem12
			' 
			Me.spreadsheetCommandBarSubItem12.CommandName = "EditingAutoSumCommandGroup"
			Me.spreadsheetCommandBarSubItem12.Id = 118
			Me.spreadsheetCommandBarSubItem12.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem73), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem74), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem75), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem76), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem77)})
			Me.spreadsheetCommandBarSubItem12.Name = "spreadsheetCommandBarSubItem12"
			Me.spreadsheetCommandBarSubItem12.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarButtonItem73
			' 
			Me.spreadsheetCommandBarButtonItem73.CommandName = "FunctionsInsertSum"
			Me.spreadsheetCommandBarButtonItem73.Id = 119
			Me.spreadsheetCommandBarButtonItem73.Name = "spreadsheetCommandBarButtonItem73"
			' 
			' spreadsheetCommandBarButtonItem74
			' 
			Me.spreadsheetCommandBarButtonItem74.CommandName = "FunctionsInsertAverage"
			Me.spreadsheetCommandBarButtonItem74.Id = 120
			Me.spreadsheetCommandBarButtonItem74.Name = "spreadsheetCommandBarButtonItem74"
			' 
			' spreadsheetCommandBarButtonItem75
			' 
			Me.spreadsheetCommandBarButtonItem75.CommandName = "FunctionsInsertCountNumbers"
			Me.spreadsheetCommandBarButtonItem75.Id = 121
			Me.spreadsheetCommandBarButtonItem75.Name = "spreadsheetCommandBarButtonItem75"
			' 
			' spreadsheetCommandBarButtonItem76
			' 
			Me.spreadsheetCommandBarButtonItem76.CommandName = "FunctionsInsertMax"
			Me.spreadsheetCommandBarButtonItem76.Id = 122
			Me.spreadsheetCommandBarButtonItem76.Name = "spreadsheetCommandBarButtonItem76"
			' 
			' spreadsheetCommandBarButtonItem77
			' 
			Me.spreadsheetCommandBarButtonItem77.CommandName = "FunctionsInsertMin"
			Me.spreadsheetCommandBarButtonItem77.Id = 123
			Me.spreadsheetCommandBarButtonItem77.Name = "spreadsheetCommandBarButtonItem77"
			' 
			' spreadsheetCommandBarSubItem13
			' 
			Me.spreadsheetCommandBarSubItem13.CommandName = "EditingFillCommandGroup"
			Me.spreadsheetCommandBarSubItem13.Id = 124
			Me.spreadsheetCommandBarSubItem13.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem78), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem79), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem80), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem81)})
			Me.spreadsheetCommandBarSubItem13.Name = "spreadsheetCommandBarSubItem13"
			Me.spreadsheetCommandBarSubItem13.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarButtonItem78
			' 
			Me.spreadsheetCommandBarButtonItem78.CommandName = "EditingFillDown"
			Me.spreadsheetCommandBarButtonItem78.Id = 125
			Me.spreadsheetCommandBarButtonItem78.Name = "spreadsheetCommandBarButtonItem78"
			' 
			' spreadsheetCommandBarButtonItem79
			' 
			Me.spreadsheetCommandBarButtonItem79.CommandName = "EditingFillRight"
			Me.spreadsheetCommandBarButtonItem79.Id = 126
			Me.spreadsheetCommandBarButtonItem79.Name = "spreadsheetCommandBarButtonItem79"
			' 
			' spreadsheetCommandBarButtonItem80
			' 
			Me.spreadsheetCommandBarButtonItem80.CommandName = "EditingFillUp"
			Me.spreadsheetCommandBarButtonItem80.Id = 127
			Me.spreadsheetCommandBarButtonItem80.Name = "spreadsheetCommandBarButtonItem80"
			' 
			' spreadsheetCommandBarButtonItem81
			' 
			Me.spreadsheetCommandBarButtonItem81.CommandName = "EditingFillLeft"
			Me.spreadsheetCommandBarButtonItem81.Id = 128
			Me.spreadsheetCommandBarButtonItem81.Name = "spreadsheetCommandBarButtonItem81"
			' 
			' spreadsheetCommandBarSubItem14
			' 
			Me.spreadsheetCommandBarSubItem14.CommandName = "FormatClearCommandGroup"
			Me.spreadsheetCommandBarSubItem14.Id = 129
			Me.spreadsheetCommandBarSubItem14.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem82), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem83), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem84), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem85), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem86), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem87)})
			Me.spreadsheetCommandBarSubItem14.Name = "spreadsheetCommandBarSubItem14"
			Me.spreadsheetCommandBarSubItem14.RibbonStyle = DevExpress.XtraBars.Ribbon.RibbonItemStyles.SmallWithText
			' 
			' spreadsheetCommandBarButtonItem82
			' 
			Me.spreadsheetCommandBarButtonItem82.CommandName = "FormatClearAll"
			Me.spreadsheetCommandBarButtonItem82.Id = 130
			Me.spreadsheetCommandBarButtonItem82.Name = "spreadsheetCommandBarButtonItem82"
			' 
			' spreadsheetCommandBarButtonItem83
			' 
			Me.spreadsheetCommandBarButtonItem83.CommandName = "FormatClearFormats"
			Me.spreadsheetCommandBarButtonItem83.Id = 131
			Me.spreadsheetCommandBarButtonItem83.Name = "spreadsheetCommandBarButtonItem83"
			' 
			' spreadsheetCommandBarButtonItem84
			' 
			Me.spreadsheetCommandBarButtonItem84.CommandName = "FormatClearContents"
			Me.spreadsheetCommandBarButtonItem84.Id = 132
			Me.spreadsheetCommandBarButtonItem84.Name = "spreadsheetCommandBarButtonItem84"
			' 
			' spreadsheetCommandBarButtonItem85
			' 
			Me.spreadsheetCommandBarButtonItem85.CommandName = "FormatClearComments"
			Me.spreadsheetCommandBarButtonItem85.Id = 133
			Me.spreadsheetCommandBarButtonItem85.Name = "spreadsheetCommandBarButtonItem85"
			' 
			' spreadsheetCommandBarButtonItem86
			' 
			Me.spreadsheetCommandBarButtonItem86.CommandName = "FormatClearHyperlinks"
			Me.spreadsheetCommandBarButtonItem86.Id = 134
			Me.spreadsheetCommandBarButtonItem86.Name = "spreadsheetCommandBarButtonItem86"
			' 
			' spreadsheetCommandBarButtonItem87
			' 
			Me.spreadsheetCommandBarButtonItem87.CommandName = "FormatRemoveHyperlinks"
			Me.spreadsheetCommandBarButtonItem87.Id = 135
			Me.spreadsheetCommandBarButtonItem87.Name = "spreadsheetCommandBarButtonItem87"
			' 
			' functionLibraryRibbonPageGroup1
			' 
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem15)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsFinancialItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsLogicalItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsTextItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsDateAndTimeItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsLookupAndReferenceItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.functionsMathAndTrigonometryItem1)
			Me.functionLibraryRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarSubItem16)
			Me.functionLibraryRibbonPageGroup1.Name = "functionLibraryRibbonPageGroup1"
			' 
			' formulasRibbonPage1
			' 
			Me.formulasRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.functionLibraryRibbonPageGroup1, Me.formulaAuditingRibbonPageGroup1})
			Me.formulasRibbonPage1.Name = "formulasRibbonPage1"
			' 
			' spreadsheetCommandBarSubItem15
			' 
			Me.spreadsheetCommandBarSubItem15.CommandName = "FunctionsAutoSumCommandGroup"
			Me.spreadsheetCommandBarSubItem15.Id = 136
			Me.spreadsheetCommandBarSubItem15.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem73), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem74), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem75), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem76), New DevExpress.XtraBars.LinkPersistInfo(Me.spreadsheetCommandBarButtonItem77)})
			Me.spreadsheetCommandBarSubItem15.Name = "spreadsheetCommandBarSubItem15"
			' 
			' spreadsheetCommandBarButtonItem88
			' 
			Me.spreadsheetCommandBarButtonItem88.CommandName = "FunctionsInsertSum"
			Me.spreadsheetCommandBarButtonItem88.Id = -1
			Me.spreadsheetCommandBarButtonItem88.Name = "spreadsheetCommandBarButtonItem88"
			' 
			' spreadsheetCommandBarButtonItem89
			' 
			Me.spreadsheetCommandBarButtonItem89.CommandName = "FunctionsInsertAverage"
			Me.spreadsheetCommandBarButtonItem89.Id = -1
			Me.spreadsheetCommandBarButtonItem89.Name = "spreadsheetCommandBarButtonItem89"
			' 
			' spreadsheetCommandBarButtonItem90
			' 
			Me.spreadsheetCommandBarButtonItem90.CommandName = "FunctionsInsertCountNumbers"
			Me.spreadsheetCommandBarButtonItem90.Id = -1
			Me.spreadsheetCommandBarButtonItem90.Name = "spreadsheetCommandBarButtonItem90"
			' 
			' spreadsheetCommandBarButtonItem91
			' 
			Me.spreadsheetCommandBarButtonItem91.CommandName = "FunctionsInsertMax"
			Me.spreadsheetCommandBarButtonItem91.Id = -1
			Me.spreadsheetCommandBarButtonItem91.Name = "spreadsheetCommandBarButtonItem91"
			' 
			' spreadsheetCommandBarButtonItem92
			' 
			Me.spreadsheetCommandBarButtonItem92.CommandName = "FunctionsInsertMin"
			Me.spreadsheetCommandBarButtonItem92.Id = -1
			Me.spreadsheetCommandBarButtonItem92.Name = "spreadsheetCommandBarButtonItem92"
			' 
			' functionsFinancialItem1
			' 
			Me.functionsFinancialItem1.Id = 137
			Me.functionsFinancialItem1.Name = "functionsFinancialItem1"
			' 
			' functionsLogicalItem1
			' 
			Me.functionsLogicalItem1.Id = 138
			Me.functionsLogicalItem1.Name = "functionsLogicalItem1"
			' 
			' functionsTextItem1
			' 
			Me.functionsTextItem1.Id = 139
			Me.functionsTextItem1.Name = "functionsTextItem1"
			' 
			' functionsDateAndTimeItem1
			' 
			Me.functionsDateAndTimeItem1.Id = 140
			Me.functionsDateAndTimeItem1.Name = "functionsDateAndTimeItem1"
			' 
			' functionsLookupAndReferenceItem1
			' 
			Me.functionsLookupAndReferenceItem1.Id = 141
			Me.functionsLookupAndReferenceItem1.Name = "functionsLookupAndReferenceItem1"
			' 
			' functionsMathAndTrigonometryItem1
			' 
			Me.functionsMathAndTrigonometryItem1.Id = 142
			Me.functionsMathAndTrigonometryItem1.Name = "functionsMathAndTrigonometryItem1"
			' 
			' spreadsheetCommandBarSubItem16
			' 
			Me.spreadsheetCommandBarSubItem16.CommandName = "FunctionsMoreCommandGroup"
			Me.spreadsheetCommandBarSubItem16.Id = 143
			Me.spreadsheetCommandBarSubItem16.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.functionsStatisticalItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.functionsEngineeringItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.functionsInformationItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.functionsCompatibilityItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.functionsWebItem1)})
			Me.spreadsheetCommandBarSubItem16.Name = "spreadsheetCommandBarSubItem16"
			' 
			' functionsStatisticalItem1
			' 
			Me.functionsStatisticalItem1.Id = 144
			Me.functionsStatisticalItem1.Name = "functionsStatisticalItem1"
			' 
			' functionsEngineeringItem1
			' 
			Me.functionsEngineeringItem1.Id = 145
			Me.functionsEngineeringItem1.Name = "functionsEngineeringItem1"
			' 
			' functionsInformationItem1
			' 
			Me.functionsInformationItem1.Id = 146
			Me.functionsInformationItem1.Name = "functionsInformationItem1"
			' 
			' functionsCompatibilityItem1
			' 
			Me.functionsCompatibilityItem1.Id = 147
			Me.functionsCompatibilityItem1.Name = "functionsCompatibilityItem1"
			' 
			' functionsWebItem1
			' 
			Me.functionsWebItem1.Id = 148
			Me.functionsWebItem1.Name = "functionsWebItem1"
			' 
			' formulaAuditingRibbonPageGroup1
			' 
			Me.formulaAuditingRibbonPageGroup1.ItemLinks.Add(Me.spreadsheetCommandBarCheckItem13)
			Me.formulaAuditingRibbonPageGroup1.Name = "formulaAuditingRibbonPageGroup1"
			' 
			' spreadsheetCommandBarCheckItem13
			' 
			Me.spreadsheetCommandBarCheckItem13.CommandName = "ViewShowFormulas"
			Me.spreadsheetCommandBarCheckItem13.Id = 149
			Me.spreadsheetCommandBarCheckItem13.Name = "spreadsheetCommandBarCheckItem13"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(941, 566)
			Me.Controls.Add(Me.spreadsheetControl1)
			Me.Controls.Add(Me.splitterControl1)
			Me.Controls.Add(Me.splitContainerControl1)
			Me.Controls.Add(Me.ribbonControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.spreadsheetNameBoxControl1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.splitContainerControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.splitContainerControl1.ResumeLayout(False)
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.spreadsheetBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.commandBarGalleryDropDown1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemSpreadsheetFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.repositoryItemPopupGalleryEdit1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.commandBarGalleryDropDown2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.commandBarGalleryDropDown3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.commandBarGalleryDropDown4, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.commandBarGalleryDropDown5, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region

		Private spreadsheetControl1 As DevExpress.XtraSpreadsheet.SpreadsheetControl
		Private ribbonControl1 As DevExpress.XtraBars.Ribbon.RibbonControl
		Private spreadsheetCommandBarButtonItem1 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem2 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem3 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem4 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem5 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem6 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem7 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem8 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem9 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem10 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem11 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem12 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem13 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private barButtonGroup1 As DevExpress.XtraBars.BarButtonGroup
		Private changeFontNameItem1 As DevExpress.XtraSpreadsheet.UI.ChangeFontNameItem
		Private repositoryItemFontEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemFontEdit
		Private changeFontSizeItem1 As DevExpress.XtraSpreadsheet.UI.ChangeFontSizeItem
		Private repositoryItemSpreadsheetFontSizeEdit1 As DevExpress.XtraSpreadsheet.Design.RepositoryItemSpreadsheetFontSizeEdit
		Private spreadsheetCommandBarButtonItem14 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem15 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private barButtonGroup2 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarCheckItem1 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem2 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem3 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem4 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private barButtonGroup3 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarSubItem1 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem16 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem17 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem18 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem19 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem20 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem21 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem22 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem23 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem24 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem25 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem26 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem27 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem28 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private changeBorderLineColorItem1 As DevExpress.XtraSpreadsheet.UI.ChangeBorderLineColorItem
		Private changeBorderLineStyleItem1 As DevExpress.XtraSpreadsheet.UI.ChangeBorderLineStyleItem
		Private commandBarGalleryDropDown1 As DevExpress.XtraBars.Commands.CommandBarGalleryDropDown
		Private barButtonGroup4 As DevExpress.XtraBars.BarButtonGroup
		Private changeCellFillColorItem1 As DevExpress.XtraSpreadsheet.UI.ChangeCellFillColorItem
		Private changeFontColorItem1 As DevExpress.XtraSpreadsheet.UI.ChangeFontColorItem
		Private barButtonGroup5 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarCheckItem5 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem6 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem7 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private barButtonGroup6 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarCheckItem8 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem9 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarCheckItem10 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private barButtonGroup7 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarButtonItem29 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem30 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarCheckItem11 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarSubItem2 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarCheckItem12 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private spreadsheetCommandBarButtonItem31 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem32 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem33 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private barButtonGroup8 As DevExpress.XtraBars.BarButtonGroup
		Private changeNumberFormatItem1 As DevExpress.XtraSpreadsheet.UI.ChangeNumberFormatItem
		Private repositoryItemPopupGalleryEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemPopupGalleryEdit
		Private barButtonGroup9 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarSubItem3 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem34 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem35 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem36 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem37 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem38 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem39 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem40 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private barButtonGroup10 As DevExpress.XtraBars.BarButtonGroup
		Private spreadsheetCommandBarButtonItem41 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem42 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem4 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarSubItem5 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem43 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem44 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem45 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem46 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem47 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem48 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem49 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem6 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem50 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem51 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem52 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem53 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem54 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem55 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonGalleryDropDownItem1 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem
		Private commandBarGalleryDropDown2 As DevExpress.XtraBars.Commands.CommandBarGalleryDropDown
		Private spreadsheetCommandBarButtonGalleryDropDownItem2 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem
		Private commandBarGalleryDropDown3 As DevExpress.XtraBars.Commands.CommandBarGalleryDropDown
		Private spreadsheetCommandBarButtonGalleryDropDownItem3 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonGalleryDropDownItem
		Private commandBarGalleryDropDown4 As DevExpress.XtraBars.Commands.CommandBarGalleryDropDown
		Private spreadsheetCommandBarSubItem7 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem56 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem57 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private galleryFormatAsTableItem1 As DevExpress.XtraSpreadsheet.UI.GalleryFormatAsTableItem
		Private commandBarGalleryDropDown5 As DevExpress.XtraBars.Commands.CommandBarGalleryDropDown
		Private galleryChangeStyleItem1 As DevExpress.XtraSpreadsheet.UI.GalleryChangeStyleItem
		Private spreadsheetCommandBarSubItem8 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem58 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem59 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem60 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem9 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem61 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem62 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem63 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem10 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem64 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem65 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem11 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem66 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem67 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem68 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem69 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem70 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem71 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem72 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem12 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem73 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem74 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem75 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem76 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem77 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem13 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem78 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem79 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem80 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem81 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem14 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private spreadsheetCommandBarButtonItem82 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem83 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem84 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem85 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem86 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem87 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarSubItem15 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private functionsFinancialItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsFinancialItem
		Private functionsLogicalItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsLogicalItem
		Private functionsTextItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsTextItem
		Private functionsDateAndTimeItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsDateAndTimeItem
		Private functionsLookupAndReferenceItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsLookupAndReferenceItem
		Private functionsMathAndTrigonometryItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsMathAndTrigonometryItem
		Private spreadsheetCommandBarSubItem16 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarSubItem
		Private functionsStatisticalItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsStatisticalItem
		Private functionsEngineeringItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsEngineeringItem
		Private functionsInformationItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsInformationItem
		Private functionsCompatibilityItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsCompatibilityItem
		Private functionsWebItem1 As DevExpress.XtraSpreadsheet.UI.FunctionsWebItem
		Private spreadsheetCommandBarCheckItem13 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarCheckItem
		Private fileRibbonPage1 As DevExpress.XtraSpreadsheet.UI.FileRibbonPage
		Private commonRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.CommonRibbonPageGroup
		Private homeRibbonPage1 As DevExpress.XtraSpreadsheet.UI.HomeRibbonPage
		Private clipboardRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.ClipboardRibbonPageGroup
		Private fontRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.FontRibbonPageGroup
		Private alignmentRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.AlignmentRibbonPageGroup
		Private numberRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.NumberRibbonPageGroup
		Private stylesRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.StylesRibbonPageGroup
		Private cellsRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.CellsRibbonPageGroup
		Private editingRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.EditingRibbonPageGroup
		Private formulasRibbonPage1 As DevExpress.XtraSpreadsheet.UI.FormulasRibbonPage
		Private functionLibraryRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.FunctionLibraryRibbonPageGroup
		Private formulaAuditingRibbonPageGroup1 As DevExpress.XtraSpreadsheet.UI.FormulaAuditingRibbonPageGroup
		Private spreadsheetFormulaBarControl1 As DevExpress.XtraSpreadsheet.SpreadsheetFormulaBarControl
		Private spreadsheetNameBoxControl1 As DevExpress.XtraSpreadsheet.SpreadsheetNameBoxControl
		Private splitContainerControl1 As DevExpress.XtraEditors.SplitContainerControl
		Private splitterControl1 As DevExpress.XtraEditors.SplitterControl
		Private spreadsheetBarController1 As DevExpress.XtraSpreadsheet.UI.SpreadsheetBarController
		Private spreadsheetCommandBarButtonItem88 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem89 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem90 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem91 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
		Private spreadsheetCommandBarButtonItem92 As DevExpress.XtraSpreadsheet.UI.SpreadsheetCommandBarButtonItem
	End Class
End Namespace

