Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Text
Imports DevExpress.XtraEditors
Imports DevExpress.Services
Imports System.Windows.Forms
Imports System.Drawing

Namespace ProgressIndicator
	#Region "#myprogressindicator"
	Friend Class MyProgressIndicatorService
		Implements IProgressIndicationService
		Private _Indicator As ProgressBarControl
		Public Property Indicator() As ProgressBarControl
			Get
				Return _Indicator
			End Get
			Set(ByVal value As ProgressBarControl)
				_Indicator = value
			End Set
		End Property

		Public Sub New(ByVal provider As IServiceProvider, ByVal indicator As ProgressBarControl)
			_Indicator = indicator
		End Sub

		#Region "IProgressIndicationService Members"

		Private Sub Begin(ByVal displayName As String, ByVal minProgress As Integer, ByVal maxProgress As Integer, ByVal currentProgress As Integer) Implements IProgressIndicationService.Begin
			_Indicator.Properties.Minimum = minProgress
			_Indicator.Properties.Maximum = maxProgress
			_Indicator.Properties.ShowTitle = True
			_Indicator.EditValue = currentProgress
			_Indicator.Refresh()
			_Indicator.Show()
		End Sub

		Private Sub [End]() Implements IProgressIndicationService.End
			_Indicator.Refresh()
			_Indicator.Hide()
		End Sub

		Private Sub SetProgress(ByVal currentProgress As Integer) Implements IProgressIndicationService.SetProgress
			_Indicator.EditValue = currentProgress
			_Indicator.Refresh()
		End Sub
		#End Region
	End Class
#End Region ' #myprogressindicatorsindicator
End Namespace
