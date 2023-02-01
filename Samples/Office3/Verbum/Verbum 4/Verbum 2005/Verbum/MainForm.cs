using System;
using System.IO;
using System.Threading;
using System.Reflection;
using System.Diagnostics;
using System.Collections;
using System.Windows.Forms;

using DevExpress.XtraEditors;
using DevExpress.LookAndFeel;

namespace Rizonesoft.Verbum
{
    public partial class MainForm : Form
    {

        /// <summary>
        /// Array of all forms currently open, application closes when all closed
        /// </summary>
        private ArrayList childForms;

        /// <summary>
        /// The CopyData class used for message sending.
        /// </summary>
        private CopyData copyData = null;

        private int docIndex = 0;
        public int DocumentIndex
        {
            get { return docIndex; }
            set { docIndex = value; }
        }

        public MainForm()
        {

            InitializeComponent();

            // Do everything possible to keep this window hidden
            // note: form.Opacity = 0 set in designer will keep
            // the window from flashing during startup
            this.ShowInTaskbar = false;
            this.Opacity = 0;
            this.Hide();

            createAppDirectories();
            InitializeSkins();
            initialize();

        }

        private void createAppDirectories()
        {
            if (!Directory.Exists(Rizonesoft.Verbum.Configuration.RuntimeConfig.userAppDataDir))
            {
                Directory.CreateDirectory(Rizonesoft.Verbum.Configuration.RuntimeConfig.userAppDataDir);
            }

        }

        private void InitializeSkins()
        {
            LoadSkins("DevExpress.BonusSkins.v11.1.dll");
            LoadSkins("DevExpress.OfficeSkins.v11.1.dll");
            LookAndFeelHelper.ForceDefaultLookAndFeelChanged();
            //UserLookAndFeel.Default.SkinName = conf.applicationSkin;
        }

        private void LoadSkins(string skinFileName)
        {
            if (File.Exists(skinFileName))
            {
                Assembly verbumAssembly = Assembly.LoadFile(Path.GetFullPath(skinFileName));
                DevExpress.Skins.SkinManager.Default.RegisterAssembly(verbumAssembly);
            }
            //else MessageBox.Show("File not found");
        }

        private void initialize()
        {
            childForms = new ArrayList();
            // Create a new instance of the class:
            copyData = new CopyData();
            // Assign the handle:
            copyData.AssignHandle(this.Handle);
            // Create the named channels to send and receive on.
            copyData.Channels.Add("DocChannel");
            // Hook up event notifications whenever a message is received:
            copyData.DataReceived += new Rizonesoft.Verbum.DataReceivedEventHandler(
                copyData_DataReceived);
        }

        /// <summary>
        /// Fired whenever message is received from another instance.
        /// Open file name in new form
        /// </summary>
        /// <param name="sender">The CopyData class which receieved the data.</param>
        /// <param name="e">Data that was receieved.</param>
        private void copyData_DataReceived(object sender, Rizonesoft.Verbum.DataReceivedEventArgs e)
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

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            //conf.Store();
            // if (applicationMutex != null)
            //{
               // applicationMutex.ReleaseMutex();
            //}
        }
    }
}