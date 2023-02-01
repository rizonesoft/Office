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

    public class ChartImage {
        ViewType _ViewType = ViewType.Pie;

        void ParseTypeSwitches(InstructionCollection switches) {
            string type = switches.GetString("c");
            if (type == null)
                type = String.Empty;
            switch (type.ToLower()) {
                case "bar":
                    _ViewType = ViewType.Bar;
                    break;
                case "line":
                    _ViewType = ViewType.Line;
                    break;
                case "pie":
                default:
                    _ViewType = ViewType.Pie;
                    break;
            }
        }

        Nullable<int> _Width = null;
        Nullable<int> _Height = null;

        void ParseSizeSwitches(InstructionCollection switches) {
            _Width = switches.GetNullableInt("w");
            _Height = switches.GetNullableInt("h");
        }
        List<KeyValuePair<string, double>> _Data = new List<KeyValuePair<string, double>>();

        void ParseDataSwitches(InstructionCollection switches) {
            string data = switches.GetString("d");
            if (data == null)
                data = String.Empty;

            foreach (string t in data.Split(',')) {
                double value;

                string[] pair = t.Split('|');

                if (pair.Length == 0) {
                    continue;
                }

                if (pair.Length == 1) {
                    if (!double.TryParse(pair[0], out value)) {
                        _Data.Add(new KeyValuePair<string, double>(pair[0], 0));
                    } else {
                        _Data.Add(new KeyValuePair<string, double>(String.Empty, value));
                    }
                } else
                    if (pair.Length == 2) {
                        if (!double.TryParse(pair[1], out value)) {
                            _Data.Add(new KeyValuePair<string, double>(pair[0], 0));
                        } else {
                            _Data.Add(new KeyValuePair<string, double>(pair[0], value));
                        }
                    }
            }
        }

        bool _ShowLegent = false;

        void ParseLegentSwitches(InstructionCollection switches) {
            _ShowLegent = switches.GetBool("l");
        }

        public void Initialize(InstructionCollection switches) {
            ParseDataSwitches(switches);
            ParseSizeSwitches(switches);
            ParseTypeSwitches(switches);
            ParseLegentSwitches(switches);
        }

        public Stream CreateChart() {

            using (ChartControl chart = new ChartControl()) {
                if (_Width.HasValue) {
                    chart.Width = _Width.Value;
                }
                if (_Height.HasValue) {
                    chart.Height = _Height.Value;
                }

                int undefined = 1;
                MemoryStream stream = new MemoryStream();
                try {
                    Series series = new Series("Chart", _ViewType);
                    try {
                        if (series.Label is DevExpress.XtraCharts.PieSeriesLabel) {
                            ((DevExpress.XtraCharts.PieSeriesLabel)series.Label).Position = PieSeriesLabelPosition.Inside;
                        }

                        if (_ViewType == ViewType.Pie) {
                            series.PointOptions.ValueNumericOptions.Format = DevExpress.XtraCharts.NumericFormat.Percent;
                        }

                        if (_Data == null || _Data.Count == 0) {
                            series.Points.Add(new SeriesPoint("Undefined", new double[] { 1 }));
                            series.PointOptions.PointView = PointView.SeriesName;

                        } else {
                            series.PointOptions.PointView = PointView.ArgumentAndValues;

                            for (int i = 0; i < _Data.Count; i++) {

                                string argument = _Data[i].Key.Trim();

                                if (String.IsNullOrEmpty(argument)) {
                                    argument = "Undefined " + undefined;
                                    undefined++;
                                }

                                series.Points.Add(new SeriesPoint(argument, new double[] {
                                    _Data[i].Value }));
                            }
                        }

                        chart.Legend.Visible = _ShowLegent;
                        chart.BorderOptions.Visible = false;

                        chart.Series.AddRange(new Series[] { series });
                        series = null;

                        chart.ExportToImage(stream, ImageFormat.Bmp);

                        return stream;

                    } catch {
                        if (series != null) {
                            series.Dispose();
                        }
                        throw;
                    }

                } catch {
                    if (stream != null) {
                        stream.Dispose();
                    }
                    throw;
                }
            }
        }

        public RichEditImage CreateImage() {
            return RichEditImage.CreateImage(CreateChart());
        }

    }
}
