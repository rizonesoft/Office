namespace BizPad {
    using System.Collections;
    using System.Drawing;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraRichEdit.Fields;
    using System.Collections.Generic;
    using System;

    internal class PDF417GeneratorHelper : PDF417Generator, IBarCodeGenerator {
        static Dictionary<string, PDF417CompactionMode> Modes = new Dictionary<string, PDF417CompactionMode>();
        static PDF417GeneratorHelper() {
            Modes.Add("t", PDF417CompactionMode.Text);
            Modes.Add("text", PDF417CompactionMode.Text);
            Modes.Add("txt", PDF417CompactionMode.Text);
            Modes.Add("b", PDF417CompactionMode.Binary);
            Modes.Add("binary", PDF417CompactionMode.Binary);
            Modes.Add("bin", PDF417CompactionMode.Binary);
        }
        
        void IBarCodeGenerator.Initialize(InstructionCollection switches) {
            string m = switches.GetString("m") ?? String.Empty;

            PDF417CompactionMode mode = PDF417CompactionMode.Text;
            if (Modes.ContainsKey(m.ToLower())) {
                mode = Modes[m.ToLower()];
            }

            this.CompactionMode = mode;

            Nullable<int> r = switches.GetNullableInt("r");
            Nullable<int> c = switches.GetNullableInt("c");
            
            if (c.HasValue && c > 0) {
                this.Columns = c.Value;
            }

            if (r.HasValue && r > 0) {
                this.Rows = r.Value;
            }

            Single p = 0f;
            if (!float.TryParse(switches.GetString("p") ?? String.Empty, out p)) {
                p = 0f;
            }

            if (p <= 0f) {
                p = 3f;
            }

            this.YToXRatio = p;

            Nullable<int> e = switches.GetNullableInt("e");
            if (!e.HasValue || e.Value < 1 || e.Value > 8) {
                e = 2;
            }

            this.ErrorCorrectionLevel = (DevExpress.XtraPrinting.BarCode.ErrorCorrectionLevel)e.Value;

            this.TruncateSymbol = switches.GetBool("o");
        }

        string IBarCodeGenerator.GetValidCharSet() {
            return base.GetValidCharSet();
        }

        ArrayList IBarCodeGenerator.MakeBarCodePattern(string text) {
            return base.MakeBarCodePattern(text);
        }

        public bool SupressAutoTextAlignment() {
            return false;
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
