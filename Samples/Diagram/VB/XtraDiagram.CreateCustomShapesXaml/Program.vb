Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Windows.Documents
Imports System.Windows.Forms

Namespace XtraDiagram.CreateCustomShapes
    Friend NotInheritable Class Program

        Private Sub New()
        End Sub

        ''' <summary>
        ''' The main entry point for the application.
        ''' </summary>
        <STAThread> _
        Shared Sub Main()
            RegisterPackUriScheme()
            Application.EnableVisualStyles()
            Application.SetCompatibleTextRenderingDefault(False)
            Application.Run(New Form1())
        End Sub
        Private Shared Sub RegisterPackUriScheme()
            Dim TempFlowDocument As FlowDocument = New FlowDocument()
        End Sub
    End Class
End Namespace
