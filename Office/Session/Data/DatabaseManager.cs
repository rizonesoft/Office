namespace Rizonesoft.Office.Session.Data
{
    using System;
    using System.IO;
    using System.Windows.Forms;
    using Microsoft.Data.Sqlite;

    /// <summary>
    /// The DatabaseManager class is responsible for managing the SQLite database connection,
    /// creating the database if it doesn't exist, and ensuring the database folder is writable.
    /// </summary>
    public class DatabaseManager
    {
        /// <summary>
        /// Gets the database file path.
        /// </summary>
        public static string? DatabasePath { get; private set; }

        /// <summary>
        /// Initializes a new instance of the DatabaseManager class and sets the connection string.
        /// </summary>
        public DatabaseManager()
        {
            InitializeDatabase();
        }

        /// <summary>
        /// Sets the connection string for the SQLite database and creates the database if it doesn't exist.
        /// Also checks if the database folder exists and is writable before attempting to create the database.
        /// </summary>
        public static void InitializeDatabase()
        {
            var documentsFolderPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            var databaseFolder = Path.Combine(documentsFolderPath, "Session");

            // Check if the folder exists and create it if it doesn't
            Directory.CreateDirectory(databaseFolder);

            // Check if the folder is writable
            if (!IsDirectoryWritable(databaseFolder))
            {
                using var folderBrowserDialog = new FolderBrowserDialog();
                folderBrowserDialog.Description = @"Select a writable folder for the database";
                folderBrowserDialog.ShowNewFolderButton = true;

                if (folderBrowserDialog.ShowDialog() == DialogResult.OK)
                {
                    databaseFolder = folderBrowserDialog.SelectedPath;
                }
                else
                {
                    MessageBox.Show(@"No writable folder selected for the database. The application will close.",
                        @"Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    throw new InvalidOperationException("No writable folder selected for the database.");
                }
            }

            string databaseFilename = "DatabaseFile.db";
            DatabasePath = Path.Combine(databaseFolder, databaseFilename);

            // Check if the database file exists
            bool isDatabaseFileExists = File.Exists(DatabasePath);

            // Create and set up the database if it doesn't exist
            if (!isDatabaseFileExists)
            {
                CreateDatabase();
            }
        }

        /// <summary>
        /// Checks if the specified directory is writable by trying to create and delete a temporary file.
        /// </summary>
        /// <param name="directoryPath">The path of the directory to check.</param>
        /// <returns>True if the directory is writable, false otherwise.</returns>
        private static bool IsDirectoryWritable(string directoryPath)
        {
            try
            {
                string tempFile = Path.Combine(directoryPath, Path.GetRandomFileName());
                using (FileStream fs = File.Create(tempFile, 1, FileOptions.DeleteOnClose))
                {
                }
                return true;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Creates the SQLite database by connecting to the database specified in the connection string
        /// and executing the create table query.
        /// </summary>
        private static void CreateDatabase()
        {
            string connectionString = $"Data Source={DatabasePath};";

            using (SqliteConnection connection = new(connectionString))
            {
                connection.Open();

                string createTableQuery = @"CREATE TABLE IF NOT EXISTS Appointments (
                    UniqueID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Type INTEGER,
                    StartDate TEXT,
                    EndDate TEXT,
                    AllDay INTEGER,
                    Subject TEXT,
                    Location TEXT,
                    Description TEXT,
                    Status INTEGER,
                    Label INTEGER,
                    ResourceID TEXT,
                    ResourceIDs TEXT,
                    ReminderInfo TEXT,
                    RecurrenceInfo TEXT,
                    TimeZoneID TEXT,
                    CustomField1 TEXT
                );

                CREATE TABLE IF NOT EXISTS Resources (
                    UniqueID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ResourceID INTEGER NOT NULL,
                    ResourceName TEXT,
                    Color INTEGER,
                    Image BLOB,
                    CustomField1 TEXT
                );

                INSERT OR IGNORE INTO Resources (UniqueID, ResourceID, ResourceName, Color, Image, CustomField1) VALUES (1, 1, 'Resource One', NULL, NULL, NULL);
                INSERT OR IGNORE INTO Resources (UniqueID, ResourceID, ResourceName, Color, Image, CustomField1) VALUES (2, 2, 'Resource Two', NULL, NULL, NULL);
                INSERT OR IGNORE INTO Resources (UniqueID, ResourceID, ResourceName, Color, Image, CustomField1) VALUES (3, 3, 'Resource Three', NULL, NULL, NULL);";




                using (SqliteCommand command = new(createTableQuery, connection))
                {
                    command.ExecuteNonQuery();
                }
            }
        }
    }
}