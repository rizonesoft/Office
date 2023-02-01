using System;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Windows.Forms;
using DevExpress.LookAndFeel;
using DevExpress.Skins;
using DevExpress.XtraBars;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSplashScreen;
using Rizonesoft.Verbum.Properties;


namespace Rizonesoft.Verbum
{
    public partial class MainForm : DevExpress.XtraEditors.XtraForm
    {
     
        
       
        #region File menu

        private void shutdownItem_ItemClick(object sender, ItemClickEventArgs e)
        {
            this.Close();
            Application.Exit();
        }

        private void closeAllItem_ItemClick(object sender, ItemClickEventArgs e)
        {

            Form[] arrChildren = this.MdiChildren;

            foreach (Form docForm in arrChildren)
                docForm.Close();

        }

        #endregion


        #region Dictionaries

        private void dictionariesWorker_DoWork(object sender, System.ComponentModel.DoWorkEventArgs e)
        {
            LoadDictionaries();
        }

        private void LoadDictionaries()
        {
            try
            {
                string[] dicFiles = Directory.GetFiles("Dictionaries");
                foreach (string sFile in dicFiles)
                {
                    if (sFile.EndsWith(".dic"))
                    {
                        try
                        {
                            string sFileNoExtension = Path.GetFileNameWithoutExtension(sFile);
                            string[] sFileParts = sFileNoExtension.Split('_');

                            AddHunspellDictionary(sFile, "Dictionaries\\" + sFileNoExtension + ".aff",
                            new CultureInfo(String.Format("{0}-{1}", sFileParts[0], sFileParts[1])));

                        }
                        catch (Exception e)
                        {
                            MessageBox.Show(e.ToString() + Environment.NewLine + sFile.ToString(),
                                "Dictionaries Configuration Error", MessageBoxButtons.OK,
                                MessageBoxIcon.Error, MessageBoxDefaultButton.Button1);
                        }
                    }
                }
            }
            catch (DirectoryNotFoundException e)
            {
                Cataloguing.WriteBugToFile(String.Format("ERROR ~ {0}", e.Message.ToString()));
                Cataloguing.WriteBugToFile("WORKER ~ Creating a new Dictionaries folder.");
                Directory.CreateDirectory("Dictionaries");
                //MessageBox.Show(e.Message.ToString(),
                //    "Dictionaries Error", MessageBoxButtons.OK,
                //    MessageBoxIcon.Error, MessageBoxDefaultButton.Button1);

            }

        }

        /// <summary>
        /// Adds a Hunspell dictionary.
        /// </summary>
        /// <param name="dictionaryPath">The dictionary path.</param>
        /// <param name="grammarPath">The grammar path.</param>
        /// <param name="dicCulture">The culture.</param>
        private void AddHunspellDictionary(
          string dictionaryPath,
          string grammarPath,
          CultureInfo dicCulture)
        {
            if (File.Exists(dictionaryPath) && File.Exists(grammarPath))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary spellCheckerHunspellDic =
                    new DevExpress.XtraSpellChecker.HunspellDictionary();

                spellCheckerHunspellDic.Culture = dicCulture;
                spellCheckerHunspellDic.DictionaryPath = dictionaryPath;
                spellCheckerHunspellDic.GrammarPath = grammarPath;
                this.coreDictionaryStorage.Dictionaries.Add(spellCheckerHunspellDic);

                Assistants.availableDictionaries.Add(dicCulture.Name, spellCheckerHunspellDic);

                AddCustomDictionary(dictionaryPath, dicCulture);

            }
        }

        private void AddCustomDictionary(
           string dictionaryPath,
           CultureInfo customCulture)
        {

            string userCustomDicDir = Configuration.UserAppDataPath + "\\Dictionaries";
            if (!Directory.Exists(userCustomDicDir))
            { Directory.CreateDirectory(userCustomDicDir); }

            SpellCheckerCustomDictionary customDictionary = new SpellCheckerCustomDictionary();
            customDictionary.AlphabetPath = userCustomDicDir + "\\custom_" + Path.GetFileNameWithoutExtension(dictionaryPath) + ".txt";
            customDictionary.DictionaryPath = userCustomDicDir + "\\custom_" + Path.GetFileNameWithoutExtension(dictionaryPath) + ".dic";
            customDictionary.Culture = customCulture;
            this.coreDictionaryStorage.Dictionaries.Add(customDictionary);
        }

        #endregion


