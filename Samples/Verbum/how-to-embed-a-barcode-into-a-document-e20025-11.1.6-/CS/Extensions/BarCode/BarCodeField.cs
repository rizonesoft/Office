namespace BizPad {
    using System.Collections.Generic;
    using DevExpress.XtraRichEdit.Fields;
    using DevExpress.XtraRichEdit.Model;
    using DevExpress.XtraRichEdit.Utils;

    public class BarCodeField : CalculatedFieldBase {
        public static readonly string FieldType = "BRCODE";
        protected override string FieldTypeName {
            get {
                return FieldType;
            }
        }

        static readonly Dictionary<string, bool> switchesWithArgument = CreateSwitchesWithArgument("w", "h", "d", "t", "k", "s", "r", "p", "c", "f", "o", "m", "e");
        protected override Dictionary<string, bool> SwitchesWithArguments {
            get {
                return switchesWithArgument;
            }
        }

        BarCodeImage barcode = new BarCodeImage();

        public override void Initialize(InstructionCollection switches) {
            base.Initialize(switches);
            barcode.Initialize(switches);
        }

        public override object GetCalculatedValueCore(PieceTable sourcePieceTable,
            DocumentModel targetModel,
            MailMergeDataMode mailMergeDataMode,
            Field documentField) {

            RichEditImage image = barcode.CreateImage();
            targetModel.MainPieceTable.InsertInlinePicture(
                DocumentLogPosition.Zero,
                image);
            return targetModel;
        }
    }
}
