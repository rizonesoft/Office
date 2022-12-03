Imports System
Imports DevExpress.XtraBars.Helpers
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.Services
Imports DevExpress.XtraRichEdit.Menu
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native

Namespace RichEditContextMenu
    Partial Public Class Form1
        Inherits RibbonForm

        Public Sub New()
            InitializeComponent()
            InitSkinGallery()
            InitializeRichEditControl()
            ribbonControl.SelectedPage = homeRibbonPage1

            richEditControl.Document.AppendText("Table Test" & ControlChars.CrLf)
            Dim table As Table = richEditControl.Document.Tables.Create(richEditControl.Document.Paragraphs(1).Range.Start, 8, 8, AutoFitBehaviorType.AutoFitToWindow)

            table.BeginUpdate()
            table.ForEachCell(Sub(cell As TableCell, rowIndex As Integer, cellIndex As Integer) richEditControl.Document.InsertText(cell.Range.Start, String.Format("{0}:{1}", rowIndex, cellIndex)))
            table.EndUpdate()
        End Sub
        Private Sub InitSkinGallery()
            SkinHelper.InitSkinGallery(rgbiSkins, True)
        End Sub
        Private Sub InitializeRichEditControl()
        End Sub

        #Region "#PopupMenuShowing"
        Private Sub richEditControl_PopupMenuShowing(ByVal sender As Object, ByVal e As PopupMenuShowingEventArgs) Handles richEditControl.PopupMenuShowing
            If (e.MenuType And RichEditMenuType.TableCell) <> 0 Then
                ' Remove the "Paste" menu item:
                e.Menu.RemoveMenuItem(RichEditCommandId.PasteSelection)

                ' Disable the "Hyperlink..." menu item:
                e.Menu.DisableMenuItem(RichEditCommandId.CreateHyperlink)

                ' Create a RichEdit command, which inserts an inline picture into a document:
                Dim service As IRichEditCommandFactoryService = DirectCast(richEditControl.GetService(GetType(IRichEditCommandFactoryService)), IRichEditCommandFactoryService)
                Dim cmd As RichEditCommand = service.CreateCommand(RichEditCommandId.InsertPicture)

                'Create a menu item for the new command:
                Dim menuItemCommandAdapter As New RichEditMenuItemCommandWinAdapter(cmd)
                Dim menuItem As RichEditMenuItem = CType(menuItemCommandAdapter.CreateMenuItem(DevExpress.Utils.Menu.DXMenuItemPriority.Normal), RichEditMenuItem)
                menuItem.BeginGroup = True
                e.Menu.Items.Add(menuItem)

                ' Insert a new item into the Richedit popup menu and handle its click event:
                Dim myItem As New RichEditMenuItem("Highlight Selection", New EventHandler(AddressOf MyClickHandler))
                e.Menu.Items.Add(myItem)
            End If
        End Sub
        #End Region ' #PopupMenuShowing

        Public Sub MyClickHandler(ByVal sender As Object, ByVal e As EventArgs)
            Dim charProps As CharacterProperties = richEditControl.Document.BeginUpdateCharacters(richEditControl.Document.Selection)
            charProps.BackColor = System.Drawing.Color.Yellow
            richEditControl.Document.EndUpdateCharacters(charProps)
        End Sub

    End Class
End Namespace
