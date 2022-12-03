#region #usings
using DevExpress.Office.Utils;
using DevExpress.XtraRichEdit.API.Native;
using System.Drawing;
using System.Windows.Forms;
#endregion #usings

namespace RichEdit_GetPositionFromPoint
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm
    {
        public Form1()
        {
            InitializeComponent();
            #region #subscribe
            this.richEditControl1.MouseMove += richEditControl1_MouseMove;
            #endregion #subscribe
        }
        #region #getpositionfrompoint
        void richEditControl1_MouseMove(object sender, MouseEventArgs e)
        {
            Point docPoint = Units.PixelsToDocuments(e.Location,
        richEditControl1.DpiX, richEditControl1.DpiY);
            DocumentPosition pos = richEditControl1.GetPositionFromPoint(docPoint);
            if (pos != null)
                this.Text = System.String.Format("Mouse is over position {0}",pos);
            else this.Text = "";
        }
        #endregion #getpositionfrompoint
    }
}
