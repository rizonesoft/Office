Imports Microsoft.VisualBasic
Imports System
Namespace RichEditWordTooltip
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
			Me.components = New System.ComponentModel.Container()
			Dim resources As New System.ComponentModel.ComponentResourceManager(GetType(Form1))
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.toolTipController1 = New DevExpress.Utils.ToolTipController(Me.components)
			Me.SuspendLayout()
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(0, 0)
			Me.richEditControl1.Margin = New System.Windows.Forms.Padding(2)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(894, 286)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = resources.GetString("richEditControl1.Text")
'			Me.richEditControl1.MouseMove += New System.Windows.Forms.MouseEventHandler(Me.richEditControl1_MouseMove);
			' 
			' toolTipController1
			' 
			Me.toolTipController1.Rounded = True
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(894, 286)
			Me.Controls.Add(Me.richEditControl1)
			Me.Margin = New System.Windows.Forms.Padding(2)
			Me.Name = "Form1"
			Me.Text = "Form1"
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private toolTipController1 As DevExpress.Utils.ToolTipController
	End Class
End Namespace

