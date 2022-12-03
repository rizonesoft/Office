Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Windows.Forms

Namespace RichEditCustomInsertMergeFieldMenu
	Public Class DataBindingController
		Private Shared bindingContext As New BindingContext()
		Private dataSource As Object
		Private dataMember As String
		Private bindingManager As BindingManagerBase = Nothing
		Private itemProperties As PropertyDescriptorCollection = Nothing

		Public Sub New(ByVal dataSource As Object, ByVal dataMember As String)
			Me.dataSource = dataSource
			Me.dataMember = dataMember
			InitializeBindingManagerAndItemProperties()
		End Sub

		Private Sub InitializeBindingManagerAndItemProperties()
			If dataSource IsNot Nothing Then
				If dataMember.Length > 0 Then
					bindingManager = bindingContext(dataSource, dataMember)
				Else
					bindingManager = bindingContext(dataSource)
				End If
			End If
			If bindingManager IsNot Nothing Then
				itemProperties = bindingManager.GetItemProperties()
			End If
		End Sub

		Public ReadOnly Property ItemsCount() As Integer
			Get
				Return If(bindingManager IsNot Nothing, bindingManager.Count, 0)
			End Get
		End Property

		Public ReadOnly Property ColumnNames() As List(Of String)
			Get
				Dim list As New List(Of String)()

				If itemProperties IsNot Nothing Then
					Dim count As Integer = itemProperties.Count
					For i As Integer = 0 To count - 1
						list.Add(itemProperties(i).Name)
					Next i
				End If

				Return list
			End Get
		End Property

		Public Function GetColumnInfo(ByVal columnName As String) As PropertyDescriptor
			If itemProperties IsNot Nothing Then
				Dim prop As PropertyDescriptor = itemProperties.Find(columnName, False)

				If prop Is Nothing Then
					Throw New ArgumentException(String.Format("'{0}' column does not exist", columnName))
				End If

				Return (If(itemProperties IsNot Nothing, itemProperties(columnName), Nothing))
			End If

			Return Nothing
		End Function

		Public Function GetRowValue(ByVal columnName As String, ByVal rowIndex As Integer) As Object
			If bindingManager IsNot Nothing AndAlso itemProperties IsNot Nothing Then
				Dim prop As PropertyDescriptor = itemProperties.Find(columnName, False)

				If prop Is Nothing Then
					Throw New ArgumentException(String.Format("'{0}' column does not exist", columnName))
				End If

				If TypeOf bindingManager Is CurrencyManager Then
					Return prop.GetValue(CType(bindingManager, CurrencyManager).List(rowIndex))
				Else
					If rowIndex <> 0 Then
						Throw New ArgumentOutOfRangeException("rowIndex")
					End If
					Return prop.GetValue(CType(bindingManager, PropertyManager).Current)
				End If
			End If

			Return Nothing
		End Function
	End Class
End Namespace
