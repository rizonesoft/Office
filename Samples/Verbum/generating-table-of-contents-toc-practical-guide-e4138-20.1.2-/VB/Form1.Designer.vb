Namespace RichEditTOCGeneration
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
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.label1 = New System.Windows.Forms.Label()
			Me.btnStyles = New System.Windows.Forms.Button()
			Me.btnOutlineLevels = New System.Windows.Forms.Button()
			Me.btnTCFields = New System.Windows.Forms.Button()
			Me.btnLoadTemplate = New System.Windows.Forms.Button()
			Me.btnShowAllFieldCodes = New System.Windows.Forms.Button()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Anchor = (CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) Or System.Windows.Forms.AnchorStyles.Left) Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles))
			Me.richEditControl1.Location = New System.Drawing.Point(12, 42)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(1263, 620)
			Me.richEditControl1.TabIndex = 0
			' 
			' label1
			' 
			Me.label1.AutoSize = True
			Me.label1.Font = New System.Drawing.Font("Microsoft Sans Serif", 7.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, (CByte(204)))
			Me.label1.Location = New System.Drawing.Point(398, 15)
			Me.label1.Name = "label1"
			Me.label1.Size = New System.Drawing.Size(208, 17)
			Me.label1.TabIndex = 1
			Me.label1.Text = "Build Table Of Contents by:"
			' 
			' btnStyles
			' 
			Me.btnStyles.Location = New System.Drawing.Point(612, 11)
			Me.btnStyles.Name = "btnStyles"
			Me.btnStyles.Size = New System.Drawing.Size(127, 25)
			Me.btnStyles.TabIndex = 2
			Me.btnStyles.Text = "Styles"
			Me.btnStyles.UseVisualStyleBackColor = True
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.btnStyles.Click += new System.EventHandler(this.btnStyles_Click);
			' 
			' btnOutlineLevels
			' 
			Me.btnOutlineLevels.Location = New System.Drawing.Point(745, 11)
			Me.btnOutlineLevels.Name = "btnOutlineLevels"
			Me.btnOutlineLevels.Size = New System.Drawing.Size(127, 25)
			Me.btnOutlineLevels.TabIndex = 3
			Me.btnOutlineLevels.Text = "Outline Levels"
			Me.btnOutlineLevels.UseVisualStyleBackColor = True
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.btnOutlineLevels.Click += new System.EventHandler(this.btnOutlineLevels_Click);
			' 
			' btnTCFields
			' 
			Me.btnTCFields.Location = New System.Drawing.Point(878, 11)
			Me.btnTCFields.Name = "btnTCFields"
			Me.btnTCFields.Size = New System.Drawing.Size(127, 25)
			Me.btnTCFields.TabIndex = 4
			Me.btnTCFields.Text = "TC Fields"
			Me.btnTCFields.UseVisualStyleBackColor = True
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.btnTCFields.Click += new System.EventHandler(this.btnTCFields_Click);
			' 
			' btnLoadTemplate
			' 
			Me.btnLoadTemplate.Location = New System.Drawing.Point(12, 11)
			Me.btnLoadTemplate.Name = "btnLoadTemplate"
			Me.btnLoadTemplate.Size = New System.Drawing.Size(127, 25)
			Me.btnLoadTemplate.TabIndex = 5
			Me.btnLoadTemplate.Text = "Load Template"
			Me.btnLoadTemplate.UseVisualStyleBackColor = True
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.btnLoadTemplate.Click += new System.EventHandler(this.btnLoadTemplate_Click);
			' 
			' btnShowAllFieldCodes
			' 
			Me.btnShowAllFieldCodes.Location = New System.Drawing.Point(145, 11)
			Me.btnShowAllFieldCodes.Name = "btnShowAllFieldCodes"
			Me.btnShowAllFieldCodes.Size = New System.Drawing.Size(127, 25)
			Me.btnShowAllFieldCodes.TabIndex = 6
			Me.btnShowAllFieldCodes.Text = "Show All Field Codes"
			Me.btnShowAllFieldCodes.UseVisualStyleBackColor = True
'INSTANT VB NOTE: The following InitializeComponent event wireup was converted to a 'Handles' clause:
'ORIGINAL LINE: this.btnShowAllFieldCodes.Click += new System.EventHandler(this.btnShowAllFieldCodes_Click);
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(8F, 16F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(1287, 674)
			Me.Controls.Add(Me.btnShowAllFieldCodes)
			Me.Controls.Add(Me.btnLoadTemplate)
			Me.Controls.Add(Me.btnTCFields)
			Me.Controls.Add(Me.btnOutlineLevels)
			Me.Controls.Add(Me.btnStyles)
			Me.Controls.Add(Me.label1)
			Me.Controls.Add(Me.richEditControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region

		Private richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private label1 As System.Windows.Forms.Label
		Private WithEvents btnStyles As System.Windows.Forms.Button
		Private WithEvents btnOutlineLevels As System.Windows.Forms.Button
		Private WithEvents btnTCFields As System.Windows.Forms.Button
		Private WithEvents btnLoadTemplate As System.Windows.Forms.Button
		Private WithEvents btnShowAllFieldCodes As System.Windows.Forms.Button
	End Class
End Namespace

