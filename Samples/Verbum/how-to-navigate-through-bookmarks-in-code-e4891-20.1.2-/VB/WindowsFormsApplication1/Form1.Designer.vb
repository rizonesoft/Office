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
			Me.components = New System.ComponentModel.Container()
			Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.ribbonControl1 = New DevExpress.XtraBars.Ribbon.RibbonControl()
			Me.barButtonItemNext = New DevExpress.XtraBars.BarButtonItem()
			Me.barButtonItemPrev = New DevExpress.XtraBars.BarButtonItem()
			Me.fileRibbonPage1 = New DevExpress.XtraRichEdit.UI.FileRibbonPage()
			Me.ribbonPageGroup1 = New DevExpress.XtraBars.Ribbon.RibbonPageGroup()
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController()
			Me.commonRibbonPageGroup1 = New DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup()
			Me.fileNewItem1 = New DevExpress.XtraRichEdit.UI.FileNewItem()
			Me.fileOpenItem1 = New DevExpress.XtraRichEdit.UI.FileOpenItem()
			Me.fileSaveItem1 = New DevExpress.XtraRichEdit.UI.FileSaveItem()
			Me.fileSaveAsItem1 = New DevExpress.XtraRichEdit.UI.FileSaveAsItem()
			Me.quickPrintItem1 = New DevExpress.XtraRichEdit.UI.QuickPrintItem()
			Me.printItem1 = New DevExpress.XtraRichEdit.UI.PrintItem()
			Me.printPreviewItem1 = New DevExpress.XtraRichEdit.UI.PrintPreviewItem()
			Me.undoItem1 = New DevExpress.XtraRichEdit.UI.UndoItem()
			Me.redoItem1 = New DevExpress.XtraRichEdit.UI.RedoItem()
			Me.imageCollection1 = New DevExpress.Utils.ImageCollection(Me.components)
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.imageCollection1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(0, 144)
			Me.richEditControl1.MenuManager = Me.ribbonControl1
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Options.Fields.UseCurrentCultureDateTimeFormat = False
			Me.richEditControl1.Options.MailMerge.KeepLastParagraph = False
			Me.richEditControl1.Size = New System.Drawing.Size(879, 527)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
			' 
			' ribbonControl1
			' 
			Me.ribbonControl1.ExpandCollapseItem.Id = 0
			Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem, Me.barButtonItemNext, Me.barButtonItemPrev, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.undoItem1, Me.redoItem1})
			Me.ribbonControl1.LargeImages = Me.imageCollection1
			Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
			Me.ribbonControl1.MaxItemId = 242
			Me.ribbonControl1.Name = "ribbonControl1"
			Me.ribbonControl1.Pages.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPage() { Me.fileRibbonPage1})
			Me.ribbonControl1.Size = New System.Drawing.Size(879, 144)
			' 
			' barButtonItemNext
			' 
			Me.barButtonItemNext.Caption = "Next"
			Me.barButtonItemNext.Id = 231
			Me.barButtonItemNext.LargeImageIndex = 1
			Me.barButtonItemNext.Name = "barButtonItemNext"
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.barButtonItemNext.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barButtonItemNext_ItemClick);
			' 
			' barButtonItemPrev
			' 
			Me.barButtonItemPrev.Caption = "Prev"
			Me.barButtonItemPrev.Id = 232
			Me.barButtonItemPrev.LargeImageIndex = 0
			Me.barButtonItemPrev.Name = "barButtonItemPrev"
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.barButtonItemPrev.ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(this.barButtonItemPrev_ItemClick);
			' 
			' fileRibbonPage1
			' 
			Me.fileRibbonPage1.Groups.AddRange(New DevExpress.XtraBars.Ribbon.RibbonPageGroup() { Me.commonRibbonPageGroup1, Me.ribbonPageGroup1})
			Me.fileRibbonPage1.Name = "fileRibbonPage1"
			' 
			' ribbonPageGroup1
			' 
			Me.ribbonPageGroup1.ItemLinks.Add(Me.barButtonItemPrev)
			Me.ribbonPageGroup1.ItemLinks.Add(Me.barButtonItemNext)
			Me.ribbonPageGroup1.Name = "ribbonPageGroup1"
			Me.ribbonPageGroup1.Text = "Bookmarks"
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
			Me.richEditBarController1.Control = Me.richEditControl1
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
			' 
			' fileNewItem1
			' 
			Me.fileNewItem1.Id = 233
			Me.fileNewItem1.Name = "fileNewItem1"
			' 
			' fileOpenItem1
			' 
			Me.fileOpenItem1.Id = 234
			Me.fileOpenItem1.Name = "fileOpenItem1"
			' 
			' fileSaveItem1
			' 
			Me.fileSaveItem1.Id = 235
			Me.fileSaveItem1.Name = "fileSaveItem1"
			' 
			' fileSaveAsItem1
			' 
			Me.fileSaveAsItem1.Id = 236
			Me.fileSaveAsItem1.Name = "fileSaveAsItem1"
			' 
			' quickPrintItem1
			' 
			Me.quickPrintItem1.Id = 237
			Me.quickPrintItem1.Name = "quickPrintItem1"
			' 
			' printItem1
			' 
			Me.printItem1.Id = 238
			Me.printItem1.Name = "printItem1"
			' 
			' printPreviewItem1
			' 
			Me.printPreviewItem1.Id = 239
			Me.printPreviewItem1.Name = "printPreviewItem1"
			' 
			' undoItem1
			' 
			Me.undoItem1.Id = 240
			Me.undoItem1.Name = "undoItem1"
			' 
			' redoItem1
			' 
			Me.redoItem1.Id = 241
			Me.redoItem1.Name = "redoItem1"
			' 
			' imageCollection1
			' 
			Me.imageCollection1.ImageSize = New System.Drawing.Size(32, 32)
			Me.imageCollection1.ImageStream = (CType(resources.GetObject("imageCollection1.ImageStream"), DevExpress.Utils.ImageCollectionStreamer))
			Me.imageCollection1.InsertGalleryImage("backward_32x32.png", "images/navigation/backward_32x32.png", DevExpress.Images.ImageResourceCache.Default.GetImage("images/navigation/backward_32x32.png"), 0)
			Me.imageCollection1.Images.SetKeyName(0, "backward_32x32.png")
			Me.imageCollection1.InsertGalleryImage("forward_32x32.png", "images/navigation/forward_32x32.png", DevExpress.Images.ImageResourceCache.Default.GetImage("images/navigation/forward_32x32.png"), 1)
			Me.imageCollection1.Images.SetKeyName(1, "forward_32x32.png")
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(879, 671)
			Me.Controls.Add(Me.richEditControl1)
			Me.Controls.Add(Me.ribbonControl1)
			Me.Name = "Form1"
			Me.Ribbon = Me.ribbonControl1
			Me.Text = "Form1"
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.Load += new System.EventHandler(this.Form1_Load);
			CType(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.imageCollection1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private ribbonControl1 As DevExpress.XtraBars.Ribbon.RibbonControl
		Private fileRibbonPage1 As DevExpress.XtraRichEdit.UI.FileRibbonPage
		Private WithEvents barButtonItemNext As DevExpress.XtraBars.BarButtonItem
		Private WithEvents barButtonItemPrev As DevExpress.XtraBars.BarButtonItem
		Private ribbonPageGroup1 As DevExpress.XtraBars.Ribbon.RibbonPageGroup
		Private fileNewItem1 As DevExpress.XtraRichEdit.UI.FileNewItem
		Private fileOpenItem1 As DevExpress.XtraRichEdit.UI.FileOpenItem
		Private fileSaveItem1 As DevExpress.XtraRichEdit.UI.FileSaveItem
		Private fileSaveAsItem1 As DevExpress.XtraRichEdit.UI.FileSaveAsItem
		Private quickPrintItem1 As DevExpress.XtraRichEdit.UI.QuickPrintItem
		Private printItem1 As DevExpress.XtraRichEdit.UI.PrintItem
		Private printPreviewItem1 As DevExpress.XtraRichEdit.UI.PrintPreviewItem
		Private undoItem1 As DevExpress.XtraRichEdit.UI.UndoItem
		Private redoItem1 As DevExpress.XtraRichEdit.UI.RedoItem
		Private imageCollection1 As DevExpress.Utils.ImageCollection
		Private commonRibbonPageGroup1 As DevExpress.XtraRichEdit.UI.CommonRibbonPageGroup
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
	End Class
End Namespace

