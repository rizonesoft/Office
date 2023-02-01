using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using Rizonesoft.Properties;
using DevExpress.XtraBars.Helpers;
using DevExpress.LookAndFeel;

namespace Rizonesoft.Verbum.Configuration
{
    public partial class OptionsForm : DevExpress.XtraEditors.XtraForm
    {

        private AppConfig conf = AppConfig.GetInstance();

        public OptionsForm()
        {
            InitializeComponent();

            this.checkConvStURLs.Checked = Settings.Default.OptionsConvStaticURLs;
            SkinHelper.InitSkinGallery(this.gallSkins);
            this.buttApply.Enabled = false;

        }

        private void checkConvStURLs_CheckedChanged(object sender, EventArgs e)
        {
            this.buttApply.Enabled = true;
        }

        private void applyOptions()
        {
            conf.applicationSkin = UserLookAndFeel.Default.SkinName;
            //Settings.Default.OptionsConvStaticURLs = this.checkConvStURLs.Checked;
            //conf.Store();
        }

        private void buttApply_Click(object sender, EventArgs e)
        {
            this.applyOptions();
            this.buttApply.Enabled = false;
        }

        private void OptionsForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            UserLookAndFeel.Default.SkinName = conf.applicationSkin;
        }

        private void galleryControlGallery1_ItemClick(object sender, DevExpress.XtraBars.Ribbon.GalleryItemClickEventArgs e)
        {
            this.buttApply.Enabled = true;
        }

        private void buttOk_Click(object sender, EventArgs e)
        {

        }

       
    }
}