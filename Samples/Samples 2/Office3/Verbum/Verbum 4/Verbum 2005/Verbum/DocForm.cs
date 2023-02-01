using DevExpress.Skins;
using DevExpress.LookAndFeel;
//using DevExpress.XtraBars;
//using DevExpress.XtraBars.Helpers;
using DevExpress.XtraReports.UI;
using DevExpress.XtraPrinting;
using DevExpress.XtraSpellChecker;
using DevExpress.XtraSpellChecker.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.XtraEditors;
using DevExpress.SpellChecker.Native;
using DevExpress.Utils.Drawing.Helpers;
using System;
using System.IO;
using System.Xml;
using System.Data;
using System.Text;
using System.Drawing;
using System.Collections;
using System.Globalization;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Rizonesoft.Verbum.Configuration;



namespace Rizonesoft.Verbum
{
    public partial class DocForm : DevExpress.XtraEditors.XtraForm
    {

        private static string dictionariesDir = Path.Combine(Application.StartupPath, "Dictionaries");
     


        private void processFileName(string fileName, int docIndex)
        {
        }

        public string FileName
        {
        }

        public DocForm()
        {
            InitializeComponent();
            //spellingLanguage = conf.spellingCulture;
            
            

            DevExpress.XtraBars.Helpers.SkinHelper.InitSkinPopupMenu(this.mSkins);


            
        }

        public DocForm(string fileName, int docIndex)
            : this()
        {

        }


        #region File Menu


        private void iNew_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
        }

        private void iPageSetup_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            ShowPageSetupFormCommand pageSetupCommand = new ShowPageSetupFormCommand(mainDoc);
            pageSetupCommand.Execute();
        }


        private void mainDoc_SelectionChanged(object sender, EventArgs e)
        {

        }


        #region Document Management


        private void mainDoc_DocumentLoaded(object sender, EventArgs e)
        {
            // if (Settings.Default.OptionsConvStaticURLs)
            //{
                //CreateHyperlinks();
            //}
        }

        private void CreateHyperlinks()
        {

            DevExpress.XtraRichEdit.API.Native.Document currDoc = this.mainDoc.Document;

            currDoc.BeginUpdate();

            DocumentRange[] urls = this.mainDoc.Document.FindAll(urlRegex);

            for (int i = 0; i < urls.Length; i++)
            {
                Hyperlink hyperlink = currDoc.CreateHyperlink(urls[i]);
                hyperlink.NavigateUri = currDoc.GetText(hyperlink.Range);
            }

            currDoc.EndUpdate();
        }

        #endregion Document Management


        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {



            //OptionsSpelling spellOptions = coreSpellChecker.GetSpellCheckerOptions(mainDoc);
            coreSpellChecker.OptionsSpelling.CombineOptions(coreSpellChecker.GetSpellCheckerOptions(mainDoc));
            coreSpellChecker.SaveToXML(userSpellingOptions);

            //Properties.Settings.Default.OptionsConvStaticURLs = false;
            // persist our geometry string.

            Properties.Settings.Default.DocWindowState = this.WindowState;
            if (this.WindowState == FormWindowState.Normal)
            {
                Properties.Settings.Default.DocWindowSize = this.Size;
                //Properties.Settings.Default.DocWindowLocation = this.Location;
            }
            Properties.Settings.Default.Save();

            //conf.spellingCulture = coreSpellChecker.Culture.ToString();
            
        }

        #region Exception Handlers

        private void coreSpellChecker_UnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            Console.WriteLine("Exception: {0}", e.ToString());
        }

        #endregion Exception Handlers

        private void iSpellOptions_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsSpelling spellOptions = coreSpellChecker.GetSpellCheckerOptions(mainDoc);
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

                    coreSpellChecker.SetSpellCheckerOptions(mainDoc, spellOptions);
                }
            }
        }

        private void iOptions_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsForm OptionsDlg = new OptionsForm();
            OptionsDlg.Show();
        }

        private void iSkins_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            //OptionsForm OptionsDlg = new OptionsForm();
           // OptionsDlg.coreOpTAB.SelectedTabPageIndex = 1;
            //OptionsDlg.Show();
        }

        private void DocForm_SizeChanged(object sender, EventArgs e)
        {
            //conf.windowSize = this.Size;
        }

        



       

    }
}