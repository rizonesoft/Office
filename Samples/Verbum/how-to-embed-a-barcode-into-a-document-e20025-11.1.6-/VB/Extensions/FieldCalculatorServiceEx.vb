Imports Microsoft.VisualBasic
	Imports System
	Imports System.Collections.Generic
	Imports System.Linq
	Imports DevExpress.XtraRichEdit.Fields
	Imports DevExpress.XtraRichEdit.Model
Namespace BizPad

	Public Class FieldCalculatorServiceEx
		Inherits FieldCalculatorService
		Implements IFieldCalculatorService
		Protected Overrides Function CreateInitializedCalculatedField(ByVal pieceTable As PieceTable, ByVal firstToken As Token, ByVal scanner As FieldScanner) As CalculatedFieldBase

			Dim chartToken As Token = firstToken

			If chartToken IsNot Nothing Then
				If String.Equals(chartToken.val, "CHART", StringComparison.OrdinalIgnoreCase) Then
					Return CreateInitializedField(Of ChartField)(scanner)
				ElseIf String.Equals(chartToken.val, "BRCODE", StringComparison.OrdinalIgnoreCase) Then
					Return CreateInitializedField(Of BarCodeField)(scanner)
				End If
			End If

			Return MyBase.CreateInitializedCalculatedField(pieceTable, firstToken, scanner)
		End Function

		Private Shared Function CreateInitializedField(Of T As {CalculatedFieldBase, New})(ByVal scanner As FieldScanner) As CalculatedFieldBase
			Dim field As CalculatedFieldBase = New T()
			If field Is Nothing Then
				Return Nothing
			End If

			Dim instructions As InstructionCollection = ParseInstructions(scanner, field)
			field.Initialize(instructions)
			Return field
		End Function
	End Class
End Namespace
