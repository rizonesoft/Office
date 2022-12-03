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
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Windows.Forms

Namespace WindowsFormsApplication1
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()
		End Sub

		Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load

		End Sub
	End Class
End Namespace
