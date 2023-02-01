using System;
using System.IO;
using System.Data;
using System.Text;
using System.Drawing;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;

using DevExpress.Skins;
using DevExpress.XtraEditors;
using DevExpress.LookAndFeel;
using DevExpress.XtraReports.UI;

using DevExpress.XtraBars.Helpers;

using DevExpress.Utils.Drawing.Helpers;

using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.XtraRichEdit.Export;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.API.Native;

using DevExpress.XtraPrinting;
using DevExpress.XtraSpellChecker;
using System.Globalization;
using DevExpress.XtraBars;
using Rizonesoft.Properties;


namespace Rizonesoft.Verbum
{
    public partial class DocForm : DevExpress.XtraEditors.XtraForm
    {
        private string newFileName;
        private string spellingLanguage;
        PrintableComponentLink printLink;

        private void processFileName(string fileName, int docIndex)
        {

            if (!String.IsNullOrEmpty(fileName))
            {
                FileInfo fileInf = new FileInfo(fileName);
                this.mainDoc.LoadDocument(fileName);
                this.Text = fileInf.Name + " - " + this.Text;
            }
            else
            {
                this.Text = @"Document " + docIndex.ToString() + " - " + this.Text;
            }

        }

        private void loadFile()
        {
        }

        public string FileName
        {
            get { return newFileName; }
            set { newFileName = value; }
        }

        public DocForm()
        {
            InitializeComponent();

            spellingLanguage = Settings.Default["SpellingLanguage"].ToString();
            
            EmlDocumentExporter.Register(mainDoc);
            EmlDocumentImporter.Register(mainDoc);

            SkinHelper.InitSkinPopupMenu(this.mSkins);

            if (!iFormSkins.Checked)
            {
                DevExpress.Skins.SkinManager.DisableFormSkins();
            }

            printLink = new PrintableComponentLink(new PrintingSystem());
            printLink.Component = this.mainDoc;
            printLink.PrintingSystem.AfterMarginsChange += new MarginsChangeEventHandler(PrintingSystem_AfterMarginsChange);
            
            //this.coreHelp.HelpNamespace = Application.StartupPath + "\\Support\\Verbum.chm";

            dictionariesWorker.RunWorkerAsync();

            //this.coreSpellChecker.OptionsSpelling.OptionChanged += coreSpellChecker_OptionChanged;
            this.coreSpellChecker.OptionsSpelling.OptionChanged += new System.EventHandler(this.coreSpellChecker_OptionChanged);
        }

        private void dictionariesWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            this.mLanguage.Enabled = false;
            LoadDictionaries();
        }

        private void dictionariesWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            coreSpellChecker.SpellCheckMode = SpellCheckMode.AsYouType;
            this.mLanguage.Enabled = true;
            syncLanguageOptions();
        }

        private void LoadDictionaries()
        {
            string currentDirectory = Directory.GetCurrentDirectory();
            string[] dicFiles = Directory.GetFiles(currentDirectory + "\\Dictionaries\\");


                foreach (string sFile in dicFiles)
                {
                    if (sFile.EndsWith(".dic") && Path.GetFileNameWithoutExtension(sFile).Length == 5)
                    {
                        string cultureString = Convert.ToString(Path.GetFileNameWithoutExtension(sFile)).Replace("_", "-");
                        CultureInfo currCulture = new CultureInfo(cultureString);

                        DevExpress.XtraBars.BarCheckItem lngItem = new DevExpress.XtraBars.BarCheckItem();
                        lngItem.ButtonStyle = DevExpress.XtraBars.BarButtonStyle.Check;

                        lngItem.Caption = currCulture.EnglishName;
                        lngItem.Tag = currCulture;

                        mLanguage.AddItem(lngItem);

                        lngItem.ItemClick += mLanguage_ItemsClick;
                        lngItem.CheckedChanged += barCheckItem_CheckedChanged;

                        HunspellDictionary openOfficeDictionary = new HunspellDictionary();
                        openOfficeDictionary.DictionaryPath = sFile;
                        openOfficeDictionary.GrammarPath = currentDirectory + "\\Dictionaries\\" + Path.GetFileNameWithoutExtension(sFile) + ".aff";
                        openOfficeDictionary.Culture = currCulture;
                        coreSpellChecker.Dictionaries.Add(openOfficeDictionary);
                    }
                }

                coreSpellChecker.Culture = new CultureInfo(spellingLanguage);
        }

        private void coreSpellChecker_OptionChanged(object sender, EventArgs e)
        {
            syncLanguageOptions();
        }

        private void syncLanguageOptions()
        {
            foreach (BarCheckItemLink lngLink in mLanguage.ItemLinks)
            {
               if (coreSpellChecker.Culture.DisplayName == lngLink.Item.Caption)
                {
                   lngLink.Item.Down = true;
                }
           }
        }

        private void mLanguage_ItemsClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            MessageBox.Show(e.Item.Caption, "");
            spellingLanguage = e.Item.Tag.ToString();
            CultureInfo cuSpelling = (CultureInfo)e.Item.Tag;
            coreSpellChecker.Culture = cuSpelling;
            syncLanguageOptions();
        }

        private void barCheckItem_CheckedChanged(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            DevExpress.XtraBars.BarCheckItem item = sender as DevExpress.XtraBars.BarCheckItem;
            if ((!item.Checked))
            {
                return;
            }
            foreach (DevExpress.XtraBars.BarItemLink link in mLanguage.ItemLinks)
            {
                BarCheckItem it = link.Item as BarCheckItem;
                if (it != null && !object.ReferenceEquals(it, item) && it.Checked)
                {
                    it.Checked = false;
                    break; // TODO: might not be correct. Was : Exit For
                }
            }
        }


        public DocForm(string fileName, int docIndex)
            : this()
        {
            newFileName = fileName;
            processFileName(newFileName, docIndex);
        }


        #region File Menu

        private void iNew_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            CreateNewFile();
        }

        private void iOpen_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OpenFileDialog openFileDlg = new OpenFileDialog();

            openFileDlg.AddExtension = true;
            openFileDlg.CheckFileExists = true;
            openFileDlg.CheckPathExists = true;
            openFileDlg.DereferenceLinks = true;
            openFileDlg.Filter = "All Files (*.*)|*.*|" +
                "All Supported Documents (*.docx, *.doc, *.rtf)|*.docx;*.doc;*.rtf|" +
                "Word 2007-2010 Document (*.docx)|*.docx|" +
                "Word 97-2003 Document (*.doc)|*.doc|" +
                "Rich Text Format (*.rtf)|*.rtf|" +
                "Text Files (*.txt)|*.txt";
            openFileDlg.FilterIndex = 2;
            openFileDlg.ValidateNames = true;

            if (openFileDlg.ShowDialog() == DialogResult.OK)
            {
                CreateNewFile(openFileDlg.FileName);
            }
        }

        private void iPageSetup_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            ShowPageSetupFormCommand pageSetupCommand = new ShowPageSetupFormCommand(mainDoc);
            pageSetupCommand.Execute();

        }

        #region Change Margins

        void PrintingSystem_AfterMarginsChange(object sender, MarginsChangeEventArgs e)
        {
            // Change document margins in the source RichEditControl
            SectionMargins margins = this.mainDoc.Document.Sections[0].Margins;
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

        #endregion Change Margins

        private void iPrintPreview_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
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

        #endregion File Menu


        #region Edit Menu

        private void iEditDelete_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            DeleteCommand docDeleteCommand = new DeleteCommand(mainDoc);
            docDeleteCommand.Execute();
        }

        private void iSelectAll_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            SelectAllCommand docSelectCommand = new SelectAllCommand(mainDoc);
            docSelectCommand.Execute();
        }

#endregion Edit Menu

        private void mainDoc_SelectionChanged(object sender, EventArgs e)
        {

        }

#region View Menu

        private void iFormSkins_CheckedChanged(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            if (iFormSkins.Checked)
                DevExpress.Skins.SkinManager.EnableFormSkins();
            else
                DevExpress.Skins.SkinManager.DisableFormSkins();
            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();
        }

#endregion View Menu

        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            Settings.Default["SpellingLanguage"] = spellingLanguage;
            Settings.Default.Save();
        }

        #region Exception Handlers

        private void coreSpellChecker_UnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            new ExceptionForm(e.Exception).ShowDialog();
        }

        #endregion Exception Handlers

    }
}