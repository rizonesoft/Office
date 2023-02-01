Imports Microsoft.VisualBasic
	Imports System
	Imports System.Collections.Generic
	Imports System.Linq
Namespace BizPad

	Friend NotInheritable Class BarCodeGeneratorHelper
		Private Sub New()
		End Sub
		Public Shared Function IsValidText(ByVal generator As IBarCodeGenerator, ByVal text As String) As Boolean
			If String.IsNullOrEmpty(text) Then
				Return False
			End If
			Dim charSet As String = generator.GetValidCharSet()
			Dim length As Integer = text.Length
			For i As Integer = 0 To length - 1
				If charSet.IndexOf(text.Chars(i)) < 0 Then
					Return False
				End If
			Next i
			Return True
		End Function
	End Class
End Namespace
