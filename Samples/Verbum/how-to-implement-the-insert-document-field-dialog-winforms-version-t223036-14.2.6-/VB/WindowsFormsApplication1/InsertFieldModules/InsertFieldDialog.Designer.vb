Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class InsertFieldDialog
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
			Me.memoEdit1 = New DevExpress.XtraEditors.MemoEdit()
			Me.simpleButtonCancel = New DevExpress.XtraEditors.SimpleButton()
			Me.simpleButtonOk = New DevExpress.XtraEditors.SimpleButton()
			Me.listBoxFieldNames = New DevExpress.XtraEditors.ListBoxControl()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem3 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.emptySpaceItem1 = New DevExpress.XtraLayout.EmptySpaceItem()
			Me.layoutControlItemMainContent = New DevExpress.XtraLayout.LayoutControlItem()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.memoEdit1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.listBoxFieldNames, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItemMainContent, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.memoEdit1)
			Me.layoutControl1.Controls.Add(Me.simpleButtonCancel)
			Me.layoutControl1.Controls.Add(Me.simpleButtonOk)
			Me.layoutControl1.Controls.Add(Me.listBoxFieldNames)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.OptionsCustomizationForm.DesignTimeCustomizationFormPositionAndSize = New System.Drawing.Rectangle(687, 210, 705, 582)
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(761, 509)
			Me.layoutControl1.TabIndex = 0
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' memoEdit1
			' 
			Me.memoEdit1.Location = New System.Drawing.Point(212, 28)
			Me.memoEdit1.Name = "memoEdit1"
			Me.memoEdit1.Size = New System.Drawing.Size(537, 443)
			Me.memoEdit1.StyleController = Me.layoutControl1
			Me.memoEdit1.TabIndex = 7
			' 
			' simpleButtonCancel
			' 
			Me.simpleButtonCancel.DialogResult = System.Windows.Forms.DialogResult.Cancel
			Me.simpleButtonCancel.Location = New System.Drawing.Point(622, 475)
			Me.simpleButtonCancel.Name = "simpleButtonCancel"
			Me.simpleButtonCancel.Size = New System.Drawing.Size(127, 22)
			Me.simpleButtonCancel.StyleController = Me.layoutControl1
			Me.simpleButtonCancel.TabIndex = 6
			Me.simpleButtonCancel.Text = "Cancel"
			' 
			' simpleButtonOk
			' 
			Me.simpleButtonOk.Location = New System.Drawing.Point(499, 475)
			Me.simpleButtonOk.Name = "simpleButtonOk"
			Me.simpleButtonOk.Size = New System.Drawing.Size(119, 22)
			Me.simpleButtonOk.StyleController = Me.layoutControl1
			Me.simpleButtonOk.TabIndex = 5
			Me.simpleButtonOk.Text = "Ok"
'			Me.simpleButtonOk.Click += New System.EventHandler(Me.simpleButtonOk_Click);
			' 
			' listBoxFieldNames
			' 
			Me.listBoxFieldNames.Location = New System.Drawing.Point(12, 28)
			Me.listBoxFieldNames.Name = "listBoxFieldNames"
			Me.listBoxFieldNames.Size = New System.Drawing.Size(196, 443)
			Me.listBoxFieldNames.StyleController = Me.layoutControl1
			Me.listBoxFieldNames.TabIndex = 4
'			Me.listBoxFieldNames.SelectedIndexChanged += New System.EventHandler(Me.listBoxFieldNames_SelectedIndexChanged);
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem2, Me.layoutControlItem3, Me.emptySpaceItem1, Me.layoutControlItemMainContent})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "Root"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(761, 509)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.AppearanceItemCaption.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlItem1.AppearanceItemCaption.Options.UseFont = True
			Me.layoutControlItem1.Control = Me.listBoxFieldNames
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(200, 463)
			Me.layoutControlItem1.Text = "Please choose a field"
			Me.layoutControlItem1.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(117, 13)
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.simpleButtonOk
			Me.layoutControlItem2.Location = New System.Drawing.Point(487, 463)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(123, 26)
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem2.TextVisible = False
			' 
			' layoutControlItem3
			' 
			Me.layoutControlItem3.Control = Me.simpleButtonCancel
			Me.layoutControlItem3.Location = New System.Drawing.Point(610, 463)
			Me.layoutControlItem3.Name = "layoutControlItem3"
			Me.layoutControlItem3.Size = New System.Drawing.Size(131, 26)
			Me.layoutControlItem3.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem3.TextVisible = False
			' 
			' emptySpaceItem1
			' 
			Me.emptySpaceItem1.AllowHotTrack = False
			Me.emptySpaceItem1.Location = New System.Drawing.Point(0, 463)
			Me.emptySpaceItem1.Name = "emptySpaceItem1"
			Me.emptySpaceItem1.Size = New System.Drawing.Size(446, 26)
			Me.emptySpaceItem1.TextSize = New System.Drawing.Size(0, 0)
			' 
			' layoutControlItemMainContent
			' 
			Me.layoutControlItemMainContent.AppearanceItemCaption.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlItemMainContent.AppearanceItemCaption.Options.UseFont = True
			Me.layoutControlItemMainContent.Control = Me.memoEdit1
			Me.layoutControlItemMainContent.Location = New System.Drawing.Point(200, 0)
			Me.layoutControlItemMainContent.Name = "layoutControlItemMainContent"
			Me.layoutControlItemMainContent.Size = New System.Drawing.Size(541, 463)
			Me.layoutControlItemMainContent.Text = "Field properties"
			Me.layoutControlItemMainContent.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItemMainContent.TextSize = New System.Drawing.Size(117, 13)
			' 
			' InsertFieldDialog
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.CancelButton = Me.simpleButtonCancel
			Me.ClientSize = New System.Drawing.Size(761, 509)
			Me.Controls.Add(Me.layoutControl1)
			Me.Name = "InsertFieldDialog"
			Me.Text = "Insert field"
'			Me.Load += New System.EventHandler(Me.InsertFieldDialog_Load);
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.memoEdit1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.listBoxFieldNames, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItemMainContent, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private memoEdit1 As DevExpress.XtraEditors.MemoEdit
		Private simpleButtonCancel As DevExpress.XtraEditors.SimpleButton
		Private WithEvents simpleButtonOk As DevExpress.XtraEditors.SimpleButton
		Private WithEvents listBoxFieldNames As DevExpress.XtraEditors.ListBoxControl
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem3 As DevExpress.XtraLayout.LayoutControlItem
		Private emptySpaceItem1 As DevExpress.XtraLayout.EmptySpaceItem
		Private layoutControlItemMainContent As DevExpress.XtraLayout.LayoutControlItem
	End Class
End Namespace