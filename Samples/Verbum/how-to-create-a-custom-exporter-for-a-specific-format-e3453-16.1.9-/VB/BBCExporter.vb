Imports Microsoft.VisualBasic
Imports System
Imports System.IO
Imports System.Text
Imports DevExpress.Utils
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.Export
Imports DevExpress.XtraRichEdit.Internal
Imports DevExpress.XtraRichEdit.Model
Imports System.Drawing
Imports DevExpress.Office
Imports DevExpress.Office.Export
Imports DevExpress.Office.Internal
Imports DevExpress.XtraRichEdit.API.Native.Implementation

Namespace RichEditBBCExporter
	Public Class BBCodeDocumentExporter
		Implements IExporter(Of DocumentFormat, Boolean)
		Friend Shared ReadOnly filter_Renamed As New FileDialogFilter("Bulletin Board Code", "bbc")

        Public ReadOnly Property Filter() As FileDialogFilter Implements IExporter(Of DevExpress.XtraRichEdit.DocumentFormat, Boolean).Filter
            Get
                Return filter_Renamed
            End Get
        End Property
        Public ReadOnly Property Format() As DocumentFormat Implements IExporter(Of DevExpress.XtraRichEdit.DocumentFormat, Boolean).Format
            Get
                Return BBCodeDocumentFormat.Id
            End Get
        End Property
        Public Function SetupSaving() As IExporterOptions Implements IExporter(Of DevExpress.XtraRichEdit.DocumentFormat, Boolean).SetupSaving
            Return New BBCodeDocumentExporterOptions()
        End Function

        Public Function SaveDocument(ByVal documentModel As IDocumentModel, ByVal stream As Stream, ByVal options As IExporterOptions) As Boolean Implements IExporter(Of DevExpress.XtraRichEdit.DocumentFormat, Boolean).SaveDocument
            Dim exporter As New BBCodeExporter(CType(documentModel, DocumentModel), CType(options, BBCodeDocumentExporterOptions))
            exporter.Export(stream)
            Return True
        End Function

		Public Shared Sub Register(ByVal provider As IServiceProvider)
			If provider Is Nothing Then
				Return
			End If
			Dim service As IDocumentExportManagerService = TryCast(provider.GetService(GetType(IDocumentExportManagerService)), IDocumentExportManagerService)
			If service IsNot Nothing Then
				service.RegisterExporter(New BBCodeDocumentExporter())
			End If
		End Sub
	End Class

	Public Class BBCodeDocumentExporterOptions
		Inherits DocumentExporterOptions
		Protected Overrides ReadOnly Property Format() As DocumentFormat
			Get
				Return BBCodeDocumentFormat.Id
			End Get
		End Property
	End Class

	Public Class BBCodeExporter
		Inherits DocumentModelExporter
		Private ReadOnly options_Renamed As BBCodeDocumentExporterOptions
		Private outputStream As Stream
		Private documentContentWriter_Renamed As StreamWriter
		Private hyperlinkExporting As Boolean

		Public Sub New(ByVal documentModel As DocumentModel, ByVal options As BBCodeDocumentExporterOptions)
			MyBase.New(documentModel)
			Guard.ArgumentNotNull(options, "options")
			Me.options_Renamed = options
		End Sub

		Protected ReadOnly Property Options() As BBCodeDocumentExporterOptions
			Get
				Return options_Renamed
			End Get
		End Property
		Protected Friend Property DocumentContentWriter() As StreamWriter
			Get
				Return documentContentWriter_Renamed
			End Get
			Set(ByVal value As StreamWriter)
				documentContentWriter_Renamed = value
			End Set
		End Property

        Public Overridable Shadows Sub Export(ByVal outputStream As Stream)
            Me.outputStream = outputStream
            Using streamWriter As New StreamWriter(outputStream, Encoding.UTF8)
                DocumentContentWriter = streamWriter
                MyBase.Export()
                streamWriter.Flush()
            End Using
        End Sub

        Protected Overrides Sub ExportTextRun(ByVal run As TextRun)
            Dim text As String = run.GetPlainText(PieceTable.TextBuffer)

            If (Not hyperlinkExporting) Then
                If run.FontBold Then
                    DocumentContentWriter.Write("[b]")
                End If
                If run.FontItalic Then
                    DocumentContentWriter.Write("[i]")
                End If
                If run.FontUnderlineType <> UnderlineType.None Then
                    DocumentContentWriter.Write("[u]")
                End If
                If run.FontStrikeoutType <> StrikeoutType.None Then
                    DocumentContentWriter.Write("[s]")
                End If
                If run.ForeColorIndex <> DevExpress.Office.Model.ColorModelInfoCache.EmptyColorIndex Then
                    DocumentContentWriter.Write(String.Format("[color=#{0}]", ColorTranslator.ToHtml(DocumentModel.GetColor(run.ForeColorIndex))))
                End If
                If run.DoubleFontSize <> DocumentModel.DefaultCharacterProperties.DoubleFontSize Then
                    DocumentContentWriter.Write(String.Format("[size={0}]", Math.Min(run.DoubleFontSize, 39)))
                End If
            End If

            DocumentContentWriter.Write(text)

            If (Not hyperlinkExporting) Then
                If run.DoubleFontSize <> DocumentModel.DefaultCharacterProperties.DoubleFontSize Then
                    DocumentContentWriter.Write("[/size]")
                End If
                If run.ForeColorIndex <> DevExpress.Office.Model.ColorModelInfoCache.EmptyColorIndex Then
                    DocumentContentWriter.Write("[/color]")
                End If
                If run.FontStrikeoutType <> StrikeoutType.None Then
                    DocumentContentWriter.Write("[/s]")
                End If
                If run.FontUnderlineType <> UnderlineType.None Then
                    DocumentContentWriter.Write("[/u]")
                End If
                If run.FontBold Then
                    DocumentContentWriter.Write("[/b]")
                End If
                If run.FontItalic Then
                    DocumentContentWriter.Write("[/i]")
                End If
            End If

            MyBase.ExportTextRun(run)
        End Sub

        Protected Overrides Sub ExportFieldCodeStartRun(ByVal run As FieldCodeStartRun)
            MyBase.ExportFieldCodeStartRun(run)
            Dim hyperlinkInfo As HyperlinkInfo = GetHyperlinkInfo(run)
            If hyperlinkInfo Is Nothing Then
                Return
            End If

            DocumentContentWriter.Write(String.Format("[url={0}]", hyperlinkInfo.NavigateUri))
            hyperlinkExporting = True
        End Sub

        Protected Overrides Sub ExportFieldResultEndRun(ByVal run As FieldResultEndRun)
            MyBase.ExportFieldResultEndRun(run)
            If GetHyperlinkInfo(run) Is Nothing Then
                Return
            End If

            DocumentContentWriter.Write("[/url]")
            hyperlinkExporting = False
        End Sub

        Protected Overrides Sub ExportInlinePictureRun(ByVal run As InlinePictureRun)
            DocumentContentWriter.Write(String.Format("[img]{0}[/img]", run.Image.Uri))
            MyBase.ExportInlinePictureRun(run)
        End Sub

        Protected Overrides Function ExportParagraph(ByVal paragraph As Paragraph) As ParagraphIndex
            Dim pi As ParagraphIndex = MyBase.ExportParagraph(paragraph)
            DocumentContentWriter.Write(Environment.NewLine)
            Return pi
        End Function

        Private Function GetHyperlinkInfo(ByVal run As TextRun) As HyperlinkInfo
            Dim runIndex As RunIndex = run.GetRunIndex()
            Dim field As Field = PieceTable.FindFieldByRunIndex(runIndex)
            System.Diagnostics.Debug.Assert(field IsNot Nothing)
            Dim hyperlinkInfo As HyperlinkInfo = Nothing
            If PieceTable.HyperlinkInfos.TryGetHyperlinkInfo(field.Index, hyperlinkInfo) Then
                Return hyperlinkInfo
            End If
            Return Nothing
        End Function
    End Class

	Public NotInheritable Class BBCodeDocumentFormat
		Public Shared ReadOnly Id As New DocumentFormat(431)
	End Class
End Namespace
