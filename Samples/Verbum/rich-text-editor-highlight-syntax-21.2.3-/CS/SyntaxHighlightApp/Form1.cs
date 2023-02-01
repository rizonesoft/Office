using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using DevExpress.CodeParser;
using DevExpress.LookAndFeel;
using DevExpress.Skins;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Services;

namespace SyntaxHighlightApp
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm
    {
        public Form1()
        {
            string path = "Form1.cs";
            InitializeComponent();
            // Use service substitution to register a custom service that implements syntax highlighting.
            richEditControl1.ReplaceService<ISyntaxHighlightService>(new MySyntaxHighlightService(richEditControl1));
            richEditControl1.LoadDocument(path);
        }
    }
    /// <summary>
    ///  This class implements the Execute method of the ISyntaxHighlightService interface to parse and colorize text.
    /// </summary>
    public class MySyntaxHighlightService : ISyntaxHighlightService
    {
        readonly RichEditControl syntaxEditor;
        SyntaxColors syntaxColors;
        SyntaxHighlightProperties commentProperties;
        SyntaxHighlightProperties keywordProperties;
        SyntaxHighlightProperties stringProperties;
        SyntaxHighlightProperties xmlCommentProperties;
        SyntaxHighlightProperties textProperties;

        public MySyntaxHighlightService(RichEditControl syntaxEditor)
        {
            this.syntaxEditor = syntaxEditor;
            syntaxColors = new SyntaxColors(UserLookAndFeel.Default);
        }

        void HighlightSyntax(TokenCollection tokens)
        {
            commentProperties = new SyntaxHighlightProperties();
            commentProperties.ForeColor = syntaxColors.CommentColor;

            keywordProperties = new SyntaxHighlightProperties();
            keywordProperties.ForeColor = syntaxColors.KeywordColor;

            stringProperties = new SyntaxHighlightProperties();
            stringProperties.ForeColor = syntaxColors.StringColor;

            xmlCommentProperties = new SyntaxHighlightProperties();
            xmlCommentProperties.ForeColor = syntaxColors.XmlCommentColor;

            textProperties = new SyntaxHighlightProperties();
            textProperties.ForeColor = syntaxColors.TextColor;

            Document document = syntaxEditor.Document;
            List<SyntaxHighlightToken> syntaxTokens = new List<SyntaxHighlightToken>(tokens.Count);
            foreach (Token token in tokens)
            {
                var categorizedToken = token as CategorizedToken;
                if (categorizedToken != null)
                    HighlightCategorizedToken(categorizedToken, syntaxTokens);
            }
            if (syntaxTokens.Count > 0) 
            {
                document.ApplySyntaxHighlight(syntaxTokens);
            }
        }
        void HighlightCategorizedToken(CategorizedToken token, List<SyntaxHighlightToken> syntaxTokens)
        {
            Color backColor = syntaxEditor.ActiveView.BackColor;
            TokenCategory category = token.Category;           
            switch (category)
            {
                case TokenCategory.Comment:
                    syntaxTokens.Add(SetTokenColor(token, commentProperties, backColor));
                    break;
                case TokenCategory.Keyword:
                    syntaxTokens.Add(SetTokenColor(token, keywordProperties, backColor));
                    break;
                case TokenCategory.String:
                    syntaxTokens.Add(SetTokenColor(token, stringProperties, backColor));
                    break;
                case TokenCategory.XmlComment:
                    syntaxTokens.Add(SetTokenColor(token, xmlCommentProperties, backColor));
                    break;
                default:
                    syntaxTokens.Add(SetTokenColor(token, textProperties, backColor));
                    break;
            }
        }
        SyntaxHighlightToken SetTokenColor(Token token, SyntaxHighlightProperties foreColor, Color backColor)
        {
            if (syntaxEditor.Document.Paragraphs.Count < token.Range.Start.Line)
                return null;
            int paragraphStart = syntaxEditor.Document.Paragraphs[token.Range.Start.Line - 1].Range.Start.ToInt();
            int tokenStart = paragraphStart + token.Range.Start.Offset - 1;
            if (token.Range.End.Line != token.Range.Start.Line)
                paragraphStart = syntaxEditor.Document.Paragraphs[token.Range.End.Line - 1].Range.Start.ToInt();

            int tokenEnd = paragraphStart + token.Range.End.Offset - 1;
            Debug.Assert(tokenEnd > tokenStart);
            return new SyntaxHighlightToken(tokenStart, tokenEnd - tokenStart, foreColor);
        }

        #region #ISyntaxHighlightServiceMembers
        public void Execute()
        {
            string newText = syntaxEditor.Text;
            // Determine the language by file extension.
            string ext = System.IO.Path.GetExtension(syntaxEditor.Options.DocumentSaveOptions.CurrentFileName);
            ParserLanguageID lang_ID = ParserLanguage.FromFileExtension(ext);
            // Do not parse HTML or XML.
            if (lang_ID == ParserLanguageID.Html ||
                lang_ID == ParserLanguageID.Xml ||
                lang_ID == ParserLanguageID.None) return;
            // Use DevExpress.CodeParser to parse text into tokens.
            ITokenCategoryHelper tokenHelper = TokenCategoryHelperFactory.CreateHelper(lang_ID);
            if (tokenHelper != null) 
            { 
                TokenCollection highlightTokens = tokenHelper.GetTokens(newText);
                if (highlightTokens != null && highlightTokens.Count > 0) 
                {
                    HighlightSyntax(highlightTokens);
                }
                
            }
        }

        public void ForceExecute()
        {
            Execute();
        }
        #endregion #ISyntaxHighlightServiceMembers
    }
    /// <summary>
    ///  This class defines colors to highlight tokens.
    /// </summary>
    public class SyntaxColors
    {
        static Color DefaultCommentColor { get { return Color.Green; } }
        static Color DefaultKeywordColor { get { return Color.Blue; } }
        static Color DefaultStringColor { get { return Color.Brown; } }
        static Color DefaultXmlCommentColor { get { return Color.Gray; } }
        static Color DefaultTextColor { get { return Color.Black; } }
        UserLookAndFeel lookAndFeel;

        public Color CommentColor { get { return GetCommonColorByName(CommonSkins.SkinInformationColor, DefaultCommentColor); } }
        public Color KeywordColor { get { return GetCommonColorByName(CommonSkins.SkinQuestionColor, DefaultKeywordColor); } }
        public Color TextColor { get { return GetCommonColorByName(CommonColors.WindowText, DefaultTextColor); } }
        public Color XmlCommentColor { get { return GetCommonColorByName(CommonColors.DisabledText, DefaultXmlCommentColor); } }
        public Color StringColor { get { return GetCommonColorByName(CommonSkins.SkinWarningColor, DefaultStringColor); } }

        public SyntaxColors(UserLookAndFeel lookAndFeel)
        {
            this.lookAndFeel = lookAndFeel;
        }

        Color GetCommonColorByName(string colorName, Color defaultColor)
        {
            Skin skin = CommonSkins.GetSkin(lookAndFeel);
            if (skin == null)
                return defaultColor;
            return skin.Colors[colorName];
        }
    }
}
