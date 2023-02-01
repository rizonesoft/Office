using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraEditors;
using DevExpress.LookAndFeel;
using Datum.Verbum.Properties;


namespace Datum.Verbum
{
    public partial class OptionsForm : DevExpress.XtraEditors.XtraForm
    {
        public OptionsForm()
        {
            InitializeComponent();

            //this.checkConvStURLs.Checked = Settings.Default.OptionsConvStaticURLs;
            DevExpress.XtraBars.Helpers.SkinHelper.InitSkinGallery(this.gallSkins);
            this.checkAllowFormSkins.Checked = DevExpress.Skins.SkinManager.AllowFormSkins;
            this.checkAllowArrowDragIndicators.Checked = DevExpress.Skins.SkinManager.AllowArrowDragIndicators;
            this.checkAllowWindowGhosting.Checked = DevExpress.Skins.SkinManager.AllowWindowGhosting;
            this.buttonApply.Enabled = false;
        }

        private void buttonApply_Click(object sender, EventArgs e)
        {
            applyOptions();
            this.buttonApply.Enabled = false;
        }

        private void gallSkins_Click(object sender, EventArgs e)
        {
            this.buttonApply.Enabled = true;
        }

        private void checkAllowFrmSkins_CheckedChanged(object sender, EventArgs e)
        {
            this.buttonApply.Enabled = true;
        }

        private void checkAllowArrowDragIndicators_CheckedChanged(object sender, EventArgs e)
        {
            this.buttonApply.Enabled = true;
        }

        private void checkAllowWindowGhosting_CheckedChanged(object sender, EventArgs e)
        {
            this.buttonApply.Enabled = true;
        }

        private void applyOptions()
        {
            if (this.checkAllowFormSkins.Checked)
            { DevExpress.Skins.SkinManager.EnableFormSkins(); }
            else
            { DevExpress.Skins.SkinManager.DisableFormSkins(); }

            DevExpress.Skins.SkinManager.AllowArrowDragIndicators = checkAllowArrowDragIndicators.Checked;
            DevExpress.Skins.SkinManager.AllowWindowGhosting = checkAllowWindowGhosting.Checked;

            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();

            Settings.Default.AllowFormSkins = DevExpress.Skins.SkinManager.AllowFormSkins;
            Settings.Default.ApplicationSkinName = UserLookAndFeel.Default.SkinName;
            //Settings.Default.OptionsConvStaticURLs = this.checkConvStURLs.Checked;
            Settings.Default.Save();
        }

        private void buttonOK_Click(object sender, EventArgs e)
        {
            applyOptions();
            this.Close();
        }

        private void buttonCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }





    }
}