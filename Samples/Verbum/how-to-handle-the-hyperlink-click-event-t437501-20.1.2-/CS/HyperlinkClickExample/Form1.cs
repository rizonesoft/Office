using DevExpress.Office.Utils;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using HyperlinkClickExample.Forms;
using System;
using System.Collections.Generic;
using System.Drawing;

namespace HyperlinkClickExample
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        #region #DataList
        static List<string> products = CreateProducts();
        static List<string> CreateProducts()
        {
            List<string> result = new List<string>();
            result.Add("XtraScheduler™ Suite");
            result.Add("XtraRichEdit™ Suite");
            result.Add("XtraSpellChecker™");
            result.Add("XtraReports™ Suite");
            result.Add("XtraGrid™ Suite");
            result.Add("XtraPivotGrid™ Suite");
            result.Add("XtraTreeList™ Suite");
            result.Add("XtraGauges™ Suite");
            result.Add("XtraWizard™ Control");
            result.Add("XtraVerticalGrid™ Suite");
            result.Add("XtraCharts™ Suite");
            result.Add("XtraLayoutControl™ Suite");
            result.Add("XtraNavBar™");
            result.Add("XtraEditors™ Library");
            result.Add("XtraPrinting™ Library");
            return result;
        }
        #endregion #DataList

        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("HyperlinkClickHandling.rtf");
            richEditControl1.HyperlinkClick += new HyperlinkClickEventHandler(OnHyperlinkClick);
        }

        #region #HyperlinkClickEvent
        public Hyperlink activeLink;
        void OnHyperlinkClick(object sender, HyperlinkClickEventArgs e)
        {
            activeLink = e.Hyperlink;
            SelectProductForm form = new SelectProductForm(products);
            // Set the Commit event handler:
            form.Commit += OnProductFormCommit;
            //Set the Range property to the hyperlink range:
            form.Range =  activeLink.Range;
            //Set the Location property to specify the location where the form is going to be invoked:  
            form.Location = GetFormLocation();
            form.Show();
            e.Handled = true;            
        }

        //This method places the form to the right of the cursor position: 
        Point GetFormLocation()
        {
            DocumentPosition position = this.richEditControl1.Document.CaretPosition;
            Rectangle rect = this.richEditControl1.GetBoundsFromPosition(position);
            Point location = new Point(rect.Right, rect.Bottom);
            Point localPoint = Units.DocumentsToPixels(location, this.richEditControl1.DpiX, this.richEditControl1.DpiY);
            return this.richEditControl1.PointToScreen(localPoint);
        }
        #endregion #HyperlinkClickEvent

        #region #OnProductFormCommit

        // Handle the event to replace the hyperlink with the selected item value: 
        void OnProductFormCommit(object sender, EventArgs e)
        {
            SelectProductForm form = (SelectProductForm)sender;
            string value = (string)form.EditValue;
            Document document = this.richEditControl1.Document;
            document.BeginUpdate();
            document.Replace(form.Range, value);
            //Uncomment this line to remove the clicked hyperlink once a desired value has been selected
            //richEditControl1.Document.Hyperlinks.Remove(activeLink);
            document.EndUpdate();
        }

        #endregion #OnProductFormCommit


        
        
    }
}



