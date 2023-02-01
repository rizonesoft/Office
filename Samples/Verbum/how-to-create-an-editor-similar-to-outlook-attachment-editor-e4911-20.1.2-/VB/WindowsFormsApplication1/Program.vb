' Developer Express Code Central Example:
' How to create an editor similar to Outlook Attachment Editor
' 
' This example demonstrates how the RichEditControl component can be used to
' emulate the Outlook Attachment Editor behavior.
' The main idea of the approach
' demonstrated in this sample is to use the DOCVARIABLE field
' (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
' display corresponding RTF content for each inserted file.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E4911


Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Windows.Forms

Namespace WindowsFormsApplication1
	Friend NotInheritable Class Program
		''' <summary>
		''' The main entry point for the application.
		''' </summary>
		Private Sub New()
		End Sub
		<STAThread> _
		Shared Sub Main()
			Application.EnableVisualStyles()
			Application.SetCompatibleTextRenderingDefault(False)
			Application.Run(New Form1())
		End Sub
	End Class
End Namespace
