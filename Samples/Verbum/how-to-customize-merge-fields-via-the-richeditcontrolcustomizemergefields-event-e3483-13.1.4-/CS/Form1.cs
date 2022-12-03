using System;
using System.Collections.Generic;
using System.Windows.Forms;
using DevExpress.XtraRichEdit.API.Native;

namespace RichEditCustomizeMergeFields {
    public partial class Form1 : Form {
        public Form1() {
            InitializeComponent();

            List<Invoice> invoices = new List<Invoice>(10);

            invoices.Add(new Invoice(0, "Invoice1", 10.0m, Guid.NewGuid()));
            invoices.Add(new Invoice(1, "Invoice2", 15.0m, Guid.NewGuid()));
            invoices.Add(new Invoice(2, "Invoice3", 20.0m, Guid.NewGuid()));

            richEditControl1.Options.MailMerge.DataSource = invoices;
        }

        private void richEditControl1_CustomizeMergeFields(object sender, DevExpress.XtraRichEdit.CustomizeMergeFieldsEventArgs e) {
            List<MergeFieldName> mergeFieldNames = new List<MergeFieldName>(e.MergeFieldsNames);

            mergeFieldNames.Remove(mergeFieldNames.Find(mfn => mfn.Name.ToLower() == "password"));
            mergeFieldNames.ForEach(ChangeDisplayName);
            mergeFieldNames.Sort(new ReverseComparer());
            
            e.MergeFieldsNames = mergeFieldNames.ToArray();
        }

        private static void ChangeDisplayName(MergeFieldName mfn) {
            mfn.DisplayName += " (field)";
        }
    }

    public class ReverseComparer : IComparer<MergeFieldName> {
        #region IComparer<MergeFieldName> Members
        public int Compare(MergeFieldName mfn1, MergeFieldName mfn2) {
            return -string.Compare(mfn1.Name, mfn2.Name);
        }
        #endregion
    }

    public class Invoice {
        private int id;

        public int Id {
            get { return id; }
            set { id = value; }
        }
        private string description;

        public string Description {
            get { return description; }
            set { description = value; }
        }
        private decimal price;

        public decimal Price {
            get { return price; }
            set { price = value; }
        }
        private Guid password;

        public Guid Password {
            get { return password; }
            set { password = value; }
        }

        public Invoice(int id, string description, decimal price, Guid password) {
            this.Id = id;
            this.Description = description;
            this.Price = price;
            this.Password = password;
        }
    }

}