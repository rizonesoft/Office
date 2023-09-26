using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Scholar.Language;
using Rizonesoft.Office.Settings.ProgramSettings;
using Rizonesoft.Office.Utilities;
using SautinSoft;

namespace Rizonesoft.Office.Scholar.Forms
{
    /// <summary>
    /// Represents a form for exporting options.
    /// </summary>
    public partial class ExportOptionsForm : XtraForm
    {
        [SuppressMessage("ReSharper", "InconsistentNaming")]
        public enum ExportOptionResult
        {
            None,
            ExportToDocx,
            ExportToXLS,
            ExportToImage,
            ExportToHTML,
            ExportToXML,
            ExportToText
        }

        /// <summary>
        /// Gets the custom dialog result indicating the selected export option.
        /// </summary>
        public ExportOptionResult CustomDialogResult { get; private set; } = ExportOptionResult.None;
        private readonly Dictionary<CheckEdit, Action<bool>> checkboxActions;

        /// <summary>
        /// Initializes a new instance of the <see cref="ExportOptionsForm"/> class.
        /// </summary>
        public ExportOptionsForm()
        {
            InitializeComponent();

            var pdfFocus = new PdfFocus();
            labelPdfFocusVersion.Text = string.Format(Strings.ExportOptionsForm_PdfFocusVersion, pdfFocus.Version);

            InitializeSettings();
            checkboxActions = CreateCheckboxActions();
            BindEvents();
        }

        private void InitializeSettings()
        {
            InitializeCommonSettings();
            InitializeDocxExportSettings();
            InitializeImageExportSettings();

            NumDecimalTextEdit.Text = ScholarSettings.NumDecimalSeparator;
            NumGroupTextEdit.Text = ScholarSettings.NumGroupSeparator;
            HtmlTitleTextEdit.Text = ScholarSettings.HtmlTitle;
            preserveFontsCheckEdit.Checked = ScholarSettings.PreserveFonts;
            preserveImagesCheckEdit.Checked = ScholarSettings.PreserveImages;
            preserveGraphicsCheckEdit.Checked = ScholarSettings.PreserveGraphics;
            XlsConvertTabularCheckEdit.Checked = ScholarSettings.XlsConvertNonTabularData;
            PreservePageLayoutCheckEdit.Checked = ScholarSettings.PreservePageLayout;
            XmlConvertTabularCheckEdit.Checked = ScholarSettings.XmlConvertNonTabularData;
            HtmlKeepCharScaleCheckEdit.Checked = ScholarSettings.HtmlKeepCharScale;
            HtmlEmbedImagesCheckEdit.Checked = ScholarSettings.HtmlEmbedImages;
            HtmlRenderModeRadioGroup.SelectedIndex = ScholarSettings.HtmlRenderMode;
            HtmlImageFormatComboEdit.SelectedIndex = ScholarSettings.HtmlImageFormat;
        }

        private void InitializeCommonSettings()
        {
            copyrightCheckEdit.Checked = ScholarSettings.InsertCopyright;
            copyrightTextEdit.Text = ScholarSettings.Copyright;
            copyrightTextEdit.Enabled = copyrightCheckEdit.Checked;
        }

        private void InitializeDocxExportSettings()
        {
            RenderModeRadioGroup.SelectedIndex = ScholarSettings.PdfRenderMode;
            DetectTablesCheckEdit.Checked = ScholarSettings.DocxDetectTables;
            ShowInvisibleTextCheckEdit.Checked = ScholarSettings.DocxShowInvisibleText;
            KeepCharScaleCheckEdit.Checked = ScholarSettings.DocxKeepCharacterScale;
        }

        private void InitializeImageExportSettings()
        {
            imageAutoSizeCheckEdit.Checked = ScholarSettings.ImageAutoSize;
            imageDpiSpinEdit.Value = ScholarSettings.ImageDpi;
            imageWidthSpinEdit.Value = ScholarSettings.ImageWidth;
            imageHeightSpinEdit.Value = ScholarSettings.ImageHeight;
            imageColorDepthComboEdit.SelectedIndex = ScholarSettings.ImageColorDepthIndex;
            jpegQualityTrackBar.Value = ScholarSettings.JpegQuality;
            jpegQualityLayoutItem.Text = CalculateJpegQuality(jpegQualityTrackBar.Value).ToString();
        }

        private void BindEvents()
        {
            copyrightCheckEdit.CheckStateChanged += CheckEdit_CheckStateChanged;
            preserveFontsCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            preserveImagesCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            preserveGraphicsCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            DetectTablesCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            ShowInvisibleTextCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            KeepCharScaleCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            XlsConvertTabularCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            XmlConvertTabularCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            PreservePageLayoutCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            HtmlKeepCharScaleCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;
            HtmlEmbedImagesCheckEdit.CheckedChanged += CheckEdit_CheckStateChanged;

            ExportToDocxButton.Click += ExportButton_Click;
            ExportToXlsButton.Click += ExportButton_Click;
            ExportToImageButton.Click += ExportButton_Click;
            ExportToHtmlButton.Click += ExportButton_Click;
            ExportToXmlButton.Click += ExportButton_Click;


        }

        private Dictionary<CheckEdit, Action<bool>> CreateCheckboxActions()
        {
            return new Dictionary<CheckEdit, Action<bool>>
            {
                { copyrightCheckEdit, isChecked => {
                    ScholarSettings.InsertCopyright = isChecked;
                    copyrightTextEdit.Enabled = isChecked;
                }},
                { preserveFontsCheckEdit, isChecked => ScholarSettings.PreserveFonts = isChecked },
                { preserveImagesCheckEdit, isChecked => ScholarSettings.PreserveImages = isChecked },
                { preserveGraphicsCheckEdit, isChecked => ScholarSettings.PreserveGraphics = isChecked},
                { DetectTablesCheckEdit, isChecked => ScholarSettings.DocxDetectTables = isChecked },
                { ShowInvisibleTextCheckEdit, isChecked => ScholarSettings.DocxShowInvisibleText = isChecked },
                { KeepCharScaleCheckEdit, isChecked => ScholarSettings.DocxKeepCharacterScale = isChecked },
                { XlsConvertTabularCheckEdit, isChecked => ScholarSettings.XlsConvertNonTabularData = isChecked },
                { PreservePageLayoutCheckEdit, isChecked => ScholarSettings.PreservePageLayout = isChecked },
                { XmlConvertTabularCheckEdit, isChecked => ScholarSettings.XmlConvertNonTabularData = isChecked },
                { HtmlKeepCharScaleCheckEdit, isChecked => ScholarSettings.HtmlKeepCharScale = isChecked },
                { HtmlEmbedImagesCheckEdit, isChecked => ScholarSettings.HtmlEmbedImages = isChecked }
            };
        }

        private void SponsorSvgBox_Click(object sender, EventArgs e)
        {
            try
            {
                FileLauncher.OpenLinkInBrowser(LinkManager.Sautinsoft);
            }
            catch (Exception ex)
            {
                Serilogger.LogMessage(LogLevel.Error, message: $"Could not open {LinkManager.Sautinsoft}.", ex);
            }
        }

        private void CheckEdit_CheckStateChanged(object sender, EventArgs e)
        {
            if (sender is CheckEdit checkbox && checkboxActions.TryGetValue(checkbox, out var action))
            {
                action(checkbox.Checked);
            }
        }

        private void CopyrightTextEdit_Leave(object sender, EventArgs e)
        {
            ScholarSettings.Copyright = copyrightTextEdit.Text;
        }

        private void RenderModeRadioGroup_SelectedIndexChanged(object sender, EventArgs e)
        {
            ScholarSettings.PdfRenderMode = RenderModeRadioGroup.SelectedIndex;
        }

        private void ExportButton_Click(object sender, EventArgs e)
        {
            if (sender is not SimpleButton simpleButton) return;
            CustomDialogResult = simpleButton.Name switch
            {
                "ExportToDocxButton" => ExportOptionResult.ExportToDocx,
                "ExportToXlsButton" => ExportOptionResult.ExportToXLS,
                "ExportToImageButton" => ExportOptionResult.ExportToImage,
                "ExportToHtmlButton" => ExportOptionResult.ExportToHTML,
                "ExportToXmlButton" => ExportOptionResult.ExportToXML,
                _ => ExportOptionResult.None
            };
            Close();
        }

        private void HtmlTitleTextEdit_Leave(object sender, EventArgs e)
        {
            ScholarSettings.HtmlTitle = HtmlTitleTextEdit.Text;
        }

        private void HtmlRenderModeRadioGroup_SelectedIndexChanged(object sender, EventArgs e)
        {
            ScholarSettings.HtmlRenderMode = HtmlRenderModeRadioGroup.SelectedIndex;
            HtmlKeepCharScaleCheckEdit.Enabled = HtmlRenderModeRadioGroup.SelectedIndex != 1;
        }

        private void HtmlImageFormatComboEdit_SelectedIndexChanged(object sender, EventArgs e)
        {
            ScholarSettings.HtmlImageFormat = HtmlImageFormatComboEdit.SelectedIndex;
        }

        private void ImageAutoSizeCheckEdit_CheckedChanged(object sender, EventArgs e)
        {
            ScholarSettings.ImageAutoSize = imageAutoSizeCheckEdit.Checked;
            var dependentControls = new List<Control> { imageDpiSpinEdit, imageWidthSpinEdit, imageHeightSpinEdit, imageColorDepthComboEdit };
            foreach (var ctrl in dependentControls)
            { ctrl.Enabled = !imageAutoSizeCheckEdit.Checked; }
        }

        private void ImageDpiSpinEdit_Leave(object sender, EventArgs e)
        {
            ScholarSettings.ImageDpi = (int)imageDpiSpinEdit.Value;
        }

        private void ImageWidthSpinEdit_Leave(object sender, EventArgs e)
        {
            ScholarSettings.ImageWidth = (int)imageWidthSpinEdit.Value;
        }

        private void ImageHeightSpinEdit_Leave(object sender, EventArgs e)
        {
            ScholarSettings.ImageHeight = (int)imageHeightSpinEdit.Value;
        }

        private void ImageColorDepthComboEdit_SelectedIndexChanged(object sender, EventArgs e)
        {
            ScholarSettings.ImageColorDepthIndex = imageColorDepthComboEdit.SelectedIndex;
        }

        private void JpegQualityTrackBar_ValueChanged(object sender, EventArgs e)
        {
            ScholarSettings.JpegQuality = jpegQualityTrackBar.Value;
            jpegQualityLayoutItem.Text = CalculateJpegQuality(jpegQualityTrackBar.Value).ToString();
        }

        private static int CalculateJpegQuality(int value)
        {
            return value * 10;

        }

    }

}
