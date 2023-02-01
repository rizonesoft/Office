Imports Microsoft.VisualBasic
	Imports System.Collections
	Imports System.Drawing
	Imports DevExpress.XtraPrinting
	Imports DevExpress.XtraPrinting.BarCode
	Imports DevExpress.XtraRichEdit.Fields
Namespace BizPad

	Friend Interface IBarCodeGenerator
		Sub Initialize(ByVal switches As InstructionCollection)
		Function MakeBarCodePattern(ByVal text As String) As ArrayList
		Function MakeDisplayText(ByVal text As String) As String
		Function FormatText(ByVal text As String) As String
		Function IsValidPattern(ByVal pattern As ArrayList) As Boolean
		Function IsValidTextFormat(ByVal text As String) As Boolean
		Function IsValidText(ByVal text As String) As Boolean
		Function CalcBarCodeWidth(ByVal pattern As ArrayList) As Single
		Function CalcBarCodeHeight(ByVal pattern As ArrayList) As Single
		Function GetValidCharSet() As String
		Function SupressAutoTextAlignment() As Boolean
		Sub DrawBarCode(ByVal gr As IGraphics, ByVal barBounds As RectangleF, ByVal textBounds As RectangleF, ByVal data As IBarCodeData, ByVal xModule As Single, ByVal yModule As Single)
	End Interface
End Namespace