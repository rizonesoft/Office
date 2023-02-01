Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Windows.Forms
Imports DevExpress.XtraRichEdit.API.Native

Namespace RichEditCustomizeMergeFields
	Partial Public Class Form1
		Inherits Form
		Public Sub New()
			InitializeComponent()

			Dim invoices As New List(Of Invoice)(10)

			invoices.Add(New Invoice(0, "Invoice1", 10.0D, Guid.NewGuid()))
			invoices.Add(New Invoice(1, "Invoice2", 15.0D, Guid.NewGuid()))
			invoices.Add(New Invoice(2, "Invoice3", 20.0D, Guid.NewGuid()))

			richEditControl1.Options.MailMerge.DataSource = invoices
		End Sub

		Private Sub richEditControl1_CustomizeMergeFields(ByVal sender As Object, ByVal e As DevExpress.XtraRichEdit.CustomizeMergeFieldsEventArgs) Handles richEditControl1.CustomizeMergeFields
			Dim mergeFieldNames As New List(Of MergeFieldName)(e.MergeFieldsNames)

			mergeFieldNames.Remove(mergeFieldNames.Find(Function(mfn) mfn.Name.ToLower() = "password"))
			mergeFieldNames.ForEach(AddressOf ChangeDisplayName)
			mergeFieldNames.Sort(New ReverseComparer())

			e.MergeFieldsNames = mergeFieldNames.ToArray()
		End Sub

		Private Shared Sub ChangeDisplayName(ByVal mfn As MergeFieldName)
			mfn.DisplayName &= " (field)"
		End Sub
	End Class

	Public Class ReverseComparer
		Implements IComparer(Of MergeFieldName)
		#Region "IComparer<MergeFieldName> Members"
		Public Function Compare(ByVal mfn1 As MergeFieldName, ByVal mfn2 As MergeFieldName) As Integer Implements IComparer(Of MergeFieldName).Compare
			Return -String.Compare(mfn1.Name, mfn2.Name)
		End Function
		#End Region
	End Class

	Public Class Invoice
		Private id_Renamed As Integer

		Public Property Id() As Integer
			Get
				Return id_Renamed
			End Get
			Set(ByVal value As Integer)
				id_Renamed = value
			End Set
		End Property
		Private description_Renamed As String

		Public Property Description() As String
			Get
				Return description_Renamed
			End Get
			Set(ByVal value As String)
				description_Renamed = value
			End Set
		End Property
		Private price_Renamed As Decimal

		Public Property Price() As Decimal
			Get
				Return price_Renamed
			End Get
			Set(ByVal value As Decimal)
				price_Renamed = value
			End Set
		End Property
		Private password_Renamed As Guid

		Public Property Password() As Guid
			Get
				Return password_Renamed
			End Get
			Set(ByVal value As Guid)
				password_Renamed = value
			End Set
		End Property

		Public Sub New(ByVal id As Integer, ByVal description As String, ByVal price As Decimal, ByVal password As Guid)
			Me.Id = id
			Me.Description = description
			Me.Price = price
			Me.Password = password
		End Sub
	End Class

End Namespace