Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Text
#Region "#usings"
Imports DevExpress.XtraEditors
Imports DevExpress.XtraRichEdit
Imports DevExpress.Utils.Commands
Imports DevExpress.XtraRichEdit.Commands
#End Region ' #usings

Namespace RichEditCommandExample
	#Region "#commandbutton"
	Public Class CommandButton
		Inherits SimpleButton
		Private commandId_Renamed As RichEditCommandId
		Private control As RichEditControl

		Public Sub Initialize(ByVal initControl As RichEditControl, ByVal initId As RichEditCommandId)
			UnsubscribeControlEvents()
			control = initControl
			commandId_Renamed = initId
			SubscribeControlEvents()
		End Sub

		Public Property RichEditControl() As RichEditControl
			Get
				Return control
			End Get
			Set(ByVal value As RichEditControl)
				If control Is value Then
					Return
				End If
				UnsubscribeControlEvents()
				Me.control = value
				SubscribeControlEvents()
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Public Property CommandId() As RichEditCommandId
			Get
				Return commandId_Renamed
			End Get
			Set(ByVal value As RichEditCommandId)
				If commandId_Renamed = value Then
					Return
				End If
				commandId_Renamed = value
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property

		Private Sub SubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			AddHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub
		Private Sub UnsubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			RemoveHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub

		Private Sub OnUpdateUI(ByVal sender As Object, ByVal e As EventArgs)
			Dim command As Command = CreateCommand()
			If command IsNot Nothing Then
				Dim state As New CommandButtonUIState(Me)
				command.UpdateUIState(state)
			End If
		End Sub

		Protected Overrides Sub OnClick(ByVal e As EventArgs)
			MyBase.OnClick(e)
			Dim command As Command = CreateCommand()
			If command IsNot Nothing Then
				command.Execute()
			End If
		End Sub

		' You may override this method to create a command
		Protected Overridable Function CreateCommand() As Command

			Return control.CreateCommand(commandId_Renamed)
		End Function
	End Class
	#End Region ' #commandbutton
	#Region "#commandbuttonuistate"
	Public Class CommandButtonUIState
		Implements ICommandUIState
		Private ReadOnly button As SimpleButton
		Public Sub New(ByVal button As SimpleButton)
			Me.button = button
		End Sub
		#Region "ICommandUIState Members"
		Public Property Checked() As Boolean Implements ICommandUIState.Checked
			Get
				Return False
			End Get
			Set(ByVal value As Boolean)
			End Set
		End Property
		Public Property Enabled() As Boolean Implements ICommandUIState.Enabled
			Get
				Return button.Enabled
			End Get
			Set(ByVal value As Boolean)
				button.Enabled = value
			End Set
		End Property
		Public Property Visible() As Boolean Implements ICommandUIState.Visible
			Get
				Return button.Visible
			End Get
			Set(ByVal value As Boolean)
				button.Visible = value
			End Set
		End Property
		Public Overridable Property EditValue() As Object Implements ICommandUIState.EditValue
			Get
				Return Nothing
			End Get
			Set(ByVal value As Object)
			End Set
		End Property



		#End Region
	End Class
	#End Region ' #commandbuttonuistate

	Public Class CommandCheckBoxAdapter
		Private commandId_Renamed As RichEditCommandId
		Private control As RichEditControl
		Private checkBox_Renamed As CheckEdit

		Public Property CheckBox() As CheckEdit
			Get
				Return checkBox_Renamed
			End Get
			Set(ByVal value As CheckEdit)
				If checkBox_Renamed Is value Then
					Return
				End If

				UnsubscribeCheckBoxEvents()
				checkBox_Renamed = value
				SubscribeCheckBoxEvents()
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Private Sub SubscribeCheckBoxEvents()
			If checkBox_Renamed Is Nothing Then
				Return
			End If

			AddHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
		End Sub
		Private Sub UnsubscribeCheckBoxEvents()
			If checkBox_Renamed Is Nothing Then
				Return
			End If

			RemoveHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
		End Sub
		Public Property RichEditControl() As RichEditControl
			Get
				Return control
			End Get
			Set(ByVal value As RichEditControl)
				If control Is value Then
					Return
				End If
				UnsubscribeControlEvents()
				Me.control = value
				SubscribeControlEvents()
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Public Property CommandId() As RichEditCommandId
			Get
				Return commandId_Renamed
			End Get
			Set(ByVal value As RichEditCommandId)
				If commandId_Renamed = value Then
					Return
				End If
				commandId_Renamed = value
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property

		Private Sub SubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			AddHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub
		Private Sub UnsubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			RemoveHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub

		Private Sub OnUpdateUI(ByVal sender As Object, ByVal e As EventArgs)
			If checkBox_Renamed Is Nothing Then
				Return
			End If
			RemoveHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
			Try
				Dim command As Command = CreateCommand()
				If command IsNot Nothing Then
					Dim state As New CommandCheckBoxUIState(checkBox_Renamed)
					command.UpdateUIState(state)
				End If
			Finally
				AddHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
			End Try
		End Sub

		Private Sub OnCheckedChanged(ByVal sender As Object, ByVal e As EventArgs)
			RemoveHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
			Try
				Dim command As Command = CreateCommand()
				If command IsNot Nothing Then
					command.Execute()
				End If
			Finally
				AddHandler checkBox_Renamed.CheckedChanged, AddressOf OnCheckedChanged
			End Try
		End Sub

		' You may override this method to create command
		Protected Overridable Function CreateCommand() As Command
			Return control.CreateCommand(commandId_Renamed)
		End Function
	End Class

	Public Class CommandCheckBoxUIState
		Implements ICommandUIState
		Private ReadOnly checkBox As CheckEdit
		Public Sub New(ByVal checkBox As CheckEdit)
			Me.checkBox = checkBox
		End Sub
		#Region "ICommandUIState Members"
		Public Property Checked() As Boolean Implements ICommandUIState.Checked
			Get
				Return checkBox.Checked
			End Get
			Set(ByVal value As Boolean)
				checkBox.Checked = value
			End Set
		End Property
		Public Property Enabled() As Boolean Implements ICommandUIState.Enabled
			Get
				Return checkBox.Enabled
			End Get
			Set(ByVal value As Boolean)
				checkBox.Enabled = value
			End Set
		End Property
		Public Property Visible() As Boolean Implements ICommandUIState.Visible
			Get
				Return checkBox.Visible
			End Get
			Set(ByVal value As Boolean)
				checkBox.Visible = value
			End Set
		End Property
		Public Overridable Property EditValue() As Object Implements ICommandUIState.EditValue
			Get
				Return Nothing
			End Get
			Set(ByVal value As Object)
			End Set
		End Property
		#End Region
	End Class
	#Region "#commandbuttonadapter"
	Public Class CommandButtonAdapter
		Private commandId_Renamed As RichEditCommandId
		Private control As RichEditControl
		Private button_Renamed As SimpleButton

		Public Sub Initialize(ByVal initControl As RichEditControl, ByVal initId As RichEditCommandId)
			UnsubscribeControlEvents()
			control = initControl
			commandId_Renamed = initId
			SubscribeControlEvents()
		End Sub

		Public Property RichEditControl() As RichEditControl
			Get
				Return control
			End Get
			Set(ByVal value As RichEditControl)
				If control Is value Then
					Return
				End If
				UnsubscribeControlEvents()
				Me.control = value
				SubscribeControlEvents()
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Public Property CommandId() As RichEditCommandId
			Get
				Return commandId_Renamed
			End Get
			Set(ByVal value As RichEditCommandId)
				If commandId_Renamed = value Then
					Return
				End If
				commandId_Renamed = value
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Public Property Button() As SimpleButton
			Get
				Return button_Renamed
			End Get
			Set(ByVal value As SimpleButton)
				If button_Renamed Is value Then
					Return
				End If

				UnsubscribeButtonEvents()
				button_Renamed = value
				SubscribeButtonEvents()
				OnUpdateUI(Me, EventArgs.Empty)
			End Set
		End Property
		Private Sub SubscribeButtonEvents()
			If button_Renamed Is Nothing Then
				Return
			End If

			AddHandler button_Renamed.Click, AddressOf OnClick
		End Sub
		Private Sub UnsubscribeButtonEvents()
			If button_Renamed Is Nothing Then
				Return
			End If

			RemoveHandler button_Renamed.Click, AddressOf OnClick
		End Sub
		Private Sub SubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			AddHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub
		Private Sub UnsubscribeControlEvents()
			If control Is Nothing Then
				Return
			End If
			RemoveHandler control.UpdateUI, AddressOf OnUpdateUI
		End Sub

		Private Sub OnUpdateUI(ByVal sender As Object, ByVal e As EventArgs)
			If button_Renamed Is Nothing Then
				Return
			End If

			Dim command As Command = CreateCommand()
			If command IsNot Nothing Then
				Dim state As New CommandButtonUIState(button_Renamed)
				command.UpdateUIState(state)
			End If
		End Sub

		Private Sub OnClick(ByVal sender As Object, ByVal e As EventArgs)
			Dim command As Command = CreateCommand()
			If command IsNot Nothing Then
				command.Execute()
			End If
		End Sub

		' You may override this method to create a command
		Protected Overridable Function CreateCommand() As Command
			Return control.CreateCommand(commandId_Renamed)
		End Function
	End Class
	#End Region ' #commandbuttonadapter
End Namespace

