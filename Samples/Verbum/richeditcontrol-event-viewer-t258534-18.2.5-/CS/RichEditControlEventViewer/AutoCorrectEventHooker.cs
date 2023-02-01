using System;
using System.Collections.Generic;
using System.Linq;

namespace RichEditControlEventViewer
{
    #region RichEditEventHooker
    public class AutoCorrectEventHooker : RichEditEventHooker
    {
        public AutoCorrectEventHooker(string eventName, Form1 owner) :
            base(eventName, owner)
        {
        }
        protected override string MethodName { get { return "InitializeAutoCorrectEventLogger"; } }
    }
    #endregion
}
