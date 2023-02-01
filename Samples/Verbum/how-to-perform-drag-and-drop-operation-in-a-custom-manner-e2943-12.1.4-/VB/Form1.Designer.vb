Imports Microsoft.VisualBasic
Imports System
Namespace RichListDragDrop
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
			Me.listBox1 = New System.Windows.Forms.ListBox()
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Anchor = (CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) Or System.Windows.Forms.AnchorStyles.Left) Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles))
			Me.richEditControl1.Location = New System.Drawing.Point(142, 10)
			Me.richEditControl1.Margin = New System.Windows.Forms.Padding(2)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(364, 267)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
'			Me.richEditControl1.DragOver += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragOver);
'			Me.richEditControl1.DragDrop += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragDrop);
'			Me.richEditControl1.DragEnter += New System.Windows.Forms.DragEventHandler(Me.richEditControl1_DragEnter);
			' 
			' listBox1
			' 
			Me.listBox1.Anchor = (CType(((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) Or System.Windows.Forms.AnchorStyles.Left), System.Windows.Forms.AnchorStyles))
			Me.listBox1.FormattingEnabled = True
			Me.listBox1.Items.AddRange(New Object() { "Item1", "Item2", "Item3", "Item4", "Item5", "Item6", "Item7"})
			Me.listBox1.Location = New System.Drawing.Point(12, 12)
			Me.listBox1.Name = "listBox1"
			Me.listBox1.Size = New System.Drawing.Size(120, 264)
			Me.listBox1.TabIndex = 1
'			Me.listBox1.MouseDown += New System.Windows.Forms.MouseEventHandler(Me.listBox1_MouseDown);
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(515, 288)
			Me.Controls.Add(Me.listBox1)
			Me.Controls.Add(Me.richEditControl1)
			Me.Margin = New System.Windows.Forms.Padding(2)
			Me.Name = "Form1"
			Me.Text = "Form1"
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private WithEvents listBox1 As System.Windows.Forms.ListBox
	End Class
End Namespace
