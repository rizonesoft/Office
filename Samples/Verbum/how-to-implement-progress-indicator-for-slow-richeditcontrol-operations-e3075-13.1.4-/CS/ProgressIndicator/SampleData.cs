using System;
using System.Collections.Generic;
using System.Text;
using System.Collections;

namespace ProgressIndicator {
    class SampleData : ArrayList {
        public SampleData() {
            Add(new AddresseeRecord("Maria", "Alfreds Futterkiste", "Obere Str. 57, Berlin"));
            Add(new AddresseeRecord("Ana", "Ana Trujillo Emparedados y helados", "Avda. de la Constitucion 2222, Mexico D.F."));
            Add(new AddresseeRecord("Antonio", "Antonio Moreno Taqueria", "Mataderos  2312, Mexico D.F."));
            Add(new AddresseeRecord("Thomas", "Around the Horn", "120 Hanover Sq., London"));
            Add(new AddresseeRecord("Christina", "Berglunds snabbkop", "Berguvsvagen  8, Lulea"));
            Add(new AddresseeRecord("Hanna", "Blauer See Delikatessen", "Forsterstr. 57, Mannheim"));
            Add(new AddresseeRecord("Frederique", "Blondel pere et fils", "24, place Kleber, Strasbourg"));
            Add(new AddresseeRecord("Martin", "Bolido Comidas preparadas", "C/ Araquil, 67, Madrid"));
            Add(new AddresseeRecord("Laurence", "Bon app'", "12, rue des Bouchers, Marseille"));
            Add(new AddresseeRecord("Elizabeth", "Bottom-Dollar Markets", "23 Tsawassen Blvd., Tsawwassen"));
            Add(new AddresseeRecord("Victoria", "B's Beverages", "Fauntleroy Circus, London"));
            Add(new AddresseeRecord("Patricio", "Cactus Comidas para llevar", "Cerrito 333, Buenos Aires"));
            Add(new AddresseeRecord("Francisco", "Centro comercial Moctezuma", "Sierras de Granada 9993, Mexico D.F."));
            Add(new AddresseeRecord("Yang", "Chop-suey Chinese", "Hauptstr. 29, Bern"));
            Add(new AddresseeRecord("Pedro", "Comercio Mineiro", "Av. dos Lusiadas, 23, Sao Paulo"));
            Add(new AddresseeRecord("Elizabeth","Consolidated Holdings","Berkeley Gardens12  Brewery , London"));
            Add(new AddresseeRecord("Sven","Drachenblut Delikatessen","Walserweg 21, Aachen"));
            Add(new AddresseeRecord("Janine", "Du monde entier", "67, rue des Cinquante Otages, Nantes"));
        }
    }

    public class AddresseeRecord {
        private string fName;
        private string fCompany;
        private string fAddress;

        public string Name {
            get { return fName; }
            set { fName = value; }
        }
        public string Company {
            get { return fCompany; }
            set { fCompany = value; }
        }
        public string Address {
            get { return fAddress; }
            set { fAddress = value; }
        }

        public AddresseeRecord(string fName, string fCompany, string fAddress) {
            this.fName = fName;            
            this.fCompany = fCompany;
            this.fAddress = fAddress;
        }
    }
}
