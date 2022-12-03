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
Imports System.ComponentModel
Imports System.Drawing
Imports System.Linq
Imports System.Reflection
Imports System.Windows.Forms
Imports DevExpress.Office.Utils
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit.API.Native

Namespace RTFRibbonMini
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        Public Sub New()
            InitializeComponent()
            AddHandler richEditControl1.MouseUp, AddressOf richEditControl1_MouseUp
        End Sub

        Private Sub richEditControl1_MouseUp(ByVal sender As Object, ByVal e As MouseEventArgs)
            If richEditControl1.Document.Selection.Length <> 0 Then
                Dim documentPosition As DocumentPosition = richEditControl1.Document.CaretPosition
                Dim documentRectangle As Rectangle = richEditControl1.GetBoundsFromPosition(documentPosition)
                Dim documentPoint As New Point(documentRectangle.Left, documentRectangle.Bottom)
                Dim clientPoint As Point = Units.DocumentsToPixels(documentPoint, richEditControl1.DpiX, richEditControl1.DpiY)
                Dim screenPoint As Point = richEditControl1.PointToScreen(clientPoint)
                ribbonMiniToolbar1.Show(screenPoint)

            End If
        End Sub


        Private Function GetRibbonMiniToolbarHeight() As Integer
            Dim p As PropertyInfo = GetType(RibbonMiniToolbar).GetProperty("Form", BindingFlags.NonPublic Or BindingFlags.Instance)
            Dim f As DevExpress.XtraBars.Ribbon.RibbonMiniToolbarPopupForm = TryCast(p.GetValue(ribbonMiniToolbar1, Nothing), DevExpress.XtraBars.Ribbon.RibbonMiniToolbarPopupForm)
            Dim height As Integer = f.Size.Height
            Return height
        End Function
        Private Sub richEditControl1_PopupMenuShowing(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.PopupMenuShowingEventArgs) Handles richEditControl1.PopupMenuShowing
            Dim defaultMenu As DevExpress.XtraRichEdit.Menu.RichEditPopupMenu = e.Menu
            AddHandler defaultMenu.CloseUp, AddressOf defaultMenu_CloseUp

             ribbonMiniToolbar1.OpacityOptions.AllowTransparency = False
             Dim height As Integer = GetRibbonMiniToolbarHeight()
             ribbonMiniToolbar1.Show(New Point(Control.MousePosition.X, Control.MousePosition.Y - height))
        End Sub

        Private Sub defaultMenu_CloseUp(ByVal sender As Object, ByVal e As EventArgs)
            Dim menu As DevExpress.XtraRichEdit.Menu.RichEditPopupMenu = TryCast(sender, DevExpress.XtraRichEdit.Menu.RichEditPopupMenu)
            ribbonMiniToolbar1.OpacityOptions.AllowTransparency = True
            RemoveHandler menu.CloseUp, AddressOf defaultMenu_CloseUp
        End Sub
    End Class

End Namespace
