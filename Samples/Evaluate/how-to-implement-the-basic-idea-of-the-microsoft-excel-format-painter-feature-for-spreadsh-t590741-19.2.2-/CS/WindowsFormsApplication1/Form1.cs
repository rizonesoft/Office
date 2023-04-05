using DevExpress.Spreadsheet;
using System;
using System.Linq;
using System.Windows.Forms;

namespace WindowsFormsApplication1 {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();
            FormatPainterProvider formatPainterProvider = new FormatPainterProvider();
            formatPainterProvider.RegisterFormatPainter(spreadsheetControl1, biFormatPainter);
        }
    }

    
}
