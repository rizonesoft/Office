namespace BizPad {
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using DevExpress.XtraRichEdit.Fields;
    using DevExpress.XtraRichEdit.Model;

    public class FieldCalculatorServiceEx : FieldCalculatorService, IFieldCalculatorService {
        protected override CalculatedFieldBase CreateInitializedCalculatedField(
            PieceTable pieceTable,
            Token firstToken,
            FieldScanner scanner) {

            Token chartToken = firstToken;

            if (chartToken != null) {
                if (String.Equals(chartToken.val, "CHART", StringComparison.OrdinalIgnoreCase)) {
                    return CreateInitializedField<ChartField>(scanner);
                }
                else if (String.Equals(chartToken.val, "BRCODE", StringComparison.OrdinalIgnoreCase)) {
                    return CreateInitializedField<BarCodeField>(scanner);
                }
            }

            return base.CreateInitializedCalculatedField(
                pieceTable,
                firstToken,
                scanner);
        }

        static CalculatedFieldBase CreateInitializedField<T>(FieldScanner scanner) where T : CalculatedFieldBase, new() {
            CalculatedFieldBase field = new T();
            if (field == null) {
                return null;
            }

            InstructionCollection instructions = ParseInstructions(scanner, field);
            field.Initialize(instructions);
            return field;
        }
    }
}
