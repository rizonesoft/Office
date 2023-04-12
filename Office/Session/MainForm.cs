using DevExpress.XtraEditors;

namespace Rizonesoft.Office.Session
{
    using System;
    using System.Data;
    using DevExpress.XtraScheduler;
    using System.Data.SQLite;
    using Data;

    /// <summary>
    /// The MainForm class represents the main application form.
    /// </summary>
    public partial class MainForm : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        private DataSet? schedulerDataSet;
        private SQLiteDataAdapter? appointmentsDataAdapter;
        private SQLiteDataAdapter? resourcesDataAdapter;


        /// <summary>
        /// Initializes a new instance of the MainForm class.
        /// </summary>
        public MainForm()
        {
            InitializeComponent();

            // Subscribe to Storage events required for updating the data source.
            schedulerDataStorage1.AppointmentsInserted += OnChangedInsertedDeleted;
            schedulerDataStorage1.AppointmentsChanged += OnChangedInsertedDeleted;
            schedulerDataStorage1.AppointmentsDeleted += OnChangedInsertedDeleted;
            DatabaseManager.InitializeDatabase(); // Call this method before accessing DatabasePath

        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            schedulerDataStorage1.Appointments.ResourceSharing = true;
            //schedulerControl1.GroupType = SchedulerGroupType.Resource;
            schedulerControl1.Start = DateTime.Today;

            schedulerDataSet = new DataSet();

            var connectionString = "Data Source=" + DatabaseManager.DatabasePath;
            var connection = new SQLiteConnection(connectionString);
            connection.Open();

            SetupAppointmentsAdapter(connection);
            SetupResourcesAdapter(connection);

            // Set up the Resources data adapter and bind it to the scheduler storage


        }

        /// <summary>
        /// Sets up the Appointments data adapter and maps the appointment data.
        /// </summary>
        private void SetupAppointmentsAdapter(SQLiteConnection connection)
        {
            appointmentsDataAdapter = new SQLiteDataAdapter("SELECT * FROM Appointments", connection);

            appointmentsDataAdapter.RowUpdated += (_, e) =>
            {
                if (e.StatementType != StatementType.Insert ||
                    e.Status != UpdateStatus.Continue) return;
                using var cmd = new SQLiteCommand("SELECT last_insert_rowid()", connection);
                e.Row["UniqueID"] = Convert.ToInt32(cmd.ExecuteScalar());
                //e.Row["TimeZoneId"] = "UTC";
            };

            // ReSharper disable once UnusedVariable
            var appointmentsCommandBuilder = new SQLiteCommandBuilder(appointmentsDataAdapter);
            schedulerDataSet = new DataSet();
            if (schedulerDataSet != null)
            {
                appointmentsDataAdapter.Fill(schedulerDataSet, "Appointments");
                schedulerDataStorage1.Appointments.DataSource = schedulerDataSet.Tables["Appointments"];
            }

            MapAppointmentData();
        }

        /// <summary>
        /// Sets up the Resources data adapter and maps the resource data.
        /// </summary>
        private void SetupResourcesAdapter(SQLiteConnection connection)
        {
            resourcesDataAdapter = new SQLiteDataAdapter("SELECT * FROM Resources", connection);
            // ReSharper disable once UnusedVariable
            var resourcesCommandBuilder = new SQLiteCommandBuilder(resourcesDataAdapter);
            if (schedulerDataSet != null)
            {
                resourcesDataAdapter.Fill(schedulerDataSet, "Resources");
                schedulerDataStorage1.Resources.DataSource = schedulerDataSet.Tables["Resources"];
            }

            MapResourceData();
        }

        /// <summary>
        /// Maps the appointment data to the scheduler storage.
        /// </summary>
        private void MapAppointmentData()
        {
            schedulerDataStorage1.Appointments.Mappings.AppointmentId = "UniqueID";
            schedulerDataStorage1.Appointments.Mappings.Type = "Type";
            schedulerDataStorage1.Appointments.Mappings.Start = "StartDate"; // Required mapping.
            schedulerDataStorage1.Appointments.Mappings.End = "EndDate"; // Required mapping.
            schedulerDataStorage1.Appointments.Mappings.AllDay = "AllDay";
            schedulerDataStorage1.Appointments.Mappings.Subject = "Subject";
            schedulerDataStorage1.Appointments.Mappings.Location = "Location";
            schedulerDataStorage1.Appointments.Mappings.Description = "Description";
            schedulerDataStorage1.Appointments.Mappings.Status = "Status";
            schedulerDataStorage1.Appointments.Mappings.Label = "Label";
            schedulerDataStorage1.Appointments.Mappings.ResourceId = "ResourceID";
            schedulerDataStorage1.Appointments.Mappings.ReminderInfo = "ReminderInfo";
            schedulerDataStorage1.Appointments.Mappings.RecurrenceInfo = "RecurrenceInfo";
            schedulerDataStorage1.Appointments.Mappings.TimeZoneId = "TimeZoneId";
        }

        /// <summary>
        /// Maps the resource data to the scheduler storage.
        /// </summary>
        private void MapResourceData()
        {
            schedulerDataStorage1.Resources.Mappings.Id = "ResourceID";
            schedulerDataStorage1.Resources.Mappings.Caption = "ResourceName";
            schedulerDataStorage1.Resources.Mappings.Color = "Color";
            schedulerDataStorage1.Resources.Mappings.Image = "Image";
        }

        private void OnChangedInsertedDeleted(object sender, PersistentObjectsEventArgs e)
        {
            try
            {
                appointmentsDataAdapter?.Update(schedulerDataSet?.Tables["Appointments"] ?? throw new InvalidOperationException());
                schedulerDataSet?.AcceptChanges();
            }
            catch (Exception ex)
            {
                // Handle exceptions appropriately, e.g., log the error or show a message to the user
                Console.WriteLine($@"Error updating appointments: {ex.Message}");
            }

        }

        private void schedulerControl1_ActiveViewChanging(object sender, ActiveViewChangingEventArgs e)
        {
            
        }

        private void schedulerControl1_ActiveViewChanged(object sender, EventArgs e)
        {
            if (schedulerControl1.ActiveViewType is SchedulerViewType.Timeline or SchedulerViewType.Year)
            {
                splitContainerControl2.PanelVisibility = SplitPanelVisibility.Panel2;
            }
            else
            {
                splitContainerControl2.PanelVisibility = SplitPanelVisibility.Both;
            }
        }
    }
}
