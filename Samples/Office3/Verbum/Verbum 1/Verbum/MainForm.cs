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

        bool IsFloating = false;
        int documentIndex = 0;
        
        
        public MainForm(string fileName)
        {
         
            InitializeComponent();

            loadSettings();
            
            //this.dictionariesWorker.RunWorkerAsync();

            InitializeSkins();

            SplashScreenManager.ShowForm(this, typeof(SplashScreen1), true, true, false);
            
            this.CreateNewDocument(fileName);

            SplashScreenManager.CloseForm();
        }


        
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


        #region Document Handling

        public void CreateNewDocument(string fileName)
        {
            // Detect whether file is already open
            if (!string.IsNullOrEmpty(fileName))
            {
                foreach (DocumentForm openForm in this.MdiChildren)
                {
                    if (string.Compare(openForm.FileName, fileName, true) == 0)
                    {
                        openForm.Activate();
                        return;
                    }
                }
            }
            else
            {
                documentIndex++;
            }

            // If file not open, open it
            DocumentForm newDoc = new DocumentForm();
            newDoc.OpenFile(fileName, documentIndex);
            newDoc.MdiParent = this;
            newDoc.Show();
        }

        private void tabbedMdiManager_PageAdded(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (this.MdiChildren.Length > 0)
            {
                this.closeAllItem.Enabled = true;
            }
        }

        private void tabbedMdiManager_PageRemoved(object sender, DevExpress.XtraTabbedMdi.MdiTabPageEventArgs e)
        {
            if (this.MdiChildren.Length == 0)
            {
                this.formatBar.Visible = false;
                this.utilitiesBar.Visible = false;
                this.closeAllItem.Enabled = false;

                this.Text = formHeading;
            }
        }

        private void tabbedMdiManager_SelectedPageChanged(object sender, EventArgs e)
        {
            try
            {
                if (this.ActiveMdiChild.Name == "DocumentForm")
                {
                    DocumentForm obDocumentForm = (DocumentForm)this.ActiveMdiChild;
                    this.Text = formHeading + " ( " + obDocumentForm.Text + " )";
                }
            }
            catch (Exception ex)
            {
                Cataloguing.WriteBugToFile("ERROR ~ " + ex.Message.ToString());
            }
            
        }

        #endregion


        private void mainBarManager_Merge(object sender, BarManagerMergeEventArgs e)
        {
            foreach (Bar bar in e.ChildManager.Bars)
            {
                Bar mainBar = mainBarManager.Bars[bar.BarName];
                if (mainBar != null)
                {
                    bar.Visible = false;
                    mainBar.Merge(bar);
                }
            }

            if (this.MdiChildren.Length >= 1) { 
                this.formatBar.Visible = true;
                this.utilitiesBar.Visible = true; 
            }

        }

        private void mainBarManager_UnMerge(object sender, DevExpress.XtraBars.BarManagerMergeEventArgs e)
        {
            foreach (Bar childBar in e.ChildManager.Bars)
            {
                Bar mainBar = mainBarManager.Bars[childBar.BarName];
                if (mainBar != null)
                {
                    if (IsFloating)
                    {
                        childBar.Visible = true;
                        mainBar.UnMerge();
                    }
                    
                }
            }

            if (IsFloating)
            {
                e.ChildManager.Bars["Common"].ItemLinks[0].Visible = true;
            }
        }

        private void tabbedMdiManager_BeginFloating(object sender, DevExpress.XtraTabbedMdi.FloatingCancelEventArgs e)
        {
            IsFloating = true;
        }


        private void tabbedMdiManager_EndFloating(object sender, DevExpress.XtraTabbedMdi.FloatingEventArgs e)
        {
            IsFloating = false;
        }

       



        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            
            
        }










        
    }
}