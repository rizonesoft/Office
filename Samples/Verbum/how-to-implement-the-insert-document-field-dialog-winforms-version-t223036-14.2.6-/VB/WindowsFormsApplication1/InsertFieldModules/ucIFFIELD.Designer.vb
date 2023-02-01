Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class ucIFFIELD
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
			Me.textEditLeftExpression = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControl1 = New DevExpress.XtraLayout.LayoutControl()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.checkEditInsertLeftAsField = New DevExpress.XtraEditors.CheckEdit()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.comboBoxEditOperation = New DevExpress.XtraEditors.ComboBoxEdit()
			Me.layoutControlItem3 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditRIGHTExpression = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem4 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.checkEditInsertRightAsField = New DevExpress.XtraEditors.CheckEdit()
			Me.layoutControlItem5 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditResultTRUE = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem6 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditResultFALSE = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem7 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.emptySpaceItem1 = New DevExpress.XtraLayout.EmptySpaceItem()
			Me.emptySpaceItem2 = New DevExpress.XtraLayout.EmptySpaceItem()
			Me.layoutControlGroup2 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlGroup3 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.checkEditInsertResultTRUEAsField = New DevExpress.XtraEditors.CheckEdit()
			Me.layoutControlItem8 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.checkEditInsertResultFALSEAsField = New DevExpress.XtraEditors.CheckEdit()
			Me.layoutControlItem9 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlGroup4 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlGroup5 = New DevExpress.XtraLayout.LayoutControlGroup()
			CType(Me.textEditLeftExpression.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.checkEditInsertLeftAsField.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.comboBoxEditOperation.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditRIGHTExpression.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.checkEditInsertRightAsField.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditResultTRUE.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem6, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditResultFALSE.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem7, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.emptySpaceItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup3, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.checkEditInsertResultTRUEAsField.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem8, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.checkEditInsertResultFALSEAsField.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem9, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup4, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup5, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' textEditLeftExpression
			' 
			Me.textEditLeftExpression.Location = New System.Drawing.Point(24, 43)
			Me.textEditLeftExpression.Name = "textEditLeftExpression"
			Me.textEditLeftExpression.Size = New System.Drawing.Size(520, 20)
			Me.textEditLeftExpression.StyleController = Me.layoutControl1
			Me.textEditLeftExpression.TabIndex = 0
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.checkEditInsertResultFALSEAsField)
			Me.layoutControl1.Controls.Add(Me.checkEditInsertResultTRUEAsField)
			Me.layoutControl1.Controls.Add(Me.textEditResultFALSE)
			Me.layoutControl1.Controls.Add(Me.textEditResultTRUE)
			Me.layoutControl1.Controls.Add(Me.checkEditInsertRightAsField)
			Me.layoutControl1.Controls.Add(Me.textEditRIGHTExpression)
			Me.layoutControl1.Controls.Add(Me.comboBoxEditOperation)
			Me.layoutControl1.Controls.Add(Me.checkEditInsertLeftAsField)
			Me.layoutControl1.Controls.Add(Me.textEditLeftExpression)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.OptionsCustomizationForm.DesignTimeCustomizationFormPositionAndSize = New System.Drawing.Rectangle(820, 380, 635, 506)
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(568, 463)
			Me.layoutControl1.TabIndex = 1
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem3, Me.emptySpaceItem1, Me.emptySpaceItem2, Me.layoutControlGroup2, Me.layoutControlGroup3, Me.layoutControlGroup4, Me.layoutControlGroup5})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "Root"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(568, 463)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.textEditLeftExpression
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(524, 24)
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem1.TextVisible = False
			' 
			' checkEditInsertLeftAsField
			' 
			Me.checkEditInsertLeftAsField.Location = New System.Drawing.Point(24, 67)
			Me.checkEditInsertLeftAsField.Name = "checkEditInsertLeftAsField"
			Me.checkEditInsertLeftAsField.Properties.Caption = "Insert as a nested calculated field"
			Me.checkEditInsertLeftAsField.Size = New System.Drawing.Size(520, 19)
			Me.checkEditInsertLeftAsField.StyleController = Me.layoutControl1
			Me.checkEditInsertLeftAsField.TabIndex = 4
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.checkEditInsertLeftAsField
			Me.layoutControlItem2.Location = New System.Drawing.Point(0, 24)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(524, 23)
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem2.TextVisible = False
			' 
			' comboBoxEditOperation
			' 
			Me.comboBoxEditOperation.EditValue = "="
			Me.comboBoxEditOperation.Location = New System.Drawing.Point(12, 118)
			Me.comboBoxEditOperation.Name = "comboBoxEditOperation"
			Me.comboBoxEditOperation.Properties.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.comboBoxEditOperation.Properties.Items.AddRange(New Object() { "=", "<>", ">", "<", ">=", "<="})
			Me.comboBoxEditOperation.Size = New System.Drawing.Size(140, 20)
			Me.comboBoxEditOperation.StyleController = Me.layoutControl1
			Me.comboBoxEditOperation.TabIndex = 5
'			Me.comboBoxEditOperation.SelectedIndexChanged += New System.EventHandler(Me.comboBoxEdit1_SelectedIndexChanged);
			' 
			' layoutControlItem3
			' 
			Me.layoutControlItem3.AppearanceItemCaption.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlItem3.AppearanceItemCaption.Options.UseFont = True
			Me.layoutControlItem3.Control = Me.comboBoxEditOperation
			Me.layoutControlItem3.Location = New System.Drawing.Point(0, 90)
			Me.layoutControlItem3.Name = "layoutControlItem3"
			Me.layoutControlItem3.Size = New System.Drawing.Size(144, 40)
			Me.layoutControlItem3.Text = "OPERATION"
			Me.layoutControlItem3.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem3.TextSize = New System.Drawing.Size(64, 13)
			' 
			' textEditRIGHTExpression
			' 
			Me.textEditRIGHTExpression.Location = New System.Drawing.Point(24, 173)
			Me.textEditRIGHTExpression.Name = "textEditRIGHTExpression"
			Me.textEditRIGHTExpression.Size = New System.Drawing.Size(520, 20)
			Me.textEditRIGHTExpression.StyleController = Me.layoutControl1
			Me.textEditRIGHTExpression.TabIndex = 6
			' 
			' layoutControlItem4
			' 
			Me.layoutControlItem4.Control = Me.textEditRIGHTExpression
			Me.layoutControlItem4.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem4.Name = "layoutControlItem4"
			Me.layoutControlItem4.Size = New System.Drawing.Size(524, 24)
			Me.layoutControlItem4.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem4.TextVisible = False
			' 
			' checkEditInsertRightAsField
			' 
			Me.checkEditInsertRightAsField.Location = New System.Drawing.Point(24, 197)
			Me.checkEditInsertRightAsField.Name = "checkEditInsertRightAsField"
			Me.checkEditInsertRightAsField.Properties.Caption = "Insert as a nested calculated field"
			Me.checkEditInsertRightAsField.Size = New System.Drawing.Size(520, 19)
			Me.checkEditInsertRightAsField.StyleController = Me.layoutControl1
			Me.checkEditInsertRightAsField.TabIndex = 7
			' 
			' layoutControlItem5
			' 
			Me.layoutControlItem5.Control = Me.checkEditInsertRightAsField
			Me.layoutControlItem5.Location = New System.Drawing.Point(0, 24)
			Me.layoutControlItem5.Name = "layoutControlItem5"
			Me.layoutControlItem5.Size = New System.Drawing.Size(524, 23)
			Me.layoutControlItem5.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem5.TextVisible = False
			' 
			' textEditResultTRUE
			' 
			Me.textEditResultTRUE.Location = New System.Drawing.Point(24, 263)
			Me.textEditResultTRUE.Name = "textEditResultTRUE"
			Me.textEditResultTRUE.Size = New System.Drawing.Size(520, 20)
			Me.textEditResultTRUE.StyleController = Me.layoutControl1
			Me.textEditResultTRUE.TabIndex = 8
			' 
			' layoutControlItem6
			' 
			Me.layoutControlItem6.Control = Me.textEditResultTRUE
			Me.layoutControlItem6.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem6.Name = "layoutControlItem6"
			Me.layoutControlItem6.Size = New System.Drawing.Size(524, 24)
			Me.layoutControlItem6.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem6.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem6.TextVisible = False
			' 
			' textEditResultFALSE
			' 
			Me.textEditResultFALSE.Location = New System.Drawing.Point(24, 353)
			Me.textEditResultFALSE.Name = "textEditResultFALSE"
			Me.textEditResultFALSE.Size = New System.Drawing.Size(520, 20)
			Me.textEditResultFALSE.StyleController = Me.layoutControl1
			Me.textEditResultFALSE.TabIndex = 9
			' 
			' layoutControlItem7
			' 
			Me.layoutControlItem7.Control = Me.textEditResultFALSE
			Me.layoutControlItem7.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem7.Name = "layoutControlItem7"
			Me.layoutControlItem7.Size = New System.Drawing.Size(524, 24)
			Me.layoutControlItem7.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem7.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem7.TextVisible = False
			' 
			' emptySpaceItem1
			' 
			Me.emptySpaceItem1.AllowHotTrack = False
			Me.emptySpaceItem1.Location = New System.Drawing.Point(0, 400)
			Me.emptySpaceItem1.Name = "emptySpaceItem1"
			Me.emptySpaceItem1.Size = New System.Drawing.Size(548, 43)
			Me.emptySpaceItem1.TextSize = New System.Drawing.Size(0, 0)
			' 
			' emptySpaceItem2
			' 
			Me.emptySpaceItem2.AllowHotTrack = False
			Me.emptySpaceItem2.Location = New System.Drawing.Point(144, 90)
			Me.emptySpaceItem2.Name = "emptySpaceItem2"
			Me.emptySpaceItem2.Size = New System.Drawing.Size(404, 40)
			Me.emptySpaceItem2.TextSize = New System.Drawing.Size(0, 0)
			' 
			' layoutControlGroup2
			' 
			Me.layoutControlGroup2.AppearanceGroup.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlGroup2.AppearanceGroup.Options.UseFont = True
			Me.layoutControlGroup2.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem2})
			Me.layoutControlGroup2.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup2.Name = "layoutControlGroup2"
			Me.layoutControlGroup2.Size = New System.Drawing.Size(548, 90)
			Me.layoutControlGroup2.Text = "LEFT Expression"
			' 
			' layoutControlGroup3
			' 
			Me.layoutControlGroup3.AppearanceGroup.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlGroup3.AppearanceGroup.Options.UseFont = True
			Me.layoutControlGroup3.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem4, Me.layoutControlItem5})
			Me.layoutControlGroup3.Location = New System.Drawing.Point(0, 130)
			Me.layoutControlGroup3.Name = "layoutControlGroup3"
			Me.layoutControlGroup3.Size = New System.Drawing.Size(548, 90)
			Me.layoutControlGroup3.Text = "RIGHT Expression"
			' 
			' checkEditInsertResultTRUEAsField
			' 
			Me.checkEditInsertResultTRUEAsField.Location = New System.Drawing.Point(24, 287)
			Me.checkEditInsertResultTRUEAsField.Name = "checkEditInsertResultTRUEAsField"
			Me.checkEditInsertResultTRUEAsField.Properties.Caption = "Insert as a nested calculated field"
			Me.checkEditInsertResultTRUEAsField.Size = New System.Drawing.Size(520, 19)
			Me.checkEditInsertResultTRUEAsField.StyleController = Me.layoutControl1
			Me.checkEditInsertResultTRUEAsField.TabIndex = 10
			' 
			' layoutControlItem8
			' 
			Me.layoutControlItem8.Control = Me.checkEditInsertResultTRUEAsField
			Me.layoutControlItem8.Location = New System.Drawing.Point(0, 24)
			Me.layoutControlItem8.Name = "layoutControlItem8"
			Me.layoutControlItem8.Size = New System.Drawing.Size(524, 23)
			Me.layoutControlItem8.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem8.TextVisible = False
			' 
			' checkEditInsertResultFALSEAsField
			' 
			Me.checkEditInsertResultFALSEAsField.Location = New System.Drawing.Point(24, 377)
			Me.checkEditInsertResultFALSEAsField.Name = "checkEditInsertResultFALSEAsField"
			Me.checkEditInsertResultFALSEAsField.Properties.Caption = "Insert as a nested calculated field"
			Me.checkEditInsertResultFALSEAsField.Size = New System.Drawing.Size(520, 19)
			Me.checkEditInsertResultFALSEAsField.StyleController = Me.layoutControl1
			Me.checkEditInsertResultFALSEAsField.TabIndex = 11
			' 
			' layoutControlItem9
			' 
			Me.layoutControlItem9.Control = Me.checkEditInsertResultFALSEAsField
			Me.layoutControlItem9.Location = New System.Drawing.Point(0, 24)
			Me.layoutControlItem9.Name = "layoutControlItem9"
			Me.layoutControlItem9.Size = New System.Drawing.Size(524, 23)
			Me.layoutControlItem9.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem9.TextVisible = False
			' 
			' layoutControlGroup4
			' 
			Me.layoutControlGroup4.AppearanceGroup.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlGroup4.AppearanceGroup.Options.UseFont = True
			Me.layoutControlGroup4.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem6, Me.layoutControlItem8})
			Me.layoutControlGroup4.Location = New System.Drawing.Point(0, 220)
			Me.layoutControlGroup4.Name = "layoutControlGroup4"
			Me.layoutControlGroup4.Size = New System.Drawing.Size(548, 90)
			' 
			' layoutControlGroup5
			' 
			Me.layoutControlGroup5.AppearanceGroup.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.layoutControlGroup5.AppearanceGroup.Options.UseFont = True
			Me.layoutControlGroup5.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem7, Me.layoutControlItem9})
			Me.layoutControlGroup5.Location = New System.Drawing.Point(0, 310)
			Me.layoutControlGroup5.Name = "layoutControlGroup5"
			Me.layoutControlGroup5.Size = New System.Drawing.Size(548, 90)
			' 
			' ucIFFIELD
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.Controls.Add(Me.layoutControl1)
			Me.Name = "ucIFFIELD"
			Me.Size = New System.Drawing.Size(568, 463)
			CType(Me.textEditLeftExpression.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.checkEditInsertLeftAsField.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.comboBoxEditOperation.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditRIGHTExpression.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem4, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.checkEditInsertRightAsField.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem5, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditResultTRUE.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem6, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditResultFALSE.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem7, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.emptySpaceItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.emptySpaceItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup3, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.checkEditInsertResultTRUEAsField.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem8, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.checkEditInsertResultFALSEAsField.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem9, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup4, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup5, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private textEditLeftExpression As DevExpress.XtraEditors.TextEdit
		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private textEditResultFALSE As DevExpress.XtraEditors.TextEdit
		Private textEditResultTRUE As DevExpress.XtraEditors.TextEdit
		Private checkEditInsertRightAsField As DevExpress.XtraEditors.CheckEdit
		Private textEditRIGHTExpression As DevExpress.XtraEditors.TextEdit
		Private WithEvents comboBoxEditOperation As DevExpress.XtraEditors.ComboBoxEdit
		Private checkEditInsertLeftAsField As DevExpress.XtraEditors.CheckEdit
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem6 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem7 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem3 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem4 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem5 As DevExpress.XtraLayout.LayoutControlItem
		Private emptySpaceItem1 As DevExpress.XtraLayout.EmptySpaceItem
		Private emptySpaceItem2 As DevExpress.XtraLayout.EmptySpaceItem
		Private layoutControlGroup2 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlGroup3 As DevExpress.XtraLayout.LayoutControlGroup
		Private checkEditInsertResultFALSEAsField As DevExpress.XtraEditors.CheckEdit
		Private checkEditInsertResultTRUEAsField As DevExpress.XtraEditors.CheckEdit
		Private layoutControlGroup4 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem8 As DevExpress.XtraLayout.LayoutControlItem
		Private layoutControlGroup5 As DevExpress.XtraLayout.LayoutControlGroup
		Private layoutControlItem9 As DevExpress.XtraLayout.LayoutControlItem
	End Class
End Namespace
