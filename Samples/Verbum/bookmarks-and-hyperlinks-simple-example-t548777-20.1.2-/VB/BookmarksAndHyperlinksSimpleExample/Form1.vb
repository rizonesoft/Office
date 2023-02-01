Imports DevExpress.XtraBars.Ribbon
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit
Imports DevExpress.Portable.Input

Namespace BookmarksAndHyperlinksSimpleExample
    Partial Public Class Form1
        Inherits RibbonForm

        Private hyperlinkOptions As HyperlinkOptions
        Private bookmarkOptions As BookmarkOptions
        Public Sub New()
            InitializeComponent()
        End Sub

        Private Sub Form1_Load(ByVal sender As Object, ByVal e As EventArgs) Handles MyBase.Load
            richEditControl1.LoadDocument("Hyperlinks.docx")
            InsertHyperlink()
            InsertBookmark()

            '            #Region "#HyperlinkOptions"
            hyperlinkOptions = richEditControl1.Options.Hyperlinks

            hyperlinkOptions.EnableUriCorrection = False
            hyperlinkOptions.ModifierKeys = PortableKeys.Shift
            hyperlinkOptions.ShowToolTip = True
            '            #End Region ' #Hyperlinkoptions

            '            #Region "#BookmarkOptions"
            bookmarkOptions = richEditControl1.Options.Bookmarks
            bookmarkOptions.ConflictNameResolution = ConflictNameAction.Rename
            bookmarkOptions.Visibility = RichEditBookmarkVisibility.Hidden
            '            #End Region ' #BookmarkOptions
        End Sub

        Private Sub InsertBookmark()
            '            #Region "#InsertBookmark"
            Dim document As Document = richEditControl1.Document
            document.BeginUpdate()
            Dim pos As DocumentPosition = document.Range.Start

            'Create a bookmark to a given position
            document.Bookmarks.Create(document.CreateRange(pos, 1), "Top")

            'Insert the hyperlink anchored to the created bookmark:
            Dim foundRanges() As DocumentRange = document.FindAll("To the Top", SearchOptions.CaseSensitive)
            If foundRanges.Length > 0 Then
                document.Hyperlinks.Create(foundRanges(0))
                document.Hyperlinks(1).Anchor = "Top"
            End If
            document.EndUpdate()
            '            #End Region ' #InsertBookmark
        End Sub

        Private Sub InsertHyperlink()
            '            #Region "#InsertHyperlink"
            Dim document As Document = richEditControl1.Document

            'Find the specific text string in a document
            Dim foundRanges() As DocumentRange = document.FindAll("DevExpress WinForms Rich Text Editor", SearchOptions.CaseSensitive)
            If foundRanges.Length > 0 Then
                'Create a hyperlink from a found range
                document.Hyperlinks.Create(foundRanges(0))

                'Set the URI and the tooltip for the created hyperlink
                document.Hyperlinks(0).NavigateUri = "https://www.devexpress.com/Products/NET/Controls/WinForms/Rich_Editor/"
                document.Hyperlinks(0).ToolTip = "WinForms Rich Text Editor"
            End If
            '            #End Region ' #InsertHyperlink
        End Sub

#Region "#Events"
        Private Sub checkEdit1_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit1.CheckedChanged
            If checkEdit1.Checked = False Then
                hyperlinkOptions.ShowToolTip = False
            Else
                hyperlinkOptions.ShowToolTip = True
            End If
        End Sub

        Private Sub checkEdit2_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit2.CheckedChanged
            If checkEdit2.Checked = False Then
                hyperlinkOptions.EnableUriCorrection = False
            Else
                hyperlinkOptions.EnableUriCorrection = True
            End If

        End Sub

        Private Sub checkEdit4_ColorChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit4.ColorChanged
            bookmarkOptions.Color = checkEdit4.Color
        End Sub

        Private Sub checkEdit5_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit5.CheckedChanged
            If checkEdit5.Checked = True Then
                bookmarkOptions.Visibility = RichEditBookmarkVisibility.Visible
            Else
                bookmarkOptions.Visibility = RichEditBookmarkVisibility.Auto
            End If
        End Sub


        Private Sub checkEdit3_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit3.CheckedChanged
            If checkEdit3.CheckState = CheckState.Checked Then
                checkEdit6.CheckState = CheckState.Unchecked
                checkEdit7.CheckState = CheckState.Unchecked
                hyperlinkOptions.ModifierKeys = PortableKeys.Control

            Else
                hyperlinkOptions.ModifierKeys = PortableKeys.None
            End If
        End Sub

        Private Sub checkEdit6_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit6.CheckedChanged
            If checkEdit6.CheckState = CheckState.Checked Then
                checkEdit3.CheckState = CheckState.Unchecked
                checkEdit7.CheckState = CheckState.Unchecked
                hyperlinkOptions.ModifierKeys = PortableKeys.Alt

            Else
                hyperlinkOptions.ModifierKeys = PortableKeys.None
            End If

        End Sub

        Private Sub checkEdit7_CheckedChanged(ByVal sender As Object, ByVal e As EventArgs) Handles checkEdit7.CheckedChanged
            If checkEdit7.CheckState = CheckState.Checked Then
                checkEdit6.CheckState = CheckState.Unchecked
                checkEdit3.CheckState = CheckState.Unchecked

                hyperlinkOptions.ModifierKeys = PortableKeys.Shift

            Else
                hyperlinkOptions.ModifierKeys = PortableKeys.None
            End If

        End Sub
#End Region ' #Events
    End Class
End Namespace
