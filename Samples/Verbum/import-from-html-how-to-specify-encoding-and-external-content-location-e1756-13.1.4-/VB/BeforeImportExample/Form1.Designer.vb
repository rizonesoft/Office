Imports Microsoft.VisualBasic
Imports System
Namespace BeforeImport
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
			Me.panelControl1 = New DevExpress.XtraEditors.PanelControl()
			Me.rgImgPath = New DevExpress.XtraEditors.RadioGroup()
			Me.labelControl1 = New DevExpress.XtraEditors.LabelControl()
			Me.richEditControl1 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.xtraTabControl1 = New DevExpress.XtraTab.XtraTabControl()
			Me.tbLoadHTML = New DevExpress.XtraTab.XtraTabPage()
			Me.tbLoadText = New DevExpress.XtraTab.XtraTabPage()
			Me.richEditControl2 = New DevExpress.XtraRichEdit.RichEditControl()
			Me.panelControl2 = New DevExpress.XtraEditors.PanelControl()
			Me.btnLoadRTF = New DevExpress.XtraEditors.SimpleButton()
			Me.cmbEncodings = New DevExpress.XtraEditors.ComboBoxEdit()
			Me.labelControl2 = New DevExpress.XtraEditors.LabelControl()
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.panelControl1.SuspendLayout()
			CType(Me.rgImgPath.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			CType(Me.xtraTabControl1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.xtraTabControl1.SuspendLayout()
			Me.tbLoadHTML.SuspendLayout()
			Me.tbLoadText.SuspendLayout()
			CType(Me.panelControl2, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.panelControl2.SuspendLayout()
			CType(Me.cmbEncodings.Properties, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' panelControl1
			' 
			Me.panelControl1.Controls.Add(Me.rgImgPath)
			Me.panelControl1.Controls.Add(Me.labelControl1)
			Me.panelControl1.Dock = System.Windows.Forms.DockStyle.Top
			Me.panelControl1.Location = New System.Drawing.Point(0, 0)
			Me.panelControl1.Name = "panelControl1"
			Me.panelControl1.Size = New System.Drawing.Size(717, 40)
			Me.panelControl1.TabIndex = 0
			' 
			' rgImgPath
			' 
			Me.rgImgPath.EditValue = "//Img01/"
			Me.rgImgPath.Location = New System.Drawing.Point(5, 5)
			Me.rgImgPath.Name = "rgImgPath"
			Me.rgImgPath.Properties.Items.AddRange(New DevExpress.XtraEditors.Controls.RadioGroupItem() { New DevExpress.XtraEditors.Controls.RadioGroupItem("//Img01/", "Img01"), New DevExpress.XtraEditors.Controls.RadioGroupItem("//Img02/", "Img02")})
			Me.rgImgPath.Size = New System.Drawing.Size(132, 30)
			Me.rgImgPath.TabIndex = 2
'			Me.rgImgPath.SelectedIndexChanged += New System.EventHandler(Me.rgImgPath_SelectedIndexChanged);
			' 
			' labelControl1
			' 
			Me.labelControl1.Location = New System.Drawing.Point(143, 21)
			Me.labelControl1.Name = "labelControl1"
			Me.labelControl1.Size = New System.Drawing.Size(63, 13)
			Me.labelControl1.TabIndex = 1
			Me.labelControl1.Text = "labelControl1"
			' 
			' richEditControl1
			' 
			Me.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl1.Location = New System.Drawing.Point(0, 40)
			Me.richEditControl1.Name = "richEditControl1"
			Me.richEditControl1.Size = New System.Drawing.Size(717, 365)
			Me.richEditControl1.TabIndex = 1
			Me.richEditControl1.Text = "richEditControl1"
'			Me.richEditControl1.BeforeImport += New DevExpress.XtraRichEdit.BeforeImportEventHandler(Me.richEditControl1_BeforeImport);
			' 
			' xtraTabControl1
			' 
			Me.xtraTabControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.xtraTabControl1.Location = New System.Drawing.Point(0, 0)
			Me.xtraTabControl1.Name = "xtraTabControl1"
			Me.xtraTabControl1.SelectedTabPage = Me.tbLoadHTML
			Me.xtraTabControl1.Size = New System.Drawing.Size(724, 434)
			Me.xtraTabControl1.TabIndex = 2
			Me.xtraTabControl1.TabPages.AddRange(New DevExpress.XtraTab.XtraTabPage() { Me.tbLoadHTML, Me.tbLoadText})
			' 
			' tbLoadHTML
			' 
			Me.tbLoadHTML.Controls.Add(Me.richEditControl1)
			Me.tbLoadHTML.Controls.Add(Me.panelControl1)
			Me.tbLoadHTML.Name = "tbLoadHTML"
			Me.tbLoadHTML.Size = New System.Drawing.Size(717, 405)
			Me.tbLoadHTML.Text = "Load HTML"
			' 
			' tbLoadText
			' 
			Me.tbLoadText.Controls.Add(Me.richEditControl2)
			Me.tbLoadText.Controls.Add(Me.panelControl2)
			Me.tbLoadText.Name = "tbLoadText"
			Me.tbLoadText.Size = New System.Drawing.Size(717, 405)
			Me.tbLoadText.Text = "Load Text"
			' 
			' richEditControl2
			' 
			Me.richEditControl2.Dock = System.Windows.Forms.DockStyle.Fill
			Me.richEditControl2.Location = New System.Drawing.Point(0, 40)
			Me.richEditControl2.Name = "richEditControl2"
			Me.richEditControl2.Size = New System.Drawing.Size(717, 365)
			Me.richEditControl2.TabIndex = 0
			Me.richEditControl2.Text = "richEditControl2"
'			Me.richEditControl2.BeforeImport += New DevExpress.XtraRichEdit.BeforeImportEventHandler(Me.richEditControl2_BeforeImport);
			' 
			' panelControl2
			' 
			Me.panelControl2.Controls.Add(Me.btnLoadRTF)
			Me.panelControl2.Controls.Add(Me.cmbEncodings)
			Me.panelControl2.Controls.Add(Me.labelControl2)
			Me.panelControl2.Dock = System.Windows.Forms.DockStyle.Top
			Me.panelControl2.Location = New System.Drawing.Point(0, 0)
			Me.panelControl2.Name = "panelControl2"
			Me.panelControl2.Size = New System.Drawing.Size(717, 40)
			Me.panelControl2.TabIndex = 1
			' 
			' btnLoadRTF
			' 
			Me.btnLoadRTF.Location = New System.Drawing.Point(143, 10)
			Me.btnLoadRTF.Name = "btnLoadRTF"
			Me.btnLoadRTF.Size = New System.Drawing.Size(75, 20)
			Me.btnLoadRTF.TabIndex = 3
			Me.btnLoadRTF.Text = "Load"
'			Me.btnLoadRTF.Click += New System.EventHandler(Me.btnLoadRTF_Click);
			' 
			' cmbEncodings
			' 
			Me.cmbEncodings.Location = New System.Drawing.Point(5, 10)
			Me.cmbEncodings.Name = "cmbEncodings"
			Me.cmbEncodings.Properties.Buttons.AddRange(New DevExpress.XtraEditors.Controls.EditorButton() { New DevExpress.XtraEditors.Controls.EditorButton(DevExpress.XtraEditors.Controls.ButtonPredefines.Combo)})
			Me.cmbEncodings.Properties.TextEditStyle = DevExpress.XtraEditors.Controls.TextEditStyles.DisableTextEditor
			Me.cmbEncodings.Size = New System.Drawing.Size(132, 20)
			Me.cmbEncodings.TabIndex = 2
			' 
			' labelControl2
			' 
			Me.labelControl2.Location = New System.Drawing.Point(224, 14)
			Me.labelControl2.Name = "labelControl2"
			Me.labelControl2.Size = New System.Drawing.Size(63, 13)
			Me.labelControl2.TabIndex = 1
			Me.labelControl2.Text = "labelControl2"
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(724, 434)
			Me.Controls.Add(Me.xtraTabControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.panelControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.panelControl1.ResumeLayout(False)
			Me.panelControl1.PerformLayout()
			CType(Me.rgImgPath.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			CType(Me.xtraTabControl1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.xtraTabControl1.ResumeLayout(False)
			Me.tbLoadHTML.ResumeLayout(False)
			Me.tbLoadText.ResumeLayout(False)
			CType(Me.panelControl2, System.ComponentModel.ISupportInitialize).EndInit()
			Me.panelControl2.ResumeLayout(False)
			Me.panelControl2.PerformLayout()
			CType(Me.cmbEncodings.Properties, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private panelControl1 As DevExpress.XtraEditors.PanelControl
		Private WithEvents richEditControl1 As DevExpress.XtraRichEdit.RichEditControl
		Private labelControl1 As DevExpress.XtraEditors.LabelControl
		Private WithEvents rgImgPath As DevExpress.XtraEditors.RadioGroup
		Private xtraTabControl1 As DevExpress.XtraTab.XtraTabControl
		Private tbLoadHTML As DevExpress.XtraTab.XtraTabPage
		Private tbLoadText As DevExpress.XtraTab.XtraTabPage
		Private panelControl2 As DevExpress.XtraEditors.PanelControl
		Private labelControl2 As DevExpress.XtraEditors.LabelControl
		Private WithEvents richEditControl2 As DevExpress.XtraRichEdit.RichEditControl
		Private cmbEncodings As DevExpress.XtraEditors.ComboBoxEdit
		Private WithEvents btnLoadRTF As DevExpress.XtraEditors.SimpleButton
	End Class
End Namespace

