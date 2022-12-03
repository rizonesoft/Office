using System;
using System.Text;
using DevExpress.XtraRichEdit.Utils;
using DevExpress.Office.Utils;
using DevExpress.Office.Services;
using DevExpress.Office.Services.Implementation;

namespace RichEditCustomCopyPaste {
    public class CF_HTMLHelper {
        //HTML Clipboard Format http://msdn.microsoft.com/en-us/library/aa767917(v=vs.85).aspx
        const string StartFragmentTag = "<!--StartFragment-->";
        const string EndFragmentTag = "<!--EndFragment-->";

        const string bodyTag = "<body>\r\n";
        const string bodyTagClose = "</body>";
        const string EmptyDescription = "Version:0.9\r\nStartHTML:{0:D10}\r\nEndHTML:{1:D10}\r\nStartFragment:{2:D10}\r\nEndFragment:{3:D10}\r\n";

        public static string GetHtmlClipboardFormat(string html) {
            int startBodyTagPos = html.IndexOf(bodyTag);
            int bodyEndTagPos = html.LastIndexOf(bodyTagClose);
            
            int contentBeforeFramentLength = startBodyTagPos + bodyTag.Length;
            string contentBeforeFragment = html.Substring(0, contentBeforeFramentLength) ;

            string fragment = html.Substring(contentBeforeFramentLength, bodyEndTagPos - contentBeforeFramentLength);

            string contentAfterFragment = html.Substring(bodyEndTagPos, html.Length - bodyEndTagPos);

            string result = Get_CF_HTML(contentBeforeFragment + StartFragmentTag, fragment, EndFragmentTag + contentAfterFragment);

            return result;
        }

        static string Get_CF_HTML(string contentBeforeFragment, string fragment, string contentAfterFragment) {
            int contentBeforeFragmentCount = Encoding.UTF8.GetByteCount(contentBeforeFragment);
            int fragmentCount = Encoding.UTF8.GetByteCount(fragment);
            int contentAfterFragmentCount = Encoding.UTF8.GetByteCount(contentAfterFragment);

            int descriptionOffset = Encoding.UTF8.GetByteCount(String.Format(EmptyDescription, 0, 0, 0, 0));
            int endHTMLOffset = descriptionOffset + contentBeforeFragmentCount + fragmentCount + contentAfterFragmentCount;
            int startFragmentOffset = descriptionOffset + contentBeforeFragmentCount;
            int endFragmentOffset = descriptionOffset + contentBeforeFragmentCount + fragmentCount;

            string description = String.Format(EmptyDescription, descriptionOffset, endHTMLOffset, startFragmentOffset, endFragmentOffset);

            StringBuilder content = new StringBuilder();
            content.Append(description);
            content.Append(contentBeforeFragment);
            content.Append(fragment);
            content.Append(contentAfterFragment);
            return content.ToString();
        }
    }

    public class CustomUriProvider : IUriProvider {
        public string CreateCssUri(string rootUri, string styleText, string relativeUri) {
            return String.Empty;
        }

        public string CreateImageUri(string rootUri, OfficeImage image, string relativeUri) {
            if (string.IsNullOrEmpty(image.Uri))
                return new DataStringUriProvider().CreateImageUri(rootUri, image, relativeUri);
            else
                return image.Uri;
        }
    }
}
