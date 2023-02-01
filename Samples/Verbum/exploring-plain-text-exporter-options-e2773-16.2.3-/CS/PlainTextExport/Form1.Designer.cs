namespace PlainTextExport
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.panelControl1 = new DevExpress.XtraEditors.PanelControl();
            this.btnExport = new DevExpress.XtraEditors.SimpleButton();
            this.richEditControl1 = new DevExpress.XtraRichEdit.RichEditControl();
            this.dockManager1 = new DevExpress.XtraBars.Docking.DockManager(this.components);
            this.dockPanel1 = new DevExpress.XtraBars.Docking.DockPanel();
            this.dockPanel1_Container = new DevExpress.XtraBars.Docking.ControlContainer();
            this.propertyGridControl1 = new DevExpress.XtraVerticalGrid.PropertyGridControl();
            this.categoryMisc = new DevExpress.XtraVerticalGrid.Rows.CategoryRow();
            this.rowOptions = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_Encoding = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_ExportHiddenText = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_FieldCodeStartMarker = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_FieldCodeEndMarker = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_FieldResultEndMarker = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_FootNoteSeparator = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_EndNoteSeparator = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.rowOptions_Export_PlainText_ExportedDocumentProperties = new DevExpress.XtraVerticalGrid.Rows.PGridEditorRow();
            this.memoEdit1 = new DevExpress.XtraEditors.MemoEdit();
            this.defaultLookAndFeel1 = new DevExpress.LookAndFeel.DefaultLookAndFeel(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).BeginInit();
            this.panelControl1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dockManager1)).BeginInit();
            this.dockPanel1.SuspendLayout();
            this.dockPanel1_Container.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.propertyGridControl1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoEdit1.Properties)).BeginInit();
            this.SuspendLayout();
            // 
            // panelControl1
            // 
            this.panelControl1.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.panelControl1.Controls.Add(this.btnExport);
            this.panelControl1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelControl1.Location = new System.Drawing.Point(343, 0);
            this.panelControl1.Name = "panelControl1";
            this.panelControl1.Size = new System.Drawing.Size(665, 47);
            this.panelControl1.TabIndex = 0;
            // 
            // btnExport
            // 
            this.btnExport.Location = new System.Drawing.Point(12, 12);
            this.btnExport.Name = "btnExport";
            this.btnExport.Size = new System.Drawing.Size(119, 23);
            this.btnExport.TabIndex = 0;
            this.btnExport.Text = "Export to Plain Text";
            this.btnExport.Click += new System.EventHandler(this.btnExport_Click);
            // 
            // richEditControl1
            // 
            this.richEditControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richEditControl1.Location = new System.Drawing.Point(343, 47);
            this.richEditControl1.Name = "richEditControl1";
            this.richEditControl1.Size = new System.Drawing.Size(665, 290);
            this.richEditControl1.TabIndex = 1;
            this.richEditControl1.Text = "richEditControl1";
            // 
            // dockManager1
            // 
            this.dockManager1.Form = this;
            this.dockManager1.RootPanels.AddRange(new DevExpress.XtraBars.Docking.DockPanel[] {
            this.dockPanel1});
            this.dockManager1.TopZIndexControls.AddRange(new string[] {
            "DevExpress.XtraBars.BarDockControl",
            "DevExpress.XtraBars.StandaloneBarDockControl",
            "System.Windows.Forms.StatusBar",
            "DevExpress.XtraBars.Ribbon.RibbonStatusBar",
            "DevExpress.XtraBars.Ribbon.RibbonControl"});
            // 
            // dockPanel1
            // 
            this.dockPanel1.Controls.Add(this.dockPanel1_Container);
            this.dockPanel1.Dock = DevExpress.XtraBars.Docking.DockingStyle.Left;
            this.dockPanel1.ID = new System.Guid("cd17b78d-09ea-4d72-9410-1dfd76b16e7c");
            this.dockPanel1.Location = new System.Drawing.Point(0, 0);
            this.dockPanel1.Name = "dockPanel1";
            this.dockPanel1.OriginalSize = new System.Drawing.Size(343, 200);
            this.dockPanel1.Size = new System.Drawing.Size(343, 562);
            this.dockPanel1.Text = "RichEditControl Properties";
            // 
            // dockPanel1_Container
            // 
            this.dockPanel1_Container.Controls.Add(this.propertyGridControl1);
            this.dockPanel1_Container.Location = new System.Drawing.Point(4, 38);
            this.dockPanel1_Container.Name = "dockPanel1_Container";
            this.dockPanel1_Container.Size = new System.Drawing.Size(334, 520);
            this.dockPanel1_Container.TabIndex = 0;
            // 
            // propertyGridControl1
            // 
            this.propertyGridControl1.Cursor = System.Windows.Forms.Cursors.SizeNS;
            this.propertyGridControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.propertyGridControl1.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.propertyGridControl1.Location = new System.Drawing.Point(0, 0);
            this.propertyGridControl1.Name = "propertyGridControl1";
            this.propertyGridControl1.RecordWidth = 62;
            this.propertyGridControl1.RowHeaderWidth = 138;
            this.propertyGridControl1.Rows.AddRange(new DevExpress.XtraVerticalGrid.Rows.BaseRow[] {
            this.categoryMisc});
            this.propertyGridControl1.SelectedObject = this.richEditControl1;
            this.propertyGridControl1.Size = new System.Drawing.Size(334, 520);
            this.propertyGridControl1.TabIndex = 0;
            // 
            // categoryMisc
            // 
            this.categoryMisc.ChildRows.AddRange(new DevExpress.XtraVerticalGrid.Rows.BaseRow[] {
            this.rowOptions});
            this.categoryMisc.Name = "categoryMisc";
            this.categoryMisc.Properties.Caption = "Misc";
            this.categoryMisc.Properties.Value = this.richEditControl1;
            // 
            // rowOptions
            // 
            this.rowOptions.ChildRows.AddRange(new DevExpress.XtraVerticalGrid.Rows.BaseRow[] {
            this.rowOptions_Export});
            this.rowOptions.Height = 16;
            this.rowOptions.IsChildRowsLoaded = true;
            this.rowOptions.Name = "rowOptions";
            this.rowOptions.Properties.Caption = "Options";
            this.rowOptions.Properties.FieldName = "Options";
            this.rowOptions.Properties.Value = this.richEditControl1.Options;
            // 
            // rowOptions_Export
            // 
            this.rowOptions_Export.ChildRows.AddRange(new DevExpress.XtraVerticalGrid.Rows.BaseRow[] {
            this.rowOptions_Export_PlainText});
            this.rowOptions_Export.IsChildRowsLoaded = true;
            this.rowOptions_Export.Name = "rowOptions_Export";
            this.rowOptions_Export.Properties.Caption = "Export";
            this.rowOptions_Export.Properties.FieldName = "Options.Export";
            this.rowOptions_Export.Properties.Value = this.richEditControl1.Options.Export;
            // 
            // rowOptions_Export_PlainText
            // 
            this.rowOptions_Export_PlainText.ChildRows.AddRange(new DevExpress.XtraVerticalGrid.Rows.BaseRow[] {
            this.rowOptions_Export_PlainText_Encoding,
            this.rowOptions_Export_PlainText_ExportHiddenText,
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering,
            this.rowOptions_Export_PlainText_FieldCodeStartMarker,
            this.rowOptions_Export_PlainText_FieldCodeEndMarker,
            this.rowOptions_Export_PlainText_FieldResultEndMarker,
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat,
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat,
            this.rowOptions_Export_PlainText_FootNoteSeparator,
            this.rowOptions_Export_PlainText_EndNoteSeparator,
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark,
            this.rowOptions_Export_PlainText_ExportedDocumentProperties});
            this.rowOptions_Export_PlainText.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText.Name = "rowOptions_Export_PlainText";
            this.rowOptions_Export_PlainText.Properties.Caption = "PlainText";
            this.rowOptions_Export_PlainText.Properties.FieldName = "Options.Export.PlainText";
            this.rowOptions_Export_PlainText.Properties.Value = this.richEditControl1.Options.Export.PlainText;
            // 
            // rowOptions_Export_PlainText_Encoding
            // 
            this.rowOptions_Export_PlainText_Encoding.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_Encoding.Name = "rowOptions_Export_PlainText_Encoding";
            this.rowOptions_Export_PlainText_Encoding.Properties.Caption = "Encoding";
            this.rowOptions_Export_PlainText_Encoding.Properties.FieldName = "Options.Export.PlainText.Encoding";
            this.rowOptions_Export_PlainText_Encoding.Properties.Value = ((object)(resources.GetObject("rowOptions_Export_PlainText_Encoding.Properties.Value")));
            // 
            // rowOptions_Export_PlainText_ExportHiddenText
            // 
            this.rowOptions_Export_PlainText_ExportHiddenText.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_ExportHiddenText.Name = "rowOptions_Export_PlainText_ExportHiddenText";
            this.rowOptions_Export_PlainText_ExportHiddenText.Properties.Caption = "ExportHiddenText";
            this.rowOptions_Export_PlainText_ExportHiddenText.Properties.FieldName = "Options.Export.PlainText.ExportHiddenText";
            this.rowOptions_Export_PlainText_ExportHiddenText.Properties.Value = false;
            // 
            // rowOptions_Export_PlainText_ExportBulletsAndNumbering
            // 
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering.Name = "rowOptions_Export_PlainText_ExportBulletsAndNumbering";
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering.Properties.Caption = "ExportBulletsAndNumbering";
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering.Properties.FieldName = "Options.Export.PlainText.ExportBulletsAndNumbering";
            this.rowOptions_Export_PlainText_ExportBulletsAndNumbering.Properties.Value = true;
            // 
            // rowOptions_Export_PlainText_FieldCodeStartMarker
            // 
            this.rowOptions_Export_PlainText_FieldCodeStartMarker.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_FieldCodeStartMarker.Name = "rowOptions_Export_PlainText_FieldCodeStartMarker";
            this.rowOptions_Export_PlainText_FieldCodeStartMarker.Properties.Caption = "FieldCodeStartMarker";
            this.rowOptions_Export_PlainText_FieldCodeStartMarker.Properties.FieldName = "Options.Export.PlainText.FieldCodeStartMarker";
            this.rowOptions_Export_PlainText_FieldCodeStartMarker.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_FieldCodeEndMarker
            // 
            this.rowOptions_Export_PlainText_FieldCodeEndMarker.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_FieldCodeEndMarker.Name = "rowOptions_Export_PlainText_FieldCodeEndMarker";
            this.rowOptions_Export_PlainText_FieldCodeEndMarker.Properties.Caption = "FieldCodeEndMarker";
            this.rowOptions_Export_PlainText_FieldCodeEndMarker.Properties.FieldName = "Options.Export.PlainText.FieldCodeEndMarker";
            this.rowOptions_Export_PlainText_FieldCodeEndMarker.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_FieldResultEndMarker
            // 
            this.rowOptions_Export_PlainText_FieldResultEndMarker.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_FieldResultEndMarker.Name = "rowOptions_Export_PlainText_FieldResultEndMarker";
            this.rowOptions_Export_PlainText_FieldResultEndMarker.Properties.Caption = "FieldResultEndMarker";
            this.rowOptions_Export_PlainText_FieldResultEndMarker.Properties.FieldName = "Options.Export.PlainText.FieldResultEndMarker";
            this.rowOptions_Export_PlainText_FieldResultEndMarker.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_FootNoteNumberStringFormat
            // 
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat.Name = "rowOptions_Export_PlainText_FootNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat.Properties.Caption = "FootNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat.Properties.FieldName = "Options.Export.PlainText.FootNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_FootNoteNumberStringFormat.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_EndNoteNumberStringFormat
            // 
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat.Name = "rowOptions_Export_PlainText_EndNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat.Properties.Caption = "EndNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat.Properties.FieldName = "Options.Export.PlainText.EndNoteNumberStringFormat";
            this.rowOptions_Export_PlainText_EndNoteNumberStringFormat.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_FootNoteSeparator
            // 
            this.rowOptions_Export_PlainText_FootNoteSeparator.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_FootNoteSeparator.Name = "rowOptions_Export_PlainText_FootNoteSeparator";
            this.rowOptions_Export_PlainText_FootNoteSeparator.Properties.Caption = "FootNoteSeparator";
            this.rowOptions_Export_PlainText_FootNoteSeparator.Properties.FieldName = "Options.Export.PlainText.FootNoteSeparator";
            this.rowOptions_Export_PlainText_FootNoteSeparator.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_EndNoteSeparator
            // 
            this.rowOptions_Export_PlainText_EndNoteSeparator.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_EndNoteSeparator.Name = "rowOptions_Export_PlainText_EndNoteSeparator";
            this.rowOptions_Export_PlainText_EndNoteSeparator.Properties.Caption = "EndNoteSeparator";
            this.rowOptions_Export_PlainText_EndNoteSeparator.Properties.FieldName = "Options.Export.PlainText.EndNoteSeparator";
            this.rowOptions_Export_PlainText_EndNoteSeparator.Properties.Value = "";
            // 
            // rowOptions_Export_PlainText_ExportFinalParagraphMark
            // 
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark.Name = "rowOptions_Export_PlainText_ExportFinalParagraphMark";
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark.Properties.Caption = "ExportFinalParagraphMark";
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark.Properties.FieldName = "Options.Export.PlainText.ExportFinalParagraphMark";
            this.rowOptions_Export_PlainText_ExportFinalParagraphMark.Properties.Value = DevExpress.XtraRichEdit.Export.PlainText.ExportFinalParagraphMark.Never;
            // 
            // rowOptions_Export_PlainText_ExportedDocumentProperties
            // 
            this.rowOptions_Export_PlainText_ExportedDocumentProperties.IsChildRowsLoaded = true;
            this.rowOptions_Export_PlainText_ExportedDocumentProperties.Name = "rowOptions_Export_PlainText_ExportedDocumentProperties";
            this.rowOptions_Export_PlainText_ExportedDocumentProperties.Properties.Caption = "ExportedDocumentProperties";
            this.rowOptions_Export_PlainText_ExportedDocumentProperties.Properties.FieldName = "Options.Export.PlainText.ExportedDocumentProperties";
            this.rowOptions_Export_PlainText_ExportedDocumentProperties.Properties.Value = ((DevExpress.XtraRichEdit.Export.DocumentPropertyNames)(((((((((((((((((DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Category | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.ContentStatus) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.ContentType) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Created) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Creator) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Description) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Identifier) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Keywords) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Language) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.LastModifiedBy) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.LastPrinted) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Modified) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Revision) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Subject) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Title) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.Version) 
            | DevExpress.XtraRichEdit.Export.DocumentPropertyNames.CustomProperties)));
            // 
            // memoEdit1
            // 
            this.memoEdit1.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.memoEdit1.Location = new System.Drawing.Point(343, 337);
            this.memoEdit1.Name = "memoEdit1";
            this.memoEdit1.Size = new System.Drawing.Size(665, 225);
            this.memoEdit1.TabIndex = 6;
            // 
            // defaultLookAndFeel1
            // 
            this.defaultLookAndFeel1.LookAndFeel.SkinName = "Office 2016 Colorful";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1008, 562);
            this.Controls.Add(this.richEditControl1);
            this.Controls.Add(this.memoEdit1);
            this.Controls.Add(this.panelControl1);
            this.Controls.Add(this.dockPanel1);
            this.Name = "Form1";
            this.Text = "Plain Text Export Example";
            this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
            ((System.ComponentModel.ISupportInitialize)(this.panelControl1)).EndInit();
            this.panelControl1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dockManager1)).EndInit();
            this.dockPanel1.ResumeLayout(false);
            this.dockPanel1_Container.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.propertyGridControl1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.memoEdit1.Properties)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraEditors.PanelControl panelControl1;
        private DevExpress.XtraEditors.SimpleButton btnExport;
        private DevExpress.XtraRichEdit.RichEditControl richEditControl1;
        private DevExpress.XtraBars.Docking.DockManager dockManager1;
        private DevExpress.XtraBars.Docking.DockPanel dockPanel1;
        private DevExpress.XtraBars.Docking.ControlContainer dockPanel1_Container;
        private DevExpress.XtraVerticalGrid.PropertyGridControl propertyGridControl1;
        private DevExpress.XtraEditors.MemoEdit memoEdit1;
        private DevExpress.XtraVerticalGrid.Rows.CategoryRow categoryMisc;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_Encoding;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_ExportHiddenText;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_ExportBulletsAndNumbering;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_FieldCodeStartMarker;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_FieldCodeEndMarker;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_FieldResultEndMarker;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_FootNoteNumberStringFormat;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_EndNoteNumberStringFormat;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_FootNoteSeparator;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_EndNoteSeparator;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_ExportFinalParagraphMark;
        private DevExpress.XtraVerticalGrid.Rows.PGridEditorRow rowOptions_Export_PlainText_ExportedDocumentProperties;
        private DevExpress.LookAndFeel.DefaultLookAndFeel defaultLookAndFeel1;
    }
}

