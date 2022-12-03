Imports Microsoft.VisualBasic
#Region "#usings"
Imports DevExpress.Office.Utils
Imports DevExpress.XtraRichEdit.API.Native
Imports System.Drawing
Imports System.Windows.Forms
#End Region ' #usings

Namespace RichEdit_GetPositionFromPoint
	Partial Public Class Form1
		Inherits DevExpress.XtraEditors.XtraForm
		Public Sub New()
			InitializeComponent()
'			#Region "#subscribe"
			AddHandler Me.richEditControl1.MouseMove, AddressOf richEditControl1_MouseMove
'			#End Region ' #subscribe
		End Sub
		#Region "#getpositionfrompoint"
		Private Sub richEditControl1_MouseMove(ByVal sender As Object, ByVal e As MouseEventArgs)
			Dim docPoint As Point = Units.PixelsToDocuments(e.Location, richEditControl1.DpiX, richEditControl1.DpiY)
			Dim pos As DocumentPosition = richEditControl1.GetPositionFromPoint(docPoint)
			If pos IsNot Nothing Then
				Me.Text = System.String.Format("Mouse is over position {0}",pos)
			Else
				Me.Text = ""
			End If
		End Sub
		#End Region ' #getpositionfrompoint
	End Class
End Namespace
