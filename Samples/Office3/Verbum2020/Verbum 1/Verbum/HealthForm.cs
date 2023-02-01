using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using System.IO;

namespace Rizonesoft.Verbum
{
    public partial class HealthForm : DevExpress.XtraEditors.XtraForm
    {
        public HealthForm()
        {
            InitializeComponent();
            fileRibugWatcher.Filter = "*.log";
            fileRibugWatcher.Path = Configuration.UserAppDataPath;
            readRibugFile();

        }

        private void fileSystemWatcher_Changed(object sender, FileSystemEventArgs e)
        {
            readRibugFile();
        }

        private void readRibugFile()
        {
            if (File.Exists(Cataloguing.UserBugFilePath))
            {
                StreamReader bugReader = new StreamReader(Cataloguing.UserBugFilePath, Encoding.UTF8);
                this.memoBoxConsole.Text = bugReader.ReadToEnd();
                bugReader.Close();
            }

        }

        private void memoBoxConsole_TextChanged(object sender, EventArgs e)
        {
            this.memoBoxConsole.SelectionStart = this.memoBoxConsole.Text.Length;
            this.memoBoxConsole.ScrollToCaret();
            this.memoBoxConsole.Refresh();
        }

        private void componentsButton_Click(object sender, EventArgs e)
        {
            DevExpress.Utils.About.frmAbout DevExAboutDlg = new DevExpress.Utils.About.frmAbout("Rizonesoft is powered by DevExpress");
            DevExAboutDlg.ShowDialog();
        }

    }
}