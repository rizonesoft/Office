namespace BizPad {
    using System.Collections;
    using System.Drawing;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraRichEdit.Fields;

    internal interface IBarCodeGenerator {
        void Initialize(InstructionCollection switches);
        ArrayList MakeBarCodePattern(string text);
        string MakeDisplayText(string text);
        string FormatText(string text);
        bool IsValidPattern(ArrayList pattern);
        bool IsValidTextFormat(string text);
        bool IsValidText(string text);
        float CalcBarCodeWidth(ArrayList pattern);
        float CalcBarCodeHeight(ArrayList pattern);
        string GetValidCharSet();
        bool SupressAutoTextAlignment();
        void DrawBarCode(IGraphics gr, RectangleF barBounds, RectangleF textBounds, IBarCodeData data, float xModule, float yModule);
    }
}