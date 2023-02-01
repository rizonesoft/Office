using DevExpress.XtraBars.Ribbon;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit;
using DevExpress.Portable.Input;

namespace BookmarksAndHyperlinksSimpleExample
{
    public partial class Form1 : RibbonForm
    {
        HyperlinkOptions hyperlinkOptions;
        BookmarkOptions bookmarkOptions;
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            richEditControl1.LoadDocument("Hyperlinks.docx");
            InsertHyperlink();
            InsertBookmark();

            #region #HyperlinkOptions
            hyperlinkOptions = richEditControl1.Options.Hyperlinks;

            hyperlinkOptions.EnableUriCorrection = false;
            hyperlinkOptions.ModifierKeys = PortableKeys.Shift;
            hyperlinkOptions.ShowToolTip = true;
            #endregion #Hyperlinkoptions

            #region #BookmarkOptions
            bookmarkOptions = richEditControl1.Options.Bookmarks;
            bookmarkOptions.ConflictNameResolution = ConflictNameAction.Rename;
            bookmarkOptions.Visibility = RichEditBookmarkVisibility.Hidden;
            #endregion #BookmarkOptions
        }

        private void InsertBookmark()
        {
            #region #InsertBookmark
            Document document = richEditControl1.Document;
            document.BeginUpdate();
            DocumentPosition pos = document.Range.Start;

            //Create a bookmark to a given position
            document.Bookmarks.Create(document.CreateRange(pos, 1), "Top");

            //Insert the hyperlink anchored to the created bookmark:
            DocumentRange[] foundRanges = document.FindAll("To the Top", SearchOptions.CaseSensitive);
            if (foundRanges.Length > 0)
            {
                document.Hyperlinks.Create(foundRanges[0]);
                document.Hyperlinks[1].Anchor = "Top";
            }
            document.EndUpdate();
            #endregion #InsertBookmark
        }

        private void InsertHyperlink()
        {
            #region #InsertHyperlink
            Document document = richEditControl1.Document;

            //Find the specific text string in a document
            DocumentRange[] foundRanges = document.FindAll("DevExpress WinForms Rich Text Editor",
            SearchOptions.CaseSensitive);
            if (foundRanges.Length > 0)
            {
                //Create a hyperlink from a found range
                document.Hyperlinks.Create(foundRanges[0]);

                //Set the URI and the tooltip for the created hyperlink
                document.Hyperlinks[0].NavigateUri = "https://www.devexpress.com/Products/NET/Controls/WinForms/Rich_Editor/";
                document.Hyperlinks[0].ToolTip = "WinForms Rich Text Editor";
            }
            #endregion #InsertHyperlink
        }

        #region #Events
        private void checkEdit1_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit1.Checked == false)
            {
                hyperlinkOptions.ShowToolTip = false;
            }
            else
            {
                hyperlinkOptions.ShowToolTip = true;
            }
        }

        private void checkEdit2_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit2.Checked == false)
            {
                hyperlinkOptions.EnableUriCorrection = false;
            }
            else
            {
                hyperlinkOptions.EnableUriCorrection = true;
            }

        }

        private void checkEdit4_ColorChanged(object sender, EventArgs e)
        {
            bookmarkOptions.Color = checkEdit4.Color;
        }

        private void checkEdit5_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit5.Checked == true)
            {
                bookmarkOptions.Visibility = RichEditBookmarkVisibility.Visible;
            }
            else
            {
                bookmarkOptions.Visibility = RichEditBookmarkVisibility.Auto;
            }
        }


        private void checkEdit3_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit3.CheckState == CheckState.Checked)
            {
                checkEdit6.CheckState = CheckState.Unchecked;
                checkEdit7.CheckState = CheckState.Unchecked;
                hyperlinkOptions.ModifierKeys = PortableKeys.Control;

            }
            else
                hyperlinkOptions.ModifierKeys = PortableKeys.None;
        }

        private void checkEdit6_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit6.CheckState == CheckState.Checked)
            {
                checkEdit3.CheckState = CheckState.Unchecked;
                checkEdit7.CheckState = CheckState.Unchecked;
                hyperlinkOptions.ModifierKeys = PortableKeys.Alt;

            }
            else
                hyperlinkOptions.ModifierKeys = PortableKeys.None;

        }

        private void checkEdit7_CheckedChanged(object sender, EventArgs e)
        {
            if (checkEdit7.CheckState == CheckState.Checked)
            {
                checkEdit6.CheckState = CheckState.Unchecked;
                checkEdit3.CheckState = CheckState.Unchecked;

                hyperlinkOptions.ModifierKeys = PortableKeys.Shift;

            }
            else
                hyperlinkOptions.ModifierKeys = PortableKeys.None;

        }
        #endregion #Events
    }
}
