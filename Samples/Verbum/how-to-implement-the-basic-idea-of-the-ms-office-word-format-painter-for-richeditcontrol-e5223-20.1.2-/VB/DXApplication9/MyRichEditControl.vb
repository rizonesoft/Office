' Developer Express Code Central Example:
' How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
' 
' This example demonstrates how to copy the characters and paragraphs properties
' and apply formatting to the selected text. Try the Format Painter button on the
' ribbon Home tab.
' 
' To obtain the selected text range, the
' RichEditDocument.Document.Selection property is used. The characters and
' paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
' handler. Then, they are stored in the CharacterPropertiesObject and
' ParagraphPropertiesObject object containers.
' 
' In order to change the current
' RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
' the custom MouseCursorCalculator class Calculate method for clarification.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E5223

Imports System
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Linq
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Internal
Imports DevExpress.XtraRichEdit.Mouse
Imports DevExpress.XtraRichEdit.Layout
Imports System.ComponentModel
Imports DevExpress.Portable.Input

Namespace DXApplication9
	Public Class MyRichEditControl
		Inherits RichEditControl

		Protected Overrides Function CreateInnerControl() As InnerRichEditControl
			Return New MyInnerControl(Me)
		End Function

		' Fields...
		Private _FormatCalculatorEnabled As Boolean
		<DefaultValue(False)>
		Public Property FormatCalculatorEnabled() As Boolean
			Get
				Return _FormatCalculatorEnabled
			End Get
			Set(ByVal value As Boolean)
				_FormatCalculatorEnabled = value
			End Set
		End Property

	End Class

	Public Class MyInnerControl
		Inherits InnerRichEditControl

		Public Sub New(ByVal owner As IInnerRichEditControlOwner)
			MyBase.New(owner)
		End Sub


		Protected Overrides Function CreateMouseCursorCalculator() As DevExpress.XtraRichEdit.Mouse.MouseCursorCalculator
			Return New MyMouseCursorCalculator(ActiveView)
		End Function
	End Class
	Public Class MyMouseCursorCalculator
		Inherits MouseCursorCalculator

		Public Sub New(ByVal view As RichEditView)
			MyBase.New(view)

		End Sub

		Public Overrides Function Calculate(ByVal hitTestResult As RichEditHitTestResultCore, ByVal physicalPoint As Point) As IPortableCursor

			If (TryCast(View.Control, MyRichEditControl)).FormatCalculatorEnabled Then
				Return DevExpress.XtraRichEdit.Utils.RichEditCursors.Hand
			End If

			Return MyBase.Calculate(hitTestResult, physicalPoint)
		End Function
	End Class

End Namespace
