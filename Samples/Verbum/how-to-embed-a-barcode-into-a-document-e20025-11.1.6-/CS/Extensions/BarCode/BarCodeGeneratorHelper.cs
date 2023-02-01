namespace BizPad {
    using System;
    using System.Collections.Generic;
    using System.Linq;

    internal static class BarCodeGeneratorHelper {
        public static bool IsValidText(IBarCodeGenerator generator, string text) {
            if (string.IsNullOrEmpty(text)) return false;
            string charSet = generator.GetValidCharSet();
            int length = text.Length;
            for (int i = 0; i < length; i++)
                if (charSet.IndexOf(text[i]) < 0)
                    return false;
            return true;
        }
    }
}
