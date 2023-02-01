' Developer Express Code Central Example:
' How to create an editor similar to Outlook Attachment Editor
' 
' This example demonstrates how the RichEditControl component can be used to
' emulate the Outlook Attachment Editor behavior.
' The main idea of the approach
' demonstrated in this sample is to use the DOCVARIABLE field
' (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
' display corresponding RTF content for each inserted file.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E4911


Imports Microsoft.VisualBasic
Imports System
Namespace WindowsFormsApplication1
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
			Me.attachmentsEditor1 = New WindowsFormsApplication1.AttachmentsEditor()
			Me.SuspendLayout()
			' 
			' attachmentsEditor1
			' 
			Me.attachmentsEditor1.Dock = System.Windows.Forms.DockStyle.Top
			Me.attachmentsEditor1.Location = New System.Drawing.Point(0, 0)
			Me.attachmentsEditor1.Name = "attachmentsEditor1"
			Me.attachmentsEditor1.Size = New System.Drawing.Size(828, 51)
			Me.attachmentsEditor1.TabIndex = 0
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(828, 366)
			Me.Controls.Add(Me.attachmentsEditor1)
			Me.Name = "Form1"
			Me.Text = "Form1"
'			Me.Load += New System.EventHandler(Me.Form1_Load);
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private attachmentsEditor1 As AttachmentsEditor









	End Class
End Namespace

