Namespace RichEditControl_Encryption
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
			Me.simpleButton1 = New DevExpress.XtraEditors.SimpleButton()
			Me.label2 = New System.Windows.Forms.Label()
			Me.passwordEdit1 = New DevExpress.XtraEditors.TextEdit()
			Me.label1 = New System.Windows.Forms.Label()
			Me.encryptionComboBox1 = New DevExpress.XtraEditors.ComboBoxEdit()
			Me.richEditControl1 = New RichEditControl_Encryption.MyRichEditControl()
			Me.barManager1 = New DevExpress.XtraBars.BarManager(Me.components)
			Me.commonBar1 = New DevExpress.XtraRichEdit.UI.CommonBar()
			Me.undoItem1 = New DevExpress.XtraRichEdit.UI.UndoItem()
			Me.redoItem1 = New DevExpress.XtraRichEdit.UI.RedoItem()
			Me.fileNewItem1 = New DevExpress.XtraRichEdit.UI.FileNewItem()
			Me.fileOpenItem1 = New DevExpress.XtraRichEdit.UI.FileOpenItem()
			Me.fileSaveItem1 = New DevExpress.XtraRichEdit.UI.FileSaveItem()
			Me.fileSaveAsItem1 = New DevExpress.XtraRichEdit.UI.FileSaveAsItem()
			Me.quickPrintItem1 = New DevExpress.XtraRichEdit.UI.QuickPrintItem()
			Me.printItem1 = New DevExpress.XtraRichEdit.UI.PrintItem()
			Me.printPreviewItem1 = New DevExpress.XtraRichEdit.UI.PrintPreviewItem()
			Me.fileInfoBar1 = New DevExpress.XtraRichEdit.UI.FileInfoBar()
			Me.showDocumentPropertiesFormItem1 = New DevExpress.XtraRichEdit.UI.ShowDocumentPropertiesFormItem()
			Me.barDockControlTop = New DevExpress.XtraBars.BarDockControl()
			Me.barDockControlBottom = New DevExpress.XtraBars.BarDockControl()
			Me.barDockControlLeft = New DevExpress.XtraBars.BarDockControl()
			Me.barDockControlRight = New DevExpress.XtraBars.BarDockControl()
			Me.dockManager1 = New DevExpress.XtraBars.Docking.DockManager(Me.components)
			Me.dockPanel1 = New DevExpress.XtraBars.Docking.DockPanel()
			Me.dockPanel1_Container = New DevExpress.XtraBars.Docking.ControlContainer()
			Me.richEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController(Me.components)
			DirectCast(Me.passwordEdit1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.encryptionComboBox1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.barManager1, System.ComponentModel.ISupportInitialize).BeginInit()
			DirectCast(Me.dockManager1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.dockPanel1.SuspendLayout()
			Me.dockPanel1_Container.SuspendLayout()
			DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' simpleButton1
			' 
			Me.simpleButton1.Location = New System.Drawing.Point(25, 132)
			Me.simpleButton1.Name = "simpleButton1"
			Me.simpleButton1.Size = New System.Drawing.Size(75, 23)
			Me.simpleButton1.TabIndex = 4
			Me.simpleButton1.Text = "Export As..."
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.simpleButton1.Click += new System.EventHandler(this.SimpleButton1_Click);
			' 
			' label2
			' 
			Me.label2.AutoSize = True
			Me.label2.Location = New System.Drawing.Point(25, 79)
			Me.label2.Name = "label2"
			Me.label2.Size = New System.Drawing.Size(53, 13)
			Me.label2.TabIndex = 3
			Me.label2.Text = "Password"
			' 
			' passwordEdit1
			' 
			Me.passwordEdit1.Location = New System.Drawing.Point(25, 95)
			Me.passwordEdit1.Name = "passwordEdit1"
			Me.passwordEdit1.Properties.PasswordChar = "*"c
			Me.passwordEdit1.Properties.UseSystemPasswordChar = True
			Me.passwordEdit1.Size = New System.Drawing.Size(173, 20)
			Me.passwordEdit1.TabIndex = 2
			' 
			' label1
			' 
			Me.label1.AutoSize = True
			Me.label1.Location = New System.Drawing.Point(22, 21)
			Me.label1.Name = "label1"
			Me.label1.Size = New System.Drawing.Size(89, 13)
			Me.label1.TabIndex = 1
			Me.label1.Text = "Encryption Type:"
			' 
			' encryptionComboBox1
			' 
			Me.encryptionComboBox1.Location = New System.Drawing.Point(25, 37)
			Me.encryptionComboBox1.Name = "encryptionComboBox1"
			Me.encryptionComboBox1.Properties.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.encryptionComboBox1.Size = New System.Drawing.Size(173, 20)
			Me.encryptionComboBox1.TabIndex = 0
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(257, 27)
			Me.richEditControl1.MenuManager = Me.barManager1
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Options.Printing.PrintPreviewFormKind = DevExpress.XtraRichEdit.PrintPreviewFormKind.Bars
			Me.richEditControl1.Size = New System.Drawing.Size(551, 423)
			Me.richEditControl1.TabIndex = 1
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.richEditControl1.BeforeImport += new DevExpress.XtraRichEdit.BeforeImportEventHandler(this.RichEditControl1_BeforeImport);
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.richEditControl1.DecryptionFailed += new DevExpress.XtraRichEdit.DecryptionFailedEventHandler(this.RichEditControl1_DecryptionFailed);
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.richEditControl1.EncryptedFilePasswordRequested += new DevExpress.XtraRichEdit.EncryptedFilePasswordRequestedEventHandler(this.RichEditControl1_EncryptedFilePasswordRequested);
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.richEditControl1.EncryptedFilePasswordCheckFailed += new DevExpress.XtraRichEdit.EncryptedFilePasswordCheckFailedEventHandler(this.RichEditControl1_EncryptedFilePasswordCheckFailed);
			' 
			' barManager1
			' 
			Me.barManager1.Bars.AddRange(New DevExpress.XtraBars.Bar() { Me.commonBar1, Me.fileInfoBar1})
			Me.barManager1.DockControls.Add(Me.barDockControlTop)
			Me.barManager1.DockControls.Add(Me.barDockControlBottom)
			Me.barManager1.DockControls.Add(Me.barDockControlLeft)
			Me.barManager1.DockControls.Add(Me.barDockControlRight)
			Me.barManager1.DockManager = Me.dockManager1
			Me.barManager1.Form = Me
			Me.barManager1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.undoItem1, Me.redoItem1, Me.fileNewItem1, Me.fileOpenItem1, Me.fileSaveItem1, Me.fileSaveAsItem1, Me.quickPrintItem1, Me.printItem1, Me.printPreviewItem1, Me.showDocumentPropertiesFormItem1})
			Me.barManager1.MaxItemId = 10
			' 
			' commonBar1
			' 
			Me.commonBar1.Control = Me.richEditControl1
			Me.commonBar1.DockCol = 0
			Me.commonBar1.DockRow = 0
			Me.commonBar1.DockStyle = DevExpress.XtraBars.BarDockStyle.Top
			Me.commonBar1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {
				New DevExpress.XtraBars.LinkPersistInfo(Me.undoItem1),
				New DevExpress.XtraBars.LinkPersistInfo(Me.redoItem1),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.fileNewItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "N", ""),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.fileOpenItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "O", ""),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.fileSaveItem1, "", False, True, False, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "S", ""),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.fileSaveAsItem1, "", False, True, False, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "A", ""),
				New DevExpress.XtraBars.LinkPersistInfo(Me.quickPrintItem1),
				New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.printItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "P", ""),
				New DevExpress.XtraBars.LinkPersistInfo(Me.printPreviewItem1)
			})
			' 
			' undoItem1
			' 
			Me.undoItem1.Id = 0
			Me.undoItem1.Name = "undoItem1"
			' 
			' redoItem1
			' 
			Me.redoItem1.Id = 1
			Me.redoItem1.Name = "redoItem1"
			' 
			' fileNewItem1
			' 
			Me.fileNewItem1.Id = 2
			Me.fileNewItem1.Name = "fileNewItem1"
			' 
			' fileOpenItem1
			' 
			Me.fileOpenItem1.Id = 3
			Me.fileOpenItem1.Name = "fileOpenItem1"
			' 
			' fileSaveItem1
			' 
			Me.fileSaveItem1.Id = 4
			Me.fileSaveItem1.Name = "fileSaveItem1"
			' 
			' fileSaveAsItem1
			' 
			Me.fileSaveAsItem1.Id = 5
			Me.fileSaveAsItem1.Name = "fileSaveAsItem1"
			' 
			' quickPrintItem1
			' 
			Me.quickPrintItem1.Id = 6
			Me.quickPrintItem1.Name = "quickPrintItem1"
			' 
			' printItem1
			' 
			Me.printItem1.Id = 7
			Me.printItem1.Name = "printItem1"
			' 
			' printPreviewItem1
			' 
			Me.printPreviewItem1.Id = 8
			Me.printPreviewItem1.Name = "printPreviewItem1"
			' 
			' fileInfoBar1
			' 
			Me.fileInfoBar1.Control = Me.richEditControl1
			Me.fileInfoBar1.DockCol = 1
			Me.fileInfoBar1.DockRow = 0
			Me.fileInfoBar1.DockStyle = DevExpress.XtraBars.BarDockStyle.Top
			Me.fileInfoBar1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() { New DevExpress.XtraBars.LinkPersistInfo(Me.showDocumentPropertiesFormItem1)})
			' 
			' showDocumentPropertiesFormItem1
			' 
			Me.showDocumentPropertiesFormItem1.Id = 9
			Me.showDocumentPropertiesFormItem1.Name = "showDocumentPropertiesFormItem1"
			' 
			' barDockControlTop
			' 
			Me.barDockControlTop.CausesValidation = False
			Me.barDockControlTop.Dock = System.Windows.Forms.DockStyle.Top
			Me.barDockControlTop.Location = New System.Drawing.Point(0, 0)
			Me.barDockControlTop.Manager = Me.barManager1
			Me.barDockControlTop.Size = New System.Drawing.Size(808, 27)
			' 
			' barDockControlBottom
			' 
			Me.barDockControlBottom.CausesValidation = False
			Me.barDockControlBottom.Dock = System.Windows.Forms.DockStyle.Bottom
			Me.barDockControlBottom.Location = New System.Drawing.Point(0, 450)
			Me.barDockControlBottom.Manager = Me.barManager1
			Me.barDockControlBottom.Size = New System.Drawing.Size(808, 0)
			' 
			' barDockControlLeft
			' 
			Me.barDockControlLeft.CausesValidation = False
			Me.barDockControlLeft.Dock = System.Windows.Forms.DockStyle.Left
			Me.barDockControlLeft.Location = New System.Drawing.Point(0, 27)
			Me.barDockControlLeft.Manager = Me.barManager1
			Me.barDockControlLeft.Size = New System.Drawing.Size(0, 423)
			' 
			' barDockControlRight
			' 
			Me.barDockControlRight.CausesValidation = False
			Me.barDockControlRight.Dock = System.Windows.Forms.DockStyle.Right
			Me.barDockControlRight.Location = New System.Drawing.Point(808, 27)
			Me.barDockControlRight.Manager = Me.barManager1
			Me.barDockControlRight.Size = New System.Drawing.Size(0, 423)
			' 
			' dockManager1
			' 
			Me.dockManager1.Form = Me
			Me.dockManager1.MenuManager = Me.barManager1
			Me.dockManager1.RootPanels.AddRange(New DevExpress.XtraBars.Docking.DockPanel() { Me.dockPanel1})
			Me.dockManager1.TopZIndexControls.AddRange(New String() { "DevExpress.XtraBars.BarDockControl", "DevExpress.XtraBars.StandaloneBarDockControl", "System.Windows.Forms.StatusBar", "System.Windows.Forms.MenuStrip", "System.Windows.Forms.StatusStrip", "DevExpress.XtraBars.Ribbon.RibbonStatusBar", "DevExpress.XtraBars.Ribbon.RibbonControl", "DevExpress.XtraBars.Navigation.OfficeNavigationBar", "DevExpress.XtraBars.Navigation.TileNavPane", "DevExpress.XtraBars.TabFormControl", "DevExpress.XtraBars.FluentDesignSystem.FluentDesignFormControl", "DevExpress.XtraBars.ToolbarForm.ToolbarFormControl"})
			' 
			' dockPanel1
			' 
			Me.dockPanel1.Controls.Add(Me.dockPanel1_Container)
			Me.dockPanel1.Dock = DevExpress.XtraBars.Docking.DockingStyle.Left
			Me.dockPanel1.ID = New System.Guid("ddc6a711-d122-4f6e-a111-93af6ccf94e7")
			Me.dockPanel1.Location = New System.Drawing.Point(0, 27)
			Me.dockPanel1.Name = "dockPanel1"
			Me.dockPanel1.OriginalSize = New System.Drawing.Size(257, 200)
			Me.dockPanel1.Size = New System.Drawing.Size(257, 423)
			Me.dockPanel1.Text = "Encryption Options"
			' 
			' dockPanel1_Container
			' 
			Me.dockPanel1_Container.Controls.Add(Me.simpleButton1)
			Me.dockPanel1_Container.Controls.Add(Me.label1)
			Me.dockPanel1_Container.Controls.Add(Me.label2)
			Me.dockPanel1_Container.Controls.Add(Me.encryptionComboBox1)
			Me.dockPanel1_Container.Controls.Add(Me.passwordEdit1)
			Me.dockPanel1_Container.Location = New System.Drawing.Point(3, 46)
			Me.dockPanel1_Container.Name = "dockPanel1_Container"
			Me.dockPanel1_Container.Size = New System.Drawing.Size(250, 374)
			Me.dockPanel1_Container.TabIndex = 0
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
			Me.richEditBarController1.Control = Me.richEditControl1
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(808, 450)
			Me.Controls.Add(Me.richEditControl1)
			Me.Controls.Add(Me.dockPanel1)
			Me.Controls.Add(Me.barDockControlLeft)
			Me.Controls.Add(Me.barDockControlRight)
			Me.Controls.Add(Me.barDockControlBottom)
			Me.Controls.Add(Me.barDockControlTop)
			Me.Name = "Form1"
			Me.ShowIcon = False
			Me.Text = "Rich Text Editor"
			DirectCast(Me.passwordEdit1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.encryptionComboBox1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.barManager1, System.ComponentModel.ISupportInitialize).EndInit()
			DirectCast(Me.dockManager1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.dockPanel1.ResumeLayout(False)
			Me.dockPanel1_Container.ResumeLayout(False)
			Me.dockPanel1_Container.PerformLayout()
			DirectCast(Me.richEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region
		Private WithEvents richEditControl1 As MyRichEditControl
		Private WithEvents simpleButton1 As DevExpress.XtraEditors.SimpleButton
		Private label2 As System.Windows.Forms.Label
		Private passwordEdit1 As DevExpress.XtraEditors.TextEdit
		Private label1 As System.Windows.Forms.Label
		Private encryptionComboBox1 As DevExpress.XtraEditors.ComboBoxEdit
		Private richEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
		Private barManager1 As DevExpress.XtraBars.BarManager
		Private commonBar1 As DevExpress.XtraRichEdit.UI.CommonBar
		Private undoItem1 As DevExpress.XtraRichEdit.UI.UndoItem
		Private redoItem1 As DevExpress.XtraRichEdit.UI.RedoItem
		Private fileNewItem1 As DevExpress.XtraRichEdit.UI.FileNewItem
		Private fileOpenItem1 As DevExpress.XtraRichEdit.UI.FileOpenItem
		Private fileSaveItem1 As DevExpress.XtraRichEdit.UI.FileSaveItem
		Private fileSaveAsItem1 As DevExpress.XtraRichEdit.UI.FileSaveAsItem
		Private quickPrintItem1 As DevExpress.XtraRichEdit.UI.QuickPrintItem
		Private printItem1 As DevExpress.XtraRichEdit.UI.PrintItem
		Private printPreviewItem1 As DevExpress.XtraRichEdit.UI.PrintPreviewItem
		Private fileInfoBar1 As DevExpress.XtraRichEdit.UI.FileInfoBar
		Private showDocumentPropertiesFormItem1 As DevExpress.XtraRichEdit.UI.ShowDocumentPropertiesFormItem
		Private barDockControlTop As DevExpress.XtraBars.BarDockControl
		Private barDockControlBottom As DevExpress.XtraBars.BarDockControl
		Private barDockControlLeft As DevExpress.XtraBars.BarDockControl
		Private barDockControlRight As DevExpress.XtraBars.BarDockControl
		Private dockManager1 As DevExpress.XtraBars.Docking.DockManager
		Private dockPanel1 As DevExpress.XtraBars.Docking.DockPanel
		Private dockPanel1_Container As DevExpress.XtraBars.Docking.ControlContainer
	End Class
End Namespace

