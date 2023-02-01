Imports Microsoft.Win32
Imports System.Windows.Forms
Imports Microsoft.VisualBasic.Devices

Public NotInheritable Class FileAssociationHelper
	Public Shared ReadOnly DefaultRegistryKeyValueName As String = String.Empty

	Private Sub New()
	End Sub
	Public Shared Sub AssociateFileExtension(ByVal fileExtension As String)
		Dim actualFileExtension As String
		If fileExtension.Chars(0) = "."c Then
			actualFileExtension = (fileExtension)
		Else
			actualFileExtension = ("."c & fileExtension)
		End If
		Dim friendlyName As String = actualFileExtension.TrimStart(New Char() { "."c }) & "file"

		Dim computer As New Computer()

		Dim rkFileExtension As RegistryKey = computer.Registry.ClassesRoot.CreateSubKey(actualFileExtension)
		rkFileExtension.SetValue(DefaultRegistryKeyValueName, friendlyName, RegistryValueKind.String)

		Dim rkShellOpenCommand As RegistryKey = computer.Registry.ClassesRoot.CreateSubKey(friendlyName & "\shell\open\command")
		rkShellOpenCommand.SetValue(DefaultRegistryKeyValueName, Application.ExecutablePath & " ""%l"" ", RegistryValueKind.String)

		Dim rkDefaultIcon As RegistryKey = computer.Registry.ClassesRoot.CreateSubKey(friendlyName & "\DefaultIcon")
		rkDefaultIcon.SetValue(DefaultRegistryKeyValueName, Application.StartupPath & "\App.ico", RegistryValueKind.String)
	End Sub
End Class