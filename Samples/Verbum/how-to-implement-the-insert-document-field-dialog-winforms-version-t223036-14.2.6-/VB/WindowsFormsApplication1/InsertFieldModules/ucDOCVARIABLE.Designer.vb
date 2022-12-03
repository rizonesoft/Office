Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class ucDOCVARIABLE
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

		#Region "Component Designer generated code"

		''' <summary> 
		''' Required method for Designer support - do not modify 
		''' the contents of this method with the code editor.
		''' </summary>
		Private Sub InitializeComponent()
			Me.layoutControl1 = New DevExpress.XtraLayout.LayoutControl()
			Me.textEditVariableName = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditArgument1 = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditArgument2 = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem3 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditArgument3 = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem4 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditArgument4 = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem5 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.emptySpaceItem1 = New DevExpress.XtraLayout.EmptySpaceItem()
			Me.layoutControlGroup2 = New DevExpress.XtraLayout.LayoutControlGroup()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.textEditVariableName.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditArgument1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditArgument2.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditArgument3.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditArgument4.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup2, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.textEditArgument4)
			Me.layoutControl1.Controls.Add(Me.textEditArgument3)
			Me.layoutControl1.Controls.Add(Me.textEditArgument2)
			Me.layoutControl1.Controls.Add(Me.textEditArgument1)
			Me.layoutControl1.Controls.Add(Me.textEditVariableName)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.BackColor = System.Drawing.Color.LightGray
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.Font = New System.Drawing.Font("Tahoma", 10.25F)
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.Options.UseBackColor = True
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.Options.UseFont = True
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.Options.UseTextOptions = True
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Center
			Me.layoutControl1.OptionsPrint.AppearanceGroupCaption.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Center
			Me.layoutControl1.OptionsPrint.AppearanceItemCaption.Options.UseTextOptions = True
			Me.layoutControl1.OptionsPrint.AppearanceItemCaption.TextOptions.HAlignment = DevExpress.Utils.HorzAlignment.Near
			Me.layoutControl1.OptionsPrint.AppearanceItemCaption.TextOptions.VAlignment = DevExpress.Utils.VertAlignment.Center
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(506, 435)
			Me.layoutControl1.TabIndex = 0
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' textEditVariableName
			' 
			Me.textEditVariableName.Location = New System.Drawing.Point(12, 28)
			Me.textEditVariableName.Name = "textEditVariableName"
			Me.textEditVariableName.Size = New System.Drawing.Size(482, 20)
			Me.textEditVariableName.StyleController = Me.layoutControl1
			Me.textEditVariableName.TabIndex = 4
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.emptySpaceItem1, Me.layoutControlGroup2})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "layoutControlGroup1"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(506, 435)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.textEditVariableName
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(486, 40)
			Me.layoutControlItem1.Text = "New variable name"
			Me.layoutControlItem1.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(91, 13)
			' 
			' textEditArgument1
			' 
			Me.textEditArgument1.Location = New System.Drawing.Point(118, 83)
			Me.textEditArgument1.Name = "textEditArgument1"
			Me.textEditArgument1.Size = New System.Drawing.Size(364, 20)
			Me.textEditArgument1.StyleController = Me.layoutControl1
			Me.textEditArgument1.TabIndex = 5
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.textEditArgument1
			Me.layoutControlItem2.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(462, 24)
			Me.layoutControlItem2.Text = "Argument 1:"
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(91, 13)
			' 
			' textEditArgument2
			' 
			Me.textEditArgument2.Location = New System.Drawing.Point(118, 107)
			Me.textEditArgument2.Name = "textEditArgument2"
			Me.textEditArgument2.Size = New System.Drawing.Size(364, 20)
			Me.textEditArgument2.StyleController = Me.layoutControl1
			Me.textEditArgument2.TabIndex = 6
			' 
			' layoutControlItem3
			' 
			Me.layoutControlItem3.Control = Me.textEditArgument2
			Me.layoutControlItem3.Location = New System.Drawing.Point(0, 24)
			Me.layoutControlItem3.Name = "layoutControlItem3"
			Me.layoutControlItem3.Size = New System.Drawing.Size(462, 24)
			Me.layoutControlItem3.Text = "Argument 2:"
			Me.layoutControlItem3.TextSize = New System.Drawing.Size(91, 13)
			' 
			' textEditArgument3
			' 
			Me.textEditArgument3.Location = New System.Drawing.Point(118, 131)
			Me.textEditArgument3.Name = "textEditArgument3"
			Me.textEditArgument3.Size = New System.Drawing.Size(364, 20)
			Me.textEditArgument3.StyleController = Me.layoutControl1
			Me.textEditArgument3.TabIndex = 7
			' 
			' layoutControlItem4
			' 
			Me.layoutControlItem4.Control = Me.textEditArgument3
			Me.layoutControlItem4.Location = New System.Drawing.Point(0, 48)
			Me.layoutControlItem4.Name = "layoutControlItem4"
			Me.layoutControlItem4.Size = New System.Drawing.Size(462, 24)
			Me.layoutControlItem4.Text = "Argument 3:"
			Me.layoutControlItem4.TextSize = New System.Drawing.Size(91, 13)
			' 
			' textEditArgument4
			' 
			Me.textEditArgument4.Location = New System.Drawing.Point(118, 155)
			Me.textEditArgument4.Name = "textEditArgument4"
			Me.textEditArgument4.Size = New System.Drawing.Size(364, 20)
			Me.textEditArgument4.StyleController = Me.layoutControl1
			Me.textEditArgument4.TabIndex = 8
			' 
			' layoutControlItem5
			' 
			Me.layoutControlItem5.Control = Me.textEditArgument4
			Me.layoutControlItem5.Location = New System.Drawing.Point(0, 72)
			Me.layoutControlItem5.Name = "layoutControlItem5"
			Me.layoutControlItem5.Size = New System.Drawing.Size(462, 24)
			Me.layoutControlItem5.Text = "Argument 4:"
			Me.layoutControlItem5.TextSize = New System.Drawing.Size(91, 13)
			' 
			' emptySpaceItem1
			' 
			Me.emptySpaceItem1.AllowHotTrack = False
			Me.emptySpaceItem1.Location = New System.Drawing.Point(0, 179)
			Me.emptySpaceItem1.Name = "emptySpaceItem1"
			Me.emptySpaceItem1.Size = New System.Drawing.Size(486, 236)
			Me.emptySpaceItem1.TextSize = New System.Drawing.Size(0, 0)
			' 
			' layoutControlGroup2
			' 
			Me.layoutControlGroup2.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem2, Me.layoutControlItem3, Me.layoutControlItem4, Me.layoutControlItem5})
			Me.layoutControlGroup2.Location = New System.Drawing.Point(0, 40)
			Me.layoutControlGroup2.Name = "layoutControlGroup2"
			Me.layoutControlGroup2.Size = New System.Drawing.Size(486, 139)
			Me.layoutControlGroup2.Text = "Arguments"
			' 
			' ucDOCVARIABLE
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.Controls.Add(Me.layoutControl1)
			Me.Name = "ucDOCVARIABLE"
			Me.Size = New System.Drawing.Size(506, 435)
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.textEditVariableName.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditArgument1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditArgument2.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditArgument3.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditArgument4.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup2, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private textEditVariableName As DevExpress.XtraEditors.TextEdit
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private textEditArgument4 As DevExpress.XtraEditors.TextEdit
		Private textEditArgument3 As DevExpress.XtraEditors.TextEdit
		Private textEditArgument2 As DevExpress.XtraEditors.TextEdit
		Private textEditArgument1 As DevExpress.XtraEditors.TextEdit
		Private emptySpaceItem1 As DevExpress.XtraLayout.EmptySpaceItem
		Private layoutControlGroup2 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem3 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem4 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem5 As DevExpress.XtraLayout.LayoutControlItem
	End Class
End Namespace
