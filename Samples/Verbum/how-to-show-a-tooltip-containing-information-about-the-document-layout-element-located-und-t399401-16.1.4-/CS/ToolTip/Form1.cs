using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using System;
using System.Drawing;
using DevExpress.Utils;

namespace ToolTip
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        public Form1()
        {
            InitializeComponent();
            richEditControl1.LoadDocument("../../Resources/HitTest.docx");
            toolTipController1.AddClientControl(richEditControl1);
            toolTipController1.GetActiveObjectInfo += ToolTipController_GetActiveObjectInfo;
        }

        void ToolTipController_GetActiveObjectInfo(object sender, ToolTipControllerGetActiveObjectInfoEventArgs e)
        {
            #region #HitTest
            if (!e.SelectedControl.Equals(richEditControl1))
                return;

            //Obtain the mouse cursor's layout position on the page and the current page index:
            PageLayoutPosition pageLayoutPosition = richEditControl1.ActiveView.GetDocumentLayoutPosition(e.ControlMousePosition);
            if (pageLayoutPosition == null)
                return;            
            
            Point point = pageLayoutPosition.Position;  
            int pageIndex = pageLayoutPosition.PageIndex;
            LayoutPage layoutPage = richEditControl1.DocumentLayout.GetPage(pageIndex);
            
            //Create a HitTestManager instance: 
            HitTestManager hitTest = new HitTestManager(richEditControl1.DocumentLayout);

            //Perform the hit test and pass the result to the RichEditHitTestResult object:
            RichEditHitTestResult result = hitTest.HitTest(layoutPage, point);
            if (result != null)
            {
                //Retrieve the current layout element type:
                LayoutElement element = result.LayoutElement;
                string text = element.Type.ToString();

                //Obtain the the text character and its bounds under the mouse position              
                if (element.Type == LayoutType.CharacterBox)
                {
                    text += String.Format(" : \"{0}\"", (element as CharacterBox).Text);
                    text += GetBounds(element);
                    if (element.Parent.Type == LayoutType.PlainTextBox)
                    {
                        text += String.Format("\r\nPlainTextBox : \"{0}\"", (element.Parent as PlainTextBox).Text);
                        text += GetBounds(element.Parent);
                    }
                }
                else
                {
                    //Get the hovered element's bounds:
                    text += GetBounds(element);
                }

                //Get the element's location:
                string title = GetLocation(element);

                //Display all retrieved information in the tooltip:
                e.Info = new ToolTipControlInfo(element.Bounds, text, title, ToolTipIconType.Information);
                
            }
            #endregion #HitTest
        }
        string GetBounds(LayoutElement element)
        {
            return String.Format("\r\nBounds : {0}", element.Bounds);
        }
        string GetLocation(LayoutElement element)
        {
            while (element != null)
            {
                switch (element.Type)
                {
                    case LayoutType.CommentsArea:
                        return "Comments Area Location";
                    case LayoutType.Header:
                        return "Header Location";
                    case LayoutType.Footer:
                        return "Footer Location";
                }
                element = element.Parent;
            }
            return "Page Location";
        }        
    }
}
