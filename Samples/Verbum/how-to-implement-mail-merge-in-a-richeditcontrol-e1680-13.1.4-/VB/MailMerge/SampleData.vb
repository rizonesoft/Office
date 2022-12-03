Imports System
Imports System.Text

Namespace MailMerge
    #Region "#sampledata"
    Friend Class SampleData
        Inherits System.Collections.ArrayList

        Public Sub New()
            Add(New AddresseeRecord("Andrew", "XYZ Inc.", "Tullamore Way, 21"))
            Add(New AddresseeRecord("Benny", "ABC Ltd.", "Casablanca Rd., 46"))
            Add(New AddresseeRecord("Jose", "CASA S.A.", "Paseo di Ronda, 88"))
        End Sub
    End Class
    Public Class AddresseeRecord
        Public Property Name() As String
        Public Property Company() As String
        Public Property Address() As String
        Public Sub New(ByVal fName As String, ByVal fCompany As String, ByVal fAddress As String)
            Name = fName
            Company = fCompany
            Address = fAddress
        End Sub
    End Class
    #End Region ' #sampledata
End Namespace