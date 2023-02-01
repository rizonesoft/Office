Imports System
Imports System.IO
Imports System.Diagnostics
Imports System.Collections.Generic
Imports DevExpress.Office
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Services
Imports DevExpress.XtraRichEdit.API.Native

Namespace LinkUpdater
    Friend Class Program
        Shared Sub Main(ByVal args() As String)
            Dim server As New RichEditDocumentServer()
            ' Create an instance of the class implementing the IPdfLinkUpdater interface.
            Dim linkUpdater As New LinkUpdater()
            server.AddService(GetType(ILinkUpdater), linkUpdater)
            RegisterAnchor(server.Document, linkUpdater, "1.html")
            server.Document.AppendText(New String(Characters.PageBreak, 1))
            RegisterAnchor(server.Document, linkUpdater, "2.html")
            ' Export the document to PDF and open the resultant file.
            Dim resultPath As String = "..\..\result.pdf"
            Using stream As Stream = File.Create(resultPath)
                server.ExportToPdf(stream)
            End Using
            Process.Start(Path.GetFullPath(resultPath))
        End Sub

        Private Shared Sub RegisterAnchor(ByVal doc As Document, ByVal linkUpdater As LinkUpdater, ByVal uri As String)
            Dim guid As String = System.Guid.NewGuid().ToString()
            ' Create a bookmark that will be the target of the hyperlink.
            doc.Bookmarks.Create(doc.CaretPosition, 0, guid)
            ' Redirect the URI to the bookmark within the document.
            linkUpdater.RedirectUri(uri, guid)
            ' Appends the content of the specified HTML file to the document.  
            doc.AppendDocumentContent(String.Format("..\..\html\{0}", uri), DocumentFormat.Html)
        End Sub
    End Class

    Friend Class LinkUpdater
        Implements ILinkUpdater

        Private ReadOnly map As New Dictionary(Of String, String)()
        Public Function ResolveBookmarkTitle(ByVal bookmarkName As String, ByVal currentTitle As String) As String Implements ILinkUpdater.ResolveBookmarkTitle
            Return currentTitle
        End Function
        Public Sub RedirectUri(ByVal uri As String, ByVal anchor As String)
            map(uri) = anchor
        End Sub

        Public Function UpdateLinkToPage(ByVal uri As String, ByVal anchor As String) As String Implements ILinkUpdater.UpdateLinkToPage
            Dim newAnchor As String = Nothing
            If map.TryGetValue(uri, newAnchor) Then
                Return newAnchor
            End If
            Return anchor
        End Function
        Public Function UpdateLinkToUri(ByVal uri As String) As String Implements ILinkUpdater.UpdateLinkToUri
            If map.ContainsKey(uri) Then
                Return String.Empty
            End If
            Return uri
        End Function
    End Class
End Namespace
