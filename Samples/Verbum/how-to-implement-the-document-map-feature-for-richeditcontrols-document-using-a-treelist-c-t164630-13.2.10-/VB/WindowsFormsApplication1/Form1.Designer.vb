﻿Imports Microsoft.VisualBasic
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
			Me.layoutControl1 = New DevExpress.XtraLayout.LayoutControl()
			Me.treeList1 = New DevExpress.XtraTreeList.TreeList()
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
			Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
			Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.treeList1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.treeList1)
			Me.layoutControl1.Controls.Add(Me.richEditControl1)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 144)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.OptionsCustomizationForm.DesignTimeCustomizationFormPositionAndSize = New System.Drawing.Rectangle(838, 417, 250, 350)
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(899, 479)
			Me.layoutControl1.TabIndex = 0
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' treeList1
			' 
			Me.treeList1.Location = New System.Drawing.Point(12, 28)
			Me.treeList1.Name = "treeList1"
			Me.treeList1.OptionsView.ShowColumns = False
			Me.treeList1.OptionsView.ShowHorzLines = False
			Me.treeList1.OptionsView.ShowIndicator = False
			Me.treeList1.Size = New System.Drawing.Size(204, 439)
			Me.treeList1.TabIndex = 5
			' 
			' richEditControl1
			' 
			Me.richEditControl1.EnableToolTips = True
			Me.richEditControl1.Location = New System.Drawing.Point(220, 12)
			Me.richEditControl1.MenuManager = Me.ribbonControl1
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Options.CopyPaste.MaintainDocumentSectionSettings = False
			Me.richEditControl1.Options.Fields.UseCurrentCultureDateTimeFormat = False
			Me.richEditControl1.Options.MailMerge.KeepLastParagraph = False
			Me.richEditControl1.Size = New System.Drawing.Size(667, 455)
			Me.richEditControl1.TabIndex = 4
			Me.richEditControl1.Text = "richEditControl1"
			' 
			' ribbonControl1
			' 
			Me.ribbonControl1.ExpandCollapseItem.Id = 0
			Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.undoItem1, Me.redoItem1, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1})
			Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl1.MaxItemId = 10
			Me.ribbonControl1.Name = "ribbonControl1"
			Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1})
			Me.ribbonControl1.Size = New System.Drawing.Size(899, 144)
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
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.CustomizationFormText = "layoutControlGroup1"
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem2})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "layoutControlGroup1"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(899, 479)
			Me.layoutControlGroup1.Text = "layoutControlGroup1"
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.richEditControl1
			Me.layoutControlItem1.CustomizationFormText = "layoutControlItem1"
			Me.layoutControlItem1.Location = New System.Drawing.Point(208, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(671, 459)
			Me.layoutControlItem1.Text = "layoutControlItem1"
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem1.TextToControlDistance = 0
			Me.layoutControlItem1.TextVisible = False
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.treeList1
			Me.layoutControlItem2.CustomizationFormText = "Document map"
			Me.layoutControlItem2.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(208, 459)
			Me.layoutControlItem2.Text = "Document map"
			Me.layoutControlItem2.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(71, 13)
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
			Me.richEditBarController1.Control = Me.richEditControl1
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(899, 623)
			Me.Controls.Add(Me.layoutControl1)
			Me.Controls.Add(Me.ribbonControl1)
			Me.Name = "Form1"
			Me.Ribbon = Me.ribbonControl1
			Me.Text = "Form1"
'			Me.Load += New System.EventHandler(Me.Form1_Load);
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.treeList1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region

		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private treeList1 As DevExpress.XtraTreeList.TreeList
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
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
		Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
		Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
	End Class
End Namespace

