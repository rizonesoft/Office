namespace BizPad {
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using DevExpress.XtraRichEdit.Fields;
    using DevExpress.XtraRichEdit.Model;
    using System.IO;
    using DevExpress.XtraCharts;
    using System.Drawing.Imaging;
    using DevExpress.XtraRichEdit.Utils;
    using System.Text;
    using System.Drawing;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraPrinting.BarCode.Native;
    using System.Collections;
    using DevExpress.XtraPrinting;
    using System.Threading;
    using DevExpress.XtraPrinting.Localization;
    using DevExpress.Utils.Text;

    internal class Code128GeneratorHelper : Code128Generator, IBarCodeGenerator {
        static Dictionary<string, Code128Charset> Subtypes = new Dictionary<string, Code128Charset>();
        static Code128GeneratorHelper() {
            Subtypes.Add("128a", Code128Charset.CharsetA);
            Subtypes.Add("128b", Code128Charset.CharsetB);
            Subtypes.Add("128c", Code128Charset.CharsetC);
        }
        
        public Code128GeneratorHelper() {
        }

        protected Code128GeneratorHelper(Code128Generator source)
            : base(source) {
        }

        void IBarCodeGenerator.Initialize(InstructionCollection switches) {
            string p = switches.GetString("p") ?? String.Empty;

            Code128Charset subtype = Code128Charset.CharsetB;
            if (Subtypes.ContainsKey(p.ToLower())) {
                subtype = Subtypes[p.ToLower()];
            }

            this.CharacterSet = subtype;
        }

        public bool SupressAutoTextAlignment() {
            return false;
        }

        string IBarCodeGenerator.GetValidCharSet() {
            return base.GetValidCharSet();
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
