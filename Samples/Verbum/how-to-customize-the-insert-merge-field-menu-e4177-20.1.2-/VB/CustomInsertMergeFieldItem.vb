Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Drawing
Imports System.Reflection
Imports DevExpress.XtraBars
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports DevExpress.XtraRichEdit.Commands
Imports DevExpress.XtraRichEdit.Localization
Imports DevExpress.XtraRichEdit.UI

Namespace RichEditCustomInsertMergeFieldMenu
	Public Class CustomInsertMergeFieldItem
		Inherits BarButtonItem

		Private popupMenu As PopupMenu

		Public Sub New()
			InitializeItem()
		End Sub

		Public Sub New(ByVal manager As BarManager)
			MyBase.New(manager, "")
			InitializeItem()
		End Sub

'INSTANT VB NOTE: The variable caption was renamed since Visual Basic does not handle local variables named the same as class members well:
		Public Sub New(ByVal caption_Conflict As String)
			MyBase.New(Nothing, caption_Conflict)
			InitializeItem()
		End Sub

'INSTANT VB NOTE: The variable caption was renamed since Visual Basic does not handle local variables named the same as class members well:
		Public Sub New(ByVal manager As BarManager, ByVal caption_Conflict As String)
			MyBase.New(manager, caption_Conflict)
			InitializeItem()
		End Sub

		Private Sub InitializeItem()
			Me.popupMenu = New PopupMenu()
			AddHandler popupMenu.BeforePopup, AddressOf Me.OnBeforePopup
		End Sub

		#Region "Properties"
		<Browsable(False)>
		<EditorBrowsable(EditorBrowsableState.Never)>
		<DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)>
		Public Overrides Property ButtonStyle() As BarButtonStyle
			Get
				Return BarButtonStyle.DropDown
			End Get
			Set(ByVal value As BarButtonStyle)
			End Set
		End Property
		<Browsable(False)>
		<EditorBrowsable(EditorBrowsableState.Never)>
		<DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)>
		Public Overrides Property DropDownControl() As PopupControl
			Get
				Return popupMenu
			End Get
			Set(ByVal value As PopupControl)
			End Set
		End Property
		<Browsable(False)>
		<EditorBrowsable(EditorBrowsableState.Never)>
		<DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)>
		Public Overrides Property Caption() As String
			Get
				Return XtraRichEditLocalizer.Active.GetLocalizedString(XtraRichEditStringId.MenuCmd_InsertMergeField)
			End Get
			Set(ByVal value As String)
			End Set
		End Property
		<Browsable(False)>
		<EditorBrowsable(EditorBrowsableState.Never)>
		<DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)>
		Public Overrides Property Glyph() As Image
			Get
				Return Image.FromStream(System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("Images.InsertDataField_16x16.png"))
			End Get
			Set(ByVal value As Image)
			End Set
		End Property
		<Browsable(False)>
		<EditorBrowsable(EditorBrowsableState.Never)>
		<DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)>
		Public Overrides Property LargeGlyph() As Image
			Get
				Return Image.FromStream(System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream("Images.InsertDataField_32x32.png"))
			End Get
			Set(ByVal value As Image)
			End Set
		End Property
'INSTANT VB NOTE: The field richEditControl was renamed since Visual Basic does not allow fields to have the same name as other class members:
		Private richEditControl_Conflict As RichEditControl
		Public Property RichEditControl() As RichEditControl
			Get
				Return richEditControl_Conflict
			End Get
			Set(ByVal value As RichEditControl)
				richEditControl_Conflict = value
			End Set
		End Property
		#End Region

		Private Sub PopulatePopupMenu()
			Dim mailMergeOptions As RichEditMailMergeOptions = RichEditControl.Options.MailMerge
			Dim mergeFieldsController As New DataBindingController(mailMergeOptions.DataSource, mailMergeOptions.DataMember)
			Dim columnNames As List(Of String) = mergeFieldsController.ColumnNames
			Dim subItems As New Dictionary(Of String, BarSubItem)()

			For i As Integer = 0 To columnNames.Count - 1
				Dim fullColumnName As String = columnNames(i)

				Dim dotIndex As Integer = fullColumnName.IndexOf("."c)

				If dotIndex = -1 Then
					Dim item As InsertMergeFieldMenuItem = New CustomInsertMergeFieldMenuItem(RichEditControl, New MergeFieldName(fullColumnName))
					Me.popupMenu.ItemLinks.Add(item)
				Else
					Dim groupName As String = fullColumnName.Substring(0, dotIndex)
					Dim columnName As String = fullColumnName.Substring(groupName.Length + 1)

					If Not subItems.ContainsKey(groupName) Then
						Dim subItem As New BarSubItem()
						subItem.Caption = groupName
						subItems.Add(groupName, subItem)
						Me.popupMenu.ItemLinks.Add(subItem)
					End If

					Dim item As InsertMergeFieldMenuItem = New CustomInsertMergeFieldMenuItem(RichEditControl, New MergeFieldName(fullColumnName, columnName))
					subItems(groupName).ItemLinks.Add(item)
				End If
			Next i
		End Sub

		Private Sub RefreshPopupMenu()
			DeletePopupItems()
			If RichEditControl IsNot Nothing Then
				PopulatePopupMenu()
			End If
		End Sub

		Private Sub DeletePopupItems()
			Dim itemLinks As BarItemLinkCollection = Me.popupMenu.ItemLinks
			Me.popupMenu.BeginUpdate()
			Try
				Do While itemLinks.Count > 0
					itemLinks(0).Item.Dispose()
				Loop
			Finally
				Me.popupMenu.EndUpdate()
			End Try
		End Sub

		Private Sub OnBeforePopup(ByVal sender As Object, ByVal e As CancelEventArgs)
			RefreshPopupMenu()
		End Sub

		Protected Overrides Sub OnClick(ByVal link As BarItemLink)
			If RichEditControl IsNot Nothing Then
				RichEditControl.CreateCommand(RichEditCommandId.ShowInsertMergeFieldForm).Execute()
			End If
		End Sub

		Protected Overrides Sub OnManagerChanged()
			MyBase.OnManagerChanged()
			Me.popupMenu.Manager = Me.Manager
		End Sub

		#Region "IDisposable implementation"
		Protected Overrides Sub Dispose(ByVal disposing As Boolean)
			MyBase.Dispose(disposing)
			If disposing Then
				If popupMenu IsNot Nothing Then
					DeletePopupItems()
					popupMenu.Dispose()
					popupMenu = Nothing
				End If
			End If
		End Sub
		#End Region
	End Class

	Public Class CustomInsertMergeFieldMenuItem
		Inherits InsertMergeFieldMenuItem

		Private control As RichEditControl
		Private fieldName As String

		Public Sub New(ByVal control As RichEditControl, ByVal mergeFieldName As MergeFieldName)
			MyBase.New(control, mergeFieldName)
			DevExpress.Utils.Guard.ArgumentNotNull(control, "control")
			Me.control = control
			Me.fieldName = mergeFieldName.Name
		End Sub

		Protected Overrides Sub OnClick(ByVal link As BarItemLink)
			control.Document.Fields.Create(control.Document.CaretPosition, String.Format(" MERGEFIELD {0} ", Me.fieldName))
		End Sub
	End Class
End Namespace