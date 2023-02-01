Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Text
Imports System.Collections

Namespace ProgressIndicator
	Friend Class SampleData
		Inherits ArrayList
		Public Sub New()
			Add(New AddresseeRecord("Maria", "Alfreds Futterkiste", "Obere Str. 57, Berlin"))
			Add(New AddresseeRecord("Ana", "Ana Trujillo Emparedados y helados", "Avda. de la Constitucion 2222, Mexico D.F."))
			Add(New AddresseeRecord("Antonio", "Antonio Moreno Taqueria", "Mataderos  2312, Mexico D.F."))
			Add(New AddresseeRecord("Thomas", "Around the Horn", "120 Hanover Sq., London"))
			Add(New AddresseeRecord("Christina", "Berglunds snabbkop", "Berguvsvagen  8, Lulea"))
			Add(New AddresseeRecord("Hanna", "Blauer See Delikatessen", "Forsterstr. 57, Mannheim"))
			Add(New AddresseeRecord("Frederique", "Blondel pere et fils", "24, place Kleber, Strasbourg"))
			Add(New AddresseeRecord("Martin", "Bolido Comidas preparadas", "C/ Araquil, 67, Madrid"))
			Add(New AddresseeRecord("Laurence", "Bon app'", "12, rue des Bouchers, Marseille"))
			Add(New AddresseeRecord("Elizabeth", "Bottom-Dollar Markets", "23 Tsawassen Blvd., Tsawwassen"))
			Add(New AddresseeRecord("Victoria", "B's Beverages", "Fauntleroy Circus, London"))
			Add(New AddresseeRecord("Patricio", "Cactus Comidas para llevar", "Cerrito 333, Buenos Aires"))
			Add(New AddresseeRecord("Francisco", "Centro comercial Moctezuma", "Sierras de Granada 9993, Mexico D.F."))
			Add(New AddresseeRecord("Yang", "Chop-suey Chinese", "Hauptstr. 29, Bern"))
			Add(New AddresseeRecord("Pedro", "Comercio Mineiro", "Av. dos Lusiadas, 23, Sao Paulo"))
			Add(New AddresseeRecord("Elizabeth","Consolidated Holdings","Berkeley Gardens12  Brewery , London"))
			Add(New AddresseeRecord("Sven","Drachenblut Delikatessen","Walserweg 21, Aachen"))
			Add(New AddresseeRecord("Janine", "Du monde entier", "67, rue des Cinquante Otages, Nantes"))
		End Sub
	End Class

	Public Class AddresseeRecord
		Private fName As String
		Private fCompany As String
		Private fAddress As String

		Public Property Name() As String
			Get
				Return fName
			End Get
			Set(ByVal value As String)
				fName = value
			End Set
		End Property
		Public Property Company() As String
			Get
				Return fCompany
			End Get
			Set(ByVal value As String)
				fCompany = value
			End Set
		End Property
		Public Property Address() As String
			Get
				Return fAddress
			End Get
			Set(ByVal value As String)
				fAddress = value
			End Set
		End Property

		Public Sub New(ByVal fName As String, ByVal fCompany As String, ByVal fAddress As String)
			Me.fName = fName
			Me.fCompany = fCompany
			Me.fAddress = fAddress
		End Sub
	End Class
End Namespace
