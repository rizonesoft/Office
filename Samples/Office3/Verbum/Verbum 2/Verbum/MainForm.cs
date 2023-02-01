using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Collections;

using Rizonesoft.Verbum.Configuration;

using DevExpress.XtraEditors;
using System.IO;
using System.Xml;
using System.Globalization;
using DevExpress.XtraSpellChecker;
using System.Reflection;
using DevExpress.LookAndFeel;

using Verbum.Properties;
using DevExpress.XtraSplashScreen;
using System.Diagnostics;
using System.Threading;


namespace Rizonesoft.Verbum
{

    public partial class MainForm : DevExpress.XtraEditors.XtraForm
    {

        /// <summary>
        /// Array of all forms currently open, application closes when all closed
        /// </summary>
        private ArrayList childForms;

        /// <summary>
        /// The CopyData class used for message sending.
        /// </summary>
        private CopyData copyData = null;

        private bool showTipsOnStarup = Settings.Default.ShowTipsOnStartup;
         
        private int docIndex = 0;
        public int DocumentIndex
        {
            get { return docIndex; }
            set { docIndex = value; }
        }

        private static string dictionariesDir = Path.Combine(Application.StartupPath, "Dictionaries");

        public MainForm()
        {
            InitializeComponent();
            //Thread.CurrentThread.CurrentUICulture = new System.Globalization.CultureInfo("ja");

            // Do everything possible to keep this window hidden
            // note: form.Opacity = 0 set in designer will keep
            // the window from flashing during startup
            this.ShowInTaskbar = false;
            this.Opacity = 0;
            this.Hide();

            loadSettings();
            InitializeSkins();
            SplashScreenManager.ShowForm(this, typeof(SplashScreen1), true, true, false);
            LoadDictionaries();
            createAppDirectories();
            initialize();
     
        }

        private void dictionariesWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            
        }

        private void dictionariesWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            
        }

        private void createAppDirectories()
        {
            if (!Directory.Exists(runtimeConfig.userAppDataDir))
            {
                Directory.CreateDirectory(runtimeConfig.userAppDataDir);
            }

        }

        private void InitializeSkins()
        {
            LoadSkins("DevExpress.BonusSkins.v11.2.dll");
            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();
            UserLookAndFeel.Default.SkinName = Settings.Default["ApplicationSkinName"].ToString();
            //LoadSkins("DevExpress.OfficeSkins.v11.2.dll");
            //UserLookAndFeel.Default.SkinName = conf.applicationSkin;
        }

        private void LoadSkins(string skinFileName)
        {
            if (File.Exists(skinFileName))
            {
                Assembly verbumAssembly = Assembly.LoadFile(Path.GetFullPath(skinFileName));
                DevExpress.Skins.SkinManager.Default.RegisterAssembly(verbumAssembly);
            }
            //else MessageBox.Show("File not found");
        }

        private void initialize()
        {
            childForms = new ArrayList();
            // Create a new instance of the class:
            copyData = new CopyData();
            // Assign the handle:
            copyData.AssignHandle(this.Handle);
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            // Hook up event notifications whenever a message is received:
            copyData.DataReceived += new Rizonesoft.Verbum.DataReceivedEventHandler(
                copyData_DataReceived);
        }

        /// <summary>
        /// Fired whenever message is received from another instance.
        /// Open file name in new form
        /// </summary>
        /// <param name="sender">The CopyData class which receieved the data.</param>
        /// <param name="e">Data that was receieved.</param>
        private void copyData_DataReceived(object sender, Rizonesoft.Verbum.DataReceivedEventArgs e)
        {
            if (e.Data.Equals(""))
                docIndex += 1;
            // Display the data in the logging list box:
            if (e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                DocumentForm docForm = new DocumentForm(fileName, docIndex);

                docForm.Location = new Point(Utilities.countDocX + 25, Utilities.countDocY + 25);

                AddForm(docForm);

            }
        }

        /// <summary>
        /// AddForm adds and displays the new form.
        /// </summary>
        /// <param name="form"></param>
        public void AddForm(XtraForm childForm)
        {
            childForm.Closed += new EventHandler(OnChildFormClosed);
            childForms.Add(childForm);
            childForm.Show();

            // Close the Splash Screen
            SplashScreenManager.CloseForm(false);

            if ((showTipsOnStarup) && (Utilities.initRun))
            {
                ToDForm tipOfTheDayDlg = new ToDForm();
                tipOfTheDayDlg.ShowDialog();
                Utilities.initRun = false;
            }

        }

        /// <summary>
        /// Called everytime a "child" form is closed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void OnChildFormClosed(object sender, EventArgs e)
        {
            childForms.Remove(sender);
            if (childForms.Count == 0)
            {
                this.Close();
            }

        }


        //private static bool isDictionariesLoaded;

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
                
                Utilities.availableDictionaries.Add(dicCulture.Name, spellCheckerHunspellDic);
                
                AddCustomDictionary(dictionaryPath, dicCulture);

            }
        }

        private void AddCustomDictionary(
            string dictionaryPath,
            CultureInfo customCulture)
        {

            string userCustomDicDir = runtimeConfig.userAppDataDir + "\\Dictionaries";
            if (!Directory.Exists(userCustomDicDir))
            { Directory.CreateDirectory(userCustomDicDir); }

            SpellCheckerCustomDictionary customDictionary = new SpellCheckerCustomDictionary();
            customDictionary.AlphabetPath = userCustomDicDir + "\\custom_" + Path.GetFileNameWithoutExtension(dictionaryPath) + ".txt";
            customDictionary.DictionaryPath = userCustomDicDir + "\\custom_" + dictionaryPath;
            customDictionary.Culture = customCulture;
            this.coreDictionaryStorage.Dictionaries.Add(customDictionary);
        }


        private void EnsureDictionaryLoading(string culture)
        {
            if (Utilities.availableDictionaries.ContainsKey(culture))
            {
                DevExpress.XtraSpellChecker.HunspellDictionary
                  dictionary = Utilities.availableDictionaries[culture] as DevExpress.XtraSpellChecker.HunspellDictionary;
                if (!dictionary.Loaded)
                {
                    this.coreDictionaryStorage.Dictionaries.Add(dictionary);
                    dictionary.Load();
                }
            }
        }

        private void CoreForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            saveSettings();
            //if (applicationMutex != null)
            //{
            //applicationMutex.ReleaseMutex();
            //}
        }

        private void loadSettings()
        {
            if (Settings.Default.AllowFormSkins)
            { DevExpress.Skins.SkinManager.EnableFormSkins(); }
            else
            { DevExpress.Skins.SkinManager.DisableFormSkins(); }

            DevExpress.Skins.SkinManager.AllowArrowDragIndicators = Settings.Default.AllowArrowDragIndicators;
            DevExpress.Skins.SkinManager.AllowWindowGhosting = Settings.Default.AllowWindowGhosting;

            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();

            Utilities.settFormWinState = Settings.Default.DocWindowState;
            Utilities.countDocX = Settings.Default.DocWindowLocation.X;
            Utilities.countDocY = Settings.Default.DocWindowLocation.Y;
        }

        private void saveSettings()
        {
            Settings.Default["ApplicationSkinName"] = UserLookAndFeel.Default.SkinName;
            Settings.Default.DocWindowState = Utilities.settFormWinState;
            Settings.Default.DocWindowLocation = new Point(Utilities.countDocX, Utilities.countDocY);
            Settings.Default.Save();
        }


    }

}