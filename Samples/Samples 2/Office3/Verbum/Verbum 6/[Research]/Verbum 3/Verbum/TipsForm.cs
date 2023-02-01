using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using System.IO;
using Rizonesoft.Verbum.Properties;

namespace Rizonesoft.Verbum
{
    public partial class TipsForm : DevExpress.XtraEditors.XtraForm
    {

        private const string tipFile = "\\Advices.txt";
        private string[] allTips;
        private int tipCount = 0;
        private string currentTip = "";
        private static string appPath;

        public TipsForm()
        {
            InitializeComponent();

            try
            {
                appPath = GetAppPath(); // get the application path

                try
                {
                    StreamReader reader = new StreamReader(appPath + tipFile);
                    string tipBlock = reader.ReadToEnd();
                    reader.Close();
                    allTips = tipBlock.Split(new char[] { '\n' });
                }
                catch (Exception ex)
                {
                    MessageBox.Show(String.Format("Could not open tips file - {0}", ex.Message.ToString()));
                    smBtnNext.Enabled = false;
                    return;
                }

                tipCount = (Settings.Default.TipsCount + 1) % allTips.Length; // increment the count for next tip
                tipCount = tipCount % allTips.Length; // make sure we don't overrun tips file
                UpdateTip();

                this.chkShowTips.Checked = Settings.Default.ShowTipsOnStartup;

            }
            catch (Exception ex)
            {
                MessageBox.Show(String.Format("Trouble Creating Tip Dialog {0}", ex.ToString()));
            }

        }

        static string GetAppPath()
        {
            string path = Path.GetDirectoryName(Application.ExecutablePath);
            return path;
        }

        private void UpdateTip()
        {
            currentTip = allTips[tipCount];
            lblTip.Text = currentTip;
        }

        private void smBtnNext_Click(object sender, EventArgs e)
        {
            tipCount = (tipCount + 1) % allTips.Length; // increment the count for next tip
            UpdateTip();
        }

        private void TipsForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            // write the current index
            Settings.Default.TipsCount = tipCount; // increment count
            // write the startup flag
            Settings.Default.ShowTipsOnStartup = this.chkShowTips.Checked;
            Settings.Default.Save();
        }

        private void smBtnOK_Click(object sender, EventArgs e)
        {
            this.Close();
        }

    }

}