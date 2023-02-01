namespace BizPad {
    using System.Collections;
    using System.Drawing;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraRichEdit.Fields;
    using System.Collections.Generic;
    using System;
    using System.Diagnostics;

    internal class DataMatrixGeneratorHelper : DataMatrixGenerator, IBarCodeGenerator {
        static Dictionary<string, DataMatrixCompactionMode> Modes = new Dictionary<string, DataMatrixCompactionMode>();
        static Dictionary<string, DataMatrixSize> Sizes = new Dictionary<string, DataMatrixSize>();
        static DataMatrixGeneratorHelper() {
            Modes.Add("t", DataMatrixCompactionMode.Text);
            Modes.Add("text", DataMatrixCompactionMode.Text);
            Modes.Add("txt", DataMatrixCompactionMode.Text);
            Modes.Add("b", DataMatrixCompactionMode.Binary);
            Modes.Add("binary", DataMatrixCompactionMode.Binary);
            Modes.Add("bin", DataMatrixCompactionMode.Binary);
            Modes.Add("ascii", DataMatrixCompactionMode.ASCII);
            Modes.Add("a", DataMatrixCompactionMode.ASCII);
            Modes.Add("c40", DataMatrixCompactionMode.C40);
            Modes.Add("c", DataMatrixCompactionMode.C40);
            Modes.Add("edifact", DataMatrixCompactionMode.Edifact);
            Modes.Add("e", DataMatrixCompactionMode.Edifact);
            Modes.Add("x12", DataMatrixCompactionMode.X12);
            Modes.Add("x", DataMatrixCompactionMode.X12);
            foreach (string s in Enum.GetNames(typeof(DataMatrixSize))) {
                if (s.StartsWith("Matrix")) {
                    Sizes.Add(s.Substring("Matrix".Length).ToLower(),
                        (DataMatrixSize)Enum.Parse(typeof(DataMatrixSize), s));
                }
            }
        }
        
        void IBarCodeGenerator.Initialize(InstructionCollection switches) {
            
            string m = switches.GetString("m") ?? String.Empty;

            DataMatrixCompactionMode mode = DataMatrixCompactionMode.ASCII;
            if (Modes.ContainsKey(m.ToLower())) {
                mode = Modes[m.ToLower()];
            }

            if (this.CompactionMode == mode) {
                if (mode == DataMatrixCompactionMode.ASCII) {
                    this.CompactionMode = DataMatrixCompactionMode.Text;
                } else {
                    this.CompactionMode = DataMatrixCompactionMode.ASCII;
                }
            }

            this.CompactionMode = mode;

            string p = switches.GetString("p") ?? String.Empty;

            DataMatrixSize size = DataMatrixSize.MatrixAuto;
            if (Sizes.ContainsKey(p.ToLower())) {
                size = Sizes[p.ToLower()];
            }

            this.MatrixSize = size;

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
