namespace BizPad {
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Threading;
    using DevExpress.Utils.Text;
    using DevExpress.XtraPrinting;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraPrinting.Native;
    using DevExpress.XtraRichEdit.Fields;
    using DevExpress.XtraRichEdit.Utils;

    public class BarCodeImage : IBarCodeData {
        Nullable<int> _Width = null;
        Nullable<int> _Height = null;

        void ParseSizeSwitches(InstructionCollection switches) {
            _Width = switches.GetNullableInt("w");
            _Height = switches.GetNullableInt("h");
        }
        
        string _Data;

        void ParseDataSwitches(InstructionCollection switches) {
            _Data = switches.GetString("d");
        }

        bool _ShowLabel = false;

        void ParseShowLabelSwitches(InstructionCollection switches) {
            _ShowLabel = switches.GetBool("l");
        }

        double _Module = 0d;

        void ParseModuleSize(InstructionCollection switches) {
            string k = switches.GetString("k");
            if (!String.IsNullOrWhiteSpace(k)) {
                double d = 0d;
                if (!double.TryParse(k.Trim(), out d)) {
                    d = 0d;
                }
                _Module = d;
            }
        }

        IBarCodeGenerator _generator;
        IBarCodeGenerator Generator {
            get {
                return _generator;
            }
        }

        void InitializeGenerator(InstructionCollection switches) {
            _generator = BarCodeGeneratorFactory.Create(
                switches.GetString("t"),
                switches);
        }

        public void Initialize(InstructionCollection switches) {
            ParseDataSwitches(switches);
            ParseSizeSwitches(switches);
            ParseShowLabelSwitches(switches);
            ParseModuleSize(switches);
            InitializeGenerator(switches);
        }

        class GraphicsHelper : IGraphics {
            Graphics _gr;

            public GraphicsHelper(Graphics gr) {
                if (gr == null)
                    throw new ArgumentNullException("gr", "gr is null.");
                _gr = gr;
            }

            void IDisposable.Dispose() {
                Dictionary<Color, Brush> brushes = Interlocked.Exchange<Dictionary<Color, Brush>>(
                            ref _Brushes, null);
                if (brushes != null) {
                    foreach(KeyValuePair<Color, Brush> k in brushes) {
                        k.Value.Dispose();
                    }
                }
                Dictionary<Color, Pen> pens = Interlocked.Exchange<Dictionary<Color, Pen>>(
                            ref _Pens, null);
                if (pens != null) {
                    foreach (KeyValuePair<Color, Pen> k in pens) {
                        k.Value.Dispose();
                    }
                }
            }

            float IGraphics.Dpi {
                get { throw new NotImplementedException(); }
            }

            int IGraphics.GetPageCount(int basePageNumber, DevExpress.Utils.DefaultBoolean continuousPageNumbering) {
                throw new NotImplementedException();
            }

            void IGraphics.ResetDrawingPage() {
                throw new NotImplementedException();
            }

            void IGraphics.SetDrawingPage(Page page) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.ApplyTransformState(System.Drawing.Drawing2D.MatrixOrder order, bool removeState) {
                throw new NotImplementedException();
            }

            RectangleF IGraphicsBase.ClipBounds {
                get {
                    throw new NotImplementedException();
                }
                set {
                    throw new NotImplementedException();
                }
            }

            void IGraphicsBase.DrawCheckBox(RectangleF rect, System.Windows.Forms.CheckState state) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawEllipse(Pen pen, float x, float y, float width, float height) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawEllipse(Pen pen, RectangleF rect) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawImage(Image image, Point point) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawImage(Image image, RectangleF rect, Color underlyingColor) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawImage(Image image, RectangleF rect) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawLine(Pen pen, float x1, float y1, float x2, float y2) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawLine(Pen pen, PointF pt1, PointF pt2) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawLines(Pen pen, PointF[] points) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.DrawPath(Pen pen, System.Drawing.Drawing2D.GraphicsPath path) {
                throw new NotImplementedException();
            }

            public void DrawRectangle(Pen pen, RectangleF bounds) {
                _gr.DrawRectangle(pen, bounds.X, bounds.Y, bounds.Width, bounds.Height);
            }

            void IGraphicsBase.DrawString(string s, Font font, Brush brush, PointF point) {
                _gr.DrawString(s, font, brush, point);
            }

            void IGraphicsBase.DrawString(string s, Font font, Brush brush, PointF point, StringFormat format) {
                _gr.DrawString(s, font, brush, point, format);
            }

            void IGraphicsBase.DrawString(string s, Font font, Brush brush, RectangleF bounds) {
                _gr.DrawString(s, font, brush, bounds);
            }

            void IGraphicsBase.DrawString(string s, Font font, Brush brush, RectangleF bounds, StringFormat format) {
                _gr.DrawString(s, font, brush, bounds, format);
            }

            void IGraphicsBase.FillEllipse(Brush brush, float x, float y, float width, float height) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.FillEllipse(Brush brush, RectangleF rect) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.FillPath(Brush brush, System.Drawing.Drawing2D.GraphicsPath path) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.FillRectangle(Brush brush, float x, float y, float width, float height) {
                _gr.FillRectangle(brush, x, y, width, height);
            }

            void IGraphicsBase.FillRectangle(Brush brush, RectangleF bounds) {
                _gr.FillRectangle(brush, bounds);
            }

            Dictionary<Color, Brush> _Brushes = new Dictionary<Color, Brush>();

            Brush IGraphicsBase.GetBrush(Color color) {
                Brush brush;

                if (_Brushes.TryGetValue(color, out brush)) {
                    return brush;
                }

                return _Brushes[color] = new SolidBrush(color);
            }

            Dictionary<Color, Pen> _Pens = new Dictionary<Color, Pen>();

            public Pen GetPen(Color color) {
                Pen Pen;

                if (_Pens.TryGetValue(color, out Pen)) {
                    return Pen;
                }

                return _Pens[color] = new Pen(color);
            }

            GraphicsUnit IGraphicsBase.PageUnit {
                get {
                    throw new NotImplementedException();
                }
                set {
                    throw new NotImplementedException();
                }
            }

            void IGraphicsBase.ResetTransform() {
                throw new NotImplementedException();
            }

            void IGraphicsBase.RotateTransform(float angle, System.Drawing.Drawing2D.MatrixOrder order) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.RotateTransform(float angle) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.SaveTransformState() {
                throw new NotImplementedException();
            }

            void IGraphicsBase.ScaleTransform(float sx, float sy, System.Drawing.Drawing2D.MatrixOrder order) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.ScaleTransform(float sx, float sy) {
                throw new NotImplementedException();
            }

            System.Drawing.Drawing2D.SmoothingMode IGraphicsBase.SmoothingMode {
                get {
                    throw new NotImplementedException();
                }
                set {
                    throw new NotImplementedException();
                }
            }

            void IGraphicsBase.TranslateTransform(float dx, float dy, System.Drawing.Drawing2D.MatrixOrder order) {
                throw new NotImplementedException();
            }

            void IGraphicsBase.TranslateTransform(float dx, float dy) {
                throw new NotImplementedException();
            }

            Page IPrintingSystemContext.DrawingPage {
                get { throw new NotImplementedException(); }
            }

            static Measurer measurer;            
            DevExpress.XtraPrinting.Native.Measurer IPrintingSystemContext.Measurer {
                get {
                    if (measurer == null)
                        measurer = new GdiPlusMeasurer();
                    return measurer;
                }
            }

            PrintingSystemBase IPrintingSystemContext.PrintingSystem {
                get { throw new NotImplementedException(); }
            }

            object IServiceProvider.GetService(Type serviceType) {
                throw new NotImplementedException();
            }

        }

        static double CalcAutoModuleX(IBarCodeGenerator generator, IBarCodeData data, RectangleF clientBounds) {
            float barCodeWidth = clientBounds.Width;
            return (double)barCodeWidth / (double)generator.CalcBarCodeWidth(data.Pattern);
        }

        static double CalcAutoModuleY(IBarCodeGenerator generator, IBarCodeData data, RectangleF clientBounds) {
            float barCodeHeight = clientBounds.Height;
            return (double)barCodeHeight / (double)generator.CalcBarCodeHeight(data.Pattern);
        }

        public Image CreateBarCode() {
            int width = 100;
            if (_Width.HasValue && _Width.Value > 0) {
                width = _Width.Value;
            }

            int height = 45;
            if (_Height.HasValue && _Height.Value > 0) {
                height = _Height.Value;
            }

            Image image = new Bitmap(width, height);
            try
            {
                using (Graphics gr = Graphics.FromImage(image)) {
                                        
                    using (GraphicsHelper helper = new GraphicsHelper(gr)) {

                        ((IGraphics)helper).FillRectangle(Brushes.White, 0, 0, width, height);
                        
                        SizeF size = TextUtils.GetStringSize(
                            gr, 
                            _Data, 
                            ((IBarCodeData)this).Style.Font);
                        
                        RectangleF barBounds = new RectangleF(
                                                   0, 
                                                   0, 
                                                   width, 
                                                   height - size.Height - 1);

                        RectangleF textBounds = new RectangleF(
                                                    0, 
                                                    barBounds.Height + 1,
                                                    barBounds.Width,
                                                    size.Height);
                        
                        if (!Generator.SupressAutoTextAlignment()) {

                            textBounds = new RectangleF(
                                                        (width / 2) - (size.Width / 2),
                                                        barBounds.Height + 1,
                                                        width,
                                                        size.Height);
                        }

                        float ModuleX = (float)_Module;
                        if (ModuleX <= 0.001) {
                            ModuleX = (float)CalcAutoModuleX(Generator, this, barBounds);
                        }

                        float ModuleY = (float)_Module;
                        if (ModuleY <= 0.001) {
                            ModuleY = (float)CalcAutoModuleY(Generator, this, barBounds);
                        }

                        Generator.DrawBarCode(
                             helper,
                             barBounds,
                             textBounds, 
                             this,
                             ModuleX,
                             ModuleY);

                    }
                }
            
            } catch(Exception e)
            {
                if (e is StackOverflowException || e is OutOfMemoryException || e is ThreadAbortException) {
                    throw;
                }

                using (Graphics gr = Graphics.FromImage(image)) {

                    gr.FillRectangle(Brushes.White, 0, 0, width, height);
                    gr.DrawRectangle(Pens.Red, 0, 0, width, height);

                }
                
            }

            return image;
            
        }

        public RichEditImage CreateImage() {
            return RichEditImage.CreateImage(CreateBarCode());
        }


        TextAlignment IBarCodeData.Alignment {
            get { return TextAlignment.BottomCenter; }
        }

        bool IBarCodeData.AutoModule {
            get { return false; }
        }

        public string Text {
            get { return _Data; }
        }
        
        string IBarCodeData.DisplayText { get { return Generator.MakeDisplayText(((IBarCodeData)this).FinalText); } }
        string IBarCodeData.FinalText {
            get {
                if (Generator.IsValidText(Text))
                    return Generator.FormatText(Text);
                return Text;
            }
        }

        ArrayList IBarCodeData.Pattern {
            get {
                if (Generator.IsValidText(Text))
                    return Generator.MakeBarCodePattern(((IBarCodeData)this).FinalText);
                return new ArrayList();
            }
        }

        public double Module { get { return _Module; } set { _Module = value; } }

        BarCodeOrientation IBarCodeData.Orientation {
            get { return BarCodeOrientation.Normal; }
        }

        bool IBarCodeData.ShowText {
            get { return _ShowLabel; }
        }

        BrickStyle _Style;
        BrickStyle IBarCodeData.Style {
            get {
                if (_Style == null) {
                    _Style = BrickStyle.CreateDefault();
                }
                return _Style; 
            }
        }
    }
}
