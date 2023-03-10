using DevExpress.Utils.Svg;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.MessagesEx
{
    public class MessageData
    {
        public MessageData(string caption, string message, SvgImage messageIcon) 
        { 
            Caption = caption;
            Message = message;
            MessageIcon = messageIcon;
        }

        public string Caption { get; set; }
        public string Message { get; set; }
        public SvgImage MessageIcon { get; set; }

    }
}
