// Developer Express Code Central Example:
// How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
// 
// This example demonstrates how to copy the characters and paragraphs properties
// and apply formatting to the selected text. Try the Format Painter button on the
// ribbon Home tab.
// 
// To obtain the selected text range, the
// RichEditDocument.Document.Selection property is used. The characters and
// paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
// handler. Then, they are stored in the CharacterPropertiesObject and
// ParagraphPropertiesObject object containers.
// 
// In order to change the current
// RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
// the custom MouseCursorCalculator class Calculate method for clarification.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E5223

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Internal;
using DevExpress.XtraRichEdit.Mouse;
using DevExpress.XtraRichEdit.Layout;
using System.ComponentModel;
using DevExpress.Portable.Input;

namespace DXApplication9
{
    public class MyRichEditControl : RichEditControl
    {
        protected override InnerRichEditControl CreateInnerControl()
        {
            return new MyInnerControl(this);
        }

        // Fields...
        private bool _FormatCalculatorEnabled;
        [DefaultValue(false)]
        public bool FormatCalculatorEnabled
        {
            get { return _FormatCalculatorEnabled; }
            set
            {
                _FormatCalculatorEnabled = value;
            }
        }
        
    }

    public class MyInnerControl : InnerRichEditControl
    {
        public MyInnerControl(IInnerRichEditControlOwner owner)
            : base(owner)
        {
        }


        protected override DevExpress.XtraRichEdit.Mouse.MouseCursorCalculator CreateMouseCursorCalculator()
        {
            return new MyMouseCursorCalculator(ActiveView);
        }
    }
    public class MyMouseCursorCalculator : MouseCursorCalculator
    {
        public MyMouseCursorCalculator(RichEditView view)
            : base(view)
        {
            
        }

        public override IPortableCursor Calculate(RichEditHitTestResultCore hitTestResult, Point physicalPoint)
        {

            if ((View.Control as MyRichEditControl).FormatCalculatorEnabled)
                return DevExpress.XtraRichEdit.Utils.RichEditCursors.Hand;

            return base.Calculate(hitTestResult, physicalPoint);
        }
    }

}
