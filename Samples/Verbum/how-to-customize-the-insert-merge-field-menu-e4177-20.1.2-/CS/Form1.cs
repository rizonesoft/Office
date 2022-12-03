using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows.Forms;
using System.Data.OleDb;
using System.Data;
using RichEditCustomInsertMergeFieldMenu.Properties;

namespace RichEditCustomInsertMergeFieldMenu {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            richEditControl1.Options.MailMerge.DataSource = GetMailMergeData();
        }

        private object GetMailMergeData() {
            OleDbConnection connection = new OleDbConnection(Settings.Default.nwindConnectionString);
            string commandText = @"SELECT Employees.*, Customers.* FROM (Employees INNER JOIN EmployeeCustomers ON Employees.EmployeeID = EmployeeCustomers.EmployeeId) INNER JOIN Customers ON EmployeeCustomers.CustomerId = Customers.CustomerID;";
            OleDbCommand selectCommand = new System.Data.OleDb.OleDbCommand(commandText, connection);
            OleDbDataAdapter dataAdapter = new OleDbDataAdapter(selectCommand);
            DataSet dataSet = new DataSet();
            dataAdapter.Fill(dataSet);
            return dataSet.Tables[0];
        }
    }
}