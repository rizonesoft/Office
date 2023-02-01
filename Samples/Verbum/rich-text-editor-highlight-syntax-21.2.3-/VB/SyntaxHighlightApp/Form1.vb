Imports System.Collections.Generic
Imports System.Diagnostics
Imports System.Drawing
Imports DevExpress.CodeParser
Imports DevExpress.LookAndFeel
Imports DevExpress.Skins
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Services

Namespace SyntaxHighlightApp

    Public Partial Class Form1
        Inherits DevExpress.XtraEditors.XtraForm

        Public Sub New()
            Dim path As String = "Form1.vb"
            InitializeComponent()
            ' Use service substitution to register a custom service that implements syntax highlighting.
            richEditControl1.ReplaceService(Of ISyntaxHighlightService)(New MySyntaxHighlightService(richEditControl1))
            richEditControl1.LoadDocument(path)
        End Sub
    End Class

    ''' <summary>
    '''  This class implements the Execute method of the ISyntaxHighlightService interface to parse and colorize text.
    ''' </summary>
    Public Class MySyntaxHighlightService
        Implements ISyntaxHighlightService

        Private ReadOnly syntaxEditor As RichEditControl

        Private syntaxColors As SyntaxColors

        Private commentProperties As SyntaxHighlightProperties

        Private keywordProperties As SyntaxHighlightProperties

        Private stringProperties As SyntaxHighlightProperties

        Private xmlCommentProperties As SyntaxHighlightProperties

        Private textProperties As SyntaxHighlightProperties

        Public Sub New(ByVal syntaxEditor As RichEditControl)
            Me.syntaxEditor = syntaxEditor
            syntaxColors = New SyntaxColors(UserLookAndFeel.Default)
        End Sub

        Private Sub HighlightSyntax(ByVal tokens As TokenCollection)
            commentProperties = New SyntaxHighlightProperties()
            commentProperties.ForeColor = syntaxColors.CommentColor
            keywordProperties = New SyntaxHighlightProperties()
            keywordProperties.ForeColor = syntaxColors.KeywordColor
            stringProperties = New SyntaxHighlightProperties()
            stringProperties.ForeColor = syntaxColors.StringColor
            xmlCommentProperties = New SyntaxHighlightProperties()
            xmlCommentProperties.ForeColor = syntaxColors.XmlCommentColor
            textProperties = New SyntaxHighlightProperties()
            textProperties.ForeColor = syntaxColors.TextColor
            Dim document As Document = syntaxEditor.Document
            Dim syntaxTokens As List(Of SyntaxHighlightToken) = New List(Of SyntaxHighlightToken)(tokens.Count)
            For Each token As Token In tokens
                Dim categorizedToken = TryCast(token, CategorizedToken)
                If categorizedToken IsNot Nothing Then HighlightCategorizedToken(categorizedToken, syntaxTokens)
            Next

            If syntaxTokens.Count > 0 Then
                document.ApplySyntaxHighlight(syntaxTokens)
            End If
        End Sub

        Private Sub HighlightCategorizedToken(ByVal token As CategorizedToken, ByVal syntaxTokens As List(Of SyntaxHighlightToken))
            Dim backColor As Color = syntaxEditor.ActiveView.BackColor
            Dim category As TokenCategory = token.Category
            Select Case category
                Case TokenCategory.Comment
                    syntaxTokens.Add(SetTokenColor(token, commentProperties, backColor))
                Case TokenCategory.Keyword
                    syntaxTokens.Add(SetTokenColor(token, keywordProperties, backColor))
                Case TokenCategory.String
                    syntaxTokens.Add(SetTokenColor(token, stringProperties, backColor))
                Case TokenCategory.XmlComment
                    syntaxTokens.Add(SetTokenColor(token, xmlCommentProperties, backColor))
                Case Else
                    syntaxTokens.Add(SetTokenColor(token, textProperties, backColor))
            End Select
        End Sub

        Private Function SetTokenColor(ByVal token As Token, ByVal foreColor As SyntaxHighlightProperties, ByVal backColor As Color) As SyntaxHighlightToken
            If syntaxEditor.Document.Paragraphs.Count < token.Range.Start.Line Then Return Nothing
            Dim paragraphStart As Integer = syntaxEditor.Document.Paragraphs(token.Range.Start.Line - 1).Range.Start.ToInt()
            Dim tokenStart As Integer = paragraphStart + token.Range.Start.Offset - 1
            If token.Range.End.Line <> token.Range.Start.Line Then paragraphStart = syntaxEditor.Document.Paragraphs(token.Range.End.Line - 1).Range.Start.ToInt()
            Dim tokenEnd As Integer = paragraphStart + token.Range.End.Offset - 1
            Call Debug.Assert(tokenEnd > tokenStart)
            Return New SyntaxHighlightToken(tokenStart, tokenEnd - tokenStart, foreColor)
        End Function

#Region "#ISyntaxHighlightServiceMembers"
        Public Sub Execute() Implements ISyntaxHighlightService.Execute
            Dim newText As String = syntaxEditor.Text
            ' Determine the language by file extension.
            Dim ext As String = System.IO.Path.GetExtension(syntaxEditor.Options.DocumentSaveOptions.CurrentFileName)
            Dim lang_ID As ParserLanguageID = ParserLanguage.FromFileExtension(ext)
            ' Do not parse HTML or XML.
            If lang_ID = ParserLanguageID.Html OrElse lang_ID = ParserLanguageID.Xml OrElse lang_ID = ParserLanguageID.None Then Return
            ' Use DevExpress.CodeParser to parse text into tokens.
            Dim tokenHelper As ITokenCategoryHelper = TokenCategoryHelperFactory.CreateHelper(lang_ID)
            If tokenHelper IsNot Nothing Then
                Dim highlightTokens As TokenCollection = tokenHelper.GetTokens(newText)
                If highlightTokens IsNot Nothing AndAlso highlightTokens.Count > 0 Then
                    HighlightSyntax(highlightTokens)
                End If
            End If
        End Sub

        Public Sub ForceExecute() Implements ISyntaxHighlightService.ForceExecute
            Execute()
        End Sub
#End Region  ' #ISyntaxHighlightServiceMembers
    End Class

    ''' <summary>
    '''  This class defines colors to highlight tokens.
    ''' </summary>
    Public Class SyntaxColors

        Private Shared ReadOnly Property DefaultCommentColor As Color
            Get
                Return Color.Green
            End Get
        End Property

        Private Shared ReadOnly Property DefaultKeywordColor As Color
            Get
                Return Color.Blue
            End Get
        End Property

        Private Shared ReadOnly Property DefaultStringColor As Color
            Get
                Return Color.Brown
            End Get
        End Property

        Private Shared ReadOnly Property DefaultXmlCommentColor As Color
            Get
                Return Color.Gray
            End Get
        End Property

        Private Shared ReadOnly Property DefaultTextColor As Color
            Get
                Return Color.Black
            End Get
        End Property

        Private lookAndFeel As UserLookAndFeel

        Public ReadOnly Property CommentColor As Color
            Get
                Return GetCommonColorByName(CommonSkins.SkinInformationColor, DefaultCommentColor)
            End Get
        End Property

        Public ReadOnly Property KeywordColor As Color
            Get
                Return GetCommonColorByName(CommonSkins.SkinQuestionColor, DefaultKeywordColor)
            End Get
        End Property

        Public ReadOnly Property TextColor As Color
            Get
                Return GetCommonColorByName(CommonColors.WindowText, DefaultTextColor)
            End Get
        End Property

        Public ReadOnly Property XmlCommentColor As Color
            Get
                Return GetCommonColorByName(CommonColors.DisabledText, DefaultXmlCommentColor)
            End Get
        End Property

        Public ReadOnly Property StringColor As Color
            Get
                Return GetCommonColorByName(CommonSkins.SkinWarningColor, DefaultStringColor)
            End Get
        End Property

        Public Sub New(ByVal lookAndFeel As UserLookAndFeel)
            Me.lookAndFeel = lookAndFeel
        End Sub

        Private Function GetCommonColorByName(ByVal colorName As String, ByVal defaultColor As Color) As Color
            Dim skin As Skin = CommonSkins.GetSkin(lookAndFeel)
            If skin Is Nothing Then Return defaultColor
            Return skin.Colors(colorName)
        End Function
    End Class
End Namespace
