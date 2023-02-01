// Developer Express Code Central Example:
// How to create an editor similar to Outlook Attachment Editor
// 
// This example demonstrates how the RichEditControl component can be used to
// emulate the Outlook Attachment Editor behavior.
// The main idea of the approach
// demonstrated in this sample is to use the DOCVARIABLE field
// (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
// display corresponding RTF content for each inserted file.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=E4911

using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace WindowsFormsApplication1 {
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
