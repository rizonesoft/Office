Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1.InsertFieldModules
	Partial Public Class ucCREATEDATE
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
			Me.listBoxControlFormats = New DevExpress.XtraEditors.ListBoxControl()
			Me.layoutControlGroup1 = New DevExpress.XtraLayout.LayoutControlGroup()
			Me.layoutControlItem1 = New DevExpress.XtraLayout.LayoutControlItem()
			Me.textEditCurrentFormat = New DevExpress.XtraEditors.TextEdit()
			Me.layoutControlItem2 = New DevExpress.XtraLayout.LayoutControlItem()
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.layoutControl1.SuspendLayout()
			CType(Me.listBoxControlFormats, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.textEditCurrentFormat.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' layoutControl1
			' 
			Me.layoutControl1.Controls.Add(Me.textEditCurrentFormat)
			Me.layoutControl1.Controls.Add(Me.listBoxControlFormats)
			Me.layoutControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.layoutControl1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControl1.Name = "layoutControl1"
			Me.layoutControl1.Root = Me.layoutControlGroup1
			Me.layoutControl1.Size = New System.Drawing.Size(406, 400)
			Me.layoutControl1.TabIndex = 0
			Me.layoutControl1.Text = "layoutControl1"
			' 
			' listBoxControlFormats
			' 
			Me.listBoxControlFormats.Location = New System.Drawing.Point(12, 52)
			Me.listBoxControlFormats.Name = "listBoxControlFormats"
			Me.listBoxControlFormats.Size = New System.Drawing.Size(382, 336)
			Me.listBoxControlFormats.StyleController = Me.layoutControl1
			Me.listBoxControlFormats.TabIndex = 4
			' 
			' layoutControlGroup1
			' 
			Me.layoutControlGroup1.EnableIndentsWithoutBorders = DevExpress.Utils.DefaultBoolean.True
			Me.layoutControlGroup1.GroupBordersVisible = False
			Me.layoutControlGroup1.Items.AddRange(New DevExpress.XtraLayout.BaseLayoutItem() { Me.layoutControlItem1, Me.layoutControlItem2})
			Me.layoutControlGroup1.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlGroup1.Name = "layoutControlGroup1"
			Me.layoutControlGroup1.Size = New System.Drawing.Size(406, 400)
			Me.layoutControlGroup1.TextVisible = False
			' 
			' layoutControlItem1
			' 
			Me.layoutControlItem1.Control = Me.listBoxControlFormats
			Me.layoutControlItem1.Location = New System.Drawing.Point(0, 40)
			Me.layoutControlItem1.Name = "layoutControlItem1"
			Me.layoutControlItem1.Size = New System.Drawing.Size(386, 340)
			Me.layoutControlItem1.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem1.TextSize = New System.Drawing.Size(0, 0)
			Me.layoutControlItem1.TextVisible = False
			' 
			' textEditCurrentFormat
			' 
			Me.textEditCurrentFormat.Location = New System.Drawing.Point(12, 28)
			Me.textEditCurrentFormat.Name = "textEditCurrentFormat"
			Me.textEditCurrentFormat.Size = New System.Drawing.Size(382, 20)
			Me.textEditCurrentFormat.StyleController = Me.layoutControl1
			Me.textEditCurrentFormat.TabIndex = 5
			' 
			' layoutControlItem2
			' 
			Me.layoutControlItem2.Control = Me.textEditCurrentFormat
			Me.layoutControlItem2.Location = New System.Drawing.Point(0, 0)
			Me.layoutControlItem2.Name = "layoutControlItem2"
			Me.layoutControlItem2.Size = New System.Drawing.Size(386, 40)
			Me.layoutControlItem2.Text = "Date formats:"
			Me.layoutControlItem2.TextLocation = DevExpress.Utils.Locations.Top
			Me.layoutControlItem2.TextSize = New System.Drawing.Size(67, 13)
			' 
			' ucCREATEDATE
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.Controls.Add(Me.layoutControl1)
			Me.Name = "ucCREATEDATE"
			Me.Size = New System.Drawing.Size(406, 400)
			CType(Me.layoutControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.layoutControl1.ResumeLayout(False)
			CType(Me.listBoxControlFormats, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlGroup1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem1, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.textEditCurrentFormat.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.layoutControlItem2, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private layoutControl1 As DevExpress.XtraLayout.LayoutControl
		Private layoutControlGroup1 As DevExpress.XtraLayout.LayoutControlGroup
		Private listBoxControlFormats As DevExpress.XtraEditors.ListBoxControl
		Private layoutControlItem1 As DevExpress.XtraLayout.LayoutControlItem
		Private textEditCurrentFormat As DevExpress.XtraEditors.TextEdit
		Private layoutControlItem2 As DevExpress.XtraLayout.LayoutControlItem
	End Class
End Namespace
