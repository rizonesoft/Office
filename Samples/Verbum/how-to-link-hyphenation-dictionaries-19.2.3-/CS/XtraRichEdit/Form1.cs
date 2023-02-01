using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Export;
using System;
using System.IO;
using DevExpress.Office.Services;
using DevExpress.Office.Utils;
using DevExpress.BarCodes;
using System.Drawing;
using System.Windows.Forms;
using DevExpress.Pdf;
using DevExpress.XtraBars;
using System.Data;
using System.Runtime.Serialization.Formatters.Binary;
using DevExpress.XtraRichEdit.Forms;
using System.Reflection;
using System.Globalization;

namespace XtraRichEdit
{
    public partial class Form1 : RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            this.Controls.Add(richEditControl.CreateRibbon());

            richEditControl.LoadDocument("Multimodal.docx");

            HyphenateDocument(richEditControl.Document);

        }

        private void HyphenateDocument(Document document)
        {
            //Load embedded dictionaries
            var openOfficePatternStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("XtraRichEdit.hyph_en_US.dic");
            var customDictionaryStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("XtraRichEdit.hyphen_exc.dic");


            //Create dictionary objects
            OpenOfficeHyphenationDictionary hyphenationDictionary = new OpenOfficeHyphenationDictionary(openOfficePatternStream, new CultureInfo("EN-US"));
            CustomHyphenationDictionary exceptionsDictionary = new CustomHyphenationDictionary(customDictionaryStream, new CultureInfo("EN-US"));

            //Add them to the word processor's collection
            richEditControl.HyphenationDictionaries.Add(hyphenationDictionary);
            richEditControl.HyphenationDictionaries.Add(exceptionsDictionary);

            //Enable automatic hyphenation
            document.Hyphenation = true;
        }
    }
}
