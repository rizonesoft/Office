' Developer Express Code Central Example:
' How to implement an MS Word-like Mini Toolbar in RichEditControl
' 
' This example demonstrates how to implement the MS Word-like Mini Toolbar feature
' using a RibbonMiniToolbar
' (https://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsRibbonRibbonMiniToolbartopic)
' component. It is a popup toolbar, whose transparency depends on the distance
' from the mouse cursor. Show this toolbar for the selected text in the
' RichEditControl document separately and display it together with a regular
' context menu in the RichEditControl.PopupMenuShowing event handler.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=T157245

Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Windows.Forms

Namespace RTFRibbonMini
    Friend NotInheritable Class Program

        Private Sub New()
        End Sub

        ''' <summary>
        ''' The main entry point for the application.
        ''' </summary>
        <STAThread> _
        Shared Sub Main()
            Application.EnableVisualStyles()
            Application.SetCompatibleTextRenderingDefault(False)
            Application.Run(New Form1())
        End Sub
    End Class
End Namespace
