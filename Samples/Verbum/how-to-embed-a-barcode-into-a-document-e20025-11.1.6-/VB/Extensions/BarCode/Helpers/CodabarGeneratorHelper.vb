Imports Microsoft.VisualBasic
	Imports System
	Imports System.Collections
	Imports System.Collections.Generic
	Imports System.Drawing
	Imports DevExpress.XtraPrinting
	Imports DevExpress.XtraPrinting.BarCode
	Imports DevExpress.XtraRichEdit.Fields
Namespace BizPad

	Friend Class CodabarGeneratorHelper
		Inherits CodabarGenerator
		Implements IBarCodeGenerator
		Private Shared CodabarStartStopPairs As New Dictionary(Of String, CodabarStartStopPair)()
		Shared Sub New()
			CodabarStartStopPairs.Add("at", CodabarStartStopPair.AT)
			CodabarStartStopPairs.Add("bn", CodabarStartStopPair.BN)
			CodabarStartStopPairs.Add("cstar", CodabarStartStopPair.CStar)
			CodabarStartStopPairs.Add("de", CodabarStartStopPair.DE)
			CodabarStartStopPairs.Add("none", CodabarStartStopPair.None)
		End Sub

		Private Sub Initialize(ByVal switches As InstructionCollection) Implements IBarCodeGenerator.Initialize
			Dim p As String = If(switches.GetString("p"), String.Empty)

			Dim startStopPair As CodabarStartStopPair = CodabarStartStopPair.None
			If CodabarStartStopPairs.ContainsKey(p.ToLower()) Then
				startStopPair = CodabarStartStopPairs(p.ToLower())
			End If

			Me.StartStopPair = startStopPair

			Dim r As Single = 0f
			If (Not Single.TryParse(If(switches.GetString("r"), String.Empty), r)) Then
				r = 0f
			End If

			If r < 2 OrElse r > 3 Then
				r = 2f
			End If

			Me.WideNarrowRatio = r
		End Sub

		Public Function SupressAutoTextAlignment() As Boolean Implements IBarCodeGenerator.SupressAutoTextAlignment
			Return False
		End Function

		Private Function MakeBarCodePattern(ByVal text As String) As ArrayList Implements IBarCodeGenerator.MakeBarCodePattern
			Return MyBase.MakeBarCodePattern(text)
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

		Private Function GetValidCharSet() As String Implements IBarCodeGenerator.GetValidCharSet
			Return MyBase.GetValidCharSet()
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
