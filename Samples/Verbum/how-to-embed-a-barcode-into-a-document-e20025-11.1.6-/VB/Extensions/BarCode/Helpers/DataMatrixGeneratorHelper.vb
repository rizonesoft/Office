Imports Microsoft.VisualBasic
	Imports System.Collections
	Imports System.Drawing
	Imports DevExpress.XtraPrinting
	Imports DevExpress.XtraPrinting.BarCode
	Imports DevExpress.XtraRichEdit.Fields
	Imports System.Collections.Generic
	Imports System
	Imports System.Diagnostics
Namespace BizPad

	Friend Class DataMatrixGeneratorHelper
		Inherits DataMatrixGenerator
		Implements IBarCodeGenerator
		Private Shared Modes As New Dictionary(Of String, DataMatrixCompactionMode)()
		Private Shared Sizes As New Dictionary(Of String, DataMatrixSize)()
		Shared Sub New()
			Modes.Add("t", DataMatrixCompactionMode.Text)
			Modes.Add("text", DataMatrixCompactionMode.Text)
			Modes.Add("txt", DataMatrixCompactionMode.Text)
			Modes.Add("b", DataMatrixCompactionMode.Binary)
			Modes.Add("binary", DataMatrixCompactionMode.Binary)
			Modes.Add("bin", DataMatrixCompactionMode.Binary)
			Modes.Add("ascii", DataMatrixCompactionMode.ASCII)
			Modes.Add("a", DataMatrixCompactionMode.ASCII)
			Modes.Add("c40", DataMatrixCompactionMode.C40)
			Modes.Add("c", DataMatrixCompactionMode.C40)
			Modes.Add("edifact", DataMatrixCompactionMode.Edifact)
			Modes.Add("e", DataMatrixCompactionMode.Edifact)
			Modes.Add("x12", DataMatrixCompactionMode.X12)
			Modes.Add("x", DataMatrixCompactionMode.X12)
			For Each s As String In System.Enum.GetNames(GetType(DataMatrixSize))
				If s.StartsWith("Matrix") Then
					Sizes.Add(s.Substring("Matrix".Length).ToLower(), CType(System.Enum.Parse(GetType(DataMatrixSize), s), DataMatrixSize))
				End If
			Next s
		End Sub

		Private Sub Initialize(ByVal switches As InstructionCollection) Implements IBarCodeGenerator.Initialize

			Dim m As String = If(switches.GetString("m"), String.Empty)

			Dim mode As DataMatrixCompactionMode = DataMatrixCompactionMode.ASCII
			If Modes.ContainsKey(m.ToLower()) Then
				mode = Modes(m.ToLower())
			End If

			If Me.CompactionMode = mode Then
				If mode = DataMatrixCompactionMode.ASCII Then
					Me.CompactionMode = DataMatrixCompactionMode.Text
				Else
					Me.CompactionMode = DataMatrixCompactionMode.ASCII
				End If
			End If

			Me.CompactionMode = mode

			Dim p As String = If(switches.GetString("p"), String.Empty)

			Dim size As DataMatrixSize = DataMatrixSize.MatrixAuto
			If Sizes.ContainsKey(p.ToLower()) Then
				size = Sizes(p.ToLower())
			End If

			Me.MatrixSize = size

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
