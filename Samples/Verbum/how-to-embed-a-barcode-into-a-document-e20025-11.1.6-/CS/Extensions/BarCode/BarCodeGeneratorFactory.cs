namespace BizPad {
    using System;
    using System.Collections.Generic;
    using DevExpress.XtraPrinting.BarCode;
    using DevExpress.XtraPrinting.BarCode.Native;
    using DevExpress.XtraRichEdit.Fields;

    internal static class BarCodeGeneratorFactory {

        static Type defaultCodeType = typeof(CodabarGenerator);
        static Dictionary<string, Type> hashTable = new Dictionary<string, Type>();
        static BarCodeGeneratorFactory() {
            hashTable["codabar"] = typeof(CodabarGeneratorHelper);            
            hashTable["code128"] = typeof(Code128GeneratorHelper);
            hashTable["128"] = typeof(Code128GeneratorHelper);            
            hashTable["industrial2of5"] = typeof(Industrial2of5GeneratorHelper);
            hashTable["2of5"] = typeof(Industrial2of5GeneratorHelper);
            hashTable["interleaved2of5"] = typeof(Interleaved2of5GeneratorHelper);
            hashTable["2of5i"] = typeof(Interleaved2of5GeneratorHelper);            
            hashTable["code39"] = typeof(Code39GeneratorHelper);
            hashTable["39"] = typeof(Code39GeneratorHelper);
            hashTable["3of9"] = typeof(Code39GeneratorHelper);
            hashTable["code39extended"] = typeof(Code39ExtendedGeneratorHelper);
            hashTable["code39e"] = typeof(Code39ExtendedGeneratorHelper);
            hashTable["39e"] = typeof(Code39ExtendedGeneratorHelper);
            hashTable["3of9e"] = typeof(Code39ExtendedGeneratorHelper);            
            hashTable["code93"] = typeof(Code93GeneratorHelper);
            hashTable["93"] = typeof(Code93GeneratorHelper);
            hashTable["code93e"] = typeof(Code93ExtendedGeneratorHelper);
            hashTable["code93e"] = typeof(Code93ExtendedGeneratorHelper);
            hashTable["93e"] = typeof(Code93ExtendedGeneratorHelper);            
            hashTable["code11"] = typeof(Code11GeneratorHelper);
            hashTable["11"] = typeof(Code11GeneratorHelper);            
            hashTable["msi"] = typeof(CodeMSIGeneratorHelper);
            hashTable["plessey"] = typeof(CodeMSIGeneratorHelper);
            hashTable["postnet"] = typeof(PostNetGeneratorHelper);
            hashTable["post"] = typeof(PostNetGeneratorHelper);            
            hashTable["ean13"] = typeof(EAN13GeneratorHelper);
            hashTable["ean8"] = typeof(EAN8GeneratorHelper);
            hashTable["ean128"] = typeof(EAN128GeneratorHelper);
            hashTable["upca"] = typeof(UPCAGeneratorHelper);
            hashTable["upcsupplemental2"] = typeof(UPCSupplemental2GeneratorHelper);
            hashTable["upcs2"] = typeof(UPCSupplemental2GeneratorHelper);
            hashTable["upcsupplemental5"] = typeof(UPCSupplemental5GeneratorHelper);
            hashTable["upcs5"] = typeof(UPCSupplemental5GeneratorHelper);
            hashTable["upce0"] = typeof(UPCE0GeneratorHelper);
            hashTable["upce1"] = typeof(UPCE1GeneratorHelper);            
            hashTable["matrix2of5"] = typeof(Matrix2of5GeneratorHelper);
            hashTable["2of5m"] = typeof(Matrix2of5GeneratorHelper);            
            hashTable["pdf417"] = typeof(PDF417GeneratorHelper);
            hashTable["datamatrix"] = typeof(DataMatrixGeneratorHelper);
            hashTable["ecc200"] = typeof(DataMatrixGeneratorHelper);
        }

        internal static IBarCodeGenerator Create(string symbologyCode, InstructionCollection switches) {
            Type type = null;
            if (!String.IsNullOrWhiteSpace(symbologyCode)) {
                if (!hashTable.TryGetValue(symbologyCode.Trim().ToLower(), out type)) {
                    type = null;
                }
            }
            if (type == null) {
                type = defaultCodeType;
            }
            IBarCodeGenerator generator = (IBarCodeGenerator)Activator.CreateInstance(type);
            generator.Initialize(switches);
            return generator;
        }
    }
}