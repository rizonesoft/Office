Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Threading
Imports System.Windows.Forms
Imports DevExpress.LookAndFeel

Namespace DXApplication15
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

			DevExpress.Skins.SkinManager.EnableFormSkins()
			DevExpress.UserSkins.BonusSkins.Register()
			UserLookAndFeel.Default.SetSkinStyle("DevExpress Style")
			Application.Run(New Form1())
		End Sub
	End Class
End Namespace