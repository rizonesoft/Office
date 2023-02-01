using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using DevExpress.Skins;
using DevExpress.LookAndFeel;
using DevExpress.UserSkins;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraEditors;

namespace Sheets
{
    public partial class WorkbookForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        public WorkbookForm()
        {
            InitializeComponent();
            WindowsFormsSettings.DefaultLookAndFeel.SetSkinStyle("Office 2019 Colorful", "Forest");

        }

    }
}