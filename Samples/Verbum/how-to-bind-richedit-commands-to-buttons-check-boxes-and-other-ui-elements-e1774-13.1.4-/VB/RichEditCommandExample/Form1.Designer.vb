Imports Microsoft.VisualBasic
Imports System
Namespace RichEditCommandExample
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
			Me.btnToggleReadonly = New DevExpress.XtraEditors.SimpleButton()
			Me.btnRedo = New DevExpress.XtraEditors.SimpleButton()
			Me.chkToggleFontBold = New DevExpress.XtraEditors.CheckEdit()
			Me.btnUndo = New RichEditCommandExample.CommandButton()
			CType(Me.chkToggleFontBold.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Anchor = (CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) Or System.Windows.Forms.AnchorStyles.Left) Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles))
			Me.richEditControl1.Location = New System.Drawing.Point(12, 66)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(542, 323)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
			' 
			' btnToggleReadonly
			' 
			Me.btnToggleReadonly.Location = New System.Drawing.Point(430, 12)
			Me.btnToggleReadonly.Name = "btnToggleReadonly"
			Me.btnToggleReadonly.Size = New System.Drawing.Size(124, 23)
			Me.btnToggleReadonly.TabIndex = 3
			Me.btnToggleReadonly.Text = "Toggle ReadOnly"
'			Me.btnToggleReadonly.Click += New System.EventHandler(Me.btnToggleReadOnly_Click);
			' 
			' btnRedo
			' 
			Me.btnRedo.Location = New System.Drawing.Point(76, 12)
			Me.btnRedo.Name = "btnRedo"
			Me.btnRedo.Size = New System.Drawing.Size(58, 23)
			Me.btnRedo.TabIndex = 1
			Me.btnRedo.Text = "Redo"
			' 
			' chkToggleFontBold
			' 
			Me.chkToggleFontBold.Location = New System.Drawing.Point(12, 41)
			Me.chkToggleFontBold.Name = "chkToggleFontBold"
			Me.chkToggleFontBold.Properties.Caption = "Toggle Font Bold"
			Me.chkToggleFontBold.Size = New System.Drawing.Size(122, 19)
			Me.chkToggleFontBold.TabIndex = 4
			' 
			' btnUndo
			' 
			Me.btnUndo.Location = New System.Drawing.Point(12, 12)
			Me.btnUndo.Name = "btnUndo"
			Me.btnUndo.Size = New System.Drawing.Size(58, 23)
			Me.btnUndo.TabIndex = 1
			Me.btnUndo.Text = "Undo"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(566, 401)
			Me.Controls.Add(Me.chkToggleFontBold)
			Me.Controls.Add(Me.btnToggleReadonly)
			Me.Controls.Add(Me.btnRedo)
			Me.Controls.Add(Me.btnUndo)
			Me.Controls.Add(Me.richEditControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.chkToggleFontBold.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private btnUndo As CommandButton
		Private WithEvents btnToggleReadonly As DevExpress.XtraEditors.SimpleButton
		Private btnRedo As DevExpress.XtraEditors.SimpleButton
		Private chkToggleFontBold As DevExpress.XtraEditors.CheckEdit
	End Class
End Namespace

