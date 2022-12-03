Imports Microsoft.VisualBasic
Imports System
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Internal
Imports DevExpress.XtraRichEdit.Model

Namespace BizPad.Extensions
	Public Class RichEditEx
		Inherits RichEditControl
		Implements IInnerRichEditControlOwner
		Protected Overrides Sub ActivateViewPlatformSpecific(ByVal view As RichEditView)
			MyBase.ActivateViewPlatformSpecific(view)
			RemoveService(GetType(IFieldCalculatorService))
			AddService(GetType(IFieldCalculatorService), New FieldCalculatorServiceEx())
		End Sub
	End Class
End Namespace
