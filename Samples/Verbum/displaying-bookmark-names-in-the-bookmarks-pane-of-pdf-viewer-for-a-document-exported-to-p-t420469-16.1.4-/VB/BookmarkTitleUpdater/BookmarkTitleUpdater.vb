Imports DevExpress.XtraRichEdit.Services

Namespace BookmarkTitleUpdater
    Public Class BookmarkTitleUpdater
        Implements ILinkUpdater

        Public Function ResolveBookmarkTitle(ByVal bookmarkName As String, ByVal currentTitle As String) As String Implements ILinkUpdater.ResolveBookmarkTitle
            Return bookmarkName
        End Function

        Public Function UpdateLinkToPage(ByVal uri As String, ByVal anchor As String) As String Implements ILinkUpdater.UpdateLinkToPage
            Return anchor
        End Function

        Public Function UpdateLinkToUri(ByVal uri As String) As String Implements ILinkUpdater.UpdateLinkToUri
            Return uri
        End Function
    End Class
End Namespace
