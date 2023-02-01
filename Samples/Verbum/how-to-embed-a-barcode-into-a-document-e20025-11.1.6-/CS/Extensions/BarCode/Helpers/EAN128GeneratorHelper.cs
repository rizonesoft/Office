namespace BizPad {
    using System.Collections;
    using System.Drawing;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraRichEdit.Fields;
    using System.Collections.Generic;
    using System;

    internal class EAN128GeneratorHelper : EAN128Generator, IBarCodeGenerator {
        static Dictionary<string, Code128Charset> Subtypes = new Dictionary<string, Code128Charset>();
        static EAN128GeneratorHelper() {
            Subtypes.Add("128a", Code128Charset.CharsetA);
            Subtypes.Add("128b", Code128Charset.CharsetB);
            Subtypes.Add("128c", Code128Charset.CharsetC);
        }

        public EAN128GeneratorHelper() {
        }

        void IBarCodeGenerator.Initialize(InstructionCollection switches) {
            string p = switches.GetString("p") ?? String.Empty;

            Code128Charset subtype = Code128Charset.CharsetB;
            if (Subtypes.ContainsKey(p.ToLower())) {
                subtype = Subtypes[p.ToLower()];
            }

            this.CharacterSet = subtype;

            string f = switches.GetString("f") ?? String.Empty;
            if (String.IsNullOrWhiteSpace(f)) {
                f = "#";
            }

            this.FNC1Substitute = f;

            this.HumanReadableText = switches.GetBool("o");
        }

        string IBarCodeGenerator.GetValidCharSet() {
            return base.GetValidCharSet();
        }

        public bool SupressAutoTextAlignment() {
            return false;
        }

        ArrayList IBarCodeGenerator.MakeBarCodePattern(string text) {
            return base.MakeBarCodePattern(text);
        }

        void IBarCodeGenerator.DrawBarCode(IGraphics gr, RectangleF barBounds, RectangleF textBounds, IBarCodeData data, float xModule, float yModule) {
            base.DrawBarCode(gr, barBounds, textBounds, data, xModule, yModule);
        }

        string IBarCodeGenerator.MakeDisplayText(string text) {
            return base.MakeDisplayText(text);
        }

        string IBarCodeGenerator.FormatText(string text) {
            return base.FormatText(text);
        }

        bool IBarCodeGenerator.IsValidPattern(ArrayList pattern) {
            return base.IsValidPattern(pattern);
        }

        bool IBarCodeGenerator.IsValidText(string text) {
            return BarCodeGeneratorHelper.IsValidText(this, text);
        }

        bool IBarCodeGenerator.IsValidTextFormat(string text) {
            return base.IsValidTextFormat(text);
        }

        float IBarCodeGenerator.CalcBarCodeWidth(ArrayList pattern) {
            return base.CalcBarCodeWidth(pattern);
        }

        float IBarCodeGenerator.CalcBarCodeHeight(ArrayList pattern) {
            return base.CalcBarCodeHeight(pattern);
        }
    }
}
