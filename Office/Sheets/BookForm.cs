﻿using DevExpress.LookAndFeel;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Rizonesoft.Office.Sheets
{
    public partial class BookForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        private static NLog.Logger nlogger = NLog.LogManager.GetCurrentClassLogger();
        internal string fileName;

        public BookForm()
        {
            InitializeComponent();

            UserLookAndFeel.Default.StyleChanged += Default_StyleChanged;
        }


        #region Properties

        public string FileName
        {
            get
            {
                return this.fileName;
            }
        }

        #endregion Properties


        #region Workbook Processing

        public void OpenFile(string bookName, int bookIndex)
        {
            if (!string.IsNullOrEmpty(bookName))
            {
                fileName = bookName;
                SetDocumentCaption(bookName);
            }
            else
            {
                Text = @"Book " + bookIndex.ToString() + string.Empty;
            }
        }

        private void SetDocumentCaption(string fileName)
        {
            string fileCaption = Path.GetFileName(fileName);
            if (fileCaption.Length > 28)
            {
                fileCaption = fileCaption.Remove(29) + "...";
            }
            Text = fileCaption;
        }

        #endregion Workbook Processing


        #region Events

        private void Default_StyleChanged(object sender, EventArgs e)
        {
            Settings.SaveSetting("Rizonesoft\\Sheets\\Skins", "Skin", WindowsFormsSettings.DefaultLookAndFeel.ActiveSkinName);
            Settings.SaveSetting("Rizonesoft\\Sheets\\Skins", "Palette", WindowsFormsSettings.DefaultLookAndFeel.ActiveSvgPaletteName);
        }

        #endregion Events


    }
}