Imports Microsoft.VisualBasic
Imports System
Namespace RichEditSendMail
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
			Me.richEdit = New DevExpress.XtraRichEdit.RichEditControl()
			Me.btnSend = New System.Windows.Forms.Button()
			Me.lblSubject = New System.Windows.Forms.Label()
			Me.edtSubject = New System.Windows.Forms.TextBox()
			Me.lblTo = New System.Windows.Forms.Label()
			Me.edtTo = New System.Windows.Forms.TextBox()
			Me.lblSmtp = New System.Windows.Forms.Label()
			Me.edtSmtp = New System.Windows.Forms.TextBox()
			Me.panelControl1 = New DevExpress.XtraEditors.PanelControl()
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.panelControl1.SuspendLayout()
			Me.SuspendLayout()
			' 
			' richEdit
			' 
			Me.richEdit.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEdit.Location = New System.Drawing.Point(0, 0)
			Me.richEdit.Name = "richEdit"
			Me.richEdit.Size = New System.Drawing.Size(805, 391)
			Me.richEdit.TabIndex = 4
			' 
			' btnSend
			' 
			Me.btnSend.Dock = System.Windows.Forms.DockStyle.Right
			Me.btnSend.Location = New System.Drawing.Point(728, 2)
			Me.btnSend.Name = "btnSend"
			Me.btnSend.Size = New System.Drawing.Size(75, 58)
			Me.btnSend.TabIndex = 3
			Me.btnSend.Text = "Send Mail"
			Me.btnSend.UseVisualStyleBackColor = True
'			Me.btnSend.Click += New System.EventHandler(Me.btnSend_Click);
			' 
			' lblSubject
			' 
			Me.lblSubject.AutoSize = True
			Me.lblSubject.Location = New System.Drawing.Point(7, 13)
			Me.lblSubject.Name = "lblSubject"
			Me.lblSubject.Size = New System.Drawing.Size(46, 13)
			Me.lblSubject.TabIndex = 2
			Me.lblSubject.Text = "Subject:"
			' 
			' edtSubject
			' 
			Me.edtSubject.Location = New System.Drawing.Point(59, 10)
			Me.edtSubject.Name = "edtSubject"
			Me.edtSubject.Size = New System.Drawing.Size(199, 20)
			Me.edtSubject.TabIndex = 0
			Me.edtSubject.Text = "Hey, look at this!"
			' 
			' lblTo
			' 
			Me.lblTo.AutoSize = True
			Me.lblTo.Location = New System.Drawing.Point(7, 39)
			Me.lblTo.Name = "lblTo"
			Me.lblTo.Size = New System.Drawing.Size(23, 13)
			Me.lblTo.TabIndex = 2
			Me.lblTo.Text = "To:"
			' 
			' edtTo
			' 
			Me.edtTo.Location = New System.Drawing.Point(59, 36)
			Me.edtTo.Name = "edtTo"
			Me.edtTo.Size = New System.Drawing.Size(199, 20)
			Me.edtTo.TabIndex = 1
			' 
			' lblSmtp
			' 
			Me.lblSmtp.AutoSize = True
			Me.lblSmtp.Location = New System.Drawing.Point(272, 13)
			Me.lblSmtp.Name = "lblSmtp"
			Me.lblSmtp.Size = New System.Drawing.Size(60, 13)
			Me.lblSmtp.TabIndex = 2
			Me.lblSmtp.Text = "MailServer:"
			' 
			' edtSmtp
			' 
			Me.edtSmtp.Location = New System.Drawing.Point(338, 10)
			Me.edtSmtp.Name = "edtSmtp"
			Me.edtSmtp.Size = New System.Drawing.Size(199, 20)
			Me.edtSmtp.TabIndex = 2
			' 
			' panelControl1
			' 
			Me.panelControl1.Controls.Add(Me.btnSend)
			Me.panelControl1.Controls.Add(Me.edtTo)
			Me.panelControl1.Controls.Add(Me.lblSubject)
			Me.panelControl1.Controls.Add(Me.lblTo)
			Me.panelControl1.Controls.Add(Me.edtSubject)
			Me.panelControl1.Controls.Add(Me.edtSmtp)
			Me.panelControl1.Controls.Add(Me.lblSmtp)
			Me.panelControl1.Dock = System.Windows.Forms.DockStyle.Bottom
			Me.panelControl1.Location = New System.Drawing.Point(0, 391)
			Me.panelControl1.Name = "panelControl1"
			Me.panelControl1.Size = New System.Drawing.Size(805, 62)
			Me.panelControl1.TabIndex = 4
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(805, 453)
			Me.Controls.Add(Me.richEdit)
			Me.Controls.Add(Me.panelControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.panelControl1.ResumeLayout(False)
			Me.panelControl1.PerformLayout()
			Me.ResumeLayout(False)

		End Sub

		Private richEdit As DevExpress.XtraRichEdit.RichEditControl
		#End Region
		Private WithEvents btnSend As System.Windows.Forms.Button
		Private lblSubject As System.Windows.Forms.Label
		Private edtSubject As System.Windows.Forms.TextBox
		Private lblTo As System.Windows.Forms.Label
		Private edtTo As System.Windows.Forms.TextBox
		Private lblSmtp As System.Windows.Forms.Label
		Private edtSmtp As System.Windows.Forms.TextBox
		Private panelControl1 As DevExpress.XtraEditors.PanelControl
	End Class
End Namespace

