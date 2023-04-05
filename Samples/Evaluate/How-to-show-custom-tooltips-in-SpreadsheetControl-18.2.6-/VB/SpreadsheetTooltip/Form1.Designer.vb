Namespace SpreadsheetTooltip
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
			Me.spreadsheetControl1 = New DevExpress.XtraSpreadsheet.SpreadsheetControl()
			Me.toolTipController1 = New DevExpress.Utils.ToolTipController(Me.components)
			Me.svgImageCollection1 = New DevExpress.Utils.SvgImageCollection(Me.components)
			CType(Me.svgImageCollection1, System.ComponentModel.ISupportInitialize).BeginInit()
			Me.SuspendLayout()
			' 
			' spreadsheetControl1
			' 
			Me.spreadsheetControl1.Dock = System.Windows.Forms.DockStyle.Fill
			Me.spreadsheetControl1.Location = New System.Drawing.Point(0, 0)
			Me.spreadsheetControl1.Name = "spreadsheetControl1"
			Me.spreadsheetControl1.Options.Import.Csv.Encoding = (CType(resources.GetObject("spreadsheetControl1.Options.Import.Csv.Encoding"), System.Text.Encoding))
			Me.spreadsheetControl1.Options.Import.Txt.Encoding = (CType(resources.GetObject("spreadsheetControl1.Options.Import.Txt.Encoding"), System.Text.Encoding))
			Me.spreadsheetControl1.Size = New System.Drawing.Size(961, 538)
			Me.spreadsheetControl1.TabIndex = 0
			Me.spreadsheetControl1.Text = "spreadsheetControl1"
			' 
			' svgImageCollection1
			' 
			Me.svgImageCollection1.Add("text", "image://svgimages/spreadsheet/text2.svg")
			Me.svgImageCollection1.Add("boolean", "image://svgimages/content/checkbox.svg")
			Me.svgImageCollection1.Add("numeric", "image://svgimages/spreadsheet/number.svg")
			Me.svgImageCollection1.Add("error", "image://svgimages/diagramicons/del.svg")
			Me.svgImageCollection1.Add("datetime", "image://svgimages/spreadsheet/date&time.svg")
			' 
			' Form1
			' 
			Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
			Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
			Me.ClientSize = New System.Drawing.Size(961, 538)
			Me.Controls.Add(Me.spreadsheetControl1)
			Me.Name = "Form1"
			Me.Text = "Form1"
			CType(Me.svgImageCollection1, System.ComponentModel.ISupportInitialize).EndInit()
			Me.ResumeLayout(False)

		End Sub

		#End Region

		Private spreadsheetControl1 As DevExpress.XtraSpreadsheet.SpreadsheetControl
		Private toolTipController1 As DevExpress.Utils.ToolTipController
		Private svgImageCollection1 As DevExpress.Utils.SvgImageCollection
	End Class
End Namespace

