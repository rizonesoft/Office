using DevExpress.XtraBars.Alerter;
using DevExpress.XtraEditors;
using Rizonesoft.Office.Utilities;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.Window;

namespace Rizonesoft.Office.MessagesEx
{
    public partial class MessageForm : DevExpress.XtraEditors.DirectXForm
    {
        public MessageForm()
        {
            InitializeComponent();

        }

        public MessageForm(MessageData messageData)
        {
            InitializeComponent();
            messageAlertControl.HtmlElementMouseClick += (s, e) => {
                if ((e.ElementId == "closeButton") || (e.ElementId == "dismissButton"))
                {
                    Settings.Settings.SaveSetting($"Rizonesoft\\{GlobalProperties.ProductName}\\General", "UpdateMessage", "False");
                    e.HtmlPopup.Close();
                    this.Close();
                }
                if (e.ElementId == "updateButton")
                {
                    System.Diagnostics.Process.Start("https://www.rizonesoft.com");
                }

            };

            messageAlertControl.Show(messageData, this);

        }

        private void MessageAlertControl_FormClosing(object sender, AlertFormClosingEventArgs e)
        {
            if (e.CloseReason == AlertFormCloseReason.TimeUp) e.Cancel = true;
        }

    }
}