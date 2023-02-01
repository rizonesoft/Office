using System;
using System.Text;

namespace MailMerge
{
    #region #sampledata
    class SampleData : System.Collections.ArrayList
    {
        public SampleData()
        {
            Add(new AddresseeRecord("Andrew", "XYZ Inc.", "Tullamore Way, 21"));
            Add(new AddresseeRecord("Benny", "ABC Ltd.", "Casablanca Rd., 46"));
            Add(new AddresseeRecord("Jose", "CASA S.A.", "Paseo di Ronda, 88"));
        }
    }
    public class AddresseeRecord
    {
        public string Name { get; set; }
        public string Company { get; set; }
        public string Address { get; set; }
        public AddresseeRecord(string fName, string fCompany, string fAddress)
        {
            Name = fName;
            Company = fCompany;
            Address = fAddress;
        }
    }
    #endregion #sampledata
}