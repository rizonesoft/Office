Imports Microsoft.VisualBasic
Imports System
Namespace RichEditInsertDroppedFile
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
			Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.label1 = New System.Windows.Forms.Label()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Anchor = (CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) Or System.Windows.Forms.AnchorStyles.Left) Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles))
			Me.richEditControl1.Location = New System.Drawing.Point(9, 33)
			Me.richEditControl1.Margin = New System.Windows.Forms.Padding(2)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(642, 353)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = resources.GetString("richEditControl1.Text")
'			Me.richEditControl1.DragEnter += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragEnter);
'			Me.richEditControl1.DragDrop += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragDrop);
'			Me.richEditControl1.DragOver += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragOver);
			' 
			' label1
			' 
			Me.label1.AutoSize = True
			Me.label1.Location = New System.Drawing.Point(6, 9)
			Me.label1.Name = "label1"
			Me.label1.Size = New System.Drawing.Size(458, 13)
			Me.label1.TabIndex = 1
			Me.label1.Text = "Drag and drop file of one of the supported formats from Windows Explorer to the R" & "ichEditControl"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(660, 397)
			Me.Controls.Add(Me.label1)
			Me.Controls.Add(Me.richEditControl1)
			Me.Margin = New System.Windows.Forms.Padding(2)
			Me.Name = "Form1"
			Me.Text = "Form1"
			Me.ResumeLayout(False)
			Me.PerformLayout()

		End Sub

		#End Region

		Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private label1 As System.Windows.Forms.Label
	End Class
End Namespace

