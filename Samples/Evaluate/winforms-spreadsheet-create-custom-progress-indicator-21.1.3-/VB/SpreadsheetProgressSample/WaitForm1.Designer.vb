Namespace SpreadsheetProgressSample
	Partial Public Class WaitForm1
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
			Me.progressPanel1 = New DevExpress.XtraWaitForm.ProgressPanel()
			Me.tableLayoutPanel1 = New System.Windows.Forms.TableLayoutPanel()
			Me.hyperlinkLabelControl1 = New DevExpress.XtraEditors.HyperlinkLabelControl()
			Me.tableLayoutPanel1.SuspendLayout()
			Me.SuspendLayout()
			' 
			' progressPanel1
			' 
			Me.progressPanel1.Appearance.BackColor = System.Drawing.Color.Transparent
			Me.progressPanel1.Appearance.Options.UseBackColor = True
			Me.progressPanel1.AppearanceCaption.Font = New System.Drawing.Font("Microsoft Sans Serif", 12F)
			Me.progressPanel1.AppearanceCaption.Options.UseFont = True
			Me.progressPanel1.AppearanceDescription.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25F)
			Me.progressPanel1.AppearanceDescription.Options.UseFont = True
			Me.progressPanel1.ImageHorzOffset = 10
			Me.progressPanel1.Location = New System.Drawing.Point(0, 17)
			Me.progressPanel1.Margin = New System.Windows.Forms.Padding(0, 3, 0, 3)
			Me.progressPanel1.Name = "progressPanel1"
			Me.progressPanel1.Size = New System.Drawing.Size(246, 41)
			Me.progressPanel1.TabIndex = 0
			Me.progressPanel1.Text = "progressPanel1"
			' 
			' tableLayoutPanel1
			' 
			Me.tableLayoutPanel1.AutoSize = True
			Me.tableLayoutPanel1.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
			Me.tableLayoutPanel1.BackColor = System.Drawing.Color.Transparent
			Me.tableLayoutPanel1.ColumnCount = 1
			Me.tableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 246F))
			Me.tableLayoutPanel1.Controls.Add(Me.progressPanel1, 0, 0)
			Me.tableLayoutPanel1.Controls.Add(Me.hyperlinkLabelControl1, 0, 1)
			Me.tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.tableLayoutPanel1.Location = New System.Drawing.Point(0, 0)
			Me.tableLayoutPanel1.Name = "tableLayoutPanel1"
			Me.tableLayoutPanel1.Padding = New System.Windows.Forms.Padding(0, 14, 0, 14)
			Me.tableLayoutPanel1.RowCount = 2
			Me.tableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 85F))
			Me.tableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 15F))
			Me.tableLayoutPanel1.Size = New System.Drawing.Size(246, 84)
			Me.tableLayoutPanel1.TabIndex = 1
			' 
			' hyperlinkLabelControl1
			' 
			Me.hyperlinkLabelControl1.Dock = System.Windows.Forms.DockStyle.Right
			Me.hyperlinkLabelControl1.Location = New System.Drawing.Point(202, 64)
			Me.hyperlinkLabelControl1.Margin = New System.Windows.Forms.Padding(3, 3, 12, 3)
			Me.hyperlinkLabelControl1.Name = "hyperlinkLabelControl1"
			Me.hyperlinkLabelControl1.Size = New System.Drawing.Size(32, 13)
			Me.hyperlinkLabelControl1.TabIndex = 1
			Me.hyperlinkLabelControl1.Text = "Cancel"
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.hyperlinkLabelControl1.Click += new System.EventHandler(this.Cancel_Click);
			' 
			' WaitForm1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
			Me.ClientSize = New System.Drawing.Size(246, 84)
			Me.Controls.Add(Me.tableLayoutPanel1)
			Me.DoubleBuffered = True
			Me.MinimumSize = New System.Drawing.Size(246, 0)
			Me.Name = "WaitForm1"
			Me.StartPosition = System.Windows.Forms.FormStartPosition.Manual
			Me.Text = "Form1"
			Me.tableLayoutPanel1.ResumeLayout(False)
			Me.tableLayoutPanel1.PerformLayout()
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region

		Private progressPanel1 As DevExpress.XtraWaitForm.ProgressPanel
		Private tableLayoutPanel1 As System.Windows.Forms.TableLayoutPanel
		Private WithEvents hyperlinkLabelControl1 As DevExpress.XtraEditors.HyperlinkLabelControl
	End Class
End Namespace
