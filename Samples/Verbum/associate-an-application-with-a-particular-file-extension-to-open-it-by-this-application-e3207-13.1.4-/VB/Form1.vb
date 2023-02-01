Imports Microsoft.VisualBasic
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit

Namespace RichEditApplicationFileAssociation
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			FileAssociationHelper.AssociateFileExtension(".myapp")

			ProcessCommandLineInput()
		End Sub

		Private Sub ProcessCommandLineInput()
			Dim commandLineArguments() As String = System.Environment.GetCommandLineArgs()

			If commandLineArguments.Length > 1 Then
				Try
					richEditControl1.LoadDocument(commandLineArguments(1), DocumentFormat.Rtf)
				Catch ex As System.Exception
					MessageBox.Show(String.Format("Cannot load {0}:" & Constants.vbCrLf & "{1}", commandLineArguments(1), ex.Message), "Error")
				End Try
			End If
		End Sub
	End Class
End Namespace