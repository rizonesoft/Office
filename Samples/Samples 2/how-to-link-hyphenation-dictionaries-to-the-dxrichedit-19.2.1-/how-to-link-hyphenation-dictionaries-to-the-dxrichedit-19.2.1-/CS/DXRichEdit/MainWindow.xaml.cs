using DevExpress.Xpf.Core;
using DevExpress.XtraRichEdit.API.Native;
using System.Reflection;
using System.Globalization;

namespace DXRichEdit
{
    public partial class MainWindow : ThemedWindow
    {
        public MainWindow()
        {
            InitializeComponent();

            richEditControl1.LoadDocument("Multimodal.docx");
            var openOfficePatternStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("DXRichEdit.hyphen.dic");
            var customDictionaryStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("DXRichEdit.hyphen_exc.dic");

            //Create dictionary objects
            OpenOfficeHyphenationDictionary hyphenationDictionary = new OpenOfficeHyphenationDictionary(openOfficePatternStream, new CultureInfo("EN-US"));
            CustomHyphenationDictionary exceptionsDictionary = new CustomHyphenationDictionary(customDictionaryStream, new CultureInfo("EN-US"));

            //Add them to the word processor's collection
            richEditControl1.HyphenationDictionaries.Add(hyphenationDictionary);
            richEditControl1.HyphenationDictionaries.Add(exceptionsDictionary);

            richEditControl1.Document.Hyphenation = true;
        }
    }
}
