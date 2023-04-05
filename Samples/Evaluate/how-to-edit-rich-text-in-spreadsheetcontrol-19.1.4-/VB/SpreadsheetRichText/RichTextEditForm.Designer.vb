<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class RichTextEditForm
    Inherits DevExpress.XtraEditors.XtraForm

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        If disposing AndAlso components IsNot Nothing Then
            components.Dispose()
        End If
        MyBase.Dispose(disposing)
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Me.RichEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
        Me.BarManager1 = New DevExpress.XtraBars.BarManager(Me.components)
        Me.FontBar1 = New DevExpress.XtraRichEdit.UI.FontBar()
        Me.ChangeFontNameItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontNameItem()
        Me.RepositoryItemFontEdit1 = New DevExpress.XtraEditors.Repository.RepositoryItemFontEdit()
        Me.ChangeFontSizeItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontSizeItem()
        Me.RepositoryItemRichEditFontSizeEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit()
        Me.FontSizeIncreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem()
        Me.FontSizeDecreaseItem1 = New DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem()
        Me.ToggleFontBoldItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontBoldItem()
        Me.ToggleFontItalicItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontItalicItem()
        Me.ToggleFontUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem()
        Me.ToggleFontDoubleUnderlineItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem()
        Me.ToggleFontStrikeoutItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem()
        Me.ToggleFontSuperscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem()
        Me.ToggleFontSubscriptItem1 = New DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem()
        Me.ChangeFontColorItem1 = New DevExpress.XtraRichEdit.UI.ChangeFontColorItem()
        Me.ClearFormattingItem1 = New DevExpress.XtraRichEdit.UI.ClearFormattingItem()
        Me.barDockControlTop = New DevExpress.XtraBars.BarDockControl()
        Me.barDockControlBottom = New DevExpress.XtraBars.BarDockControl()
        Me.barDockControlLeft = New DevExpress.XtraBars.BarDockControl()
        Me.barDockControlRight = New DevExpress.XtraBars.BarDockControl()
        Me.RepositoryItemRichEditStyleEdit1 = New DevExpress.XtraRichEdit.Design.RepositoryItemRichEditStyleEdit()
        Me.RichEditBarController1 = New DevExpress.XtraRichEdit.UI.RichEditBarController(Me.components)
        Me.OKButton = New DevExpress.XtraEditors.SimpleButton()
        Me.CancelBtn = New DevExpress.XtraEditors.SimpleButton()
        CType(Me.BarManager1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.RepositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.RepositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.RepositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.RichEditBarController1, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'RichEditControl1
        '
        Me.RichEditControl1.ActiveViewType = DevExpress.XtraRichEdit.RichEditViewType.Simple
        Me.RichEditControl1.Dock = System.Windows.Forms.DockStyle.Top
        Me.RichEditControl1.LayoutUnit = DevExpress.XtraRichEdit.DocumentLayoutUnit.Pixel
        Me.RichEditControl1.Location = New System.Drawing.Point(0, 28)
        Me.RichEditControl1.MenuManager = Me.BarManager1
        Me.RichEditControl1.Name = "RichEditControl1"
        Me.RichEditControl1.Options.Behavior.Open = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Behavior.Printing = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Behavior.Save = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Behavior.SaveAs = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Behavior.ShowPopupMenu = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Behavior.Zooming = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Bookmarks = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.CharacterStyle = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Comments = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.EndNotes = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Fields = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.FloatingObjects = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.FootNotes = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.HeadersFooters = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Hyperlinks = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.InlinePictures = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.InlineShapes = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Numbering.Bulleted = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Numbering.MultiLevel = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Numbering.Simple = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.ParagraphFormatting = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.ParagraphFrames = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.ParagraphStyle = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.ParagraphTabs = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Sections = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.Tables = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.DocumentCapabilities.TableStyle = DevExpress.XtraRichEdit.DocumentCapability.Disabled
        Me.RichEditControl1.Options.Printing.PrintPreviewFormKind = DevExpress.XtraRichEdit.PrintPreviewFormKind.Bars
        Me.RichEditControl1.Size = New System.Drawing.Size(488, 146)
        Me.RichEditControl1.TabIndex = 0
        '
        'BarManager1
        '
        Me.BarManager1.Bars.AddRange(New DevExpress.XtraBars.Bar() {Me.FontBar1})
        Me.BarManager1.DockControls.Add(Me.barDockControlTop)
        Me.BarManager1.DockControls.Add(Me.barDockControlBottom)
        Me.BarManager1.DockControls.Add(Me.barDockControlLeft)
        Me.BarManager1.DockControls.Add(Me.barDockControlRight)
        Me.BarManager1.Form = Me
        Me.BarManager1.Items.AddRange(New DevExpress.XtraBars.BarItem() {Me.ChangeFontNameItem1, Me.ChangeFontSizeItem1, Me.FontSizeIncreaseItem1, Me.FontSizeDecreaseItem1, Me.ToggleFontBoldItem1, Me.ToggleFontItalicItem1, Me.ToggleFontUnderlineItem1, Me.ToggleFontDoubleUnderlineItem1, Me.ToggleFontStrikeoutItem1, Me.ToggleFontSuperscriptItem1, Me.ToggleFontSubscriptItem1, Me.ChangeFontColorItem1, Me.ClearFormattingItem1})
        Me.BarManager1.MaxItemId = 64
        Me.BarManager1.RepositoryItems.AddRange(New DevExpress.XtraEditors.Repository.RepositoryItem() {Me.RepositoryItemFontEdit1, Me.RepositoryItemRichEditFontSizeEdit1, Me.RepositoryItemRichEditStyleEdit1})
        '
        'FontBar1
        '
        Me.FontBar1.CanDockStyle = DevExpress.XtraBars.BarCanDockStyle.Top
        Me.FontBar1.Control = Me.RichEditControl1
        Me.FontBar1.DockCol = 0
        Me.FontBar1.DockRow = 0
        Me.FontBar1.DockStyle = DevExpress.XtraBars.BarDockStyle.Top
        Me.FontBar1.LinksPersistInfo.AddRange(New DevExpress.XtraBars.LinkPersistInfo() {New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.ChangeFontNameItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "FF", ""), New DevExpress.XtraBars.LinkPersistInfo(Me.ChangeFontSizeItem1), New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.FontSizeIncreaseItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "FG", ""), New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.FontSizeDecreaseItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "FK", ""), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontBoldItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontItalicItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontUnderlineItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontDoubleUnderlineItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontStrikeoutItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontSuperscriptItem1), New DevExpress.XtraBars.LinkPersistInfo(Me.ToggleFontSubscriptItem1), New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.ChangeFontColorItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "FC", ""), New DevExpress.XtraBars.LinkPersistInfo(DevExpress.XtraBars.BarLinkUserDefines.KeyTip, Me.ClearFormattingItem1, "", False, True, True, 0, Nothing, DevExpress.XtraBars.BarItemPaintStyle.Standard, "E", "")})
        Me.FontBar1.OptionsBar.DrawBorder = False
        Me.FontBar1.OptionsBar.DrawDragBorder = False
        Me.FontBar1.OptionsBar.UseWholeRow = True
        '
        'ChangeFontNameItem1
        '
        Me.ChangeFontNameItem1.Edit = Me.RepositoryItemFontEdit1
        Me.ChangeFontNameItem1.EditWidth = 100
        Me.ChangeFontNameItem1.Id = 5
        Me.ChangeFontNameItem1.Name = "ChangeFontNameItem1"
        '
        'RepositoryItemFontEdit1
        '
        Me.RepositoryItemFontEdit1.AutoHeight = False
        Me.RepositoryItemFontEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() {New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
        Me.RepositoryItemFontEdit1.Name = "RepositoryItemFontEdit1"
        '
        'ChangeFontSizeItem1
        '
        Me.ChangeFontSizeItem1.Edit = Me.RepositoryItemRichEditFontSizeEdit1
        Me.ChangeFontSizeItem1.EditWidth = 50
        Me.ChangeFontSizeItem1.Id = 6
        Me.ChangeFontSizeItem1.Name = "ChangeFontSizeItem1"
        '
        'RepositoryItemRichEditFontSizeEdit1
        '
        Me.RepositoryItemRichEditFontSizeEdit1.AutoHeight = False
        Me.RepositoryItemRichEditFontSizeEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() {New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
        Me.RepositoryItemRichEditFontSizeEdit1.Control = Me.RichEditControl1
        Me.RepositoryItemRichEditFontSizeEdit1.Name = "RepositoryItemRichEditFontSizeEdit1"
        '
        'FontSizeIncreaseItem1
        '
        Me.FontSizeIncreaseItem1.Id = 53
        Me.FontSizeIncreaseItem1.Name = "FontSizeIncreaseItem1"
        '
        'FontSizeDecreaseItem1
        '
        Me.FontSizeDecreaseItem1.Id = 54
        Me.FontSizeDecreaseItem1.Name = "FontSizeDecreaseItem1"
        '
        'ToggleFontBoldItem1
        '
        Me.ToggleFontBoldItem1.Id = 55
        Me.ToggleFontBoldItem1.Name = "ToggleFontBoldItem1"
        '
        'ToggleFontItalicItem1
        '
        Me.ToggleFontItalicItem1.Id = 56
        Me.ToggleFontItalicItem1.Name = "ToggleFontItalicItem1"
        '
        'ToggleFontUnderlineItem1
        '
        Me.ToggleFontUnderlineItem1.Id = 57
        Me.ToggleFontUnderlineItem1.Name = "ToggleFontUnderlineItem1"
        '
        'ToggleFontDoubleUnderlineItem1
        '
        Me.ToggleFontDoubleUnderlineItem1.Id = 58
        Me.ToggleFontDoubleUnderlineItem1.Name = "ToggleFontDoubleUnderlineItem1"
        '
        'ToggleFontStrikeoutItem1
        '
        Me.ToggleFontStrikeoutItem1.Id = 59
        Me.ToggleFontStrikeoutItem1.Name = "ToggleFontStrikeoutItem1"
        '
        'ToggleFontSuperscriptItem1
        '
        Me.ToggleFontSuperscriptItem1.Id = 60
        Me.ToggleFontSuperscriptItem1.Name = "ToggleFontSuperscriptItem1"
        '
        'ToggleFontSubscriptItem1
        '
        Me.ToggleFontSubscriptItem1.Id = 61
        Me.ToggleFontSubscriptItem1.Name = "ToggleFontSubscriptItem1"
        '
        'ChangeFontColorItem1
        '
        Me.ChangeFontColorItem1.Id = 62
        Me.ChangeFontColorItem1.Name = "ChangeFontColorItem1"
        '
        'ClearFormattingItem1
        '
        Me.ClearFormattingItem1.Id = 63
        Me.ClearFormattingItem1.Name = "ClearFormattingItem1"
        '
        'barDockControlTop
        '
        Me.barDockControlTop.CausesValidation = False
        Me.barDockControlTop.Dock = System.Windows.Forms.DockStyle.Top
        Me.barDockControlTop.Location = New System.Drawing.Point(0, 0)
        Me.barDockControlTop.Manager = Me.BarManager1
        Me.barDockControlTop.Size = New System.Drawing.Size(488, 28)
        '
        'barDockControlBottom
        '
        Me.barDockControlBottom.CausesValidation = False
        Me.barDockControlBottom.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.barDockControlBottom.Location = New System.Drawing.Point(0, 211)
        Me.barDockControlBottom.Manager = Me.BarManager1
        Me.barDockControlBottom.Size = New System.Drawing.Size(488, 0)
        '
        'barDockControlLeft
        '
        Me.barDockControlLeft.CausesValidation = False
        Me.barDockControlLeft.Dock = System.Windows.Forms.DockStyle.Left
        Me.barDockControlLeft.Location = New System.Drawing.Point(0, 28)
        Me.barDockControlLeft.Manager = Me.BarManager1
        Me.barDockControlLeft.Size = New System.Drawing.Size(0, 183)
        '
        'barDockControlRight
        '
        Me.barDockControlRight.CausesValidation = False
        Me.barDockControlRight.Dock = System.Windows.Forms.DockStyle.Right
        Me.barDockControlRight.Location = New System.Drawing.Point(488, 28)
        Me.barDockControlRight.Manager = Me.BarManager1
        Me.barDockControlRight.Size = New System.Drawing.Size(0, 183)
        '
        'RepositoryItemRichEditStyleEdit1
        '
        Me.RepositoryItemRichEditStyleEdit1.AutoHeight = False
        Me.RepositoryItemRichEditStyleEdit1.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() {New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
        Me.RepositoryItemRichEditStyleEdit1.Control = Me.RichEditControl1
        Me.RepositoryItemRichEditStyleEdit1.Name = "RepositoryItemRichEditStyleEdit1"
        '
        'RichEditBarController1
        '
        Me.RichEditBarController1.BarItems.Add(Me.ChangeFontNameItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ChangeFontSizeItem1)
        Me.RichEditBarController1.BarItems.Add(Me.FontSizeIncreaseItem1)
        Me.RichEditBarController1.BarItems.Add(Me.FontSizeDecreaseItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontBoldItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontItalicItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontUnderlineItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontDoubleUnderlineItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontStrikeoutItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontSuperscriptItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ToggleFontSubscriptItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ChangeFontColorItem1)
        Me.RichEditBarController1.BarItems.Add(Me.ClearFormattingItem1)
        Me.RichEditBarController1.Control = Me.RichEditControl1
        '
        'OKButton
        '
        Me.OKButton.DialogResult = System.Windows.Forms.DialogResult.OK
        Me.OKButton.Location = New System.Drawing.Point(350, 180)
        Me.OKButton.Name = "OKButton"
        Me.OKButton.Size = New System.Drawing.Size(60, 25)
        Me.OKButton.TabIndex = 5
        Me.OKButton.Text = "OK"
        '
        'CancelBtn
        '
        Me.CancelBtn.DialogResult = System.Windows.Forms.DialogResult.Cancel
        Me.CancelBtn.Location = New System.Drawing.Point(416, 180)
        Me.CancelBtn.Name = "CancelButton"
        Me.CancelBtn.Size = New System.Drawing.Size(60, 25)
        Me.CancelBtn.TabIndex = 6
        Me.CancelBtn.Text = "Cancel"
        '
        'RichTextEditForm
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(488, 211)
        Me.Controls.Add(Me.CancelBtn)
        Me.Controls.Add(Me.OKButton)
        Me.Controls.Add(Me.RichEditControl1)
        Me.Controls.Add(Me.barDockControlLeft)
        Me.Controls.Add(Me.barDockControlRight)
        Me.Controls.Add(Me.barDockControlBottom)
        Me.Controls.Add(Me.barDockControlTop)
        Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
        Me.MaximizeBox = False
        Me.MinimizeBox = False
        Me.Name = "RichTextEditForm"
        Me.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide
        Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent
        Me.Text = "Rich Text Edit Form"
        CType(Me.BarManager1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.RepositoryItemFontEdit1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.RepositoryItemRichEditFontSizeEdit1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.RepositoryItemRichEditStyleEdit1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.RichEditBarController1, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents RichEditControl1 As DevExpress.XtraRichEdit.RichEditControl
    Friend WithEvents BarManager1 As DevExpress.XtraBars.BarManager
    Friend WithEvents FontBar1 As DevExpress.XtraRichEdit.UI.FontBar
    Friend WithEvents ChangeFontNameItem1 As DevExpress.XtraRichEdit.UI.ChangeFontNameItem
    Friend WithEvents RepositoryItemFontEdit1 As DevExpress.XtraEditors.Repository.RepositoryItemFontEdit
    Friend WithEvents ChangeFontSizeItem1 As DevExpress.XtraRichEdit.UI.ChangeFontSizeItem
    Friend WithEvents RepositoryItemRichEditFontSizeEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditFontSizeEdit
    Friend WithEvents FontSizeIncreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeIncreaseItem
    Friend WithEvents FontSizeDecreaseItem1 As DevExpress.XtraRichEdit.UI.FontSizeDecreaseItem
    Friend WithEvents ToggleFontBoldItem1 As DevExpress.XtraRichEdit.UI.ToggleFontBoldItem
    Friend WithEvents ToggleFontItalicItem1 As DevExpress.XtraRichEdit.UI.ToggleFontItalicItem
    Friend WithEvents ToggleFontUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontUnderlineItem
    Friend WithEvents ToggleFontDoubleUnderlineItem1 As DevExpress.XtraRichEdit.UI.ToggleFontDoubleUnderlineItem
    Friend WithEvents ToggleFontStrikeoutItem1 As DevExpress.XtraRichEdit.UI.ToggleFontStrikeoutItem
    Friend WithEvents ToggleFontSuperscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSuperscriptItem
    Friend WithEvents ToggleFontSubscriptItem1 As DevExpress.XtraRichEdit.UI.ToggleFontSubscriptItem
    Friend WithEvents ChangeFontColorItem1 As DevExpress.XtraRichEdit.UI.ChangeFontColorItem
    Friend WithEvents ClearFormattingItem1 As DevExpress.XtraRichEdit.UI.ClearFormattingItem
    Friend WithEvents barDockControlTop As DevExpress.XtraBars.BarDockControl
    Friend WithEvents barDockControlBottom As DevExpress.XtraBars.BarDockControl
    Friend WithEvents barDockControlLeft As DevExpress.XtraBars.BarDockControl
    Friend WithEvents barDockControlRight As DevExpress.XtraBars.BarDockControl
    Friend WithEvents RepositoryItemRichEditStyleEdit1 As DevExpress.XtraRichEdit.Design.RepositoryItemRichEditStyleEdit
    Friend WithEvents RichEditBarController1 As DevExpress.XtraRichEdit.UI.RichEditBarController
    Friend WithEvents CancelBtn As DevExpress.XtraEditors.SimpleButton
    Friend WithEvents OKButton As DevExpress.XtraEditors.SimpleButton
End Class
