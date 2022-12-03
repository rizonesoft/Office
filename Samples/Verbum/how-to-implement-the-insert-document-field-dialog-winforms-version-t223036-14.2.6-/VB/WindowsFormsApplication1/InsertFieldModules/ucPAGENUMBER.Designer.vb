Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class ucPAGENUMBER
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
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.labelControl1 = New DevExpress.XtraEditors.LabelControl()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.listBoxControlAttributes = New DevExpress.XtraEditors.ListBoxControl()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.listBoxControlAttributes, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.labelControl1)
			Me.layoutControl1.Controls.Add(Me.listBoxControlAttributes)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(444, 380)
			Me.layoutControl1.TabIndex = 0
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem2})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "layoutControlGroup1"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(444, 380)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' labelControl1
			' 
			Me.labelControl1.AllowHtmlString = True
			Me.labelControl1.Appearance.Font = New System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Bold)
			Me.labelControl1.Appearance.ForeColor = System.Drawing.Color.Maroon
			Me.labelControl1.AutoSizeMode = DevExpress.XtraEditors.LabelAutoSizeMode.Vertical
			Me.labelControl1.Location = New System.Drawing.Point(12, 355)
			Me.labelControl1.Name = "labelControl1"
			Me.labelControl1.Size = New System.Drawing.Size(420, 13)
			Me.labelControl1.StyleController = Me.layoutControl1
			Me.labelControl1.TabIndex = 5
			Me.labelControl1.Text = "labelControl1"
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.labelControl1
			Me.layoutControlItem2.Location = New System.Drawing.Point(0, 343)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(424, 17)
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem2.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.listBoxControlAttributes
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(424, 343)
			Me.layoutControlItem1.Text = "Format:"
			Me.layoutControlItem1.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(38, 13)
			' 
			' listBoxControlAttributes
			' 
			Me.listBoxControlAttributes.Location = New System.Drawing.Point(12, 28)
			Me.listBoxControlAttributes.Name = "listBoxControlAttributes"
			Me.listBoxControlAttributes.Size = New System.Drawing.Size(420, 323)
			Me.listBoxControlAttributes.StyleController = Me.layoutControl1
			Me.listBoxControlAttributes.TabIndex = 4
			' 
			' ucPAGENUMBER
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.Controls.Add(Me.layoutControl1)
			Me.Name = "ucPAGENUMBER"
			Me.Size = New System.Drawing.Size(444, 380)
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.listBoxControlAttributes, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private labelControl1 As DevExpress.XtraEditors.LabelControl
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
		Private listBoxControlAttributes As DevExpress.XtraEditors.ListBoxControl
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
	End Class
End Namespace
