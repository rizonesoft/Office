using System;
using System.IO;
using System.Drawing;
using System.Reflection;
using System.Globalization;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.Office.NumberConverters;

namespace Expander
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.CreateNewDocument();
        }

        private Image CreateImageFromResx(string name)
        {
            Image im;
            Assembly assembly = Assembly.GetExecutingAssembly();
            using (Stream stream = assembly.GetManifestResourceStream("Expander.Images." + name)) {
                im = Image.FromStream(stream);
            }
            return im;
        }
        #region #autocorrect
        private void richEditControl1_AutoCorrect(object sender, DevExpress.XtraRichEdit.AutoCorrectEventArgs e)
        {
            AutoCorrectInfo info = e.AutoCorrectInfo;
            e.AutoCorrectInfo = null;

            if (info.Text.Length <= 0)
                return;
            for (; ; ) {
                if (!info.DecrementStartPosition())
                    return;

                if (IsSeparator(info.Text[0]))
                    return;

                if (info.Text[0] == '$') {
                    info.ReplaceWith = CreateImageFromResx("dollar_pic.png");
                    e.AutoCorrectInfo = info;
                    return;
                } 

                if (info.Text[0] == '%') {
                    string replaceString = CalculateFunction(info.Text);
                    if (!String.IsNullOrEmpty(replaceString)) {
                        info.ReplaceWith = replaceString;
                        e.AutoCorrectInfo = info;
                    }
                    return;
                }
            }
        }
        #endregion #autocorrect
        string CalculateFunction(string name)
        {
            name = name.ToLower();

            if (name.Length > 2 && name[0] == '%' && name.EndsWith("%")) {
                int value;
                if (Int32.TryParse(name.Substring(1, name.Length - 2), out value)) {
                    OrdinalBasedNumberConverter converter = OrdinalBasedNumberConverter.CreateConverter(NumberingFormat.CardinalText, LanguageId.English);
                    return converter.ConvertNumber(value);
                }
            }

            switch (name) {
                case "%date%":
                    return DateTime.Now.ToString(CultureInfo.CurrentCulture.DateTimeFormat.ShortDatePattern);
                case "%time%":
                    return DateTime.Now.ToString(CultureInfo.CurrentCulture.DateTimeFormat.ShortTimePattern);
                default:
                    return String.Empty;
            }
        }
        bool IsSeparator(char ch)
        {
            return ch != '%' && (ch == '\r' || ch == '\n' || Char.IsPunctuation(ch) || Char.IsSeparator(ch) || Char.IsWhiteSpace(ch));
        }
    }
}