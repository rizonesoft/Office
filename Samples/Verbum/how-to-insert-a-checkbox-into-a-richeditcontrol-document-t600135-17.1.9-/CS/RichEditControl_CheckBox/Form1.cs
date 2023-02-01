using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Layout;
using DevExpress.XtraRichEdit.API.Native;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace RichEditControl_CheckBox
{
    public partial class Form1 : DevExpress.XtraEditors.XtraForm
    {
        static readonly string checkedCheckBox = '\u2612'.ToString();
        static readonly string uncheckedCheckBox = '\u2610'.ToString();
        public Form1()
        {
            InitializeComponent();
        }
        private void barButtonItem1_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            DocumentPosition caretPosition = richEditControl1.Document.CaretPosition;
            SubDocument document = caretPosition.BeginUpdateDocument();
            DocumentRange checkBox = document.InsertText(caretPosition, uncheckedCheckBox);
            CharacterProperties cp = document.BeginUpdateCharacters(checkBox);
            cp.FontName = "MS Gothic";
            document.EndUpdateCharacters(cp);
            caretPosition.EndUpdateDocument(document);
        }
        private void richEditControl1_MouseClick(object sender, MouseEventArgs e)
        {
            PageLayoutPosition pageLayoutPosition = richEditControl1.ActiveView.GetDocumentLayoutPosition(e.Location);
            if (pageLayoutPosition == null)
                return;
            int pageIndex = pageLayoutPosition.PageIndex;
            Point point = pageLayoutPosition.Position;
            LayoutPage layoutPage = richEditControl1.DocumentLayout.GetPage(pageIndex);
            HitTestManager hitTest = new HitTestManager(richEditControl1.DocumentLayout);
            RichEditHitTestResult result = hitTest.HitTest(layoutPage, point);
            if (result.LayoutElement is CharacterBox && richEditControl1.Document.Selection.Length == 0)
            {
                CharacterBox character = (CharacterBox)result.LayoutElement;
                DocumentPosition caretPosition = richEditControl1.Document.CaretPosition;
                SubDocument document = caretPosition.BeginUpdateDocument();
                if (document.GetSubDocumentType() == GetLocation(character.Parent))
                {
                    DocumentRange characterRange = document.CreateRange(character.Range.Start, 1);
                    UpdateCheckState(document, characterRange, character.Text);
                }
                caretPosition.EndUpdateDocument(document);
            }
        }
        public void UpdateCheckState(SubDocument document, DocumentRange range, string prevState)
        {
            if (prevState.Equals(checkedCheckBox))
                document.Replace(range, uncheckedCheckBox);
            else if (prevState.Equals(uncheckedCheckBox))
                document.Replace(range, checkedCheckBox);
        }
        public SubDocumentType GetLocation(LayoutElement element)
        {
            while (element != null)
            {
                switch (element.Type)
                {
                    case LayoutType.CommentsArea:
                        return SubDocumentType.Comment;
                    case LayoutType.Header:
                        return SubDocumentType.Header;
                    case LayoutType.Footer:
                        return SubDocumentType.Footer;
                    case LayoutType.TextBox:
                        return SubDocumentType.TextBox;
                }
                element = element.Parent;
            }
            return SubDocumentType.Main;
        }
    }
}
