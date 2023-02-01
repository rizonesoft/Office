using DevExpress.XtraEditors;
using DevExpress.XtraSpellChecker;
using Rizonesoft.Office.Verbum.Classes;
using Rizonesoft.Office.Verbum.Helpers;
using System;
using System.Collections;
using System.Globalization;
using System.IO;
using System.Windows.Forms;


namespace Rizonesoft.Office.Verbum
{
    public partial class MainForm : XtraForm
    {


        private int docIndex = 0;
        public int DocumentIndex
        {
            get { return docIndex; }
            set { docIndex = value; }
        }


        private void Initialize()
        {
            childForms = new ArrayList();
            // Create a new instance of the class:
            copyData = new CopyData();
            // Assign the handle:
            copyData.AssignHandle(this.Handle);
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            // Hook up event notifications whenever a message is received:
            copyData.DataReceived += new Rizonesoft.Office.Verbum.Classes.DataReceivedEventHandler(copyData_DataReceived);
        }


        /// <summary>
        /// Fired whenever message is received from another instance.
        /// Open file name in new form
        /// </summary>
        /// <param name="sender">The CopyData class which receieved the data.</param>
        /// <param name="e">Data that was receieved.</param>
        private void copyData_DataReceived(object sender, Rizonesoft.Office.Verbum.Classes.DataReceivedEventArgs e)
        {
            if (e.Data.Equals(""))
                docIndex += 1;
            // Display the data in the logging list box:
            if (e.ChannelName.Equals("DocChannel"))
            {
                string fileName = (string)e.Data;
                DocForm docForm = new DocForm(fileName, docIndex);
                AddForm(docForm);
            }
        }


        /// <summary>
        /// AddForm adds and displays the new form.
        /// </summary>
        /// <param name="form"></param>
        public void AddForm(XtraForm childForm)
        {
            childForm.Closed += new EventHandler(OnChildFormClosed);
            childForms.Add(childForm);
            childForm.Show();
        }


        /// <summary>
        /// Called everytime a "child" form is closed
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void OnChildFormClosed(object sender, EventArgs e)
        {
            childForms.Remove(sender);
            if (childForms.Count == 0)
            {
                this.Close();
            }

        }


        private void CreateVerbumDirectories()
        {
            if (!Directory.Exists(Configuration.userAppDataPath))
            { Directory.CreateDirectory(Configuration.userAppDataPath); }
        }


        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            // Settings.Default["ApplicationSkinName"] = UserLookAndFeel.Default.SkinName;
            // Settings.Default.Save();
        }
    }
}

