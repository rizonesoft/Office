using DevExpress.LookAndFeel;
using DevExpress.XtraEditors;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Rizonesoft.Office.Verbum
{
    public partial class OptionsForm : DevExpress.XtraEditors.XtraForm
    {
        public OptionsForm()
        {

            InitializeComponent();
            DevExpress.XtraBars.Helpers.SkinHelper.InitSkinGallery(this.skinGallery, true, true);
            DevExpress.XtraBars.Helpers.SkinHelper.InitSkinPaletteGallery(this.skinPaletteGallery);

        }

    }
}
