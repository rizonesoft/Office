using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.Internal;
using DevExpress.XtraRichEdit.Model;

namespace BizPad.Extensions {
    public class RichEditEx : RichEditControl, IInnerRichEditControlOwner {
        protected override void ActivateViewPlatformSpecific(RichEditView view) {
            base.ActivateViewPlatformSpecific(view);
            RemoveService(typeof(IFieldCalculatorService));
            AddService(typeof(IFieldCalculatorService), new FieldCalculatorServiceEx());
        }
    }
}
