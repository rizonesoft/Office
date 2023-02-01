Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.IO
Imports System.Linq
Imports System.Text
Imports DevExpress.Utils.Zip
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Services

Namespace RichEditControlExtensions
	Public Module RichEditLoadDocumentHelper
		Private Const P As Byte = CByte(AscW("P"c))
		Private Const K As Byte = CByte(AscW("K"c))

        Private ReadOnly docSignature() As Byte = {&HD0, &HCF, &H11, &HE0, &HA1, &HB1, &H1A, &HE1}

        <System.Runtime.CompilerServices.Extension> _
        Public Sub RegisterCusomOpenFileCommand(ByVal richEdit As RichEditControl)
            Dim commandFactory As New CustomRichEditCommandFactoryService(richEdit, richEdit.GetService(Of IRichEditCommandFactoryService)())
            richEdit.RemoveService(GetType(IRichEditCommandFactoryService))
            richEdit.AddService(GetType(IRichEditCommandFactoryService), commandFactory)
        End Sub

        <System.Runtime.CompilerServices.Extension> _
        Public Sub LoadDocumentEx(ByVal richEdit As IRichEditControl, ByVal stream As Stream)
            Dim currentFormat As DevExpress.XtraRichEdit.DocumentFormat = AutoDetermineDocumentFormat(stream)
            stream.Seek(0, SeekOrigin.Begin)
            richEdit.InnerControl.LoadDocument(stream, currentFormat)
        End Sub

        <System.Runtime.CompilerServices.Extension> _
        Public Sub LoadDocumentEx(ByVal richEdit As IRichEditControl, ByVal fileName As String)
            Using fs As System.IO.FileStream = New FileStream(fileName, System.IO.FileMode.Open)
                richEdit.LoadDocumentEx(fs)
            End Using
        End Sub

        Public Function AutoDetermineDocumentFormat(ByVal stream As Stream) As DevExpress.XtraRichEdit.DocumentFormat
            Dim buffer(7) As Byte

            If stream.Length < 8 Then
                Return DevExpress.XtraRichEdit.DocumentFormat.PlainText
            End If
            stream.Read(buffer, 0, buffer.Length)

            If buffer.SequenceEqual(docSignature) Then
                Return DevExpress.XtraRichEdit.DocumentFormat.Doc

            ElseIf buffer(0) = P AndAlso buffer(1) = K Then
                Return CheckZippedFileContent(stream)
            End If

            Dim fileBeginning As String = Encoding.ASCII.GetString(buffer)
            If fileBeginning.Contains("{\rtf") Then
                Return DevExpress.XtraRichEdit.DocumentFormat.Rtf
            End If
            If fileBeginning.Contains("<!") Then
                Return DevExpress.XtraRichEdit.DocumentFormat.Html
            End If

            Return DevExpress.XtraRichEdit.DocumentFormat.PlainText
        End Function

        Private Function CheckZippedFileContent(ByVal stream As Stream) As DevExpress.XtraRichEdit.DocumentFormat
            stream.Seek(0, SeekOrigin.Begin)
            Dim files As InternalZipFileCollection = InternalZipArchive.Open(stream)
            For Each entry As InternalZipFile In files
                If entry.FileName.Contains(".rels") OrElse entry.FileName.Contains("document.xml") Then
                    Return DevExpress.XtraRichEdit.DocumentFormat.OpenXml
                End If
                If entry.FileName.Contains("content.xml") Then
                    Return DevExpress.XtraRichEdit.DocumentFormat.OpenDocument
                End If
            Next entry
            Return DevExpress.XtraRichEdit.DocumentFormat.PlainText
        End Function
	End Module
End Namespace
