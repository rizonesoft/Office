Imports Microsoft.VisualBasic
	Imports System.Collections.Generic
	Imports DevExpress.XtraRichEdit.Fields
	Imports DevExpress.XtraRichEdit.Model
	Imports DevExpress.XtraRichEdit.Utils
Namespace BizPad

	Public Class ChartField
		Inherits CalculatedFieldBase
		Public Shared ReadOnly FieldType As String = "CHART"
		Protected Overrides ReadOnly Property FieldTypeName() As String
			Get
				Return FieldType
			End Get
		End Property

		Private Shared ReadOnly switchesWithArgument As Dictionary(Of String, Boolean) = CreateSwitchesWithArgument("w", "h", "d", "c", "s")
		Protected Overrides ReadOnly Property SwitchesWithArguments() As Dictionary(Of String, Boolean)
			Get
				Return switchesWithArgument
			End Get
		End Property

		Private chart As New ChartImage()

		Public Overrides Sub Initialize(ByVal switches As InstructionCollection)
			MyBase.Initialize(switches)
			chart.Initialize(switches)
		End Sub


		Public Overrides Function GetCalculatedValueCore(ByVal sourcePieceTable As PieceTable, ByVal targetModel As DocumentModel, ByVal mailMergeDataMode As MailMergeDataMode, ByVal documentField As Field) As Object

			Dim image As RichEditImage = chart.CreateImage()
			targetModel.MainPieceTable.InsertInlinePicture(DocumentLogPosition.Zero, image)
			Return targetModel
		End Function
	End Class
End Namespace
