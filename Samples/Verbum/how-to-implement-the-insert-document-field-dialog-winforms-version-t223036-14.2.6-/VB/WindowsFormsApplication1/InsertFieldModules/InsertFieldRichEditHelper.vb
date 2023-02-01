Imports Microsoft.VisualBasic
Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Text
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraBars.Ribbon
Imports DevExpress.XtraBars
Imports System.Drawing
Imports System.Windows.Forms

Namespace WindowsFormsApplication1.InsertFieldModules

    Public Module InsertFieldRichEditHelper
        Private privateRichControl As RichEditControl
        Public Property RichControl() As RichEditControl
            Get
                Return privateRichControl
            End Get
            Set(ByVal value As RichEditControl)
                privateRichControl = value
            End Set
        End Property
        Private privateInsertDialog As InsertFieldDialog
        Public Property InsertDialog() As InsertFieldDialog
            Get
                Return privateInsertDialog
            End Get
            Set(ByVal value As InsertFieldDialog)
                privateInsertDialog = value
            End Set
        End Property

        Private _variableTypes As New System.Collections.Generic.SortedDictionary(Of String, UserControl)()
        Public ReadOnly Property VariableTypes() As System.Collections.Generic.SortedDictionary(Of String, UserControl)
            Get
                Return _variableTypes
            End Get
        End Property
        Private privateCurrentVariableType As String
        Public Property CurrentVariableType() As String
            Get
                Return privateCurrentVariableType
            End Get
            Set(ByVal value As String)
                privateCurrentVariableType = value
            End Set
        End Property


        <System.Runtime.CompilerServices.Extension()> _
        Public Sub RegisterInsertFieldDialogCommand(ByVal richEdit As RichEditControl, ByVal pageGroup As RibbonPageGroup, ByVal commandImage As Image)
            Dim buttonInsertFieldDialog As New BarButtonItem(pageGroup.Ribbon.Manager, "Insert Field")
            buttonInsertFieldDialog.LargeGlyph = If(commandImage IsNot Nothing, commandImage, Image.FromFile("InsertFieldModules\\insertFieldIcon.png"))
            AddHandler buttonInsertFieldDialog.ItemClick, AddressOf buttonInsertFieldDialog_ItemClick
            pageGroup.ItemLinks.Add(buttonInsertFieldDialog)

            RichControl = richEdit
        End Sub


        Private Sub CreateVariablesTypes()
            _variableTypes.Add("DOCVARIABLE", New ucDOCVARIABLE())
            _variableTypes.Add("PAGE", New ucPAGENUMBER("PAGE"))
            _variableTypes.Add("NUMPAGES", New ucPAGENUMBER("NUMPAGES"))
            _variableTypes.Add("CREATEDATE", New ucCREATEDATE())
            _variableTypes.Add("DATE", New ucCREATEDATE())
            _variableTypes.Add("TIME", New ucCREATEDATE())
            _variableTypes.Add("IF", New ucIFFIELD())

        End Sub

        Private Sub buttonInsertFieldDialog_ItemClick(ByVal sender As Object, ByVal e As ItemClickEventArgs)
            If VariableTypes.Keys.Count = 0 Then
                CreateVariablesTypes()
            End If
            If InsertDialog Is Nothing Then
                InsertDialog = New InsertFieldDialog(RichControl)
            End If
            InsertDialog.ShowDialog()
        End Sub

        Public Const EmptyFieldCode As String = "EMPTYFIELD"
    End Module

    ' Additional service classes
    Public Interface IFieldParametersDialog
        Function GenerateFieldParametersString() As String
    End Interface

    Public Class FieldAttributeItem
        Private privateDisplayName As String
        Public Property DisplayName() As String
            Get
                Return privateDisplayName
            End Get
            Set(ByVal value As String)
                privateDisplayName = value
            End Set
        End Property
        Private privateAttributeValue As String
        Public Property AttributeValue() As String
            Get
                Return privateAttributeValue
            End Get
            Set(ByVal value As String)
                privateAttributeValue = value
            End Set
        End Property
    End Class
End Namespace
