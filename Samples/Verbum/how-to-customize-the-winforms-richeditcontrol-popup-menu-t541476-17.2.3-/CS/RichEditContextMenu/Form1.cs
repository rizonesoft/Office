using System;
using DevExpress.XtraBars.Helpers;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Services;
using DevExpress.XtraRichEdit.Menu;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;

namespace RichEditContextMenu
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            InitSkinGallery();
            InitializeRichEditControl();
            ribbonControl.SelectedPage = homeRibbonPage1;

            richEditControl.Document.AppendText("Table Test\r\n");
            Table table = richEditControl.Document.Tables.Create(richEditControl.Document.Paragraphs[1].Range.Start, 8, 8, AutoFitBehaviorType.AutoFitToWindow);
            
            table.BeginUpdate();
            table.ForEachCell(delegate (TableCell cell, int rowIndex, int cellIndex) {
                richEditControl.Document.InsertText(cell.Range.Start, string.Format("{0}:{1}", rowIndex, cellIndex));
            });
            table.EndUpdate();
        }
        void InitSkinGallery()
        {
            SkinHelper.InitSkinGallery(rgbiSkins, true);
        }
        void InitializeRichEditControl() { }

        #region #PopupMenuShowing
        private void richEditControl_PopupMenuShowing(object sender, PopupMenuShowingEventArgs e)
        {
            if ((e.MenuType & RichEditMenuType.TableCell) != 0)
            {
                // Remove the "Paste" menu item:
                e.Menu.RemoveMenuItem(RichEditCommandId.PasteSelection);

                // Disable the "Hyperlink..." menu item:
                e.Menu.DisableMenuItem(RichEditCommandId.CreateHyperlink);

                // Create a RichEdit command, which inserts an inline picture into a document:
                IRichEditCommandFactoryService service = (IRichEditCommandFactoryService)richEditControl.GetService(typeof(IRichEditCommandFactoryService));
                RichEditCommand cmd = service.CreateCommand(RichEditCommandId.InsertPicture);

                //Create a menu item for the new command:
                RichEditMenuItemCommandWinAdapter menuItemCommandAdapter = new RichEditMenuItemCommandWinAdapter(cmd);
                RichEditMenuItem menuItem = (RichEditMenuItem)menuItemCommandAdapter.CreateMenuItem(DevExpress.Utils.Menu.DXMenuItemPriority.Normal);
                menuItem.BeginGroup = true;
                e.Menu.Items.Add(menuItem);

                // Insert a new item into the Richedit popup menu and handle its click event:
                RichEditMenuItem myItem = new RichEditMenuItem("Highlight Selection", new EventHandler(MyClickHandler));
                e.Menu.Items.Add(myItem);
            }
        }
        #endregion #PopupMenuShowing

        public void MyClickHandler(object sender, EventArgs e)
        {
            CharacterProperties charProps = richEditControl.Document.BeginUpdateCharacters(richEditControl.Document.Selection);
            charProps.BackColor = System.Drawing.Color.Yellow;
            richEditControl.Document.EndUpdateCharacters(charProps);
        }

    }
}
