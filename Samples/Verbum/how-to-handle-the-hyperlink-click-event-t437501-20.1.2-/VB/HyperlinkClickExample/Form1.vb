Imports DevExpress.Office.Utils
Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports HyperlinkClickExample.Forms
Imports System
Imports System.Collections.Generic
Imports System.Drawing

Namespace HyperlinkClickExample
    Partial Public Class Form1
        Inherits DevExpress.XtraBars.Ribbon.RibbonForm

        #Region "#DataList"
        Private Shared products As List(Of String) = CreateProducts()
        Private Shared Function CreateProducts() As List(Of String)
            Dim result As New List(Of String)()
            result.Add("XtraScheduler™ Suite")
            result.Add("XtraRichEdit™ Suite")
            result.Add("XtraSpellChecker™")
            result.Add("XtraReports™ Suite")
            result.Add("XtraGrid™ Suite")
            result.Add("XtraPivotGrid™ Suite")
            result.Add("XtraTreeList™ Suite")
            result.Add("XtraGauges™ Suite")
            result.Add("XtraWizard™ Control")
            result.Add("XtraVerticalGrid™ Suite")
            result.Add("XtraCharts™ Suite")
            result.Add("XtraLayoutControl™ Suite")
            result.Add("XtraNavBar™")
            result.Add("XtraEditors™ Library")
            result.Add("XtraPrinting™ Library")
            Return result
        End Function
        #End Region ' #DataList

        Public Sub New()
            InitializeComponent()
            richEditControl1.LoadDocument("HyperlinkClickHandling.rtf")
            AddHandler richEditControl1.HyperlinkClick, AddressOf OnHyperlinkClick
        End Sub

        #Region "#HyperlinkClickEvent"
        Public activeLink As Hyperlink
        Private Sub OnHyperlinkClick(ByVal sender As Object, ByVal e As HyperlinkClickEventArgs)
            activeLink = e.Hyperlink
            Dim form As New SelectProductForm(products)
            ' Set the Commit event handler:
            AddHandler form.Commit, AddressOf OnProductFormCommit
            'Set the Range property to the hyperlink range:
            form.Range = activeLink.Range
            'Specify the Location property to specify the location where the form is going to be invoked:  
            form.Location = GetFormLocation()
            form.Show()
            e.Handled = True
        End Sub

        'This method places the form to the right of the cursor position: 
        Private Function GetFormLocation() As Point
            Dim position As DocumentPosition = Me.richEditControl1.Document.CaretPosition
            Dim rect As Rectangle = Me.richEditControl1.GetBoundsFromPosition(position)
            Dim location As New Point(rect.Right, rect.Bottom)
            Dim localPoint As Point = Units.DocumentsToPixels(location, Me.richEditControl1.DpiX, Me.richEditControl1.DpiY)
            Return Me.richEditControl1.PointToScreen(localPoint)
        End Function
        #End Region ' #HyperlinkClickEvent

        #Region "#OnProductFormCommit"

        ' Handle the event to replace the hyperlink with the selected item value: 
        Private Sub OnProductFormCommit(ByVal sender As Object, ByVal e As EventArgs)
            Dim form As SelectProductForm = DirectCast(sender, SelectProductForm)
            Dim value As String = DirectCast(form.EditValue, String)
            Dim document As Document = Me.richEditControl1.Document
            document.BeginUpdate()
            document.Replace(form.Range, value)
            'Uncomment this line to remove the clicked hyperlink once a desired value has been selected
            'richEditControl1.Document.Hyperlinks.Remove(activeLink);
            document.EndUpdate()
        End Sub

        #End Region ' #OnProductFormCommit




    End Class
End Namespace



