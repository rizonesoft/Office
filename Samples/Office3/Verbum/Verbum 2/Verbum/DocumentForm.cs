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
using DevExpress.XtraPrinting;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraBars.Helpers;
using DevExpress.LookAndFeel;
using System.Text.RegularExpressions;
using Verbum.Properties;
using System.Threading;

namespace Rizonesoft.Verbum
{

    public partial class DocumentForm : DevExpress.XtraEditors.XtraForm 
    {

        private string newFileName;
                   
        string userSpellingOptions = Path.Combine(runtimeConfig.userAppDataDir, "SpellingOptions.xml");
        PrintableComponentLink printLink;

        private static Regex urlRegex = new Regex(@"((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|
                                www\d{0,3}[.]|ftp[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()
                                <>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+
                                |(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'"".,<>?«»“”‘’]))", RegexOptions.IgnoreCase);
      
        private void processFileName(string fileName, int docIndex)
        {

            try
            {
                if (!String.IsNullOrEmpty(fileName))
                {
                    this.coreDocument.LoadDocument(fileName);
                    FileInfo fileInf = new FileInfo(fileName);
                    this.Text = fileInf.Name + " - " + this.Text;
                }
                else
                {
                    this.Text = @"Document " + docIndex.ToString() + " - " + this.Text;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }

        }

        public string FileName
        {
            get { return newFileName; }
            set { newFileName = value; }
        }

        public DocumentForm()
        {
            InitializeComponent();
            loadDocumentSettings();

            printLink = new PrintableComponentLink(new PrintingSystem());
            printLink.Component = this.coreDocument;
            printLink.PrintingSystem.AfterMarginsChange += new MarginsChangeEventHandler(printingSystemCore_AfterMarginsChange);

            //this.coreBarManager.RegistryPath = "HKEY_CURRENT_USER\\Software\\Rizonesoft\\Verbum\\" 
                //+ this.coreBarManager.LayoutVersion.ToString();
            
            if (File.Exists(userSpellingOptions))
            { coreSpellChecker.RestoreFromXML(userSpellingOptions); }
            if (Utilities.availableDictionaries.ContainsKey(Utilities.settSpellingLanguage))
            { coreSpellChecker.Culture = new CultureInfo(Utilities.settSpellingLanguage); }

            EmlDocumentExporter.Register(coreDocument);
            EmlDocumentImporter.Register(coreDocument);

            this.coreHelp.HelpNamespace = Application.StartupPath + "\\Documentation\\Verbum.chm";

        }

        private void loadDocumentSettings()
        {

            //if (Utilities)
            //{ DevExpress.Skins.SkinManager.EnableFormSkins(); }
            //else
            //{ DevExpress.Skins.SkinManager.DisableFormSkins(); }

            int screenHeight = Screen.PrimaryScreen.WorkingArea.Height;
            int screenWidth = Screen.PrimaryScreen.WorkingArea.Width;

            int newDocHeight = this.Height;
            int newDocWidth = this.Width;

            this.WindowState = Settings.Default.DocWindowState;

            if (Utilities.settFormWinState == FormWindowState.Maximized)
            {
                this.Location = new Point(Utilities.countDocX, Utilities.countDocY);
                this.WindowState = FormWindowState.Maximized;
            }
            else
            {
                this.WindowState = FormWindowState.Normal;
                if ((Utilities.countDocY + newDocHeight) > screenHeight)
                {
                    this.Location = new Point(50, 50);
                    Utilities.countDocX = 50;
                    Utilities.countDocY = 50;
                }
                else
                {
                    this.Location = new Point(Utilities.countDocX, Utilities.countDocY);
                }

                this.Size = Settings.Default.DocWindowSize;
            }

            this.enableAutoSpell.Checked = Utilities.settEnableAutoSpellCheck;
            setSpellCheckMode();

        }

        private void setSpellCheckMode()
        {
            if (Utilities.settEnableAutoSpellCheck)
            { coreSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType; }
            else
            { coreSpellChecker.SpellCheckMode = SpellCheckMode.OnDemand; }
        }

        public DocumentForm(string fileName, int docIndex)
            : this()
        {
            newFileName = fileName;
            processFileName(newFileName, docIndex);
        }


        #region Exception Handlers

        private void coreSpellChecker_UnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            Console.WriteLine("Exception: {0}", e.ToString());
        }

        #endregion Exception Handlers



        #region File Menu

        private void fileNewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewFile();
        }
        
        private void fileCloseItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            this.Close();
        }

        private void shutdownItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Application.Exit();
        }


        private void printPreviewItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateDocument();
            PrintTool tool = new PrintTool(printLink.PrintingSystem);
            tool.ShowPreviewDialog();
        }

        private void CreateNewFile(string newFileName = "")
        {
            CopyData copyData = new CopyData();
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            copyData.Channels["DocChannel"].Send(newFileName);
        }

#endregion


        #region View Menu

        private void showSkinsFormItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            

        }

        #endregion


        #region Tools Menu

        private void optionsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                OptionsForm optionsDlg = new OptionsForm();
                optionsDlg.StartPosition = FormStartPosition.CenterScreen;
                optionsDlg.Show(this);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString(), "Error", MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        #endregion


        #region Spelling

        private void iSpellOptions_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsSpelling spellOptions = coreSpellChecker.GetSpellCheckerOptions(coreDocument);
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

                    coreSpellChecker.SetSpellCheckerOptions(coreDocument, spellOptions);
                    coreSpellChecker.OptionsSpelling.CombineOptions(coreSpellChecker.GetSpellCheckerOptions(coreDocument));
                    //Utilities.settingSpellingLanguage = coreSpellChecker.Culture.ToString();
                    coreSpellChecker.SaveToXML(userSpellingOptions);
                }

            }

        }

        #endregion


        private void iTips_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            ToDForm tipOfTheDayDlg = new ToDForm();
            tipOfTheDayDlg.ShowDialog();
        }

        private void printingSystemCore_AfterMarginsChange(object sender, DevExpress.XtraPrinting.MarginsChangeEventArgs e)
        {
            // Change document margins in the source RichEditControl
            SectionMargins margins = this.coreDocument.Document.Sections[0].Margins;
            switch (e.Side)
            {
                case MarginSide.Left:
                    margins.Left = Units.HundredthsOfInchToDocuments((int)e.Value);
                    break;
                case MarginSide.Right:
                    margins.Right = Units.HundredthsOfInchToDocuments((int)e.Value);
                    break;
                case MarginSide.Top:
                    margins.Top = Units.HundredthsOfInchToDocuments((int)e.Value);
                    break;
                case MarginSide.Bottom:
                    margins.Bottom = Units.HundredthsOfInchToDocuments((int)e.Value);
                    break;
                default:
                    break;
            }

            CreateDocument();
        }

        void CreateDocument()
        {
            printLink.CreateDocument();
            printLink.PrintingSystem.SetCommandVisibility(PrintingSystemCommand.PageMargins, CommandVisibility.All);
        }


        #region Help System

        private void helpContentsItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Help.ShowHelp(this, coreHelp.HelpNamespace);
        }

        #endregion Help System


        #region Document Management

        private void coreDoc_DocumentLoaded(object sender, EventArgs e)
        {
            if (Settings.Default.OptionsConvStaticURLs)
            {
            CreateHyperlinks();
            }
        }

        private void CreateHyperlinks()
        {

            DevExpress.XtraRichEdit.API.Native.Document currDoc = this.coreDocument.Document;

            currDoc.BeginUpdate();

            DocumentRange[] urls = this.coreDocument.Document.FindAll(urlRegex);

            for (int i = 0; i < urls.Length; i++)
            {
                Hyperlink hyperLnk = currDoc.CreateHyperlink(urls[i]);
                hyperLnk.NavigateUri = currDoc.GetText(hyperLnk.Range);
            }

            currDoc.EndUpdate();
        }

        #endregion Document Management


        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {

            if (this.coreDocument.Modified)
            {
                DialogResult dresSave = MessageBox.Show("Do you wish to save your changes to " + this.Text.Replace(" - Verbum", ""),
                    "Verbum", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
                if (dresSave == DialogResult.Yes)
                {
                    this.coreDocument.SaveDocument();
                }
                else if (dresSave == DialogResult.Cancel)
                {
                    // Cancel the Closing event from closing the form.
                    e.Cancel = true;
                }
            }

            Utilities.settFormWinState = this.WindowState;
            if (this.WindowState == FormWindowState.Normal)
            {
                Settings.Default.DocWindowSize = this.Size;
                Settings.Default.Save();
            }

            Utilities.settSpellingLanguage = coreSpellChecker.Culture.ToString();

        }

        private void DocForm_LocationChanged(object sender, EventArgs e)
        {
            recordDocLocation();
        }

        private void DocForm_Activated(object sender, EventArgs e)
        {
            Utilities.settFormWinState = this.WindowState;
            recordDocLocation();
        }

        private void recordDocLocation()
        {
            Utilities.countDocX = this.Location.X;
            Utilities.countDocY = this.Location.Y;
        }

        private void DocForm_SizeChanged(object sender, EventArgs e)
        {
            Utilities.settFormWinState = this.WindowState;
        }

        private void insertCalculationItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            try
            {
                coreDocument.Document.InsertText(coreDocument.Document.CaretPosition, calcEditItime.EditValue.ToString());
            }
            catch
            {
                
            }
        }

        private void coreDocument_SelectionChanged(object sender, EventArgs e)
        {
            if (!coreBarManager.IsCustomizing)
            {
                barTable.Visible = coreDocument.IsSelectionInTable();
                tableAlignmentItem.Enabled = coreDocument.IsSelectionInTable();
                barHeaderFooter.Visible = coreDocument.IsSelectionInHeaderOrFooter;
                barObject.Visible = coreDocument.IsFloatingObjectSelected;
            }
        }

        private void DocumentForm_Deactivate(object sender, EventArgs e)
        {
            Utilities.SetWorkingSet(750000, 300000);
        }













    }

}