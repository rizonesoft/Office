using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;

using System.IO;
using System.Xml;
using System.Collections;
using System.Globalization;
using System.Diagnostics;

using Rizonesoft.Verbum.Configuration;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSpellChecker.Forms;
using DevExpress.SpellChecker.Native;

namespace Rizonesoft.Verbum
{

    public partial class DocForm : DevExpress.XtraEditors.XtraForm
    {

        private string newFileName;
        private static string dictionariesDir = Path.Combine(Application.StartupPath, "Dictionaries");
   
        string userSpellingOptions = Path.Combine(RuntimeConfig.userAppDataDir, "SpellingOptions.xml");
        private string spellingLanguage = "en-US";
      
        private void processFileName(string fileName, int docIndex)
        {

            if (!String.IsNullOrEmpty(fileName))
            {
                FileInfo fileInf = new FileInfo(fileName);
                // this.mainDoc.LoadDocument(fileName);
                this.Text = fileInf.Name + " - " + this.Text;
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + " - " + this.Text;
            }

        }

        public string FileName
        {
            get { return newFileName; }
            set { newFileName = value; }
        }

        public DocForm()
        {
            InitializeComponent();
            dictionariesWorker.RunWorkerAsync();
        }

        public DocForm(string fileName, int docIndex)
            : this()
        {
            newFileName = fileName;
            processFileName(newFileName, docIndex);           
        }

#region Spelling

        private static bool isDictionariesLoaded;

        private void dictionariesWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            if (!isDictionariesLoaded)
            {
                LoadDictionaries();
                isDictionariesLoaded = true;
            }
        }

        private void LoadDictionaries()
        {
            try
            {
                string[] dicFiles = Directory.GetFiles(dictionariesDir);
                foreach (string sFile in dicFiles)
                {
                    if (sFile.EndsWith(".xml"))
                    {
                        //Console.WriteLine(sFile);
                        try
                        {
                            XmlDocument xmlDic = new XmlDocument(); // create an xml document object.
                            xmlDic.Load(sFile); // load the XML document from the specified file.

                            // Get elements.
                            XmlNodeList nodeDicLang = xmlDic.GetElementsByTagName("language");
                            XmlNodeList nodeDicCulture = xmlDic.GetElementsByTagName("culture");
                            XmlNodeList nodeDicPath = xmlDic.GetElementsByTagName("dictionary-path");
                            XmlNodeList nodeDicGrammPath = xmlDic.GetElementsByTagName("grammer-path");
                            AddHunspellDictionary(nodeDicPath[0].InnerText.Trim(),
                                nodeDicGrammPath[0].InnerText.Trim(),
                                nodeDicCulture[0].InnerText.Trim());
                        }
                        catch (Exception e)
                        {
                            MessageBox.Show(e.Message.ToString() + Environment.NewLine + sFile.ToString(),
                                "Dic Configuration Error", MessageBoxButtons.OK,
                                MessageBoxIcon.Error, MessageBoxDefaultButton.Button1);
                        }
                    }
                }
            }
            catch (DirectoryNotFoundException e)
            {
                MessageBox.Show(e.Message.ToString(),
                    "Dictionaries Error", MessageBoxButtons.OK,
                    MessageBoxIcon.Error, MessageBoxDefaultButton.Button1);

            }

        }

        private static Hashtable availableDictionaries = new Hashtable();

        /// <summary>
        /// Adds a Hunspell dictionary.
        /// </summary>
        /// <param name="dictionaryPath">The dictionary path.</param>
        /// <param name="grammarPath">The grammar path.</param>
        /// <param name="culture">The culture.</param>
        private void AddHunspellDictionary(
          string dictionaryPath,
          string grammarPath,
          string culture)
        {
            string fullDictionaryPath = System.IO.Path.Combine(dictionariesDir, dictionaryPath);
            string fullGrammarPath = System.IO.Path.Combine(dictionariesDir, grammarPath);
            if (File.Exists(fullDictionaryPath) && File.Exists(fullGrammarPath))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary spellCheckerHunspellDic =
                    new DevExpress.XtraSpellChecker.HunspellDictionary();
                spellCheckerHunspellDic.Culture = new System.Globalization.CultureInfo(culture);
                spellCheckerHunspellDic.DictionaryPath = fullDictionaryPath;
                spellCheckerHunspellDic.GrammarPath = fullGrammarPath;
                this.sharedDicStorage.Dictionaries.Add(spellCheckerHunspellDic);
                availableDictionaries.Add(culture, spellCheckerHunspellDic);

            }
        }

        private void dictionariesWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            if (File.Exists(userSpellingOptions))
            { coreSpellChecker.RestoreFromXML(userSpellingOptions); }
            if (availableDictionaries.ContainsKey(spellingLanguage))
            { coreSpellChecker.Culture = new CultureInfo(spellingLanguage); }

            coreSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
            this.iSpellCheck.Enabled = true;
            this.iSpellOptions.Enabled = true;
        }

        private void iSpellCheck_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            this.coreSpellChecker.Check(this.coreDoc);
        }

        private void EnsureDictionaryLoading(string culture)
        {
            if (availableDictionaries.ContainsKey(culture))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary
                  dictionary = availableDictionaries[culture] as DevExpress.XtraSpellChecker.HunspellDictionary;
                if (!dictionary.Loaded)
                {
                    this.sharedDicStorage.Dictionaries.Add(dictionary);
                    dictionary.Load();
                }
            }
        }

        private void iSpellOptions_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsSpelling spellOptions = coreSpellChecker.GetSpellCheckerOptions(coreDoc);
            coreSpellChecker.OptionsSpelling.CombineOptions(spellOptions);
            using (SpellingOptionsForm spellOptionsForm = new SpellingOptionsForm(coreSpellChecker))
            {
                spellOptionsForm.Init();
                if (spellOptionsForm.ShowDialog(this) == DialogResult.OK)
                {
                    spellOptions.BeginUpdate();
                    try
                    {
                        spellOptions.IgnoreUpperCaseWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreUpperCase);
                        spellOptions.IgnoreEmails = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreEmails);
                        spellOptions.IgnoreWordsWithNumbers = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreWordsWithDigits);
                        spellOptions.IgnoreUrls = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreUrls);
                        spellOptions.IgnoreMixedCaseWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreMixedCaseWords);
                        spellOptions.IgnoreRepeatedWords = BoolDefaultBooleanConverter.ConvertBoolToDefaultBoolean(spellOptionsForm.IgnoreRepeatedWords);
                    }
                    finally
                    {
                        spellOptions.EndUpdate();
                    }

                    coreSpellChecker.SetSpellCheckerOptions(coreDoc, spellOptions);
                }
            }
        }

#endregion


        private void iTips_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            TipsForm tipOfTheDayDlg = new TipsForm();
            tipOfTheDayDlg.ShowDialog();
        }

        private void iFileNew_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {

        }







    }

}