// Developer Express Code Central Example:
// How to implement an MS Word-like Mini Toolbar in RichEditControl
// 
// This example demonstrates how to implement the MS Word-like Mini Toolbar feature
// using a RibbonMiniToolbar
// (https://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsRibbonRibbonMiniToolbartopic)
// component. It is a popup toolbar, whose transparency depends on the distance
// from the mouse cursor. Show this toolbar for the selected text in the
// RichEditControl document separately and display it together with a regular
// context menu in the RichEditControl.PopupMenuShowing event handler.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=T157245

using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace RTFRibbonMini {
    static class Program {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main() {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1());
        }
    }
}
