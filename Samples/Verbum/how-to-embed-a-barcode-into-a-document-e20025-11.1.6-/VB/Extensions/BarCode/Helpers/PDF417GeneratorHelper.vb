Imports Microsoft.VisualBasic
	Imports System.Collections
	Imports System.Drawing
	Imports DevExpress.XtraPrinting
	Imports DevExpress.XtraPrinting.BarCode
	Imports DevExpress.XtraRichEdit.Fields
	Imports System.Collections.Generic
	Imports System
Namespace BizPad

	Friend Class PDF417GeneratorHelper
		Inherits PDF417Generator
		Implements IBarCodeGenerator
		Private Shared Modes As New Dictionary(Of String, PDF417CompactionMode)()
		Shared Sub New()
			Modes.Add("t", PDF417CompactionMode.Text)
			Modes.Add("text", PDF417CompactionMode.Text)
			Modes.Add("txt", PDF417CompactionMode.Text)
			Modes.Add("b", PDF417CompactionMode.Binary)
			Modes.Add("binary", PDF417CompactionMode.Binary)
			Modes.Add("bin", PDF417CompactionMode.Binary)
		End Sub

		Private Sub Initialize(ByVal switches As InstructionCollection) Implements IBarCodeGenerator.Initialize
			Dim m As String = If(switches.GetString("m"), String.Empty)

			Dim mode As PDF417CompactionMode = PDF417CompactionMode.Text
			If Modes.ContainsKey(m.ToLower()) Then
				mode = Modes(m.ToLower())
			End If

			Me.CompactionMode = mode

			Dim r? As Integer = switches.GetNullableInt("r")
			Dim c? As Integer = switches.GetNullableInt("c")

'INSTANT VB TODO TASK: VB does not support usage of the bitwise operators on nullable types:
			If c.HasValue AndAlso c > 0 Then
				Me.Columns = c.Value
			End If

'INSTANT VB TODO TASK: VB does not support usage of the bitwise operators on nullable types:
			If r.HasValue AndAlso r > 0 Then
				Me.Rows = r.Value
			End If

			Dim p As Single = 0f
			If (Not Single.TryParse(If(switches.GetString("p"), String.Empty), p)) Then
				p = 0f
			End If

			If p <= 0f Then
				p = 3f
			End If

			Me.YToXRatio = p

			Dim e? As Integer = switches.GetNullableInt("e")
			If (Not e.HasValue) OrElse e.Value < 1 OrElse e.Value > 8 Then
				e = 2
			End If

			Me.ErrorCorrectionLevel = CType(e.Value, DevExpress.XtraPrinting.BarCode.ErrorCorrectionLevel)

			Me.TruncateSymbol = switches.GetBool("o")
		End Sub

		Private Function GetValidCharSet() As String Implements IBarCodeGenerator.GetValidCharSet
			Return MyBase.GetValidCharSet()
		End Function

		Private Function MakeBarCodePattern(ByVal text As String) As ArrayList Implements IBarCodeGenerator.MakeBarCodePattern
			Return MyBase.MakeBarCodePattern(text)
		End Function

		Public Function SupressAutoTextAlignment() As Boolean Implements IBarCodeGenerator.SupressAutoTextAlignment
			Return False
		End Function

		Private Sub DrawBarCode(ByVal gr As IGraphics, ByVal barBounds As RectangleF, ByVal textBounds As RectangleF, ByVal data As IBarCodeData, ByVal xModule As Single, ByVal yModule As Single) Implements IBarCodeGenerator.DrawBarCode
			MyBase.DrawBarCode(gr, barBounds, textBounds, data, xModule, yModule)
		End Sub

		Private Function MakeDisplayText(ByVal text As String) As String Implements IBarCodeGenerator.MakeDisplayText
			Return MyBase.MakeDisplayText(text)
		End Function

		Private Function FormatText(ByVal text As String) As String Implements IBarCodeGenerator.FormatText
			Return MyBase.FormatText(text)
		End Function

		Private Function IsValidPattern(ByVal pattern As ArrayList) As Boolean Implements IBarCodeGenerator.IsValidPattern
			Return MyBase.IsValidPattern(pattern)
		End Function

		Private Function IsValidText(ByVal text As String) As Boolean Implements IBarCodeGenerator.IsValidText
			Return BarCodeGeneratorHelper.IsValidText(Me, text)
		End Function

		Private Function IsValidTextFormat(ByVal text As String) As Boolean Implements IBarCodeGenerator.IsValidTextFormat
			Return MyBase.IsValidTextFormat(text)
		End Function

		Private Function CalcBarCodeWidth(ByVal pattern As ArrayList) As Single Implements IBarCodeGenerator.CalcBarCodeWidth
			Return MyBase.CalcBarCodeWidth(pattern)
		End Function

		Private Function CalcBarCodeHeight(ByVal pattern As ArrayList) As Single Implements IBarCodeGenerator.CalcBarCodeHeight
			Return MyBase.CalcBarCodeHeight(pattern)
		End Function
	End Class
End Namespace
