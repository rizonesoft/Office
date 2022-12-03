Imports Microsoft.VisualBasic
	Imports System
	Imports System.Collections.Generic
	Imports DevExpress.XtraPrinting.BarCode
	Imports DevExpress.XtraPrinting.BarCode.Native
	Imports DevExpress.XtraRichEdit.Fields
Namespace BizPad

	Friend NotInheritable Class BarCodeGeneratorFactory

		Private Shared defaultCodeType As Type = GetType(CodabarGenerator)
		Private Shared hashTable As New Dictionary(Of String, Type)()
		Private Sub New()
		End Sub
		Shared Sub New()
			hashTable("codabar") = GetType(CodabarGeneratorHelper)
			hashTable("code128") = GetType(Code128GeneratorHelper)
			hashTable("128") = GetType(Code128GeneratorHelper)
			hashTable("industrial2of5") = GetType(Industrial2of5GeneratorHelper)
			hashTable("2of5") = GetType(Industrial2of5GeneratorHelper)
			hashTable("interleaved2of5") = GetType(Interleaved2of5GeneratorHelper)
			hashTable("2of5i") = GetType(Interleaved2of5GeneratorHelper)
			hashTable("code39") = GetType(Code39GeneratorHelper)
			hashTable("39") = GetType(Code39GeneratorHelper)
			hashTable("3of9") = GetType(Code39GeneratorHelper)
			hashTable("code39extended") = GetType(Code39ExtendedGeneratorHelper)
			hashTable("code39e") = GetType(Code39ExtendedGeneratorHelper)
			hashTable("39e") = GetType(Code39ExtendedGeneratorHelper)
			hashTable("3of9e") = GetType(Code39ExtendedGeneratorHelper)
			hashTable("code93") = GetType(Code93GeneratorHelper)
			hashTable("93") = GetType(Code93GeneratorHelper)
			hashTable("code93e") = GetType(Code93ExtendedGeneratorHelper)
			hashTable("code93e") = GetType(Code93ExtendedGeneratorHelper)
			hashTable("93e") = GetType(Code93ExtendedGeneratorHelper)
			hashTable("code11") = GetType(Code11GeneratorHelper)
			hashTable("11") = GetType(Code11GeneratorHelper)
			hashTable("msi") = GetType(CodeMSIGeneratorHelper)
			hashTable("plessey") = GetType(CodeMSIGeneratorHelper)
			hashTable("postnet") = GetType(PostNetGeneratorHelper)
			hashTable("post") = GetType(PostNetGeneratorHelper)
			hashTable("ean13") = GetType(EAN13GeneratorHelper)
			hashTable("ean8") = GetType(EAN8GeneratorHelper)
			hashTable("ean128") = GetType(EAN128GeneratorHelper)
			hashTable("upca") = GetType(UPCAGeneratorHelper)
			hashTable("upcsupplemental2") = GetType(UPCSupplemental2GeneratorHelper)
			hashTable("upcs2") = GetType(UPCSupplemental2GeneratorHelper)
			hashTable("upcsupplemental5") = GetType(UPCSupplemental5GeneratorHelper)
			hashTable("upcs5") = GetType(UPCSupplemental5GeneratorHelper)
			hashTable("upce0") = GetType(UPCE0GeneratorHelper)
			hashTable("upce1") = GetType(UPCE1GeneratorHelper)
			hashTable("matrix2of5") = GetType(Matrix2of5GeneratorHelper)
			hashTable("2of5m") = GetType(Matrix2of5GeneratorHelper)
			hashTable("pdf417") = GetType(PDF417GeneratorHelper)
			hashTable("datamatrix") = GetType(DataMatrixGeneratorHelper)
			hashTable("ecc200") = GetType(DataMatrixGeneratorHelper)
		End Sub

		Friend Shared Function Create(ByVal symbologyCode As String, ByVal switches As InstructionCollection) As IBarCodeGenerator
			Dim type As Type = Nothing
			If (Not String.IsNullOrWhiteSpace(symbologyCode)) Then
				If (Not hashTable.TryGetValue(symbologyCode.Trim().ToLower(), type)) Then
					type = Nothing
				End If
			End If
			If type Is Nothing Then
				type = defaultCodeType
			End If
			Dim generator As IBarCodeGenerator = CType(Activator.CreateInstance(type), IBarCodeGenerator)
			generator.Initialize(switches)
			Return generator
		End Function
	End Class
End Namespace