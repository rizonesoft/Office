Imports System
Imports System.Threading
Imports DevExpress.XtraWaitForm

Namespace SpreadsheetProgressSample
	Partial Public Class WaitForm1
		Inherits WaitForm

		Private cancellationTokenSource As CancellationTokenSource

		Public Sub New()
			InitializeComponent()
			progressPanel1.AutoSize = True
		End Sub

		Public Overrides Sub SetCaption(ByVal caption As String)
			MyBase.SetCaption(caption)
			progressPanel1.Caption = caption
		End Sub

		Public Overrides Sub SetDescription(ByVal description As String)
			MyBase.SetDescription(description)
			progressPanel1.Description = description
		End Sub

		Public Overrides Sub ProcessCommand(ByVal cmd As System.Enum, ByVal arg As Object)
			MyBase.ProcessCommand(cmd, arg)
			Dim command As WaitFormCommand = CType(cmd, WaitFormCommand)
			If command = WaitFormCommand.SetCancellationTokenSource Then
				cancellationTokenSource = DirectCast(arg, CancellationTokenSource)
			End If
		End Sub

		Public Enum WaitFormCommand
			SetCancellationTokenSource
		End Enum

		Private Sub Cancel_Click(ByVal sender As Object, ByVal e As EventArgs) Handles hyperlinkLabelControl1.Click
			cancellationTokenSource?.Cancel()
		End Sub
	End Class
End Namespace