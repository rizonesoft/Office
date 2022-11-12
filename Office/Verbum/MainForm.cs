using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace Rizonesoft.Office.Verbum
{
    public partial class MainForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {

        internal int documentIndex = 0;
        internal bool IsFloating = false;
        private static string formHeading = "Rizonesoft Verbum";
        bool updatedZoom = false;
        internal BackgroundWorker updateWorker;

        public MainForm(string fileName)
        {
            InitializeComponent();
        }
    }
}
