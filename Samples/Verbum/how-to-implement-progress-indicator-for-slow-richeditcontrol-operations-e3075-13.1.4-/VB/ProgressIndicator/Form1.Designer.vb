Imports Microsoft.VisualBasic
Imports System
Namespace ProgressIndicator
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
			Me.progressBarControl1 = New DevExpress.XtraEditors.ProgressBarControl()
			Me.xtraTabControl1 = New DevExpress.XtraTab.XtraTabControl()
			Me.xtraTabPage1 = New DevExpress.XtraTab.XtraTabPage()
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.xtraTabPage2 = New DevExpress.XtraTab.XtraTabPage()
			Me.richEditControl2 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.panelControl1 = New DevExpress.XtraEditors.PanelControl()
			Me.btnMailMerge = New DevExpress.XtraEditors.SimpleButton()
			CType(Me.progressBarControl1.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.xtraTabControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.xtraTabControl1.SuspendLayout()
			Me.xtraTabPage1.SuspendLayout()
			Me.xtraTabPage2.SuspendLayout()
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.panelControl1.SuspendLayout()
			Me.SuspendLayout()
			' 
			' progressBarControl1
			' 
			Me.progressBarControl1.Dock = System.Windows.Forms.DockStyle.Bottom
			Me.progressBarControl1.Location = New System.Drawing.Point(0, 489)
			Me.progressBarControl1.Name = "progressBarControl1"
			Me.progressBarControl1.Size = New System.Drawing.Size(871, 18)
			Me.progressBarControl1.TabIndex = 1
			' 
			' xtraTabControl1
			' 
			Me.xtraTabControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.xtraTabControl1.Location = New System.Drawing.Point(0, 37)
			Me.xtraTabControl1.Name = "xtraTabControl1"
			Me.xtraTabControl1.SelectedTabPage = Me.xtraTabPage1
			Me.xtraTabControl1.Size = New System.Drawing.Size(871, 452)
			Me.xtraTabControl1.TabIndex = 2
			Me.xtraTabControl1.TabPages.AddRange(New DevExpress.XtraTab.XtraTabPage() { Me.xtraTabPage1, Me.xtraTabPage2})
'			Me.xtraTabControl1.Selected += New DevExpress.XtraTab.TabPageEventHandler(Me.xtraTabControl1_Selected);
			' 
			' xtraTabPage1
			' 
			Me.xtraTabPage1.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom
			Me.xtraTabPage1.Controls.Add(Me.richEditControl1)
			Me.xtraTabPage1.Name = "xtraTabPage1"
			Me.xtraTabPage1.Size = New System.Drawing.Size(865, 426)
			Me.xtraTabPage1.Text = "Template"
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(0, 0)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(865, 426)
			Me.richEditControl1.TabIndex = 0
			Me.richEditControl1.Text = "richEditControl1"
'			Me.richEditControl1.MailMergeStarted += New DevExpress.XtraRichEdit.MailMergeStartedEventHandler(Me.richEditControl1_MailMergeStarted);
'			Me.richEditControl1.MailMergeFinished += New DevExpress.XtraRichEdit.MailMergeFinishedEventHandler(Me.richEditControl1_MailMergeFinished);
'			Me.richEditControl1.MailMergeRecordStarted += New DevExpress.XtraRichEdit.MailMergeRecordStartedEventHandler(Me.richEditControl1_MailMergeRecordStarted);
'			Me.richEditControl1.MailMergeRecordFinished += New DevExpress.XtraRichEdit.MailMergeRecordFinishedEventHandler(Me.richEditControl1_MailMergeRecordFinished);
			' 
			' xtraTabPage2
			' 
			Me.xtraTabPage2.Controls.Add(Me.richEditControl2)
			Me.xtraTabPage2.Name = "xtraTabPage2"
			Me.xtraTabPage2.Size = New System.Drawing.Size(865, 426)
			Me.xtraTabPage2.Text = "Result"
			' 
			' richEditControl2
			' 
			Me.richEditControl2.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl2.Location = New System.Drawing.Point(0, 0)
			Me.richEditControl2.Name = "richEditControl2"
			Me.richEditControl2.Size = New System.Drawing.Size(865, 426)
			Me.richEditControl2.TabIndex = 0
			Me.richEditControl2.Text = "richEditControl2"
			' 
			' panelControl1
			' 
			Me.panelControl1.Controls.Add(Me.btnMailMerge)
			Me.panelControl1.Dock = System.Windows.Forms.DockStyle.Top
			Me.panelControl1.Location = New System.Drawing.Point(0, 0)
			Me.panelControl1.Name = "panelControl1"
			Me.panelControl1.Size = New System.Drawing.Size(871, 37)
			Me.panelControl1.TabIndex = 3
			' 
			' btnMailMerge
			' 
			Me.btnMailMerge.Location = New System.Drawing.Point(12, 8)
			Me.btnMailMerge.Name = "btnMailMerge"
			Me.btnMailMerge.Size = New System.Drawing.Size(75, 23)
			Me.btnMailMerge.TabIndex = 0
			Me.btnMailMerge.Text = "Mail Merge"
'			Me.btnMailMerge.Click += New System.EventHandler(Me.btnMailMerge_Click);
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(871, 507)
			Me.Controls.Add(Me.xtraTabControl1)
			Me.Controls.Add(Me.progressBarControl1)
			Me.Controls.Add(Me.panelControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.progressBarControl1.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.xtraTabControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.xtraTabControl1.ResumeLayout(False)
			Me.xtraTabPage1.ResumeLayout(False)
			Me.xtraTabPage2.ResumeLayout(False)
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.panelControl1.ResumeLayout(False)
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private progressBarControl1 As DevExpress.XtraEditors.ProgressBarControl
		Private WithEvents xtraTabControl1 As DevExpress.XtraTab.XtraTabControl
		Private xtraTabPage1 As DevExpress.XtraTab.XtraTabPage
		Private xtraTabPage2 As DevExpress.XtraTab.XtraTabPage
		Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private richEditControl2 As DevExpress.XtraRichEdit.RichEditControl
		Private panelControl1 As DevExpress.XtraEditors.PanelControl
		Private WithEvents btnMailMerge As DevExpress.XtraEditors.SimpleButton

	End Class
End Namespace

