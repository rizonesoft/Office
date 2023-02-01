using System;
using System.IO;
using System.Drawing;
using System.Windows.Forms;

using DevExpress.Skins;
using DevExpress.XtraEditors;
using DevExpress.Utils.Drawing.Helpers;
using DevExpress.LookAndFeel;
using DevExpress.XtraBars.Helpers;
using DevExpress.XtraRichEdit.Commands;

using Verbum.Properties;
using Rizone.Verbum.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Export;


namespace Rizone.Verbum
{
    public partial class DocForm : XtraForm
    {

        private string newFileName;

        private void processFileName(string fileName, int docIndex)
        {

            if (!String.IsNullOrEmpty(fileName))
            {
                FileInfo fileInf = new FileInfo(fileName);
                this.coreDoc.LoadDocument(fileName);
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

            EmlDocumentExporter.Register(coreDoc);
            EmlDocumentImporter.Register(coreDoc);

            SkinHelper.InitSkinPopupMenu(this.mSkins);

            if (!iFormSkins.Checked)
            {
                DevExpress.Skins.SkinManager.DisableFormSkins();
            }

            this.coreHelp.HelpNamespace = Application.StartupPath + "\\Support\\Verbum.chm";

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
            

        }

        private void CreateNewFile(string newFileName = "")
        {
            CopyData copyData = new CopyData();
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            copyData.Channels["DocChannel"].Send(newFileName);
        }

        private void iPageSetup_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            //PageSetupDialog settings
            //pageSetupDlg.Document = printDoc;
            //pageSetupDlg.AllowMargins = false;
            //pageSetupDlg.AllowOrientation = false;
            //pageSetupDlg.AllowPaper = false;
            //pageSetupDlg.AllowPrinter = false;
            //pageSetupDlg.Reset();

            if (pageSetupDlg.ShowDialog() == DialogResult.OK)
            {

                printDoc.DefaultPageSettings = pageSetupDlg.PageSettings;

                coreDoc.Document.Sections[0].Page.PaperKind = printDoc.DefaultPageSettings.PaperSize.Kind;
                //coreDoc.Document.Sections[0].Page.PaperKind = printSystem.PageSettings.PaperKind;
                coreDoc.Document.Sections[0].Page.Landscape = printDoc.DefaultPageSettings.Landscape;
                coreDoc.Document.Sections[0].Margins.Left = printDoc.DefaultPageSettings.Margins.Left;
                
                //printDoc.DefaultPageSettings =
                //setupDlg.PageSettings;
                //printDoc.PrinterSettings =
                //setupDlg.PrinterSettings;
            }

            //printCoreDocLink.CreateDocument();
            //printSystem.PreviewFormEx.Show();
            //printSystem.PageSetup();

            

            //coreDoc.ActiveViewType = DevExpress.XtraRichEdit.RichEditViewType.PrintLayout;
            //coreDoc.ActiveView.ZoomFactor = 0.5f;
        }
        
        private void coreDoc_BeforeExport(object sender, DevExpress.XtraRichEdit.BeforeExportEventArgs e)
        {
            DocumentExportCapabilities checkDocument = coreDoc.Document.RequiredExportCapabilities;
            if ((e.DocumentFormat == DocumentFormat.Rtf) && checkDocument.InlinePictures)
            {
                if ((bool)Settings.Default["CompactFormat"])
                {
                    RtfDocumentExporterOptions options = e.Options as RtfDocumentExporterOptions;
                    if (options != null) options.Compatibility.DuplicateObjectAsMetafile = false;
                }
            }
        }

        #endregion  File Menu


        private void ihContents_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Help.ShowHelp(this, coreHelp.HelpNamespace);
        }

        private void ihIndex_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Help.ShowHelpIndex(this, coreHelp.HelpNamespace);
        }

        private void ihSearch_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            Help.ShowHelp(this, coreHelp.HelpNamespace, HelpNavigator.Find, "");
        }

        private void DocForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            
        }

        private void iOptions_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            OptionsForm options = new OptionsForm();
            options.Show();
        }
   }
}