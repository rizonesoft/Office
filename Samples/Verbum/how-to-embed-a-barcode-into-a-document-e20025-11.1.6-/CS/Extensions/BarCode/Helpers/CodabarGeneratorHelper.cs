namespace BizPad {
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Drawing;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraRichEdit.Fields;

    internal class CodabarGeneratorHelper : CodabarGenerator, IBarCodeGenerator {
        static Dictionary<string, CodabarStartStopPair> CodabarStartStopPairs = new Dictionary<string, CodabarStartStopPair>();
        static CodabarGeneratorHelper() {
            CodabarStartStopPairs.Add("at", CodabarStartStopPair.AT);
            CodabarStartStopPairs.Add("bn", CodabarStartStopPair.BN);
            CodabarStartStopPairs.Add("cstar", CodabarStartStopPair.CStar);
            CodabarStartStopPairs.Add("de", CodabarStartStopPair.DE);
            CodabarStartStopPairs.Add("none", CodabarStartStopPair.None);
        }

        void IBarCodeGenerator.Initialize(InstructionCollection switches) {
            string p = switches.GetString("p") ?? String.Empty;
            
            CodabarStartStopPair startStopPair = CodabarStartStopPair.None;
            if (CodabarStartStopPairs.ContainsKey(p.ToLower())) {
                startStopPair = CodabarStartStopPairs[p.ToLower()]; 
            }

            this.StartStopPair = startStopPair;

            float r = 0f;
            if (!float.TryParse(switches.GetString("r") ?? String.Empty, out r)) {
                r = 0f;
            }

            if (r < 2 || r > 3) {
                r = 2f;
            }

            this.WideNarrowRatio = r;
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

        string IBarCodeGenerator.GetValidCharSet() {
            return base.GetValidCharSet();
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
